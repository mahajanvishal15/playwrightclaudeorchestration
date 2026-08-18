"""
index_locators.py

Crawls the HTML source collection, extracts interactable elements with
their best-available locator attributes, and stores them as embeddings
in a local Chroma vector store for retrieval by locator_mcp_server.py.

Run this once initially, then re-run only when files under HTML_SOURCE_DIR
change (it hashes files and skips unchanged ones on incremental runs).

Usage:
    python3 scripts/index_locators.py --source ./html-source --db ./memory/locator-chroma-db
"""

import argparse
import hashlib
import json
import pathlib
import sys

from bs4 import BeautifulSoup
import chromadb

# Tags/attributes worth indexing as locator candidates.
INTERACTABLE_TAGS = {"a", "button", "input", "select", "textarea", "label", "option"}
ROLE_HINT_ATTRS = ["role", "aria-label", "aria-labelledby", "data-testid",
                    "id", "name", "placeholder", "title", "type", "value"]

MANIFEST_NAME = "index-manifest.json"


def file_hash(path: pathlib.Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def extract_elements(html_path: pathlib.Path):
    """Return a list of (chunk_text, metadata) for one HTML file."""
    soup = BeautifulSoup(html_path.read_text(errors="ignore"), "html.parser")
    elements = []

    candidates = soup.find_all(
        lambda tag: tag.name in INTERACTABLE_TAGS or tag.has_attr("role")
    )

    for el in candidates:
        attrs = {a: el.get(a) for a in ROLE_HINT_ATTRS if el.get(a)}
        text = el.get_text(strip=True)[:80]

        # Skip elements with no usable identifying info at all.
        if not attrs and not text:
            continue

        # Suggested Playwright locator, in priority order.
        if attrs.get("role") and (attrs.get("aria-label") or text):
            suggested = f'page.get_by_role("{attrs["role"]}", name="{attrs.get("aria-label") or text}")'
        elif attrs.get("aria-label"):
            suggested = f'page.get_by_label("{attrs["aria-label"]}")'
        elif attrs.get("data-testid"):
            suggested = f'page.get_by_test_id("{attrs["data-testid"]}")'
        elif attrs.get("id"):
            suggested = f'page.locator("#{attrs["id"]}")'
        elif attrs.get("name"):
            suggested = f'page.locator("[name=\'{attrs["name"]}\']")'
        else:
            suggested = f'page.get_by_text("{text}")' if text else None

        if not suggested:
            continue

        chunk_text = " ".join(
            filter(None, [el.name, text, json.dumps(attrs)])
        )

        elements.append((
            chunk_text,
            {
                "file": str(html_path),
                "tag": el.name,
                "text": text,
                "suggested_locator": suggested,
                **{f"attr_{k}": v for k, v in attrs.items()},
            },
        ))

    return elements


def load_manifest(db_dir: pathlib.Path) -> dict:
    p = db_dir / MANIFEST_NAME
    if p.exists():
        return json.loads(p.read_text())
    return {}


def save_manifest(db_dir: pathlib.Path, manifest: dict):
    (db_dir / MANIFEST_NAME).write_text(json.dumps(manifest, indent=2))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", default="./html-source",
                         help="Folder containing dev HTML files to index")
    parser.add_argument("--db", default="./memory/locator-chroma-db",
                         help="Folder to persist the Chroma vector store")
    parser.add_argument("--full", action="store_true",
                         help="Force full re-index, ignoring the manifest")
    args = parser.parse_args()

    source_dir = pathlib.Path(args.source)
    db_dir = pathlib.Path(args.db)
    db_dir.mkdir(parents=True, exist_ok=True)

    if not source_dir.exists():
        print(f"Source folder not found: {source_dir}", file=sys.stderr)
        sys.exit(1)

    client = chromadb.PersistentClient(path=str(db_dir))
    collection = client.get_or_create_collection("locators")

    manifest = {} if args.full else load_manifest(db_dir)
    html_files = list(source_dir.rglob("*.html")) + list(source_dir.rglob("*.htm"))

    indexed, skipped = 0, 0
    for html_path in html_files:
        h = file_hash(html_path)
        key = str(html_path)
        if manifest.get(key) == h:
            skipped += 1
            continue

        # Remove any stale entries for this file, then re-add.
        collection.delete(where={"file": key})

        elements = extract_elements(html_path)
        if elements:
            ids = [f"{key}::{i}" for i in range(len(elements))]
            docs = [e[0] for e in elements]
            metas = [e[1] for e in elements]
            collection.add(ids=ids, documents=docs, metadatas=metas)

        manifest[key] = h
        indexed += 1
        print(f"Indexed {len(elements):>3} elements from {html_path}")

    save_manifest(db_dir, manifest)
    print(f"\nDone. {indexed} file(s) (re)indexed, {skipped} unchanged and skipped.")
    print(f"Total elements in store: {collection.count()}")


if __name__ == "__main__":
    main()
