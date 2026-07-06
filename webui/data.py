#!/usr/bin/env python3
"""Generate webui/data.json by scanning the shared-skills filesystem.

Reads the manifest, per-skill meta.yaml, agent skill copies, and sync.log
to produce a complete JSON snapshot for the web dashboard.
"""

import hashlib
import json
import os
import yaml
from datetime import datetime, timezone
from pathlib import Path

SHARED = Path.home() / "shared-skills"
MANIFEST = SHARED / "skills-manifest.yaml"
SYNC_LOG = SHARED / "sync.log"
OUTPUT = SHARED / "webui" / "data.json"

VALID_AGENTS = ["hermes", "claude", "codex", "openclaw"]

AGENT_CONFIGS = {
    "hermes": {
        "base": str(Path.home() / ".hermes" / "skills"),
        "label": "Hermes",
    },
    "claude": {
        "base": str(Path.home() / ".claude" / "skills"),
        "label": "Claude Code",
    },
    "codex": {
        "base": str(Path.home() / ".codex" / "skills"),
        "label": "Codex",
    },
    "openclaw": {
        "base": str(Path.home() / ".openclaw" / "agents" / "main" / "skills"),
        "label": "OpenClaw",
    },
}

AGENT_LABELS_CN = {
    "hermes": "Hermes",
    "claude": "Claude Code",
    "codex": "Codex",
    "openclaw": "OpenClaw",
}


def load_manifest():
    with open(MANIFEST) as f:
        return yaml.safe_load(f)


def load_skill_meta(skill_name):
    meta_path = SHARED / skill_name / "meta.yaml"
    if not meta_path.exists():
        return {}
    with open(meta_path) as f:
        return yaml.safe_load(f)


def compute_source_hash(skill_name):
    skill_path = SHARED / skill_name / "SKILL.md"
    meta_path = SHARED / skill_name / "meta.yaml"
    if not skill_path.exists() or not meta_path.exists():
        return ""
    combined = skill_path.read_bytes() + b"\n---META---\n" + meta_path.read_bytes()
    return hashlib.sha256(combined).hexdigest()


def parse_frontmatter(filepath):
    p = Path(filepath)
    if not p.exists():
        return None
    content = p.read_text()
    if not content.startswith("---"):
        return None
    end = content.find("---", 3)
    if end == -1:
        return None
    fm_text = content[3:end].strip()
    if not fm_text:
        return None
    try:
        parsed = yaml.safe_load(fm_text)
        return parsed if isinstance(parsed, dict) else None
    except yaml.YAMLError:
        return None


def get_agent_skill_path(agent, skill_name, meta):
    """Return the Path to an agent's copy of a skill."""
    if agent not in AGENT_CONFIGS:
        return None
    base = Path(AGENT_CONFIGS[agent]["base"])
    if agent == "hermes":
        category = meta.get("hermes", {}).get("category", "shared")
        return base / category / skill_name / "SKILL.md"
    return base / skill_name / "SKILL.md"


def get_skill_description(skill_name, meta):
    """Extract the best available description for a skill."""
    # Try claude description first (usually most detailed)
    desc = meta.get("claude", {}).get("description", "")
    if not desc:
        desc = meta.get("codex", {}).get("description", "")
    if not desc:
        desc = meta.get("hermes", {}).get("description", "")
    return desc or skill_name


def load_sync_log():
    """Parse sync.log into a dict: (skill, agent) -> {timestamp, hash}."""
    entries = {}
    if not SYNC_LOG.exists():
        return entries
    for line in SYNC_LOG.read_text().strip().split("\n"):
        if not line:
            continue
        try:
            e = json.loads(line)
        except json.JSONDecodeError:
            continue
        key = (e.get("skill", ""), e.get("agent", ""))
        entries[key] = {
            "timestamp": e.get("timestamp", ""),
            "hash_after": e.get("hash_after", ""),
        }
    return entries


