# Verdict: REQUEST_CHANGES

## Findings

1. `sync_skill()` crashes on every normal sync because `sync_targets` is never defined.
   - File: `sync-skills.py:305`
   - Evidence: `python3 sync-skills.py --dry-run codebase-design` fails with `NameError: name 'sync_targets' is not defined`.
   - Expected fix: compute targets inside `sync_skill()` with `get_sync_targets(skill_name)` or pass them in explicitly.

2. Target filtering is structurally broken even after defining `sync_targets`.
   - File: `sync-skills.py:305-354`
   - The path/body/write logic is outside each `else:` block. For a skipped target, the code still proceeds to build and write that target, or references variables like `category`, `claude_path`, `codex_path`, or `openclaw_path` before assignment.
   - Expected fix: wrap each agent's path/body/write block inside its enabled branch, or `continue` through a helper per agent.

3. The new per-skill `meta.yaml` files are not actually used as sync metadata.
   - File: `sync-skills.py:442-479`
   - `main()` still loads `skills-manifest.yaml` and passes `manifest[name]` into `sync_skill()`. `load_skill_meta()` is only used by `get_sync_targets()`, and `get_sync_targets()` is currently unused.
   - Impact: edits to `meta.yaml` affect `source_hash`, but generated frontmatter still comes from the old manifest. This makes `meta.yaml` partly authoritative and partly ignored.
   - Expected fix: either replace manifest metadata loading with `load_skill_meta(name)` or keep the manifest as canonical and do not hash/use per-skill metadata.

4. `log_sync()` writes JSON Lines correctly but is never called.
   - File: `sync-skills.py:266-280`, `sync-skills.py:295-373`
   - The function appends one JSON object plus `\n`, which is valid JSON Lines format. However, sync operations never call it, so `--show-log` has no events to show unless something else writes `sync.log`.
   - Expected fix: call `log_sync()` after each actual agent write, and optionally log skipped/dry-run actions only if that is intended.

## Requested Checks

- `compute_source_hash`: PASS. It hashes `SKILL.md` bytes plus `meta.yaml` bytes with a separator at `sync-skills.py:141-154`.
- `log_sync` JSON Lines format: PASS for the function implementation, REQUEST_CHANGES for integration because it is unused.
- `meta.yaml` structure: PASS. All reviewed files parse as YAML and include `version`, `sync_to`, `hermes`, `claude`, and `codex` metadata consistent with their `sync_to` lists.

## Verification

- `python3 -m py_compile sync-skills.py`: PASS
- `python3 sync-skills.py --dry-run codebase-design`: FAIL, `NameError` for `sync_targets`
- Parsed all `*/meta.yaml` files with `yaml.safe_load`: PASS
