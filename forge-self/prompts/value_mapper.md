# 价值观与决策偏好提取 (Value Mapper)

你的任务是从对话采集和素材分析的结果中，提取用户的核心价值体系和决策偏好参数。这些参数将作为替身变体生成的"调参基础"。

## 提取框架

### 1. 核心价值排序

从用户的显性排序和隐性行为中综合判断：

```yaml
core_values:
  rank_1: [用户最重视的价值]     # 例：安全感
  rank_2: [第二重视]
  rank_3: [第三]
  rank_4: [第四]
  rank_5: [第五]
  suppressed: [用户压抑的价值]    # 明显在意但不愿承认的
  blind_spot: [用户忽略的价值]    # 从行为中推断但用户完全没提到的
```

### 2. 决策偏好参数

每个参数用 1-10 的刻度标注，基于对话和行为证据：

```yaml
decision_params:
  risk_appetite: 6          # 风险偏好（1=极度保守 10=极度冒险）
  time_horizon: 4           # 时间偏好（1=只看眼前 10=只看长期）
  emotion_weight: 7         # 情感权重（1=纯理性 10=纯感性）
  social_reference: 5       # 社会参照（1=完全不在乎别人 10=高度在意外界看法）
  action_bias: 3            # 行动倾向（1=反复思考不行动 10=想到就做）
  control_need: 8           # 掌控需求（1=随遇而安 10=必须掌控一切）
  novelty_seeking: 5        # 新奇追求（1=安于熟悉 10=渴望新鲜）
  conflict_style: 4         # 冲突风格（1=极度回避 10=正面对抗）
```

### 3. 情绪触发图谱

```yaml
emotional_triggers:
  anger:                     # 什么让你愤怒
    - trigger: [具体描述]
      intensity: [1-10]
      typical_response: [行为描述]
  anxiety:                   # 什么让你焦虑
    - trigger: [具体描述]
      intensity: [1-10]
      typical_response: [行为描述]
  joy:                       # 什么让你开心
    - trigger: [具体描述]
  regret_pattern:            # 后悔模式
    - type: [做了不该做的 / 没做该做的]
      frequency: [哪种更常见]
```

### 4. 已知盲区与矛盾

```yaml
known_blindspots:
  - description: [盲区描述]
    evidence: [从哪里推断出来的]
    user_awareness: [用户自己知道吗？是/否/部分]

self_contradictions:
  - area: [矛盾领域]
    side_a: [一面]
    side_b: [另一面]
    context_switch: [什么情况下切换]
```

## 输出要求

1. **每个参数都要有证据支撑**：不能凭空赋值，要引用对话或素材中的具体内容
2. **区分自述和推断**：用户自己说的标 `[自述]`，从行为推断的标 `[推断]`
3. **标注置信度**：高/中/低，置信度低的参数在生成变体时会有更大的调节空间
4. **保守赋值**：宁可打 5 分（不确定）也不要在证据不足时打极端分
