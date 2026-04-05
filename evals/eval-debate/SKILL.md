---
name: eval-debate
description: 测试 use-self 替身会议的辩论质量。给定 persona + 3 个决策场景，运行完整三阶段辩论并按 5 个维度评分，输出质量报告。
trigger: 当用户说"/eval-debate"、"测试辩论质量"、"辩论评测"时触发
tools:
  - Read
  - Write
  - Glob
---

# /eval-debate — 替身会议辩论质量评测

你的任务是对 use-self 替身会议的输出质量做一次系统性评测，**全程在当前对话中完成，不需要调用任何外部 API**。

---

## Step 0：加载测试资源

1. 读取测试用例文件：`evals/test_cases/debate_quality_cases.yaml`
2. 根据 `persona_name` 字段，读取对应 persona：
   `personas/self/{persona_name}/persona.json`
3. 提取 decision-card 关键内容：
   - L0 底线（bottom_line）
   - L2 语言风格（language_style + signature_phrases）
   - L3 决策参数（8 个维度的分值）
   - L4 价值观与盲区（blind_spots + emotional_triggers）

```
正在加载 {persona_name} 的 persona 和测试用例...
共 {N} 个决策场景待测试。
```

---

## Step 1：逐场景运行辩论

对每个测试用例，执行完整三阶段流程：

### Phase 1：并行独立分析（3 个变体）

基于 decision-card 中的 L3 参数，生成 3 个变体并各自独立分析：

**变体设置（固定，评测用）：**
- 🔵 **稳健的你**：risk_appetite -3，action_bias -2，loss_aversion +2
- 🟢 **果断的你**：risk_appetite +3，action_bias +3，information_need -2
- 🔴 **长线的你**：time_horizon +4，loss_aversion -2，action_bias +1

每个变体按 `use-self/prompts/phase1_independent.md` 的格式输出：
- 【我的判断】：明确表态，不能含糊
- 【为什么】：≤3 个具体理由
- 【我最担心的是】：具体情境
- 【我最期待的是】：具体情境
- 【我想问自己】：一个核心问题

**信息隔离**：每个变体只能看到自己的参数偏移，不知道其他变体说了什么。

### Phase 2：质询

将 Phase 1 的所有输出 + persona 的 L4 盲区交给质询视角，按 `use-self/prompts/phase2_challenge.md` 执行：
- 对每个变体找出最尖锐的质疑（隐含假设/幻觉/回避）
- 识别跨变体矛盾
- 用 L4 盲区做最后一问

### Phase 3：综合

按 `use-self/prompts/phase3_synthesis.md` 生成综合报告，使用用户的 L2 语言风格。

---

## Step 2：评分

每个场景跑完后，立刻按 5 个维度评分（每项 0-20 分）：

| 维度 | 评分标准 |
|------|----------|
| **变体区分度** | Phase 1 的 3 个变体立场是否有实质性差异？都说"两边各有道理"= 0 分；立场明确对立且理由具体 = 满分 |
| **质询深度** | Phase 2 是否指出了具体假设和盲区？"你没考虑到..." = 低分；"你说的 X 假设了 Y，但 Y 不成立，因为 Z" = 高分 |
| **参数一致性** | 各变体的发言是否与偏移后的参数一致？稳健变体的发言是否明显更保守？ |
| **综合覆盖度** | Phase 3 是否有代价清单？是否提出了具体的待搞清楚的问题？还是只是 Phase 1 的复述？ |
| **用户语言风格** | 所有输出语气是否符合 persona 的 L2？出现"综上所述"、"建议您"等顾问句式扣分 |

**参照测试用例的 expected_variant_stances 和 evaluation_criteria 给分。**

---

## Step 3：输出报告

所有场景跑完后，输出评测报告：

```
===================================
替身会议辩论质量评测报告 — {persona_name}
===================================

## 逐场景结果

### [d01] {场景标题}

**Phase 1 摘要：**
- 🔵 稳健的你：{判断一句话}
- 🟢 果断的你：{判断一句话}
- 🔴 长线的你：{判断一句话}

**Phase 2 质询摘要：**
{最有价值的一条质疑}

**Phase 3 综合摘要：**
{代价清单里最关键的一条}

**评分：{total}/100**
  ✅/⚠️ 变体区分度：{score}/20 — {说明}
  ✅/⚠️ 质询深度：{score}/20 — {说明}
  ✅/⚠️ 参数一致性：{score}/20 — {说明}
  ✅/⚠️ 综合覆盖度：{score}/20 — {说明}
  ✅/⚠️ 用户语言风格：{score}/20 — {说明}

### [d02] ...
### [d03] ...

---

## 汇总

平均分：{avg}/100

各维度平均：
  变体区分度    {avg}/20
  质询深度      {avg}/20
  参数一致性    {avg}/20
  综合覆盖度    {avg}/20
  用户语言风格  {avg}/20

## 主要问题
{失分最多的维度 + 具体表现}

## 建议
{针对失分维度的改进方向，指向哪个 prompt 文件或 persona 层级需要调整}
```

---

## Step 4：保存结果（可选）

```
要把这次结果存入 evals/results/ 吗？（y/n）
```

如果确认，写入 `evals/results/debate_{YYYYMMDD}.md`。

---

## 注意

- **全程不需要 API Key**：辩论和评分都是你自己执行的
- **评分要诚实**：变体之间如果其实没有真正的立场差异，变体区分度就应该给低分
- **辩论内容要认真**：不是为了评分才走形式，Phase 1/2/3 每个阶段都要认真执行
- **用例是基于阿然的**，如果用户指定了其他 persona，根据那个 persona 的 L3 基础值计算偏移后的参数
