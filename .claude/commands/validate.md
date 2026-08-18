---
description: Validate generated Playwright code against coding standards and feature-file coverage
allowed-tools: ["Read", "Glob", "Grep"]
---

Run two independent checks against everything under `tests/` and `pages/`
generated for the current feature file(s). Do not modify any code in this
stage — report only. Fixes happen in `/gen-playwright` (regeneration) or
`/execute`'s self-heal loop (runtime fixes).

## Check 1 — Coding standards
For every generated spec/page file, flag violations of the rules in
CLAUDE.md:
- Any locator not traceable back to a `search_locators` result (i.e. a
  hardcoded selector that doesn't match anything in
  `memory/known-good-snippets/` or a recent `search_locators` call) —
  flag as "unverified locator".
- Any `page.waitForTimeout` or other hard wait — flag as "hard wait,
  replace with auto-retrying assertion/locator action".
- Locator strategy not following priority order (CSS/XPath used where
  a `getByRole`/`getByLabel`/`getByTestId` was available per the locator
  index) — flag with the preferred alternative.
- Step logic living directly in the spec file instead of a Page Object
  method — flag as "POM violation".
- Missing `# source: <ISSUE-KEY>` traceability header on the spec file.

## Check 2 — Scenario coverage
Compare each `features/*.feature` file against its generated
`tests/*.spec.ts` counterpart:
- Every `Scenario:` (and every row of every `Scenario Outline` /
  `Examples:` table) must have exactly one corresponding test function.
- Every `Given`/`When`/`Then`/`And`/`But` step in that scenario must map
  to a step call in the generated test — none dropped, none silently
  merged into another step.
- Flag: missing scenarios, missing steps within a covered scenario, and
  any extra test logic present in the spec that has no corresponding
  Gherkin step (scope creep).

## Output
A single report, grouped by file, listing every flagged item with
severity (blocker vs minor) and a one-line suggested fix. End with a
pass/fail summary line: `Standards: X issues | Coverage: Y scenarios
missing, Z steps missing`. If both are zero, say so plainly — do not
invent findings to seem thorough.
