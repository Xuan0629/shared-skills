#!/usr/bin/env python3
"""Generate webui/data.json — imports core logic from sync_skills module."""
import hashlib
import json
import os
import sys
import yaml
from datetime import datetime, timezone
from pathlib import Path

# Add parent to path so we can import sync_skills
sys.path.insert(0, str(Path(__file__).parent.parent))

import sync_skills as ss

OUTPUT = Path(__file__).parent / "data.json"
AGENT_LABELS = {"hermes": "Hermes", "claude": "Claude Code", "codex": "Codex", "openclaw": "OpenClaw"}

def build_data():
    manifest = ss.load_manifest()
    agents = []
    skills = []

    # Agent info
    for akey in ss.VALID_AGENTS:
        last_sync = _last_sync_time(akey)
        agents.append({
            "key": akey, "label": AGENT_LABELS.get(akey, akey),
            "skill_count": 0, "last_sync": last_sync,
            "status": "active" if last_sync else "inactive"
        })

    # Skill info
    for name in manifest:
        meta = ss.load_skill_meta(name)
        targets = meta.get("sync_to", list(ss.VALID_AGENTS))
        source_hash = ss.compute_source_hash(name)

        skill = {
            "name": name,
            "description": meta.get("claude", {}).get("description", name),
            "sync_to": targets,
            "status": "synced",
            "agents": {},
            "last_updated": None
        }

        for agent in ss.VALID_AGENTS:
            path = ss.get_agent_skill_path(agent, name, meta)
            fm = ss.parse_frontmatter(path) if path else None
            agent_status = "missing"
            agent_hash = ""
            if fm:
                agent_hash = fm.get("source_hash", "")
                agent_status = "synced" if agent_hash == source_hash else "outdated"
            if agent not in targets:
                agent_status = "disabled"

            skill["agents"][agent] = {
                "status": agent_status,
                "hash": agent_hash[:12] if agent_hash else "",
                "path": str(path) if path else ""
            }

            # Update agent skill count
            for a in agents:
                if a["key"] == agent and agent_status in ("synced", "outdated"):
                    a["skill_count"] += 1

        skills.append(skill)

    return {"agents": agents, "skills": skills, "generated": datetime.now(timezone.utc).isoformat()}

def _last_sync_time(agent):
    log_path = ss.SHARED / "sync.log"
    if not log_path.exists():
        return None
    try:
        lines = log_path.read_text().strip().split("\n")
        for line in reversed(lines):
            e = json.loads(line)
            if e.get("agent") == agent:
                return e.get("timestamp", "")
    except:
        pass
    return None

if __name__ == "__main__":
    data = build_data()
    OUTPUT.write_text(json.dumps(data, indent=2, ensure_ascii=False))
    print(f"Generated {OUTPUT} ({len(json.dumps(data))} bytes)")
