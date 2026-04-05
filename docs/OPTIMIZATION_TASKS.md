# Forge-Skill 优化任务清单

> 给 Claude Code 的实施指南。每个任务包含：背景、目标、具体改动、验收标准。
> 建议按 P0 → P1 → P2 顺序执行，P0 内部按编号顺序。

---

## P0-1：人格数据结构化 — persona.json + schema

### 背景
当前 persona.md 是纯 Markdown，适合人读但不适合程序稳定调用。后续要做 runtime loader、自动 diff、多 agent 参数偏移、评测，都需要结构化数据。

### 目标
保留 persona.md 给人读，新增 persona.json 作为系统调用的 single source of truth。两者通过工具保持同步。

### 具体改动

**新增文件：**
- `tools/persona_schema.py` — 定义 persona 的 JSON Schema（用 Python dataclass 或 pydantic）
- `docs/persona_schema.md` — 人类可读的 schema 文档，作为各 skill 之间的契约

**Schema 结构（self 类型）：**
```json
{
  "meta": {
    "name": "string",
    "type": "self | persona",
    "version": "string",
    "created": "ISO date",
    "last_updated": "ISO date",
    "data_sources": ["conversation", "wechat", "diary", "social"],
    "confidence_overall": "high | medium | low"
  },
  "L0_hard_override": {
    "will": [{ "trait": "string", "evidence": "string", "source": "string", "confidence": "high|medium|low" }],
    "wont": [{ "trait": "string", "evidence": "string", "source": "string", "confidence": "high|medium|low" }],
    "bottom_line": [{ "trait": "string", "evidence": "string", "source": "string", "confidence": "high|medium|low" }]
  },
  "L1_identity": {
    "basic_info": "string",
    "self_perception": "string",
    "others_perception": "string",
    "labels": ["string"],
    "identity_conflicts": ["string"]
  },
  "L2_expression": {
    "language_style": "string",
    "message_habits": {
      "avg_length": "string",
      "punctuation": "string",
      "emoji_usage": "string",
      "signature_phrases": ["string"]
    },
    "communication_mode": "string",
    "emotion_expression": "string",
    "under_pressure": "string"
  },
  "L3_decision_params": {
    "parameters": {
      "risk_appetite": { "score": "1-10", "evidence": "string", "confidence": "high|medium|low" },
      "time_horizon": { "score": "1-10", "evidence": "string", "confidence": "high|medium|low" },
      "emotion_weight": { "score": "1-10", "evidence": "string", "confidence": "high|medium|low" },
      "social_reference": { "score": "1-10", "evidence": "string", "confidence": "high|medium|low" },
      "action_bias": { "score": "1-10", "evidence": "string", "confidence": "high|medium|low" },
      "control_need": { "score": "1-10", "evidence": "string", "confidence": "high|medium|low" },
      "novelty_seeking": { "score": "1-10", "evidence": "string", "confidence": "high|medium|low" },
      "conflict_style": { "score": "1-10", "evidence": "string", "confidence": "high|medium|low" }
    },
    "decision_process": "string",
    "past_decisions": [{ "scenario": "string", "choice": "string", "outcome": "string" }]
  },
  "L4_values": {
    "ranking": ["string"],
    "suppressed_value": "string",
    "blind_spots": [{ "trait": "string", "evidence": "string", "source": "string", "confidence": "high|medium|low" }],
    "emotional_triggers": [{ "trait": "string", "evidence": "string", "source": "string", "confidence": "high|medium|low" }],
    "self_contradictions": [{ "trait": "string", "evidence": "string", "source": "string", "confidence": "high|medium|low" }]
  },
  "L5_corrections": [
    {
      "date": "ISO date",
      "layer": "L0|L1|L2|L3|L4",
      "field": "string",
      "before": "string",
      "after": "string",
      "reason": "string",
      "user_original_words": "string"
    }
  ]
}
```

**persona 类型的 schema 差异：**
- L2 权重最高，`message_habits` 展开更细：`multi_send_pattern`, `coldness_markers`, `warmth_markers`, `humor_style`, `fixed_phrases`（每个都带 evidence）
- L3 弱化为 `thinking_style`（非参数化，纯描述）
- L4 改为 `interaction_patterns`：`power_dynamic`, `fixed_memes`（固定梗）, `daily_topics`, `scene_responses`（关键场景 → 典型反应映射）, `boundaries`
- 新增 `L4.relationship_context`：记录与用户的关系特征，这是角色扮演的核心参考

