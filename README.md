# Forge Skill

> 锻造人格的工具。蒸馏自己，也蒸馏身边的人。

---

## 两种模式

### `/forge-self` — 蒸馏自己

当你看不清自己时，用数字替身帮你重新看清自己。

通过多轮对话和素材导入，提取你的人格底座——然后在关键决策时，召唤多个"参数不同的自己"一起讨论。

**使用出口**：`/use-self`（替身决策会议）

---

### `/forge-persona [name]` — 蒸馏他人

把一个你身边的人——朋友、家人、前任、已离开的人——以 ta 的方式留下来。

用 ta 的聊天记录、社交媒体、你对 ta 的描述，还原 ta 说话的方式、互动的习惯、和你之间的默契。

**使用出口**：`/use-persona [name]`（以 ta 的身份和你对话）

---

## 核心设计

### forge-self 的独特之处

**不是找"更好的自己"，而是找"更看得清自己"的镜像。**

私人决策之所以难，不是缺少道理，而是人身处局中：
- 情绪干扰判断
- 环境绑架思路
- 外部建议脱离实际处境

替身的解法：基于同一个人格底座，生成多个参数不同的变体——不是固定的"保守/激进"，而是根据**这个具体场景的矛盾轴**动态生成：

```
Phase 1: 每个变体独立分析，各自表态
    ↓
Phase 2: 变体互相质疑，暴露盲区
    ↓
Phase 3: 共识、分歧、每个选择的代价清单
```

不给最优解。替身是镜子，不是顾问。

---

### forge-persona 的独特之处

**行为重于标签，关系视角为核心。**

不只还原 ta 是什么人，而是还原 ta 和你之间的具体互动模式：

- ta 的消息长度和节奏
- ta 的口头禅和句式（原样保留）
- 当你倾诉时 ta 怎么回
- 你们之间特有的固定梗

---

## 两种人格档案的层级设计

| 层级 | forge-self | forge-persona |
|------|-----------|---------------|
| L0 | 硬性覆写（底线和原则） | 硬性特征（最稳定的行为） |
| L1 | 身份认同 | 身份背景 + 关系信息 |
| L2 | 表达风格 | **表达风格（核心层）** |
| L3 | **决策模式（8维参数）** | 思维风格 |
| L4 | **价值观与盲区** | **互动模式（关系专属层）** |
| L5 | 纠正层 | 纠正层 |

---

## 安装

```bash
git clone https://github.com/YIKUAIBANZI/forge-skill.git
cd forge-skill

# 可选：素材解析功能
pip install -r requirements.txt

# 注册 Skill
claude skill add ./forge-self
claude skill add ./forge-persona
claude skill add ./use-self
claude skill add ./use-persona
```

## 使用

```
/forge-self              # 开始蒸馏自己
/forge-persona 小明      # 开始蒸馏"小明"
/use-self                # 召唤替身决策会议
/use-persona 小明        # 以小明的身份和你对话
```

---

## 数据来源支持

| 素材 | 格式 | 工具 |
|------|------|------|
| 微信聊天记录 | txt / html | `tools/wechat_parser.py` |
| 社交媒体内容 | json / txt | `tools/social_parser.py` |
| 日记/笔记 | md / txt / json | `tools/diary_parser.py` |
| 跨源综合分析 | — | `tools/journal_analyzer.py` |

---

## 目录结构

```
forge-skill/
├── forge-self/               # /forge-self Skill
│   ├── SKILL.md
│   └── prompts/
│       ├── intake.md
│       ├── self_analyzer.md
│       ├── value_mapper.md
│       ├── persona_builder.md
│       ├── merger.md
│       └── correction_handler.md
├── forge-persona/            # /forge-persona Skill
│   ├── SKILL.md
│   └── prompts/
│       ├── intake.md
│       ├── persona_builder.md
│       ├── merger.md
│       └── correction_handler.md
├── use-self/                 # /use-self Skill（替身决策会议）
│   ├── SKILL.md
│   └── prompts/
│       ├── variant_generator.md
│       └── debate_engine.md
├── use-persona/              # /use-persona Skill（以 ta 的身份对话）
│   ├── SKILL.md
│   └── prompts/
│       └── chat_engine.md
├── tools/                    # 共用解析工具
├── personas/
│   ├── self/                 # 自我替身（本地，gitignored）
│   └── others/               # 他人档案（本地，gitignored）
└── docs/PRD.md
```

---

## 隐私

- 所有数据本地处理，不上传任何服务器
- `personas/` 目录已 gitignored，不会意外提交
- 解析工具只提取人格信号，不存储原始聊天内容

---

## 致谢

设计灵感来自 [ex-skill](https://github.com/therealXiaomanChu/ex-skill) 和 [colleague-skill](https://github.com/titanwings/colleague-skill)。

---

MIT License
