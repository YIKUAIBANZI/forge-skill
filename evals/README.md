# Forge-Skill 评测框架

> 可重复运行的最小评测集，覆盖两个核心场景。没有评测，所有优化都是玄学。
> 
> **不需要 API Key**，直接在 Claude Code 里运行 Skill 即可。

## 两个 Skill

### /eval-consistency — 角色扮演一致性（use-persona）

```
/eval-consistency
```

测试 use-persona 在 10 个对话场景下的角色一致性。Claude Code 自己生成回复、自己打分。

**评分维度（各 20 分，满分 100，目标 70+）：**

| 维度 | 说明 |
|------|------|
| 消息长度一致性 | 是否符合 L2 的消息长度偏好 |
| 口头禅命中率 | L2.signature_phrases 是否自然出现 |
| 标点风格一致性 | 是否符合 L2 的标点描述 |
| 互动模式一致性 | 是否符合 L4 的 scene_responses |
| 边界遵守 | 是否违反 L0 硬性特征 |

---

### /eval-debate — 替身会议辩论质量（use-self）

```
/eval-debate
```

给 3 个决策场景跑完整三阶段辩论（Phase 1 独立 → Phase 2 质询 → Phase 3 综合），然后自我评分。

**评分维度（各 20 分，满分 100）：**

| 维度 | 说明 |
|------|------|
| 变体区分度 | Phase 1 各变体立场是否有实质性差异 |
| 质询深度 | Phase 2 是否指出了具体假设和盲区 |
| 参数一致性 | 变体发言是否与偏移后的参数一致 |
| 综合覆盖度 | Phase 3 是否涵盖所有关键分歧 |
| 用户语言风格 | 所有输出是否用了用户的 L2 风格 |

---

## 测试用例

```
evals/test_cases/
├── persona_consistency_cases.yaml  # 小美的 10 个对话场景
└── debate_quality_cases.yaml       # 阿然的 3 个决策场景
```

## 结果存储

每次运行后可选择保存到 `evals/results/`，用于对比优化前后的变化。

## 什么时候跑

- 首次跑建立基线
- 每次做完一个 P1/P2 优化后跑一遍，确认有没有提升
