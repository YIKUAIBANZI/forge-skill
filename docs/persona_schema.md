# Persona JSON Schema 文档

> 这份文档是 forge-self 和 forge-persona 生成数据的契约。
> 所有 skill 之间通过 `persona.json` 交换数据，`persona.md` 仅供人阅读。

---

## 通用规则

- 每个 trait 类条目必须包含：`trait`、`evidence`、`source`、`confidence`
- `evidence` 要求是用户原话或具体行为描述，不是 AI 的概括
- `confidence`: `high`（多源验证/用户明确自述）| `medium`（单源但证据明确）| `low`（推断）
- `source`: `conversation` | `wechat` | `diary` | `social` | `correction`
- 参数 `score` 范围：1-10 整数

---

## Self Persona（`type: "self"`）

由 `/forge-self` 生成，核心层是 L3 决策参数 + L4 价值观。

```json
{
  "meta": {
    "name": "string",
    "type": "self",
    "version": "v1.0",
    "created": "YYYY-MM-DD",
    "last_updated": "YYYY-MM-DD",
    "data_sources": ["conversation", "wechat", "diary", "social"],
    "confidence_overall": "high | medium | low"
  },

  "L0_hard_override": {
    "will": [
      { "trait": "string", "evidence": "string", "source": "string", "confidence": "string" }
    ],
    "wont": [ ... ],
    "bottom_line": [ ... ]
  },

  "L1_identity": {
    "basic_info": "年龄段/职业/人生阶段（自由描述）",
    "self_perception": "用户自述的自我认知",
    "others_perception": "他人评价，用户是否认同",
    "labels": ["自我标签1", "自我标签2"],
    "identity_conflicts": ["身份张力描述"]
  },

  "L2_expression": {
    "language_style": "综合语言风格描述",
    "message_habits": {
      "avg_length": "短/中/长，或字数描述",
      "punctuation": "标点习惯",
      "emoji_usage": "表情使用频率和风格",
      "signature_phrases": ["口头禅原话1", "口头禅原话2"]
    },
    "communication_mode": "说话顺序/思维组织方式",
    "emotion_expression": "情绪表达方式",
    "under_pressure": "压力下的变化"
  },

  "L3_decision_params": {
    "parameters": {
      "risk_appetite":    { "score": 5, "evidence": "string", "confidence": "medium" },
      "time_horizon":     { "score": 5, "evidence": "string", "confidence": "medium" },
      "emotion_weight":   { "score": 5, "evidence": "string", "confidence": "medium" },
      "social_reference": { "score": 5, "evidence": "string", "confidence": "medium" },
      "action_bias":      { "score": 5, "evidence": "string", "confidence": "medium" },
      "control_need":     { "score": 5, "evidence": "string", "confidence": "medium" },
      "novelty_seeking":  { "score": 5, "evidence": "string", "confidence": "medium" },
      "conflict_style":   { "score": 5, "evidence": "string", "confidence": "medium" }
    },
    "decision_process": "决策过程描述",
    "past_decisions": [
      { "scenario": "string", "choice": "string", "outcome": "string" }
    ]
  },

  "L4_values": {
    "ranking": ["安全感", "成长", "自由", "..."],
    "suppressed_value": "明显在意但不愿承认的价值",
    "blind_spots": [
      { "trait": "string", "evidence": "string", "source": "string", "confidence": "string" }
    ],
    "emotional_triggers": [ ... ],
    "self_contradictions": [ ... ]
  },

  "L5_corrections": [
    {
      "date": "YYYY-MM-DD",
      "layer": "L3",
      "field": "parameters.risk_appetite.score",
      "before": "4",
      "after": "7",
      "reason": "string",
      "user_original_words": "其实我骨子里还是挺冒险的"
    }
  ]
}
```

---

## Others Persona（`type: "persona"`）

由 `/forge-persona` 生成，核心层是 L2 表达风格 + L4 互动模式。

```json
{
  "meta": {
    "name": "string",
    "type": "persona",
    "version": "v1.0",
    "created": "YYYY-MM-DD",
    "last_updated": "YYYY-MM-DD",
    "data_sources": ["wechat", "social", "conversation"],
    "confidence_overall": "high | medium | low"
  },

  "L0_hard_traits": {
    "will": [ { "trait": "string", "evidence": "string", "source": "string", "confidence": "string" } ],
    "wont": [ ... ],
    "bottom_line": [ ... ]
  },

  "L1_identity": {
    "basic_info": "年龄段/职业/与用户的关系",
    "self_perception": "ta 对自己的认知（如可推断）",
    "others_perception": "他人评价",
    "labels": ["标签"],
    "identity_conflicts": []
  },

  "L2_expression": {
    "language_style": "综合语言风格",
    "message_habits": {
      "avg_length": "string",
      "punctuation": "string",
      "emoji_usage": "string",
      "signature_phrases": ["原话1", "原话2"],
      "multi_send_pattern": "拆多条发 / 一条发完 / 看情况",
      "coldness_markers": ["冷漠信号1"],
      "warmth_markers": ["温暖信号1"],
      "humor_style": "冷幽默 / 自嘲 / ...",
      "fixed_phrases": [
        { "phrase": "string", "evidence": "string", "context": "在什么情况下说" }
      ]
    },
    "communication_mode": "string",
    "emotion_expression": "string",
    "under_pressure": "string"
  },

  "L3_thinking_style": {
    "summary": "综合描述",
    "advice_giving": "给建议的方式",
    "info_preference": "倾向听细节还是结论",
    "decision_speed": "决策速度"
  },

  "L4_interaction_patterns": {
    "power_dynamic": "关系中的权力/亲密动态描述",
    "fixed_memes": [
      { "meme": "string", "evidence": "string", "context": "string" }
    ],
    "daily_topics": ["固定话题1", "固定话题2"],
    "scene_responses": [
      {
        "scene": "用户倾诉时",
        "typical_response": "string",
        "evidence": "string"
      }
    ],
    "boundaries": [
      { "trait": "string", "evidence": "string", "source": "string", "confidence": "string" }
    ],
    "relationship_context": "与用户的关系特征（角色扮演核心参考）"
  },

  "L5_corrections": [ ... ]
}
```

---

## Runtime Card 对应关系

| Card 类型 | 使用场景 | 包含层级 | Token 目标 |
|-----------|----------|----------|------------|
| `chat-card` | use-persona 对话 | L0全部 + L1.basic_info + L2全部 + L4.interaction_patterns | 原始 40-50% |
| `decision-card` | use-self 决策会议 | L0.bottom_line + L1.basic_info + L2.language_style + L3全部 + L4全部 | 原始 50-60% |
| `variant-card` | use-self 单个变体 agent | decision-card + 偏移后参数 + 变体身份 + 场景摘要 | — |

---

## 参数含义速查

| 参数 | 1（极低）| 10（极高）|
|------|---------|---------|
| risk_appetite | 极度保守 | 极度冒险 |
| time_horizon | 只看眼前 | 只看长期 |
| emotion_weight | 纯理性 | 纯感性 |
| social_reference | 完全不在乎外界 | 高度在意外界看法 |
| action_bias | 反复思考不行动 | 想到就做 |
| control_need | 随遇而安 | 必须掌控一切 |
| novelty_seeking | 安于熟悉 | 渴望新鲜 |
| conflict_style | 极度回避 | 正面对抗 |
