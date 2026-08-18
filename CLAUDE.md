# Claude-Based Playwright Orchestration — Project Instructions

## What this project does
Reads BDD test cases from Xray (via Jira MCP), converts them to a
`reference.feature` file, generates Playwright test code using locators
resolved from an indexed HTML locator store, validates the generated
code, executes it via Playwright MCP, and self-heals failures.

## Pipeline stages (run as separate slash commands — see .claude/commands/)
1. `/fetch-xray <TEST-KEY>`   — pull Gherkin from Xray via Jira MCP
2. `/gen-feature`             — write reference.feature from fetched Gherkin
3. `/gen-playwright`          — generate spec + step defs using locator search
4. `/validate`                — check coding standards + scenario coverage
5. `/execute`                 — run via Playwright MCP, capture results
6. `/heal`                    — classify + fix failures (locator/script/app defect)

## Non-negotiable rules
- NEVER invent a selector. Every locator used in generated code must come
  from a `search_locators` call against the indexed locator store — no
  guessing at `id`/`class` names from memory.
- Locator priority: `getByRole` > `getByLabel` > `getByTestId` > CSS (last resort).
- No hard waits (`page.waitForTimeout`). Use Playwright's auto-retrying
  `expect()` assertions and locator actions instead.
- One feature file scenario → one test function. Do not merge or drop
  scenarios during generation — this is checked in `/validate`.
- Page Object Model: one class per page/feature under `pages/`, step
  definitions call into POM methods, not raw locators directly.
- Every generated spec file gets a header comment linking back to the
  source Xray key.

## Folder structure
```
features/              reference.feature files (one per Xray test/epic)
pages/                 Page Object classes
tests/                 generated Playwright spec files
scripts/               indexing + utility scripts (locator vector store)
memory/                pipeline state: locator-index.json, defect-log.md,
                        known-good-snippets/
.claude/agents/        subagent definitions, one per pipeline stage
.claude/commands/       slash commands wrapping each stage
```

## Memory loop (token discipline)
- `memory/locator-index.json` — rebuilt only when files under `html-source/`
  change (see scripts/index_locators.py). Never re-crawl HTML on every run.
- `memory/known-good-snippets/` — reusable step-definition functions already
  validated; `/gen-playwright` checks here before generating a step fresh.
- `memory/defect-log.md` — app-level functional issues already found; `/heal`
  checks this before re-diagnosing a failure from scratch.
- Each stage's subagent should only load the memory files it needs, not the
  whole `memory/` folder.

## Tool usage
- Jira MCP: read-only usage only (fetch issue/test details). Never write
  back to Jira from this pipeline without explicit user confirmation.
- Playwright MCP: used for execution + tracing in `/execute` and `/heal`.
- Locator search: use the `search_locators` MCP tool (see .mcp.json,
  scripts/locator_mcp_server.py) — do not read raw files under
  `html-source/` directly in generation prompts.
