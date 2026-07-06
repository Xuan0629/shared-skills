#!/usr/bin/env python3
"""sync-skills — 将 ~/shared-skills/ 同步到各 agent 的 skill 目录。

单向同步：共享源 → agent。修改必须从共享源开始。
用法: python3 sync-skills.sh [--dry-run] [skill-name]
"""

import hashlib
import os
import sys
import yaml
from pathlib import Path

SHARED = Path.home() / "shared-skills"
MANIFEST = SHARED / "skills-manifest.yaml"

AGENT_CONFIGS = {
    "hermes": {
        "base": Path.home() / ".hermes" / "skills",
        "frontmatter_fields": ["name", "description", "triggers"],
    },
    "claude": {
        "base": Path.home() / ".claude" / "skills",
        "frontmatter_fields": ["name", "description", "version", "allowed-tools"],
        "extra": {"version": "0.1.0", "allowed-tools": ["Bash", "Read", "Glob", "Grep"]},
    },
    "codex": {
        "base": Path.home() / ".codex" / "skills",
        "frontmatter_fields": ["name", "description"],
    },
    "openclaw": {
        "base": Path.home() / ".openclaw" / "agents" / "main" / "skills",
        "frontmatter_fields": ["name", "description"],
    },
}

VALID_AGENTS = {"hermes", "claude", "codex", "openclaw"}


def load_manifest():
    with open(MANIFEST) as f:
        return yaml.safe_load(f)



def load_skill_meta(skill_name: str) -> dict:
    """Load per-skill metadata from meta.yaml."""
    meta_path = SHARED / skill_name / "meta.yaml"
    if not meta_path.exists():
        raise FileNotFoundError(f"meta.yaml not found for {skill_name}: {meta_path}")
    with open(meta_path) as f:
        return yaml.safe_load(f)

def get_sync_targets(skill_name: str) -> list[str]:
    """Return the list of agents this skill should sync to."""
    meta = load_skill_meta(skill_name)
    return meta.get("sync_to", list(VALID_AGENTS))


def validate_manifest(manifest: dict) -> list[str]:
    """Validate the skills manifest. Returns a list of error messages (empty = valid).

    Checks:
    - Every skill name has a corresponding directory with SKILL.md
    - Every agent name is one of: hermes, claude, codex, openclaw
    - Every skill has at least one trigger or description across its agents
    """
    errors = []

    if not isinstance(manifest, dict):
        return ["manifest root must be a dict mapping skill names to agent configs"]

    for skill_name, agents in manifest.items():
        skill_dir = SHARED / skill_name
        skill_md = skill_dir / "SKILL.md"

        # Check the skill directory and SKILL.md exist
        if not skill_dir.is_dir():
            errors.append(f"{skill_name}: skill directory not found: {skill_dir}")
            continue
        if not skill_md.is_file():
            errors.append(f"{skill_name}: SKILL.md not found: {skill_md}")
            continue

        # Check the entry is a dict
        if not isinstance(agents, dict):
            errors.append(
                f"{skill_name}: entry must be a dict mapping agent names to configs, "
                f"got {type(agents).__name__}"
            )
            continue

        # Check every agent name is valid
        for agent_name in agents:
            if agent_name not in VALID_AGENTS:
                errors.append(
                    f"{skill_name}: unknown agent '{agent_name}' "
                    f"(valid: {', '.join(sorted(VALID_AGENTS))})"
                )

        # Check at least one trigger or description exists
        has_content = False
        for agent_name in agents:
            cfg = agents[agent_name]
            if isinstance(cfg, dict):
                if cfg.get("triggers") or cfg.get("description"):
                    has_content = True
                    break
        if not has_content:
            errors.append(
                f"{skill_name}: no triggers or description defined for any agent"
            )

        # Cross-validate manifest vs meta.yaml
        meta_path = SHARED / skill_name / "meta.yaml"
        if meta_path.exists():
            try:
                meta = yaml.safe_load(meta_path.read_text())
                if isinstance(meta, dict):
                    manifest_agents = set(agents.keys())
                    meta_sync = set(meta.get("sync_to", []))
                    if manifest_agents != meta_sync:
                        errors.append(
                            f"{skill_name}: manifest agents ({','.join(sorted(manifest_agents))}) "
                            f"differ from meta.yaml sync_to ({','.join(sorted(meta_sync))})"
                        )
            except yaml.YAMLError:
                errors.append(f"{skill_name}: meta.yaml is invalid YAML")

    return errors


