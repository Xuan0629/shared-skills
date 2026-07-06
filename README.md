# Shared Skills · 共享 Skill 管理系统

> 单一数据源，全 Agent 同步 — 改一处，Claude Code / Codex / Hermes / OpenClaw 同时生效。

多 Agent 协作时，skill 需要在每个 Agent 中保持一致。手动复制导致版本漂移，降低审查质量。shared-skills 解决这个问题。

## 快速开始

Sync source: /home/sean/shared-skills
Targets: planning-with-files, design-system, role-play, handoff, codebase-design, domain-modeling, diagnosing-bugs, grill-design

Syncing: planning-with-files (→ hermes, claude, codex)
  ✓ hermes: /home/sean/.hermes/skills/productivity/planning-with-files/SKILL.md
  ✓ claude: /home/sean/.claude/skills/planning-with-files/SKILL.md
  ✓ codex: /home/sean/.codex/skills/planning-with-files/SKILL.md
  - openclaw (skipped)

Syncing: design-system (→ hermes, claude, codex)
  ✓ hermes: /home/sean/.hermes/skills/creative/design-system/SKILL.md
  ✓ claude: /home/sean/.claude/skills/design-system/SKILL.md
  ✓ codex: /home/sean/.codex/skills/design-system/SKILL.md
  - openclaw (skipped)

Syncing: role-play (→ hermes, claude, codex)
  ✓ hermes: /home/sean/.hermes/skills/productivity/role-play/SKILL.md
  ✓ claude: /home/sean/.claude/skills/role-play/SKILL.md
  ✓ codex: /home/sean/.codex/skills/role-play/SKILL.md
  - openclaw (skipped)

Syncing: handoff (→ hermes, claude, codex)
  ✓ hermes: /home/sean/.hermes/skills/devops/handoff/SKILL.md
  ✓ claude: /home/sean/.claude/skills/handoff/SKILL.md
  ✓ codex: /home/sean/.codex/skills/handoff/SKILL.md
  - openclaw (skipped)

Syncing: codebase-design (→ hermes, claude, codex)
  ✓ hermes: /home/sean/.hermes/skills/software-development/codebase-design/SKILL.md
  ✓ claude: /home/sean/.claude/skills/codebase-design/SKILL.md
  ✓ codex: /home/sean/.codex/skills/codebase-design/SKILL.md
  - openclaw (skipped)

Syncing: domain-modeling (→ hermes, claude, codex)
  ✓ hermes: /home/sean/.hermes/skills/software-development/domain-modeling/SKILL.md
  ✓ claude: /home/sean/.claude/skills/domain-modeling/SKILL.md
  ✓ codex: /home/sean/.codex/skills/domain-modeling/SKILL.md
  - openclaw (skipped)

Syncing: diagnosing-bugs (→ hermes, claude, codex)
  ✓ hermes: /home/sean/.hermes/skills/software-development/diagnosing-bugs/SKILL.md
  ✓ claude: /home/sean/.claude/skills/diagnosing-bugs/SKILL.md
  ✓ codex: /home/sean/.codex/skills/diagnosing-bugs/SKILL.md
  - openclaw (skipped)

Syncing: grill-design (→ hermes, claude, codex)
  ✓ hermes: /home/sean/.hermes/skills/software-development/grill-design/SKILL.md
  ✓ claude: /home/sean/.claude/skills/grill-design/SKILL.md
  ✓ codex: /home/sean/.codex/skills/grill-design/SKILL.md
  - openclaw (skipped)

Done. Synced 8 skill(s).
planning-with-files:
  hermes: UP-TO-DATE
  claude: UP-TO-DATE
  codex: UP-TO-DATE
design-system:
  hermes: UP-TO-DATE
  claude: UP-TO-DATE
  codex: UP-TO-DATE
role-play:
  hermes: UP-TO-DATE
  claude: UP-TO-DATE
  codex: UP-TO-DATE
handoff:
  hermes: UP-TO-DATE
  claude: UP-TO-DATE
  codex: UP-TO-DATE
codebase-design:
  hermes: UP-TO-DATE
  claude: UP-TO-DATE
  codex: UP-TO-DATE
domain-modeling:
  hermes: UP-TO-DATE
  claude: UP-TO-DATE
  codex: UP-TO-DATE
diagnosing-bugs:
  hermes: UP-TO-DATE
  claude: UP-TO-DATE
  codex: UP-TO-DATE
grill-design:
  hermes: UP-TO-DATE
  claude: UP-TO-DATE
  codex: UP-TO-DATE
Sync source: /home/sean/shared-skills
Targets: planning-with-files

Syncing: planning-with-files (→ hermes, claude, codex)
  ✓ hermes: /home/sean/.hermes/skills/productivity/planning-with-files/SKILL.md
  ✓ claude: /home/sean/.claude/skills/planning-with-files/SKILL.md
  ✓ codex: /home/sean/.codex/skills/planning-with-files/SKILL.md
  - openclaw (skipped)

Done. Synced 1 skill(s).
2026-07-06T02:58:16  role-play                 → claude      updated
2026-07-06T02:58:16  role-play                 → codex       updated
2026-07-06T02:58:16  handoff                   → hermes      updated
2026-07-06T02:58:16  handoff                   → claude      updated
2026-07-06T02:58:16  handoff                   → codex       updated
2026-07-06T02:58:16  codebase-design           → hermes      updated
2026-07-06T02:58:16  codebase-design           → claude      updated
2026-07-06T02:58:16  codebase-design           → codex       updated
2026-07-06T02:58:16  domain-modeling           → hermes      updated
2026-07-06T02:58:16  domain-modeling           → claude      updated
2026-07-06T02:58:16  domain-modeling           → codex       updated
2026-07-06T02:58:16  diagnosing-bugs           → hermes      updated
2026-07-06T02:58:16  diagnosing-bugs           → claude      updated
2026-07-06T02:58:16  diagnosing-bugs           → codex       updated
2026-07-06T02:58:16  grill-design              → hermes      updated
2026-07-06T02:58:16  grill-design              → claude      updated
2026-07-06T02:58:16  grill-design              → codex       updated
2026-07-06T02:58:16  planning-with-files       → hermes      updated
2026-07-06T02:58:16  planning-with-files       → claude      updated
2026-07-06T02:58:16  planning-with-files       → codex       updated
Generated: /home/sean/shared-skills/webui/data.json
  8 skills × 4 agents = 32 pairs
  synced=24 outdated=0 missing=0 disabled=8

## 工作原理

单源 → 多格式转换 → 同步到各 Agent 目录

## 添加新 Skill

1. 创建目录和 SKILL.md
2. 编写 meta.yaml（version、sync_to、per-agent 元数据）
3. 运行 sync-skills.py

## 配套项目

shared-skills 是 Unison 多 Agent 协作框架的推荐配套工具。

## 许可证

MIT
