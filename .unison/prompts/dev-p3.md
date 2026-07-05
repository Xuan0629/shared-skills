# P3: Sync Log

## Goal
Record every sync operation for audit trail.

## Implementation
1. Create `sync.log` in `~/shared-skills/` (JSON Lines format)
2. For each skill synced, append a line:
   ```json
   {"timestamp":"2026-07-06T12:00:00Z","skill":"planning-with-files","agent":"hermes","action":"updated","hash_before":"abc123","hash_after":"def456"}
   ```
3. Log actions: "created", "updated", "skipped" (unchanged), "removed"
4. Add `--show-log` CLI flag to display recent sync history

Run test and commit.