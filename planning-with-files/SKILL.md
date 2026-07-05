# Planning with Files — Crash-Proof Task Planning

## 哲学

AI agent 最大的弱点是上下文丢失——/clear、崩溃、会话超时都会让之前的计划消失。这个技能把计划持久化到磁盘上的三个 Markdown 文件，任何 agent 重启后都能无缝恢复。

## 文件结构

```
~/projects/<project>/.plan/
  task_plan.md    — 主计划（分步、有优先级、有验收标准）
  findings.md     — 过程中发现的问题/洞察（不丢失）
  progress.md     — 当前进度（哪步完成、哪步进行中、下一步）
```

## 流程

### 1. 初始化（任务开始时）

创建 `.plan/` 目录，写入 `task_plan.md`：

```markdown
# Task Plan: [任务名称]

**创建时间:** [时间戳]
**状态:** in_progress

## 步骤

### Step 1: [描述] [状态: pending|in_progress|done]
- 验收标准: [可验证的条件]
- 依赖: [前置步骤]

### Step 2: ...
```

### 2. 执行中（每步完成时）

更新 `progress.md`：

```markdown
# Progress

**最后更新:** [时间戳]
**当前步骤:** Step N

## 已完成
- [x] Step 1 — [完成时间 + 简要结果]
- [x] Step 2 — ...

## 进行中
- [ ] Step N — [开始时间]

## 阻塞
- [问题描述] — [影响哪个步骤]
```

### 3. 发现新信息时

追加到 `findings.md`：

```markdown
# Findings

## [时间戳] [发现标题]
- 发现: [具体内容]
- 影响: [影响哪些步骤]
- 行动: [需要做什么]
```

### 4. 恢复（重启/新会话时）

1. 检查 `.plan/` 是否存在
2. 读 `progress.md` → 知道做到哪了
3. 读 `task_plan.md` → 知道整体计划
4. 读 `findings.md` → 知道之前发现了什么
5. 从 `progress.md` 的"进行中"步骤继续

## 使用方式

在任务开始时说 "plan with files"，或直接告知 "将以下任务写入 plan"。
