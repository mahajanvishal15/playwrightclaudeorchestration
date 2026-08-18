---
description: Generate reference.feature from the Gherkin staged by /fetch-xray
allowed-tools: ["Read", "Write", "Glob"]
---

1. Read every file under `memory/staged/*.gherkin.json` that hasn't
   already been written to a feature file (check `features/` for an
   existing file with a matching `# source: <ISSUE-KEY>` header comment
   before regenerating — skip if already present and unchanged).
2. For each staged test:
   - Write the Gherkin **verbatim** — do not reword steps, reorder
     Given/When/Then, rename the Scenario, or "clean up" phrasing. This
     file is the coverage source of truth for `/validate`, so it must
     match Xray exactly.
   - Preserve Scenario Outlines and their Examples tables exactly as
     provided, including all rows.
   - Preserve tags (`@smoke`, etc.) above the Scenario/Feature line.
   - Add a header comment: `# source: <ISSUE-KEY> — <summary>` and
     `# fetched: <today's date>`.
3. File naming: one feature file per Xray Feature-level grouping —
   `features/<slugified-summary-or-epic>.feature`. If multiple staged
   tests share a Feature (same epic/component), combine their Scenarios
   under one `Feature:` block rather than duplicating the Feature line.
4. After writing, print a scenario count per feature file so it's easy
   to sanity-check against what was fetched (this count is also what
   `/validate` will check coverage against later).

Do not generate any Playwright code in this stage — that's `/gen-playwright`,
and it must run against the feature files written here, not against the
staged JSON directly.