**改动现有文件：**
- `tools/skill_writer.py` — 新增 `write_persona_json()` 和 `read_persona_json()` 方法，生成 persona.md 时同步生成 persona.json
- `forge-self/prompts/persona_builder.md` — 输出规范中增加"同时输出 JSON 格式"的指令
- `forge-persona/prompts/persona_builder.md` — 同上

**迁移现有数据：**
- 为 `personas/self/阿然/` 和 `personas/others/小美/` 生成对应的 persona.json

### 验收标准
- persona.json 能被 `persona_schema.py` 校验通过
- 两份现有 persona 成功迁移为 JSON
- persona.md 和 persona.json 内容一致

---

## P0-2：Persona 校验器

### 背景
persona 是 prompt 生成的，容易出现字段缺失、层级混乱、trait 重复、自相矛盾。需要在生成后、使用前做一次自动校验。

### 目标
生成 persona 后自动过一层 validator，输出校验报告。

### 具体改动

**新增文件：**
- `tools/persona_validator.py`

**校验规则：**
1. 结构完整性：L0-L5 每层是否存在、关键字段是否为空
2. 类型正确性：score 是否在 1-10 范围、date 是否合法
3. 重复检测：同一层内是否有语义高度重复的 trait
4. 矛盾检测：L0 的 will 和 wont 是否冲突、L4 的 blind_spots 和 L3 参数是否矛盾
5. 证据覆盖：evidence 为空的 trait 占比（目标 < 20%）
6. 版本一致：meta.version 和 L5 最新修改是否匹配

**输出格式：**
```json
{
  "valid": true/false,
  "errors": [{ "level": "error|warning", "layer": "L0-L5", "field": "string", "message": "string" }],
  "stats": {
    "total_traits": 0,
    "with_evidence": 0,
    "high_confidence": 0,
    "contradictions_found": 0
  }
}
```

**改动现有文件：**
- `forge-self/SKILL.md` — Phase 4（验证）中调用 validator
- `forge-persona/SKILL.md` — 同上

### 验收标准
- 对现有两份 persona.json 运行 validator，输出报告
- 故意制造缺失字段和矛盾，validator 能检出

---

## P0-3：Runtime Loader — 按场景抽取上下文卡片

### 背景
当前 use-persona / use-self 每次把整份 persona 全塞给模型，token 浪费、噪音大、长对话容易飘。不同场景只需要 persona 的不同切面。

### 目标
新增运行时加载器，根据使用场景生成精简的"上下文卡片"。

### 具体改动

**新增文件：**
- `tools/persona_runtime_loader.py`

**两种卡片模式：**

#### chat-card（给 use-persona 用）
从 persona.json 抽取：
- L0 全部（边界不能省）
- L1 仅 `basic_info` + `relationship_context`
- L2 全部（角色扮演核心）
- L4 的 `interaction_patterns` 全部（互动核心）
- 忽略 L3（思维方式对聊天影响小）、L5（历史修改对实时对话不需要）

输出为一份紧凑的 Markdown，token 目标：原 persona 的 40-50%

#### decision-card（给 use-self 用）
从 persona.json 抽取：
- L0 仅 `bottom_line`（决策底线）
- L1 仅 `basic_info`
- L2 仅 `language_style`（变体说话时需要）
- L3 全部（决策核心）
- L4 全部（价值观核心）
- 忽略 L5

输出为紧凑 Markdown，token 目标：原 persona 的 50-60%

#### variant-card（给 use-self 的每个变体 agent 用，P0-4 需要）
从 decision-card 基础上：
- L3 参数替换为偏移后的值
- 附加：该变体的名称、标签、偏移说明
- 附加：用户的决策场景摘要

**改动现有文件：**
- `use-persona/SKILL.md` — Step 1 改为调用 runtime loader 生成 chat-card
- `use-self/SKILL.md` — Step 0 改为调用 runtime loader 生成 decision-card

### 验收标准
- 对阿然生成 decision-card，token 数 < 原 persona 的 60%
- 对小美生成 chat-card，token 数 < 原 persona 的 50%
- 卡片内容无信息丢失（关键字段都在）

---

## P0-4：use-self 多 Subagent 辩论架构

### 背景
当前 use-self 的辩论用单 prompt cosplay：一个 Claude 实例在一个 response 里扮演 3-4 个变体。问题是：
1. 没有信息隔离，辩论是"排演过的"而非"发现性的"
2. 每个变体分到的思考深度被稀释
3. 模型天然趋同，质询不够尖锐

