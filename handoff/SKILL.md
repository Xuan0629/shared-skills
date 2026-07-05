# Handoff — 跨 Agent 上下文交接

## 核心原则

交接文档的目的是让下一个 agent **不需要重新问用户**就能继续工作。它回答三个问题：

1. **已经做了什么**（完成了哪些、怎么做的）
2. **现在卡在哪里**（当前状态、阻点）
3. **接下来做什么**（下一步任务、成功标准）

## 流程

### 1. 确定交接目标

明确接收方 agent 的类型和工作空间：
- **Hermes → Claude Code**：任务涉及多文件编码/重构
- **Hermes → OpenClaw**：任务涉及 GEO 业务流
- **OpenClaw Main → GEOMaster/geoguy**：任务分流到业务 agent
- **任意 agent → 新会话**：上下文过长，需 /new 重建

### 2. 写交接文档

结构：

```markdown
## 交接: [任务简述]

**发起方:** [agent 名]
**接收方:** [目标 agent 名]
**时间:** [时间戳]

### 已完成
- [具体完成的事情，带路径/命令/结果]
- [决策记录：做了什么选择 + 为什么]

### 当前状态
- [进度阶段]
- [已知问题/阻塞点]
- [关键文件列表]

### 下一步
- [明确可执行的任务描述]
- [成功标准]

### 建议加载的 skills
- [skill 名 — 原因]
- ...

### 参考文件
- [路径或 URL] — [用途]
```

### 3. 存到共享路径

交接文档保存到：
- Hermes/Claude/Codex 之间：`~/repos/_handoffs/`（所有 agent 都可访问）
- OpenClaw 内部：`~/.openclaw/agents/main/workspace/user_read/执行落地汇报/`
- 跨系统（Hermes ↔ OpenClaw）：两边各存一份，用 `cp` 同步

### 4. Redact 敏感信息

保存前检查：
- ❌ API key / token
- ❌ 密码 / 密钥
- ❌ 个人身份信息
- ✅ 替换为占位符如 `[API_KEY]` 或 `[REDACTED]`

## 与已有产物的关系

- 已有 PRD/plan/ADR/issue/commit → 引用路径或 URL，不重复内容
- 已有结构化状态文件 → 引用路径，不摘抄
- 只写「当前这个时刻」需要传递给下一个 agent 的增量信息
