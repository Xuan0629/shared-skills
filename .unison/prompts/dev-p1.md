# P1: Manifest Split — meta.yaml Per Skill

## Goal
Move agent metadata from the monolithic `skills-manifest.yaml` into per-skill `meta.yaml` files.

## New Structure
```
~/shared-skills/planning-with-files/
  SKILL.md
  meta.yaml          ← NEW: agent metadata, version, sync_to list
  references/
  scripts/

~/shared-skills/skills-manifest.yaml  ← degraded to index: [skill1, skill2, ...]
```

## meta.yaml Format
```yaml
version: "1.0.0"
sync_to: [hermes, claude, codex]
hermes:
  category: productivity
  triggers: ["plan with files", "制定计划"]
claude:
  description: "Crash-proof persistent file-based planning"
  allowed-tools: [Bash, Read, Glob]
codex:
  description: "Crash-proof persistent file-based planning"
```

## Implementation
1. Create `meta.yaml` in each of the 8 skill directories with existing metadata from skills-manifest.yaml
2. Update `skills-manifest.yaml` to be a simple list: `[planning-with-files, design-system, ...]`
3. Update `sync-skills.py` to read from per-skill meta.yaml instead of the big manifest
4. Add `sync_to` field support — only sync to agents listed in sync_to

Run test command. Commit.