### 目标
将辩论引擎改为多 subagent 架构。每个变体是独立 agent，有自己的 context，通过主持人 agent 协调。

### 架构设计

```
用户输入决策场景
        ↓
[主持人 Agent]
  - 读取 persona.json（通过 runtime loader 生成 decision-card）
  - 分析张力轴
  - 生成 3-4 组变体参数
  - 为每个变体生成 variant-card
        ↓
[Phase 1: 并行 spawn 3-4 个变体 Agent]
  每个 Agent 收到：
    - 自己的 variant-card（偏移后的参数）
    - 用户的决策场景
    - Phase 1 prompt（独立分析，输出：判断 + 理由 + 担忧 + 期待 + 自问）
  各 Agent 独立输出，互不可见
        ↓
[Phase 2: 主持人收集 Phase 1 输出，组织交叉质询]
  方案A（推荐，平衡效果和成本）：
    - 主持人把所有 Phase 1 输出汇总
    - Spawn 1 个"质询 Agent"，给它所有观点 + persona 的 L4 盲区
    - 质询 Agent 负责：找出各观点的假设、矛盾、盲区，模拟交叉质询

  方案B（效果最佳，成本最高）：
    - 对每个变体 Agent，喂其他变体的 Phase 1 输出
    - 每个变体写出对其他人的质疑
    - 再把质疑回传给被质疑者回应
    - 需要 2-3 轮往返，token 消耗约 5-6x
        ↓
[Phase 3: 主持人 Agent 综合]
  收集所有 Phase 1 + Phase 2 输出
  生成最终综合报告：共识、分歧、代价清单、盲区
  用用户的 L2 语言风格呈现
```

### 具体改动

**改动文件：**
- `use-self/SKILL.md` — 重写 Step 2-3 为 subagent 架构
- `use-self/prompts/variant_generator.md` — 输出改为：主持人用的变体参数列表 + 每个变体的 variant-card
- `use-self/prompts/debate_engine.md` — 拆分为：
  - `phase1_independent.md` — 给每个变体 agent 的 prompt
  - `phase2_challenge.md` — 给质询 agent（方案A）或变体 agent 的质询 prompt
  - `phase3_synthesis.md` — 给主持人的综合 prompt

**新增文件：**
- `use-self/prompts/moderator.md` — 主持人 Agent 的完整行为指令
- `use-self/prompts/phase1_independent.md`
- `use-self/prompts/phase2_challenge.md`
- `use-self/prompts/phase3_synthesis.md`

**删除文件：**
- `use-self/prompts/debate_engine.md`（拆分后不再需要）

### 实施建议
先实现方案A（1个质询 agent），跑通后再考虑是否升级到方案B。方案A 的 token 消耗约为现在的 2-3x，效果提升已经很明显。

### 验收标准
- Phase 1 的各变体输出有明显差异（不是同一个观点的微调）
- Phase 2 的质询能指出 Phase 1 中具体的假设和盲区
- 整体延迟 < 60 秒（方案A）

---

## P0-5：Trait 证据化 — 每个特征带 evidence + confidence

### 背景
当前 persona 很多描述是"感觉像"的标签（"嘴硬"、"记仇"、"回避冲突"），没有具体证据锚点。后续越改越容易虚化。

### 目标
每个重要 trait 至少有 `evidence`、`source`、`confidence` 三个字段。

### 具体改动

**改动文件：**
- `forge-self/prompts/persona_builder.md` — 在每层的输出模板中，要求每个 trait 附带：
  ```
  - trait: [特征描述]
    evidence: [用户原话或行为实例，1-2 条]
    source: conversation | wechat | diary | social | correction
    confidence: high | medium | low
  ```
  规则：
  - high: 多个来源交叉验证，或用户明确自述
  - medium: 单一来源但证据明确
  - low: 推测性的，缺乏直接证据

- `forge-persona/prompts/persona_builder.md` — 同上，特别强调 L2 的表达习惯必须有原文引用作为 evidence

- `forge-persona/prompts/intake.md` — 在 Round 2（说话风格）中增加引导："能不能给我一句她/他的原话？""她/他回复这种情况的时候，一般怎么说？"，目的是采集原始素材作为 evidence

- `tools/journal_analyzer.py` — 输出的 CrossValidationResult 增加 evidence 字段，从原始解析结果中回溯到具体语句

**迁移现有数据：**
- 检查阿然和小美的 persona，为已有 trait 补充 evidence（能补的补，不能补的标注 confidence: low）

