# Domain Modeling — 领域建模

## 哲学

好的领域模型不是从代码结构反推的——它是从业务概念出发，然后映射到代码。这个技能帮你从代码库（或需求文档）中提取领域概念，建立一个独立于技术实现的业务模型。

## 核心概念速查

| 概念 | 是什么 | 例子 |
|---|---|---|
| **Entity（实体）** | 有唯一标识、生命周期的对象 | User、Order、Account |
| **Value Object（值对象）** | 无标识、不可变、通过值比较 | Money、DateRange、Quantity |
| **Aggregate Root（聚合根）** | 一组关联对象的入口，保证一致性边界 | Portfolio（聚合根）→ Position（子实体） |
| **Bounded Context（有界上下文）** | 一个术语有明确定义的边界 | 交易系统里的"Order"和仓储系统里的"Order"可能是不同的概念 |
| **Domain Event（领域事件）** | 领域中发生了重要事情 | OrderPlaced、PositionClosed |

## 流程

### 1. 识别核心实体

从用户需求或代码中挑出最重要的业务对象。问：
- 什么对象有唯一标识？（Entity）
- 什么对象通过值来识别？（Value Object）
- 什么对象是其他对象的一致性的守门人？（Aggregate Root）

### 2. 定义关系

画一个简单的概念图：实体 A 引用实体 B 是通过 ID 还是对象引用？这是一个 1:1、1:N 还是 N:M 的关系？

### 3. 找到有界上下文

一个词在不同地方有不同含义 = 发现了有界上下文边界。比如：
- 「信号」在 Alpha Station 里有特定含义，在 OpenClaw 里可能是另一个东西
- 这是两个 Bounded Context，各自拥有自己的领域语言

### 4. 输出领域模型文档

```markdown
## 领域模型: [系统/功能]

### 有界上下文: [名称]
**领域语言:** (列出这个上下文中特有的术语和含义)

**实体:**
- [EntityName]: [一句话描述其业务角色]
  - 聚合根？是/否
  - 关键属性: [仅列出对业务决策有影响的属性]

**值对象:**
- [ValueObjectName]: [含义] + [约束]

**领域事件:**
- [EventName]: [触发条件] → [后续动作]

### 跨上下文映射
(如果涉及多个 Bounded Context)
- [ContextA].[Concept] ↔ [ContextB].[Concept]
```
