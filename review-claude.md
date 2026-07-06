# Review: sync-skills.py (Second Review — After Bug Fixes)

**Date:** 2026-07-06
**Verdict:** ✅ **PASS**

## Verification Commands

| Command | Result |
|---|---|
| `python3 -m py_compile sync-skills.py` | PASS |
| `python3 sync-skills.py --check` | PASS — all 8 skills show UP-TO-DATE or OUTDATED status |
| `python3 sync-skills.py --dry-run codebase-design` | PASS — no crash, openclaw correctly skipped |
| `python3 sync-skills.py --show-log` | PASS — shows 3 prior sync entries (codebase-design → hermes/claude/codex) |

## Specific Checks

### 1. `sync_skill()` uses `_do_agent()` helper that checks `sync_to` before syncing
✅ **CONFIRMED.** `_do_agent()` at line 307 checks `if agent not in sync_targets:` and skips accordingly. Verified by dry-run: codebase-design skips openclaw because its `sync_to` is `[hermes, claude, codex]`.

### 2. `main()` uses `load_skill_meta()` instead of manifest dict
✅ **CONFIRMED.** Line 458: `meta = load_skill_meta(name)` reads from per-skill `meta.yaml`, not from `load_manifest()`.

### 3. `log_sync()` is called after each agent write
✅ **CONFIRMED.** Line 327: called inside the `else` branch (non-dry-run path) after `path.write_text(content)`. Not called during dry runs — correct behavior.

### 4. `meta.yaml` files exist for all 8 skills with correct `sync_to`
✅ **CONFIRMED.** All 8 skills (codebase-design, design-system, diagnosing-bugs, domain-modeling, grill-design, handoff, planning-with-files, role-play) have `meta.yaml` files with valid `sync_to` lists.

## Minor Observations (Non-Blocking)

- **Naming in `check_skills()`:** Line 383 uses `meta` as the loop variable for manifest agent configs (`for skill_name, meta in manifest.items()`). Since `main()` now uses `load_skill_meta()` for per-skill metadata, this variable name is misleading — it holds manifest data, not meta.yaml data. Functionally correct because the manifest duplicates hermes category info, but could confuse future readers. Not a bug.
- **`compute_source_hash` scope:** Only hashes `SKILL.md + meta.yaml`. References and scripts are excluded. Intentional per the docstring (line 141-142), but means a reference-only change won't trigger an "OUTDATED" status in `--check`.

## Summary

All four verification commands pass cleanly. All four specific checks are confirmed correct. The fixes from the first review are properly applied: `_do_agent()` respects `sync_to`, `main()` uses per-skill `meta.yaml`, `log_sync()` fires after writes, and all `meta.yaml` files are present with correct `sync_to` entries. No blocking issues found.