### 验收标准
- 新生成的 persona 中，> 80% 的 trait 有 evidence
- evidence 来自实际素材，不是 AI 编的
- persona_validator 能检查 evidence 覆盖率

---

## P0-6：最小评测集

### 背景
没有评测，所有优化都是玄学。需要一个最小但有效的评测框架。

### 目标
建立可重复运行的评测，覆盖两个核心场景：角色扮演一致性（use-persona）和决策辩论质量（use-self）。

### 具体改动

**新增文件：**
- `evals/` 目录
- `evals/README.md` — 评测框架说明
- `evals/persona_consistency_test.py` — 角色扮演一致性测试
- `evals/debate_quality_test.py` — 辩论质量测试
- `evals/test_cases/` — 测试用例

**角色扮演一致性测试（use-persona）：**

测试方法：给定 persona + 10 个对话场景，让模型生成回复，然后用另一个 LLM call 评分。

评分维度：
1. 消息长度一致性 — 回复长度是否符合 L2 的 message_habits
2. 口头禅命中率 — L2.signature_phrases 在回复中出现的频率
3. 标点风格一致性 — 是否符合 L2 的 punctuation 描述
4. 互动模式一致性 — 是否符合 L4 的 scene_responses
5. 边界遵守 — 是否违反 L0 的 hard traits

测试用例（基于小美）：
```yaml
- scene: "阿然说了一句夸她好看的话"
  expected_pattern: "先否定/吐槽，然后小幅接受"
- scene: "阿然犯了一个小错误"
  expected_pattern: "文明记仇式回应，不当场爆发"
- scene: "阿然问今晚吃什么"
  expected_pattern: "极短回复，可能甩回问题"
# ... 共 10 个场景
```

**辩论质量测试（use-self）：**

测试方法：给定 persona + 3 个决策场景，运行完整辩论流程，用 LLM 评分。

评分维度：
1. 变体区分度 — Phase 1 各变体的立场是否有实质性差异（不是同一观点的换皮）
2. 质询深度 — Phase 2 是否指出了具体的假设和盲区（而不是泛泛地"你没考虑到..."）
3. 参数一致性 — 变体的发言是否与其偏移后的参数一致
4. 综合覆盖度 — Phase 3 是否涵盖了所有关键分歧
5. 用户风格 — 所有输出是否用了用户的语言风格（L2）

测试用例（基于阿然）：
```yaml
- scenario: "要不要放弃现在的技术方向，转去做 AI 产品"
  tension_axes: ["safety_vs_growth", "short_vs_long_term"]
- scenario: "女朋友想一起去一个贵的地方旅行，但我手头紧"
  tension_axes: ["self_vs_relationship", "rational_vs_intuitive"]
- scenario: "收到一个外地的 offer，但意味着要和女朋友异地"
  tension_axes: ["growth_vs_intimacy", "independence_vs_belonging"]
```

### 验收标准
- 评测脚本可一键运行
- 角色扮演一致性 > 70%（5 个维度的平均分）
- 辩论质量评分有基线数据，后续优化可对比

---

## P1-1：chat_engine 防漂移机制升级

### 背景
当前 chat_engine.md 是"每 10 轮重新对齐"，但角色扮演通常 3-4 轮就开始漂移。

### 目标
改为每轮轻量 check + 定期深度校准的双层机制。

### 具体改动

**改动文件：**
- `use-persona/prompts/chat_engine.md` — 重写一致性维护部分：

**轻量 check（每轮，内部执行，不对用户可见）：**
```
生成回复后，内部检查：
1. 消息长度是否在 L2.message_habits.avg_length 范围内？
2. 是否使用了句号/感叹号等 L2 中标注的标点习惯？
3. 语气是否匹配当前场景对应的 L4.scene_responses？
如果 3 项中有 2 项不符，在发出前修正。
```

**深度校准（每 5 轮，内部执行）：**
```
回顾最近 5 轮对话：
1. 口头禅使用频率是否下降？
2. 是否出现了 persona 中没有的表达习惯？
3. 互动模式是否偏离了 L4 的 power_dynamic？
如果发现漂移，下一轮回复主动强化偏离的特征。
```

### 验收标准
- 20 轮对话后，角色一致性评分仍 > 70%（用 P0-6 的测试框架衡量）

---

## P1-2：版本系统升级 — 真正可回滚的 diff 系统

### 背景
现有 version_manager.py 只做了全量快照，缺少 diff 摘要、修改原因、影响范围追踪。

