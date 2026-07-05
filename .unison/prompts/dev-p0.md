# P0: Fix OpenClaw Bug + Schema Validation

## Bug: OpenClaw description reads from codex
In sync-skills.py, find `build_openclaw_frontmatter()`. It reads description from `meta.get("codex", ...)` instead of `meta.get("openclaw", ...)`. Fix it.

## Add: Manifest Schema Validation
Add a `validate_manifest()` function that checks:
- Every skill name in manifest has a corresponding directory with SKILL.md
- Every agent name is one of: hermes, claude, codex, openclaw
- Every skill has at least one trigger/description
- Raise clear errors (not silent skip) on invalid entries

Run test command. Commit fixes.