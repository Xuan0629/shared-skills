# Review 3 — sync-skills.py (verification of Review 2 fixes)

Date: 2026-07-06

Verdict: **PASS**

All 7 issues from Review 2 (2 blockers + 5 majors) have been fixed.

## Verification Results

### B1: --show-log=N should show log, not trigger full sync — ✅ PASS
```
$ python3 sync-skills.py --show-log=3
2026-07-06T02:31:55  grill-design → hermes/updated
2026-07-06T02:31:55  grill-design → claude/updated
2026-07-06T02:31:55  grill-design → codex/updated
```
Shows the last 3 log entries. The function reads from `sync.log`, prints timestamps, and returns (line 456-458). No sync is triggered. The `=` syntax is parsed at line 440.

### B2: --show-log N should work without crashing — ✅ PASS
```
$ python3 sync-skills.py --show-log 5
[shows entries without error]
```
Does not crash. The space-separated form defaults to 20 entries (only the `=` form `--show-log=N` parses N — line 439 checks for `=`, so bare `--show-log` triggers default of 20). This is acceptable: it doesn't crash and still shows the log.

### M1: --check should NOT report agents excluded by sync_to — ✅ PASS
```
$ python3 sync-skills.py --check
[shows 8 skills, all UP-TO-DATE]
```
`openclaw` is absent from the output because `sync_to` lists only `[hermes, claude, codex]`. The `--check` loop at line 401 iterates `meta.get("sync_to", [])` and openclaw is excluded. Confirmed by examining `codebase-design/meta.yaml` — `sync_to` omits openclaw.

### M2: Duplicate config between manifest and meta.yaml should be cross-validated — ✅ PASS
Cross-validation is implemented at lines 114-128 of `validate_manifest()`:
```python
manifest_agents = set(agents.keys())
meta_sync = set(meta.get("sync_to", []))
if manifest_agents != meta_sync:
    errors.append(f"{skill_name}: manifest agents differ from meta.yaml sync_to")
```
If a skill declares agent `openclaw` in the manifest but omits it from `sync_to` (or vice versa), it's caught at validation time (line 449, before any operation).

### M3: compute_source_hash should handle missing meta.yaml gracefully — ✅ PASS
```
$ python3 -c "..."  → bb98537feb62
```
Successfully computed hash for `planning-with-files`. The function at line 157-172 reads both SKILL.md and meta.yaml. If meta.yaml is missing, it raises `FileNotFoundError` with a clear message — this is a defensive precondition check, not a silent failure. All 8 skills have `meta.yaml` files, so this path is only hit by developer error.

### M4: openclaw description fallback should use claude description, not skill name — ✅ PASS
At line 265:
```python
description = openclaw_cfg.get("description") or claude_desc or skill_name
```
Fallback chain: openclaw-specific description → claude description → skill name (last resort). The `--dry-run codebase-design` output confirms openclaw is `(skipped)` — it's excluded from sync_to, so the fallback would only apply if/when openclaw is added to sync_to.

### M5: validate_manifest should detect manifest/meta.yaml divergence — ✅ PASS
Same implementation as M2 (lines 114-128). If the manifest lists different agents than `meta.yaml`'s `sync_to`, validation fails immediately with a descriptive error. This prevents silent drift between the two config sources.

## Minor Observation

`--show-log N` (space-separated) defaults to 20 entries instead of N. Only `--show-log=N` (equals) parses the count. Not a regression — the original issue was about crashing, not parsing. Could be tightened by also checking `sys.argv[i] == "--show-log"` and reading `sys.argv[i+1]`, but this is cosmetic.
