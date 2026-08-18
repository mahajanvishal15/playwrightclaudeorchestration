---
description: Generate a Playwright spec + step definitions from reference.feature
allowed-tools: ["search_locators", "index_status", "Read", "Write", "Glob"]
---

Read `features/reference.feature`. For each Given/When/Then step:

1. Check `memory/known-good-snippets/` for an existing implementation of an
   equivalent step first. Reuse it if found (with a comment noting reuse).
2. Otherwise, call `search_locators` with a natural-language description of
   the element the step interacts with (include a `page_hint` if the
   feature/scenario name suggests a specific page). Never guess a selector
   that didn't come from `search_locators`.
3. Generate the step definition using the suggested locator, following
   the rules in CLAUDE.md (POM structure, no hard waits, getByRole priority).
4. Write new/updated Page Object methods under `pages/`.
5. Save the new step implementation to `memory/known-good-snippets/` so
   future runs can reuse it.

Output the generated spec to `tests/<feature-name>.spec.ts` and stop —
do not execute it yet (that's `/execute`).
