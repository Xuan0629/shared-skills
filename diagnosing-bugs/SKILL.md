# Diagnosing Bugs — 系统化 Bug 诊断

## 哲学

大多数 bug 不是修不好，是诊断错了。这个技能提供一套系统化的排查流程，避免随机试错。

## 流程

### 1. 描述 bug（What）

用一句话精确描述症状：
- ❌ "它不工作了"
- ✅ "调用 `POST /api/orders` 返回 500，日志显示 `TypeError: Cannot read property 'price' of undefined`，发生在 `orderService.ts:142`"

### 2. 复现（Reproduce）

**在没有复现之前不要开始修。** "我觉得这样应该能修"不是 debug，是赌博。

- 用**最小可复现用例**触发 bug
- 确认每次都能复现（不是间歇性的）
- 如果不能复现 → 记下触发条件，这不等于修好

### 3. 读完整错误信息（Read the Trace）

- 读 stack trace 的每一行——不是只看最后一行
- TypeError 可能有一百种含义，trace 告诉你具体是哪一种
- 在相关文件里找到对应的行号，理解它为什么在这行崩溃

### 4. 一次改一个变量（Binary Search）

- 改一个东西 → 测试 → 再改下一个
- **禁止同时改 3 个地方然后说"修好了"** — 你不知道哪个改动用
- 用二分法缩小范围：注释掉一半代码 → 哪个半边还在崩？

### 5. 找根因（Root Cause）

- 不要只加 null check 然后走人
- 问「为什么这个值是 null？」→ 追一层 → 「为什么上游没传？」→ 再追一层
- 根因通常比你想象的多 1-2 层

### 6. 验证修复（Verify）

- 运行之前写的复现测试 → 确认 bug 不再触发
- 运行已有测试套件 → 确认没有引入回归
- 如果可能，加一个回归测试防止同一个 bug 再来一次

## 反模式警告

| 反模式 | 表现 |
|---|---|
| **Shotgun debugging** | 同时改多处，碰运气哪个修好 |
| **Workaround over root cause** | 加了 try/catch 或 null guard 就算"修好" |
| **Silent symptom masking** | bug 没触发不等于修好——只是条件没满足 |
| **Code archaeology avoidance** | 不看 git blame/log 找谁什么时候引入了 bug |
