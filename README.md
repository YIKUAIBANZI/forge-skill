# Forge Skill

> 锻造人格的工具。蒸馏自己，也蒸馏身边的人。

---

## 两种模式

### `/forge-self` — 蒸馏自己

当你看不清自己时，用数字替身帮你重新看清。

通过多轮对话和素材导入，提取你的五层人格底座。在关键决策时，召唤多个「参数不同的你」真正并行思考，互相质询，帮你看清局中看不清的东西。

**使用出口**：`/use-self`（替身决策会议）

---

### `/forge-persona [name]` — 蒸馏他人

把一个你身边的人——朋友、家人、前任、已离开的人——以 ta 的方式留下来。

用 ta 的聊天记录、社交媒体内容、你的描述，还原 ta 说话的方式、互动的习惯、和你之间的默契。

**使用出口**：`/use-persona [name]`（以 ta 的身份和你对话）

---

## 核心设计

### 替身会议是怎么跑的

不是一个 Claude 扮演多个角色，而是真正的多 Agent 架构：

```
主持人分析场景张力轴，生成 3-4 个变体参数
          ↓
Phase 1：并行 spawn 多个变体 Agent（互相信息隔离）
          ↓
Phase 2：spawn 质询 Agent，接收所有 Phase 1 输出
         找出每个变体的隐含假设、矛盾、盲区
          ↓
Phase 3：综合报告
         ├─ 立场分布
         ├─ 共识区
         ├─ 核心分歧
         ├─ 代价清单（选A意味着...，选B意味着...）
         └─ 做决定前需要搞清楚的几件事
```

变体不是固定的「保守/激进」，而是根据**这个场景的核心矛盾轴**动态生成。不给最优解，只给清晰度。

---

### 人格档案层级设计

| 层级 | forge-self | forge-persona |
|------|-----------|---------------|
| L0 | 硬性覆写（底线和原则） | 硬性特征（最稳定的行为） |
| L1 | 身份认同 | 身份背景 + 关系信息 |
| L2 | 表达风格 | **表达风格（核心层，必须有原话证据）** |
| L3 | **决策模式（8 维参数化，1-10 分）** | 思维风格 |
| L4 | **价值观与盲区** | **互动模式（关系专属层）** |
| L5 | 纠正层（用户修正记录） | 纠正层 |

每个特征必须带 `evidence`、`source`、`confidence` 三个字段——没有证据的特征标注置信度，不编造。

---

## 安装

### 全局安装（所有项目都能用）

```bash
git clone https://github.com/YIKUAIBANZI/forge-skill.git ~/.claude/skills/forge-skill
```

### 项目级安装（仅当前项目可用，在 git 仓库根目录执行）

```bash
mkdir -p .claude/skills
git clone https://github.com/YIKUAIBANZI/forge-skill.git .claude/skills/forge-skill
```

安装完成后重启 Claude Code，4 个 skill 自动加载，无需其他配置。

可选：安装素材解析依赖（微信 / 社交媒体 / 日记解析）

```bash
pip install -r ~/.claude/skills/forge-skill/requirements.txt
```

## 使用

```
/forge-self              # 开始蒸馏自己（多轮对话采集 + 素材导入）
/forge-persona 小明      # 开始蒸馏"小明"
/use-self                # 召唤替身决策会议
/use-persona 小明        # 以小明的身份和你对话

/eval-consistency        # 测试角色扮演一致性（自动评分）
/eval-debate             # 测试替身会议辩论质量（自动评分）
```

---

## 数据来源支持

| 素材 | 格式 | 工具 |
|------|------|------|
| 微信聊天记录 | txt / html（多格式自动检测） | `tools/wechat_parser.py` |
| 社交媒体内容 | json / txt | `tools/social_parser.py` |
| 日记/笔记 | md / txt / json | `tools/diary_parser.py` |
| 跨源综合分析 | — | `tools/journal_analyzer.py` |

解析失败时会生成 LLM 解析 prompt，可直接交给 Claude 处理非标准格式。

---

## 目录结构

```
forge-skill/
├── forge-self/               # /forge-self Skill（蒸馏自己）
│   ├── SKILL.md
│   └── prompts/
├── forge-persona/            # /forge-persona Skill（蒸馏他人）
│   ├── SKILL.md
│   └── prompts/
├── use-self/                 # /use-self Skill（替身决策会议）
│   ├── SKILL.md
│   └── prompts/
│       ├── moderator.md          # 主持人（多 Agent 协调）
│       ├── variant_generator.md  # 变体参数生成（输出结构化 JSON）
│       ├── phase1_independent.md # 变体 Agent（信息隔离）
│       ├── phase2_challenge.md   # 质询 Agent
│       ├── phase3_synthesis.md   # 综合报告
│       ├── template_loader.md    # 场景模板加载
│       └── follow_up.md          # 决策追踪与回访
├── use-persona/              # /use-persona Skill（角色扮演对话）
│   ├── SKILL.md
│   └── prompts/
│       └── chat_engine.md        # 含每轮轻量 check + 每 5 轮深度校准
├── tools/
│   ├── persona_schema.py         # 人格数据结构定义
│   ├── persona_validator.py      # 校验器（结构/证据/矛盾检测）
│   ├── persona_runtime_loader.py # 运行时卡片生成（chat/decision/variant-card）
│   ├── skill_writer.py           # persona 读写
│   ├── version_manager.py        # 版本管理（字段级 diff + 按字段回滚）
│   ├── wechat_parser.py          # 微信记录解析
│   ├── social_parser.py          # 社交媒体解析
│   ├── diary_parser.py           # 日记解析
│   └── journal_analyzer.py       # 跨源综合分析
├── templates/                # 场景快启模板（含结构化张力轴 + 变体参数偏移）
│   ├── job_change.md
│   ├── relationship.md
│   ├── investment.md
│   └── life_change.md
├── evals/                    # 评测框架（无需 API Key）
│   ├── eval-consistency/     # /eval-consistency Skill
│   └── eval-debate/          # /eval-debate Skill
├── docs/
│   ├── persona_schema.md     # 人格数据结构文档（供各 Skill 共用）
│   └── OPTIMIZATION_TASKS.md
├── personas/                 # 生成的人格档案（本地，gitignored）
│   ├── self/
│   └── others/
└── requirements.txt
```

---

## 隐私

- 所有数据本地处理，不上传任何服务器
- `personas/` 目录已 gitignored，不会意外提交
- 解析工具只提取人格信号，不存储原始聊天内容
- `decisions.json` 决策记录同样 gitignored

---

## 致谢

设计灵感来自 [ex-skill](https://github.com/therealXiaomanChu/ex-skill) 和 [colleague-skill](https://github.com/titanwings/colleague-skill)。

---

MIT License
