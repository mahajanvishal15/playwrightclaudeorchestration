"""
locator_mcp_server.py

A small MCP server that exposes locator search over the vector store
built by index_locators.py. Claude Code (or any MCP client) queries this
instead of reading raw HTML files, keeping locator-resolution prompts small.

Run standalone for a smoke test:
    python3 scripts/locator_mcp_server.py

Wired into Claude Code via .mcp.json under "locator-store".
"""

import os

import chromadb
from mcp.server.fastmcp import FastMCP

DB_PATH = os.environ.get("LOCATOR_DB_PATH", "./memory/locator-chroma-db")

mcp = FastMCP("locator-store")
_client = chromadb.PersistentClient(path=DB_PATH)
_collection = _client.get_or_create_collection("locators")


@mcp.tool()
def search_locators(query: str, top_k: int = 5, page_hint: str = "") -> str:
    """
    Search the indexed dev HTML collection for elements matching a
    natural-language description (e.g. "submit order button",
    "email input field on login page").

    Args:
        query: what the element does / is called in the feature step.
        top_k: how many candidate matches to return.
        page_hint: optional substring of the file path/page name to
                   narrow results (e.g. "checkout", "login").

    Returns a formatted list of candidate elements with a ready-to-use
    Playwright locator suggestion for each.
    """
    where = {"file": {"$contains": page_hint}} if page_hint else None
    results = _collection.query(
        query_texts=[query],
        n_results=top_k,
        where=where,
    )

    if not results["ids"] or not results["ids"][0]:
        return f"No locator matches found for '{query}'."

    lines = [f"Top {len(results['ids'][0])} locator matches for '{query}':"]
    for meta, dist in zip(results["metadatas"][0], results["distances"][0]):
        lines.append(
            f"- [{meta.get('tag')}] text=\"{meta.get('text', '')}\" "
            f"file={meta.get('file')} | suggested: {meta.get('suggested_locator')} "
            f"(score={1 - dist:.2f})"
        )
    return "\n".join(lines)


@mcp.tool()
def index_status() -> str:
    """Return how many elements are currently indexed in the locator store."""
    return f"{_collection.count()} indexed elements at {DB_PATH}"


if __name__ == "__main__":
    mcp.run()
