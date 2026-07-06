# Shared Skills · 共享 Skill 管理系统

[**English**](README.md) | [中文](README_CN.md)

> Single source of truth, multi-agent sync — update once, take effect everywhere: Claude Code / Codex / Hermes / OpenClaw.

When multiple AI agents collaborate, skills must stay consistent across every agent. Manual copying causes version drift and degrades review quality. shared-skills solves this.

## Installation

```bash
git clone https://github.com/Xuan0629/shared-skills.git
cd shared-skills
```

Requirements: Python 3.10+, standard library only (zero third-party dependencies).

## Usage

```bash
# Sync all skills to their configured target agents
python3 sync-skills.py

# Check whether synced skills match the source
python3 sync-skills.py --check

# View sync log
python3 sync-skills.py --show-log

# Start the Web UI Dashboard
cd webui && python3 -m http.server 8080
```

## How It Works

```
shared-skills/          # Single source of truth
├── skill-name/
│   ├── SKILL.md        # Skill content
│   └── meta.yaml       # Metadata (version, sync targets, per-agent config)
├── skills-manifest.yaml
├── sync-skills.py       # Format conversion + sync engine
└── webui/               # Dashboard

        ↓ sync-skills.py

~/.hermes/skills/...    ~/.claude/skills/...    ~/.codex/skills/...    ~/.openclaw/.../skills/
    (Hermes format)       (Claude format)         (Codex format)         (OpenClaw format)
```

`sync-skills.py` reads source skills, converts them to each agent's required format (frontmatter, file structure), and writes them to the target directories.

## Adding a New Skill

```bash
mkdir my-skill
# Write my-skill/SKILL.md
# Write my-skill/meta.yaml (specify sync_to: [hermes, claude, codex])
python3 sync-skills.py
```

`meta.yaml` format:

```yaml
version: "1.0.0"
sync_to: [hermes, claude, codex]   # Target agent list
hermes:
  category: software-development
  description: "Description"
claude:
  description: "Description"
codex:
  description: "Description"
```

## Web UI Dashboard

The `webui/` directory provides a visual dashboard showing sync status for every skill across all agents.

```bash
cd webui && python3 -m http.server 8080
```

Then open `http://localhost:8080`.

## Companion Project

shared-skills is the recommended companion tool for the [Unison](https://github.com/Xuan0629/unison) multi-agent collaboration framework. In Unison workflows, shared-skills ensures every reviewing agent uses identical skill definitions — eliminating version drift.

## License

MIT
