# 场景模板加载器 (Template Loader)

在场景采集阶段，根据用户描述的决策类型，自动匹配并加载对应模板，加速会议启动。

## 模板识别规则

用户描述场景后，分析关键词，自动匹配模板：

| 关键词 | 匹配模板 |
|--------|----------|
| 跳槽、辞职、转行、工作机会、创业、offer | `templates/job_change.md` |
| 分手、在不在一起、挽回、感情、关系、喜欢 | `templates/relationship.md` |
| 钱、投资、买房、借钱、理财、大额消费 | `templates/investment.md` |
| 搬家、移居、结婚、要孩子、离开 | `templates/life_change.md` |

如果不匹配任何模板，走通用采集流程（`use-self/SKILL.md` 中的 Step 1）。

---

## 加载后的行为

匹配到模板后：

### 1. 场景采集
用模板的**快速启动问卷**替代通用采集，通常 5 个问题就够。

```
这看起来是个[类型]决策。

我用这类决策的专用问卷来快速了解情况——
比通用问题更聚焦，5 个问题就够。

[展示模板问卷]
```

### 2. 传递给 moderator 的结构化信息

加载模板后，将以下内容传给主持人（moderator.md）：

```json
{
  "template_name": "job_change",
  "tension_axes": {
    "primary": "safety_vs_growth",
    "secondary": "short_vs_long",
    "optional": null
  },
  "variant_hints": [ ... ],
  "self_questions": [ ... ]
}
```

**tension_axes**：moderator 在 Phase 0b 分析张力轴时的**优先参照**，不强制使用，但减少分析工作量。

**variant_hints**：`variant_generator.md` 在生成变体时的参考方向。如果用户的 L3 底座与模板方向明显不同，以 L3 为准。

**self_questions**：Phase 3 综合时"做决定前先想清楚这几件事"的候选池，从中选 3 条最相关的。

### 3. 模板变体 vs 用户底座

模板提供的变体参数偏移只是**方向参考**，不是固定答案：
- 如果用户的 L3 底座某参数已经在极端值（如 risk_appetite = 2），相应变体的负向偏移要缩小
- 始终以用户真实的人格底座为基础，模板是加速工具，不是覆盖工具

---

## 用户跳过模板

如果用户说"我直接说"或者不想用模板，直接切回通用采集，不强推。