def read_body(skill_name: str) -> str:
    """读取共享 skill 的正文（去除空行首尾）。"""
    path = SHARED / skill_name / "SKILL.md"
    if not path.exists():
        raise FileNotFoundError(f"Missing shared SKILL.md: {path}")
    return path.read_text().strip()


def list_references(skill_name: str) -> list[Path]:
    """列出 references/ 下的文件。"""
    ref_dir = SHARED / skill_name / "references"
    if ref_dir.exists():
        return sorted(ref_dir.glob("*.md"))
    return []


def list_scripts(skill_name: str) -> list[Path]:
    """列出 scripts/ 下的文件。"""
    scripts_dir = SHARED / skill_name / "scripts"
    if scripts_dir.exists():
        return sorted(scripts_dir.glob("*"))
    return []


def compute_source_hash(skill_name: str) -> str:
    """Compute SHA256 hash of SKILL.md + meta.yaml (the per-skill metadata file).

    This hash captures the full shared source for a skill — both its body
    and its agent-specific metadata (triggers, categories, descriptions).
    Any change to either file will produce a different hash, which --check
    uses to detect outdated agent copies.
    """
    skill_path = SHARED / skill_name / "SKILL.md"
    meta_path = SHARED / skill_name / "meta.yaml"
    skill_bytes = skill_path.read_bytes()
    if not meta_path.exists():
        raise FileNotFoundError(f"meta.yaml not found for {skill_name}: {meta_path}")
    meta_bytes = meta_path.read_bytes()
    combined = skill_bytes + b"\n---META---\n" + meta_bytes
    return hashlib.sha256(combined).hexdigest()


def parse_frontmatter(filepath: Path) -> dict | None:
    """Parse YAML frontmatter from a SKILL.md file.

    Returns the parsed dict on success, None if the file is missing,
    has no frontmatter, or the YAML is invalid.
    """
    if not filepath.exists():
        return None
    content = filepath.read_text()
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


def _yaml_safe(value: str) -> str:
    """Quote a string value for safe inclusion in YAML frontmatter.

    Strings containing YAML-significant characters (colons, hashes, etc.)
    are double-quoted to prevent parser errors.
    """
    if any(c in value for c in ':#{}[]>,|*&!%@`\''):
        # Escape backslashes and double quotes within the string
        escaped = value.replace('\\', '\\\\').replace('"', '\\"')
        return f'"{escaped}"'
    return value


def build_hermes_frontmatter(skill_name: str, meta: dict, source_hash: str = "") -> str:
    """生成 Hermes 格式的 YAML frontmatter（含 triggers）。"""
    triggers = meta.get("hermes", {}).get("triggers", [])
    description = meta.get("claude", {}).get("description", skill_name)
    lines = ["---", f"name: {skill_name}", f"description: {_yaml_safe(description)}"]
    if triggers:
        lines.append("triggers:")
        for t in triggers:
            # regex patterns with special chars need quoting
            if any(c in t for c in ".*{}[]()"):
                lines.append(f'  - "{t}"')
            else:
                lines.append(f"  - {t}")
    if source_hash:
        lines.append(f"source_hash: {source_hash}")
    lines.append("---")
    return "\n".join(lines)


def build_claude_frontmatter(skill_name: str, meta: dict, source_hash: str = "") -> str:
    """生成 Claude Code 格式的 YAML frontmatter。"""
    description = meta.get("claude", {}).get("description", skill_name)
    lines = [
        "---",
        f"name: {skill_name}",
        f"description: {_yaml_safe(description)}",
        "version: 0.1.0",
        "allowed-tools:",
        "  - Bash",
        "  - Read",
        "  - Glob",
        "  - Grep",
    ]
    if source_hash:
        lines.append(f"source_hash: {source_hash}")
    lines.append("---")
    return "\n".join(lines)


