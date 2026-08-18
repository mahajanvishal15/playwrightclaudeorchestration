---
description: Execute the generated Playwright spec via Playwright MCP and self-heal failures
allowed-tools: ["mcp__playwright__*", "search_locators", "Read", "Edit"]
---

Run the spec at `tests/<feature-name>.spec.ts` using the Playwright MCP tools.

For each failing step:
1. Check `memory/defect-log.md` for a matching known functional issue first —
   if found, report it again rather than re-diagnosing.
2. Classify the failure:
   - **Locator broken** (element not found/changed) → call `search_locators`
     again for that element, update the Page Object method, re-run just that
     scenario.
   - **Script/logic bug** (wrong assertion, race condition, bad step logic) →
     patch the step definition directly, re-run just that scenario.
   - **App defect** (locator + logic are correct but the app behaves
     incorrectly) → do NOT modify the test. Append it to
     `memory/defect-log.md` with steps to reproduce and expected vs actual.
3. Re-run at most 2 times per scenario before stopping and flagging for
   human review — do not loop indefinitely on the same failure.

At the end, output a summary: scenarios passed, scenarios auto-healed
(with what was fixed), and scenarios flagged as functional/app issues.
