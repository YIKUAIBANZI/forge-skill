# 场景模板：职业转变

**适用场景**：跳槽、转行、创业、辞职、接受新机会

---

## 快速启动问卷

用于快速收集场景信息，省去用户反复被追问的过程。

```
职业转变类决策，我需要了解几个关键信息：

1. 现状是什么？
   （现在的工作/状态）

2. 摆在你面前的选项是什么？
   （A选项 vs B选项，或者"做还是不做"）

3. 这个决定的截止日期是什么时候？
   （需要什么时候给答复）

4. 你最担心的一件事是什么？

5. 如果不考虑任何人，只考虑你自己，你更倾向哪边？
```

---

## 预设矛盾轴（结构化）

供 `variant_generator.md` 直接使用，减少张力分析时间。

```yaml
tension_axes:
  primary: "safety_vs_growth"    # 安全感 vs 成长空间
  secondary: "short_vs_long"     # 眼前收益 vs 长期回报
  optional: "self_vs_relationship"  # 仅当决策明显涉及他人时加入
```

常见场景下的主轴：
- 跳槽到同行 → `safety_vs_growth`（主）+ `short_vs_long`（次）
- 转行 → `known_vs_unknown`（主）+ `short_vs_long`（次）
- 创业 → `control_vs_belonging`（主）+ `safety_vs_growth`（次）

---

## 推荐变体参数偏移方向

基于 `safety_vs_growth` 轴的典型偏移（供 moderator 参考，不强制）：

```json
[
  {
    "name": "稳住的你",
    "tagline": "先确保不输，再想怎么赢",
    "color": "🔵",
    "shifts": { "risk_appetite": -3, "loss_aversion": 2, "action_bias": -2 }
  },
  {
    "name": "抓机会的你",
    "tagline": "窗口期有限，过了这村没这店",
    "color": "🟢",
    "shifts": { "risk_appetite": 3, "action_bias": 3, "information_need": -1 }
  },
  {
    "name": "长线的你",
    "tagline": "三年后回看，哪个选择更值",
    "color": "🔴",
    "shifts": { "time_horizon": 4, "loss_aversion": -1 }
  },
  {
    "name": "直觉的你",
    "tagline": "撇开所有分析，你的第一感觉是什么",
    "color": "🟡",
    "shifts": { "information_need": -3, "emotion_weight": 2, "action_bias": 1 }
  }
]
```

---

## 典型自问清单

Phase 3 综合时可作为"做决定前先想清楚这几件事"的候选来源：

1. **机会窗口**：这个机会真的有时限，还是你给自己制造了紧迫感？
2. **可逆性**：如果做了发现不对，能回头吗？代价多大？
3. **精力成本**：新方向要求的状态，你现在有吗？
4. **关系成本**：这个决定影响谁？他们知道你在考虑这件事吗？
5. **"必须稳"的压力**：你有没有给自己施加不必要的"必须稳"，其实没有那么必须？
6. **现有积累的真实价值**：你觉得的"沉没成本"，在新方向上真的是障碍吗？

---

## Phase 3 特别提示

代价清单里不能省的：
- **身体和精力成本**：新工作要求的状态，你现在有吗？
- **关系成本**：这个决定影响谁？他们怎么看？
- **可逆性**：如果做了发现不对，能回头吗？代价多大？
