# P2: Source Hash + --check Mode

## Goal
Track skill versions and detect when agent copies are outdated.

## Implementation
1. In sync-skills.py, before writing a skill to an agent directory:
   - Compute SHA256 of (SKILL.md + meta.yaml)
   - Write `source_hash: <sha256>` into the generated frontmatter
2. Add `--check` CLI argument:
   - Scan each agent's skill directory
   - Compare stored source_hash against current shared source
   - Report: "UP-TO-DATE", "OUTDATED", or "MISSING" for each skill-agent pair
3. Add `--verbose` flag to show hash values

Example output:
```
planning-with-files:
  hermes: OUTDATED (abc123 vs def456)
  claude: UP-TO-DATE
  codex: MISSING
```

Run test and commit.