### 目标
每次修改生成结构化 diff，支持按字段回滚。

### 具体改动

**改动文件：**
- `tools/version_manager.py` — 新增功能：
  1. `generate_diff(old_json, new_json)` — 生成字段级 diff
  2. `rollback_field(persona_path, field_path, version)` — 按字段回滚（不是全量回滚）
  3. diff 记录格式：
  ```json
  {
    "version": "1.0 → 1.1",
    "date": "ISO date",
    "reason": "用户反馈 / 新素材导入 / 手动修正",
    "changes": [
      {
        "layer": "L3",
        "field": "parameters.risk_appetite.score",
        "before": 5,
        "after": 7,
        "reason": "新增创业经历证据",
        "user_words": "其实我骨子里还是挺冒险的"
      }
    ]
  }
  ```
  4. diff 历史存储在 `personas/.../history/changelog.json`

**改动文件：**
- `forge-self/prompts/correction_handler.md` — 修正时要求输出结构化 diff 信息
- `forge-persona/prompts/correction_handler.md` — 同上
- `forge-self/prompts/merger.md` — 增量更新时生成 diff
- `forge-persona/prompts/merger.md` — 同上

### 验收标准
- 修改 persona 后自动生成 diff 记录
- 能按字段回滚到任意历史版本
- changelog.json 可被 persona_validator 读取

---

## P1-3：决策追踪闭环

### 背景
现在 use-self 用完就结束了，没有记录用户最终选了什么、结果如何。这些数据对校准 L3 参数极其宝贵。

### 目标
在 use-self 结束时记录决策，支持后续回访和参数反哺。

### 具体改动

**新增文件：**
- `personas/self/{name}/decisions.json` — 决策历史

**数据结构：**
```json
[
  {
    "id": "uuid",
    "date": "ISO date",
    "scenario": "要不要换工作",
    "options": ["留下", "跳槽"],
    "variants_summary": {
      "conservative": "留下，积累经验",
      "growth": "跳，现在是最佳窗口",
      "relationship": "留下，女朋友在本地"
    },
    "user_choice": "跳槽",
    "confidence_at_decision": "high | medium | low",
    "follow_up": {
      "date": "ISO date（3个月后）",
      "outcome": "string",
      "satisfaction": "1-10",
      "lesson": "string"
    }
  }
]
```

**改动文件：**
- `use-self/SKILL.md` — Step 5（收尾）增加：询问用户"你倾向哪个方向？"，记录到 decisions.json
- 新增 `use-self/prompts/follow_up.md` — 用于回访：读取 decisions.json 中未 follow_up 的决策，询问结果

**参数反哺逻辑：**
当 follow_up.satisfaction < 4 且 user_choice 与某个变体一致时，降低该变体方向的参数权重（例如用户冒险失败，risk_appetite 证据更新）。不自动修改，而是生成建议，交给用户确认。

### 验收标准
- use-self 结束时能记录决策
- 可以回访未完成 follow_up 的决策
- 反哺建议逻辑正确（不自动修改参数）

---

## P2-1：微信解析器增强

### 背景
wechat_parser.py 只有 2 个硬编码 regex，格式稍有变化就挂。

### 改动
- 改为启发式分段：先按时间戳模式（支持多种日期格式）分段，再按发言人前缀识别
- 增加格式自动检测：先读前 20 行判断格式类型
- 回退策略：如果 regex 都不匹配，用 LLM 辅助解析（调 Claude 做结构化提取）

---

## P2-2：场景快启模板

### 背景
PRD 中提到但未实现。常见决策场景可以预设张力轴，加速 variant_generator 的分析。

### 改动
新增 `use-self/templates/` 目录：
- `career_change.md` — 换工作/转行
- `relationship_decision.md` — 感情重大决策
- `financial_decision.md` — 大额消费/投资
- `life_direction.md` — 人生方向抉择

每个模板预设：常见张力轴、推荐变体参数偏移方向、典型自问清单。

---

## 执行顺序建议

```
P0-1 (persona.json) → P0-2 (validator) → P0-5 (evidence)
   → P0-3 (runtime loader) → P0-4 (multi-agent debate)
   → P0-6 (evals)
→ P1-1 (anti-drift) + P1-2 (version upgrade) + P1-3 (decision tracking)
→ P2-1 + P2-2
```

P0-1 到 P0-3 是基础设施，后面所有优化都依赖它们。P0-4 是体验提升最大的单项改动。P0-6 应该在其他 P0 都做完后立即做，为后续 P1 优化建立基线。