def main():
    manifest = load_manifest()
    sync_entries = load_sync_log()

    # Build per-agent data
    agents = {}
    for agent_key in VALID_AGENTS:
        cfg = AGENT_CONFIGS[agent_key]
        agents[agent_key] = {
            "key": agent_key,
            "name": cfg["label"],
            "name_cn": AGENT_LABELS_CN.get(agent_key, cfg["label"]),
            "base_path": cfg["base"],
        }

    # Build skills data
    skills = []
    total_synced = 0
    total_outdated = 0
    total_missing = 0
    total_disabled = 0

    for skill_name in sorted(manifest.keys()):
        meta = load_skill_meta(skill_name)
        sync_to = meta.get("sync_to", list(VALID_AGENTS))
        source_hash = compute_source_hash(skill_name)
        description = get_skill_description(skill_name, meta)

        skill_entry = {
            "name": skill_name,
            "description": description,
            "sync_to": sync_to,
            "source_hash": source_hash[:12] if source_hash else "",
            "agents": {},
        }

        for agent_key in VALID_AGENTS:
            is_target = agent_key in sync_to
            path = get_agent_skill_path(agent_key, skill_name, meta)

            # Determine status
            if not is_target:
                status = "disabled"
            elif path is None or not path.exists():
                status = "missing"
            else:
                fm = parse_frontmatter(path)
                if fm is None or not fm.get("source_hash"):
                    status = "missing"
                elif fm["source_hash"] == source_hash:
                    status = "synced"
                else:
                    status = "outdated"

            # Get last sync info
            log_key = (skill_name, agent_key)
            last_sync = sync_entries.get(log_key, {})

            agent_info = {
                "status": status,
                "path": str(path) if path else "",
                "stored_hash": "",
                "last_sync": last_sync.get("timestamp", ""),
            }

            if status in ("synced", "outdated") and path:
                fm = parse_frontmatter(path)
                if fm and fm.get("source_hash"):
                    agent_info["stored_hash"] = fm["source_hash"][:12]

            skill_entry["agents"][agent_key] = agent_info

            # Count statuses
            if status == "synced":
                total_synced += 1
            elif status == "outdated":
                total_outdated += 1
            elif status == "missing":
                total_missing += 1
            elif status == "disabled":
                total_disabled += 1

        skills.append(skill_entry)

    # Compute per-agent stats
    for agent_key in VALID_AGENTS:
        synced = sum(
            1 for s in skills if s["agents"][agent_key]["status"] == "synced"
        )
        outdated = sum(
            1 for s in skills if s["agents"][agent_key]["status"] == "outdated"
        )
        missing = sum(
            1 for s in skills if s["agents"][agent_key]["status"] == "missing"
        )
        disabled = sum(
            1 for s in skills if s["agents"][agent_key]["status"] == "disabled"
        )
        active = synced + outdated

        # Last sync time for this agent (most recent across all skills)
        timestamps = []
        for s in skills:
            ts = s["agents"][agent_key].get("last_sync", "")
            if ts:
                timestamps.append(ts)
        last_sync = max(timestamps) if timestamps else ""

        agents[agent_key].update({
            "synced": synced,
            "outdated": outdated,
            "missing": missing,
            "disabled": disabled,
            "active_skills": active,
            "total_skills": len(skills),
            "last_sync": last_sync,
            # Color code: green/all-synced, yellow/some-outdated, red/none-synced
            "health": (
                "green"
                if active > 0 and outdated == 0
                else "yellow"
                if active > 0
                else "red"
            ),
        })

    output = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "agents": agents,
        "skills": skills,
        "summary": {
            "total_skills": len(skills),
            "total_agents": len(VALID_AGENTS),
            "total_pairs": len(skills) * len(VALID_AGENTS),
            "synced": total_synced,
            "outdated": total_outdated,
            "missing": total_missing,
            "disabled": total_disabled,
        },
    }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT, "w") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

    print(f"Generated: {OUTPUT}")
    print(f"  {len(skills)} skills × {len(VALID_AGENTS)} agents = {len(skills) * len(VALID_AGENTS)} pairs")
    print(f"  synced={total_synced} outdated={total_outdated} missing={total_missing} disabled={total_disabled}")


if __name__ == "__main__":
    main()