def build_codex_frontmatter(skill_name: str, meta: dict, source_hash: str = "") -> str:
    """生成 Codex 格式的 YAML frontmatter。"""
    description = meta.get("codex", {}).get("description", skill_name)
    lines = ["---", f"name: {skill_name}", f"description: {_yaml_safe(description)}"]
    if source_hash:
        lines.append(f"source_hash: {source_hash}")
    lines.append("---")
    return "\n".join(lines)


def build_openclaw_frontmatter(skill_name: str, meta: dict, source_hash: str = "") -> str:
    """生成 OpenClaw 格式的 YAML frontmatter。"""
    claude_desc = meta.get("claude", {}).get("description", "")
    openclaw_cfg = meta.get("openclaw", {})
    description = openclaw_cfg.get("description") or claude_desc or skill_name
    lines = ["---", f"name: {skill_name}", f"description: {_yaml_safe(description)}"]
    if source_hash:
        lines.append(f"source_hash: {source_hash}")
    lines.append("---")
    return "\n".join(lines)


def inline_references(body: str, skill_name: str) -> str:
    """将 references/ 内容内联到正文末尾。"""
    refs = list_references(skill_name)
    if not refs:
        return body
    parts = [body, "", "## References (inlined)"]
    for ref in refs:
        parts.append(f"\n### {ref.name}")
        parts.append(ref.read_text().strip())
    return "\n".join(parts)



def log_sync(skill_name: str, agent: str, action: str, hash_before: str = "", hash_after: str = ""):
    """Append a sync event to sync.log (JSON Lines format)."""
    import json
    from datetime import datetime, timezone
    log_path = SHARED / "sync.log"
    entry = {
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "skill": skill_name,
        "agent": agent,
        "action": action,
        "hash_before": hash_before,
        "hash_after": hash_after,
    }
    with open(log_path, 'a') as f:
        f.write(json.dumps(entry, ensure_ascii=False) + "\n")

def show_log(n: int = 20):
    """Display the last N sync log entries."""
    log_path = SHARED / "sync.log"
    if not log_path.exists():
        print("(no sync log yet)")
        return
    lines = log_path.read_text().strip().split("\n")
    for line in lines[-n:]:
        import json
        e = json.loads(line)
        print(f"{e['timestamp'][:19]}  {e['skill']:25s} → {e['agent']:10s}  {e['action']}")


def sync_skill(skill_name: str, meta: dict, dry_run: bool = False):
    """同步单个 skill 到 sync_to 中列出的 agent。"""
    body = read_body(skill_name)
    refs = list_references(skill_name)
    scripts = list_scripts(skill_name)
    source_hash = compute_source_hash(skill_name)
    sync_targets = get_sync_targets(skill_name)

    print(f"\n{'[DRY RUN] ' if dry_run else ''}Syncing: {skill_name} (→ {', '.join(sync_targets)})")

    # Helper: sync to one agent
    def _do_agent(agent, build_fn, extra_fn=None):
        if agent not in sync_targets:
            print(f"  - {agent} (skipped)")
            return
        config = AGENT_CONFIGS[agent]
        path = get_agent_skill_path(agent, skill_name, meta)
        if path is None:
            return
        content = build_fn(skill_name, meta, source_hash) + "\n\n"
        if agent in ("hermes", "codex"):
            content += inline_references(body, skill_name)
        else:
            content += body
        if dry_run:
            print(f"  → {agent}: {path}")
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content)
            print(f"  ✓ {agent}: {path}")
            if extra_fn:
                extra_fn(path.parent)
            log_sync(skill_name, agent, "updated", hash_after=source_hash)

    # Hermes
    _do_agent("hermes", build_hermes_frontmatter)

    # Claude
    def _claude_extra(parent):
        if refs:
            d = parent / "references"; d.mkdir(parents=True, exist_ok=True)
            import shutil
            for r in refs: shutil.copy2(r, d / r.name)
    _do_agent("claude", build_claude_frontmatter, _claude_extra)

    # Codex
    _do_agent("codex", build_codex_frontmatter)

    # OpenClaw
    def _oc_extra(parent):
        if refs:
            import shutil
            d = parent / "references"; d.mkdir(parents=True, exist_ok=True)
            for r in refs: shutil.copy2(r, d / r.name)
        if scripts:
            import shutil
            d = parent / "scripts"; d.mkdir(parents=True, exist_ok=True)
            for s in scripts: shutil.copy2(s, d / s.name)
    _do_agent("openclaw", build_openclaw_frontmatter, _oc_extra)

