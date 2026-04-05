# Forge-Skill 评测框架

> 可重复运行的最小评测集，覆盖两个核心场景。没有评测，所有优化都是玄学。

## 两个测试模块

### 1. persona_consistency_test.py — 角色扮演一致性（use-persona）

测试 use-persona 在多个对话场景下的角色一致性。

**评分维度（各 20 分，满分 100）：**

| 维度 | 说明 |
|------|------|
| 消息长度一致性 | 回复长度是否符合 L2.message_habits |
| 口头禅命中率 | L2.signature_phrases 是否自然出现 |
| 标点风格一致性 | 是否符合 L2 的 punctuation 描述 |
| 互动模式一致性 | 是否符合 L4.scene_responses |
| 边界遵守 | 是否违反 L0 的 hard traits |

**运行方式：**
```bash
python evals/persona_consistency_test.py --persona personas/others/小美/persona.json
```

---

### 2. debate_quality_test.py — 辩论质量（use-self）

测试 use-self 替身会议在 3 个决策场景下的讨论质量。

**评分维度（各 20 分，满分 100）：**

| 维度 | 说明 |
|------|------|
| 变体区分度 | Phase 1 各变体立场是否有实质性差异 |
| 质询深度 | Phase 2 是否指出了具体假设和盲区 |
| 参数一致性 | 变体发言是否与偏移后的参数一致 |
| 综合覆盖度 | Phase 3 是否涵盖所有关键分歧 |
| 用户风格 | 所有输出是否用了用户的 L2 语言风格 |

**运行方式：**
```bash
python evals/debate_quality_test.py --persona personas/self/阿然/persona.json
```

---

## 依赖

```
anthropic  # 调用 Claude API 进行 LLM 评分
pyyaml     # 读取测试用例
```

## 输出格式

测试完成后在终端打印评分报告，同时写入 `evals/results/` 目录：

```
evals/results/
├── consistency_[timestamp].json  # 每次一致性测试结果
└── debate_[timestamp].json       # 每次辩论质量测试结果
```

## 基线数据

首次运行后得到基线分数，后续每次优化后对比：

```
baseline_consistency: --   # 待建立
baseline_debate: --        # 待建立
target_consistency: 70+    # P0-6 验收标准
```
