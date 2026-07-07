# Shared Skills

[**English**](README.md) | [中文](README_CN.md)

<p align="center">
  <a href="https://github.com/Xuan0629/shared-skills/stargazers"><img src="https://img.shields.io/github/stars/Xuan0629/shared-skills?style=social" alt="stars"></a>
  <a href="https://github.com/Xuan0629/shared-skills/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="MIT"></a>
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.10%2B-blue" alt="Python 3.10+"></a>
  <a href="https://github.com/Xuan0629/unison"><img src="https://img.shields.io/badge/companion-Unison-gold" alt="Unison companion"></a>
</p>

> **One source. Every agent. Zero drift.**

**shared-skills** is the skill sync layer for multi-agent workflows. Write a skill once — sync-skills.py converts and deploys it to Claude Code, Codex, Hermes, and OpenClaw simultaneously. Zero external dependencies. Pure Python. 4-agent format conversion.

<p align="center"><b>
  Linux ✅ &nbsp; macOS ✅ &nbsp; Windows ✅ &nbsp; | &nbsp; MIT &nbsp; | &nbsp; Python 3.10+
</b></p>

---

## Quick Links

| Start here | |
|---|---|
| [Installation](#installation) | Clone → sync |
| [Usage](#usage) | sync / --check / --show-log / Web UI |
| [How It Works](#how-it-works) | Source → format convert → deploy |
| [Adding a Skill](#adding-a-new-skill) | 2 files: SKILL.md + meta.yaml |
| [Unison](https://github.com/Xuan0629/unison) | Companion: multi-agent pipeline framework |

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