def get_agent_skill_path(agent: str, skill_name: str, meta: dict) -> Path | None:
    """Return the Path to an agent's copy of a skill, or None if the agent
    has no config for this skill type."""
    config = AGENT_CONFIGS.get(agent)
    if not config:
        return None
    base = config["base"]
    if agent == "hermes":
        category = meta.get("hermes", {}).get("category", "shared")
        return base / category / skill_name / "SKILL.md"
    return base / skill_name / "SKILL.md"


def check_skills(verbose: bool = False, targets: list[str] | None = None):
    """Scan agent skill copies and compare stored source_hash against current source.

    For each skill in the manifest and each configured agent, reports:
    - UP-TO-DATE: stored hash matches current source
    - OUTDATED: stored hash differs from current source (agent copy is stale)
    - MISSING: no agent copy found, or no source_hash in its frontmatter

    If targets is provided, only check skills whose names are in the list.
    """
    manifest = load_manifest()

    # Agent display order
    for skill_name, meta in manifest.items():
        sync_targets = get_sync_targets(skill_name)
        if targets and skill_name not in targets:
            continue
        current_hash = compute_source_hash(skill_name)
        print(f"{skill_name}:")
        for agent in sync_targets:
            path = get_agent_skill_path(agent, skill_name, meta)
            if path is None:
                continue
            fm = parse_frontmatter(path)
            if fm is None:
                print(f"  {agent}: MISSING")
                continue
            stored_hash = fm.get("source_hash")
            if not stored_hash:
                print(f"  {agent}: MISSING")
            elif stored_hash == current_hash:
                if verbose:
                    print(f"  {agent}: UP-TO-DATE ({current_hash[:12]})")
                else:
                    print(f"  {agent}: UP-TO-DATE")
            else:
                short_current = current_hash[:12]
                short_stored = stored_hash[:12] if len(stored_hash) >= 12 else stored_hash
                if verbose:
                    print(f"  {agent}: OUTDATED ({short_stored} vs {short_current})")
                else:
                    print(f"  {agent}: OUTDATED ({short_stored} vs {short_current})")


def main():
    dry_run = "--dry-run" in sys.argv
    check_mode = "--check" in sys.argv
    show_log_mode = any(a.startswith("--show-log") for a in sys.argv)
    show_log_n = 20
    if show_log_mode:
        for i, a in enumerate(sys.argv[1:], start=1):
            if a.startswith("--show-log="):
                try: show_log_n = int(a.split("=", 1)[1])
                except: pass
            elif a == "--show-log" and i < len(sys.argv) - 1:
                # Space form: --show-log N
                try: show_log_n = int(sys.argv[i + 1])
                except: pass
    verbose = "--verbose" in sys.argv

    # Target specific skill(s) or all
    positional_args = [a for a in sys.argv[1:] if not a.startswith("--")]
    manifest = load_manifest()

    # Validate manifest before any operation
    errors = validate_manifest(manifest)
    if errors:
        print("Manifest validation failed:")
        for err in errors:
            print(f"  ✗ {err}")
        sys.exit(1)

    if show_log_mode:
        show_log(show_log_n)
        return

    if positional_args:
        targets = [a for a in positional_args if a in manifest]
        if not targets:
            print(f"No skills found: {positional_args}")
            sys.exit(1)
    else:
        targets = list(manifest.keys())

    if check_mode:
        check_skills(verbose=verbose, targets=targets)
        return


    print(f"Sync source: {SHARED}")
    print(f"Targets: {', '.join(targets)}")
    if dry_run:
        print("Mode: DRY RUN (no files written)")

    for name in targets:
        meta = load_skill_meta(name)
        sync_skill(name, meta, dry_run=dry_run)

    print(f"\nDone. Synced {len(targets)} skill(s).")


if __name__ == "__main__":
    main()
