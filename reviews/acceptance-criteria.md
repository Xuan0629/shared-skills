# Acceptance Criteria (FROZEN)

**Frozen at:** 2026-07-05T18:04:05Z
**Test command:** `python3 sync-skills.py --check 2>&1 | head -5`
**Max iterations:** 3

## Rules for Reviewer

1. Judge against these criteria — do not add new criteria mid-review
2. If the code passes the test command, it meets minimum bar
3. REQUEST_CHANGES only for: test failures, security issues, architectural violations

## Project Test Command

```bash
python3 sync-skills.py --check 2>&1 | head -5
```
