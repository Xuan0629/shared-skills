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


def load_manifest():
    with open(MANIFEST) as f:
        return yaml.safe_load(f)


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


def compute_source_hash(skill_name: str, meta: dict) -> str:
    """Compute SHA256 hash of raw SKILL.md + serialized manifest metadata.

    This hash captures the full shared source for a skill — both its body
    and its agent-specific metadata (triggers, categories, descriptions).
    Any change to either will produce a different hash, which --check uses
    to detect outdated agent copies.
    """
    skill_path = SHARED / skill_name / "SKILL.md"
    skill_bytes = skill_path.read_bytes()
    meta_bytes = yaml.dump(meta, sort_keys=True, allow_unicode=True).encode("utf-8")
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


def build_hermes_frontmatter(skill_name: str, meta: dict, source_hash: str = "") -> str:
    """生成 Hermes 格式的 YAML frontmatter（含 triggers）。"""
    triggers = meta.get("hermes", {}).get("triggers", [])
    description = meta.get("claude", {}).get("description", skill_name)
    lines = ["---", f"name: {skill_name}", f"description: {description}"]
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
        f"description: {description}",
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
    lines = ["---", f"name: {skill_name}", f"description: {description}"]
    if source_hash:
        lines.append(f"source_hash: {source_hash}")
    lines.append("---")
    return "\n".join(lines)


def build_openclaw_frontmatter(skill_name: str, meta: dict, source_hash: str = "") -> str:
    """生成 OpenClaw 格式的 YAML frontmatter。"""
    description = meta.get("openclaw", {}).get("description", skill_name)
    lines = ["---", f"name: {skill_name}", f"description: {description}"]
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


def sync_skill(skill_name: str, meta: dict, dry_run: bool = False):
    """同步单个 skill 到所有 agent。"""
    body = read_body(skill_name)
    refs = list_references(skill_name)
    scripts = list_scripts(skill_name)
    source_hash = compute_source_hash(skill_name, meta)

    print(f"\n{'[DRY RUN] ' if dry_run else ''}Syncing: {skill_name}")

    # --- Hermes ---
    category = meta.get("hermes", {}).get("category", "shared")
    hermes_path = AGENT_CONFIGS["hermes"]["base"] / category / skill_name / "SKILL.md"
    hermes_body = build_hermes_frontmatter(skill_name, meta, source_hash) + "\n\n" + inline_references(body, skill_name)
    if dry_run:
        print(f"  → Hermes: {hermes_path}")
    else:
        hermes_path.parent.mkdir(parents=True, exist_ok=True)
        hermes_path.write_text(hermes_body)
        print(f"  ✓ Hermes: {hermes_path}")

    # --- Claude Code ---
    claude_path = AGENT_CONFIGS["claude"]["base"] / skill_name / "SKILL.md"
    claude_body = build_claude_frontmatter(skill_name, meta, source_hash) + "\n\n" + body
    # Claude Code keeps references/ as separate files
    if dry_run:
        print(f"  → Claude: {claude_path}")
    else:
        claude_path.parent.mkdir(parents=True, exist_ok=True)
        claude_path.write_text(claude_body)
        # Copy references as separate files for Claude Code
        if refs:
            claude_refs_dir = claude_path.parent / "references"
            claude_refs_dir.mkdir(parents=True, exist_ok=True)
            for ref in refs:
                import shutil
                shutil.copy2(ref, claude_refs_dir / ref.name)
        print(f"  ✓ Claude: {claude_path} (+ {len(refs)} refs)")

    # --- Codex ---
    codex_path = AGENT_CONFIGS["codex"]["base"] / skill_name / "SKILL.md"
    codex_body = build_codex_frontmatter(skill_name, meta, source_hash) + "\n\n" + inline_references(body, skill_name)
    if dry_run:
        print(f"  → Codex: {codex_path}")
    else:
        codex_path.parent.mkdir(parents=True, exist_ok=True)
        codex_path.write_text(codex_body)
        print(f"  ✓ Codex: {codex_path}")

    # --- OpenClaw ---
    openclaw_path = AGENT_CONFIGS["openclaw"]["base"] / skill_name / "SKILL.md"
    openclaw_body = build_openclaw_frontmatter(skill_name, meta, source_hash) + "\n\n" + body
    if dry_run:
        print(f"  → OpenClaw: {openclaw_path}")
    else:
        openclaw_path.parent.mkdir(parents=True, exist_ok=True)
        openclaw_path.write_text(openclaw_body)
        # OpenClaw gets full references/ and scripts/ as separate files
        if refs:
            import shutil
            oc_refs_dir = openclaw_path.parent / "references"
            oc_refs_dir.mkdir(parents=True, exist_ok=True)
            for ref in refs:
                shutil.copy2(ref, oc_refs_dir / ref.name)
        if scripts:
            import shutil
            oc_scripts_dir = openclaw_path.parent / "scripts"
            oc_scripts_dir.mkdir(parents=True, exist_ok=True)
            for script in scripts:
                shutil.copy2(script, oc_scripts_dir / script.name)
        print(f"  ✓ OpenClaw: {openclaw_path} (+ {len(refs)} refs, + {len(scripts)} scripts)")


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
    agent_names = list(AGENT_CONFIGS.keys())

    for skill_name, meta in manifest.items():
        if targets and skill_name not in targets:
            continue
        current_hash = compute_source_hash(skill_name, meta)
        print(f"{skill_name}:")
        for agent in agent_names:
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
    verbose = "--verbose" in sys.argv

    # Target specific skill(s) or all
    positional_args = [a for a in sys.argv[1:] if not a.startswith("--")]
    manifest = load_manifest()

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
        sync_skill(name, manifest[name], dry_run=dry_run)

    print(f"\nDone. Synced {len(targets)} skill(s).")


if __name__ == "__main__":
    main()
