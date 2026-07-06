# Shared Skills · 共享 Skill 管理系统

> 单一数据源，全 Agent 同步 — 改一处，Claude Code / Codex / Hermes / OpenClaw 同时生效。

多 Agent 协作时，skill 需要在每个 Agent 中保持一致。手动复制导致版本漂移，降低审查质量。shared-skills 解决这个问题。

## 安装

```bash
git clone https://github.com/Xuan0629/shared-skills.git
cd shared-skills
```

依赖：Python 3.10+，标准库（无第三方依赖）。

## 使用

```bash
# 同步所有 skill 到配置的目标 Agent
python3 sync-skills.py

# 检查各 Agent 中的 skill 是否与源一致
python3 sync-skills.py --check

# 查看同步日志
python3 sync-skills.py --show-log

# 启动 Web UI Dashboard
cd webui && python3 -m http.server 8080
```

## 工作原理

```
shared-skills/          # 单一数据源
├── skill-name/
│   ├── SKILL.md        # skill 内容
│   └── meta.yaml       # 元数据（版本、同步目标、per-agent 配置）
├── skills-manifest.yaml
├── sync-skills.py       # 格式转换 + 同步引擎
└── webui/               # Dashboard

        ↓ sync-skills.py

~/.hermes/skills/...    ~/.claude/skills/...    ~/.codex/skills/...    ~/.openclaw/.../skills/
    (Hermes 格式)          (Claude 格式)            (Codex 格式)           (OpenClaw 格式)
```

`sync-skills.py` 读取源 skill，转换为各 Agent 所需的格式（frontmatter、文件结构），写入目标目录。

## 添加新 Skill

```bash
mkdir my-skill
# 编写 my-skill/SKILL.md
# 编写 my-skill/meta.yaml（指定 sync_to: [hermes, claude, codex]）
python3 sync-skills.py
```

`meta.yaml` 格式：

```yaml
version: "1.0.0"
sync_to: [hermes, claude, codex]   # 目标 Agent 列表
hermes:
  category: software-development
  description: "描述"
claude:
  description: "描述"
codex:
  description: "描述"
```

## Web UI Dashboard

`webui/` 目录提供可视化 Dashboard，展示所有 skill 在各 Agent 中的同步状态。

```bash
cd webui && python3 -m http.server 8080
```

然后打开 `http://localhost:8080`。

## 配套项目

shared-skills 是 [Unison](https://github.com/Xuan0629/unison) 多 Agent 协作框架的推荐配套工具。在 Unison 工作流中，shared-skills 确保各审查 Agent 使用完全一致的 skill 定义，消除版本漂移。

## 许可证

MIT
