#!/usr/bin/env python3
"""sync-skills — 将 ~/shared-skills/ 同步到各 agent 的 skill 目录。

单向同步：共享源 → agent。修改必须从共享源开始。
用法: python3 sync-skills.sh [--dry-run] [skill-name]
"""

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


def build_hermes_frontmatter(skill_name: str, meta: dict) -> str:
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
    lines.append("---")
    return "\n".join(lines)


def build_claude_frontmatter(skill_name: str, meta: dict) -> str:
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
        "---",
    ]
    return "\n".join(lines)


def build_codex_frontmatter(skill_name: str, meta: dict) -> str:
    """生成 Codex 格式的 YAML frontmatter。"""
    description = meta.get("codex", {}).get("description", skill_name)
    return f"---\nname: {skill_name}\ndescription: {description}\n---"


def build_openclaw_frontmatter(skill_name: str, meta: dict) -> str:
    """生成 OpenClaw 格式的 YAML frontmatter。"""
    description = meta.get("codex", {}).get("description", skill_name)
    return f"---\nname: {skill_name}\ndescription: {description}\n---"


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

    print(f"\n{'[DRY RUN] ' if dry_run else ''}Syncing: {skill_name}")

    # --- Hermes ---
    category = meta.get("hermes", {}).get("category", "shared")
    hermes_path = AGENT_CONFIGS["hermes"]["base"] / category / skill_name / "SKILL.md"
    hermes_body = build_hermes_frontmatter(skill_name, meta) + "\n\n" + inline_references(body, skill_name)
    if dry_run:
        print(f"  → Hermes: {hermes_path}")
    else:
        hermes_path.parent.mkdir(parents=True, exist_ok=True)
        hermes_path.write_text(hermes_body)
        print(f"  ✓ Hermes: {hermes_path}")

    # --- Claude Code ---
    claude_path = AGENT_CONFIGS["claude"]["base"] / skill_name / "SKILL.md"
    claude_body = build_claude_frontmatter(skill_name, meta) + "\n\n" + body
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
    codex_body = build_codex_frontmatter(skill_name, meta) + "\n\n" + inline_references(body, skill_name)
    if dry_run:
        print(f"  → Codex: {codex_path}")
    else:
        codex_path.parent.mkdir(parents=True, exist_ok=True)
        codex_path.write_text(codex_body)
        print(f"  ✓ Codex: {codex_path}")

    # --- OpenClaw ---
    openclaw_path = AGENT_CONFIGS["openclaw"]["base"] / skill_name / "SKILL.md"
    openclaw_body = build_openclaw_frontmatter(skill_name, meta) + "\n\n" + body
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


def main():
    dry_run = "--dry-run" in sys.argv

    # Target specific skill(s) or all
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    manifest = load_manifest()

    if args:
        targets = [a for a in args if a in manifest]
        if not targets:
            print(f"No skills found: {args}")
            sys.exit(1)
    else:
        targets = list(manifest.keys())

    print(f"Sync source: {SHARED}")
    print(f"Targets: {', '.join(targets)}")
    if dry_run:
        print("Mode: DRY RUN (no files written)")

    for name in targets:
        sync_skill(name, manifest[name], dry_run=dry_run)

    print(f"\nDone. Synced {len(targets)} skill(s).")


if __name__ == "__main__":
    main()
