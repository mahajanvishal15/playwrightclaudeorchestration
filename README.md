# Setup

## 1. Prerequisites
- Node.js 18+ (for Claude Code and the Playwright/Jira MCP servers)
- Python 3.10+
- Claude Code installed: `npm install -g @anthropic-ai/claude-code`
- A Jira/Xray Cloud site with API access

## 2. Project layout
Unzip/copy this folder as your repo root (or drop these files into an
existing repo). Then create the two folders the scripts expect:
```
mkdir html-source   # put your dev HTML collection here (or symlink it)
mkdir tests pages features
```

## 3. Python environment for the locator store
```bash
cd scripts
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## 4. Build the locator vector store
Point this at wherever your dev HTML collection lives (copy it into
`html-source/` first, or pass a direct path):
```bash
python3 scripts/index_locators.py --source ./html-source --db ./memory/locator-chroma-db
```
Re-run this any time the HTML changes — it hashes files and only
re-indexes what's new/changed. This is the step that keeps later stages
cheap: Claude never reads raw HTML again after this.

## 5. Configure MCP servers
`.mcp.json` is already set up for three servers:
- `jira` — uses Atlassian's remote MCP. First time you use it in Claude
  Code, it'll prompt an OAuth login in your browser.
- `playwright` — `@playwright/mcp`, installed automatically via `npx` on
  first use. Make sure `npx playwright install` has been run once so
  browsers are available.
- `locator-store` — the custom server in `scripts/locator_mcp_server.py`,
  reading the DB you built in step 4. Update the `command`/venv path in
  `.mcp.json` if your Python environment isn't on PATH.

## 6. Open in Claude Code
```bash
cd claude-playwright-orchestration
claude
```
Claude Code auto-loads `CLAUDE.md` and `.mcp.json` on startup. Verify the
servers connected with `/mcp` inside the Claude Code session.

## 7. Run the pipeline
```
/fetch-xray PROJ-1234
/gen-feature
/gen-playwright
/validate
/execute
```
`/execute` includes the self-heal loop (see .claude/commands/execute.md).
Only `/fetch-xray` and `/gen-feature` are stubs to fill in — the two
included commands (`gen-playwright.md`, `execute.md`) show the pattern;
add `fetch-xray.md`, `gen-feature.md`, and `validate.md` the same way,
following the stage descriptions in CLAUDE.md.

## 8. Ongoing use
- Only re-run step 4 (indexing) when HTML changes — not every pipeline run.
- `memory/known-good-snippets/` and `memory/defect-log.md` grow over time;
  periodically review and prune stale entries.
- Everything in `memory/` is local to the repo — commit it (except the
  Chroma DB binary files, which you may want to `.gitignore` and rebuild
  per-environment instead).
