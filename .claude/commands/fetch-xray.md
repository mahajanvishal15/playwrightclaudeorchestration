---
description: Fetch a Xray BDD test case from Jira and stage the raw Gherkin for conversion
allowed-tools: ["mcp__jira__*", "Write"]
---

Argument: `$ARGUMENTS` is the Xray test issue key (e.g. `PROJ-1234`), or a
JQL/epic key if fetching multiple linked tests.

1. Use the Jira MCP tools to fetch the issue(s) for `$ARGUMENTS`.
   - Xray stores Cucumber/Gherkin tests in the issue's "Test Details" /
     "Gherkin Definition" custom field (surfaced by Jira MCP as part of
     the issue fields — inspect the returned fields for something
     containing `Given`/`When`/`Then` text; field name varies by
     instance, commonly `customfield_xxxxx` labeled Cucumber/Gherkin).
   - If `$ARGUMENTS` is an epic/JQL rather than a single test key, fetch
     all linked/child Xray Test issues first, then each one's Gherkin.
2. Read-only. Do not transition status, add comments, or edit the Jira
   issue in any way.
3. Discard everything except: issue key, test summary, the raw Gherkin
   body, tags/labels, and any linked example/data tables. Do not carry
   over comments, watchers, attachments metadata, or changelog — this
   keeps the payload small for the next stage.
4. Write the extracted result to `memory/staged/<ISSUE-KEY>.gherkin.json`
   with this shape:
   ```json
   {
     "key": "PROJ-1234",
     "summary": "...",
     "tags": ["@smoke"],
     "gherkin": "Feature: ...\n  Scenario: ...\n    Given ...\n    When ...\n    Then ...",
     "examples": []
   }
   ```
5. If the Gherkin field is empty or not found, stop and report that
   clearly instead of guessing at scenario content — do not fabricate
   steps from the summary/description alone.

Output a one-line confirmation per issue fetched (key + scenario count).
Do not print the full Gherkin back to the user unless asked — it's
already staged in memory/staged/ for `/gen-feature` to pick up.
