# Forge Skill

> 蒸馏自己，看清自己。  
> 蒸馏亲友，留住他们的余温与回声  
> 让 AI 不再是冰冷的吐字机器。

**中文** | [English](README_EN.md) | [日本語](README_JA.md)

![License](https://img.shields.io/badge/License-MIT-yellow.svg)
![Claude Code](https://img.shields.io/badge/Claude_Code-Skill-purple.svg)
![forge-self](https://img.shields.io/badge/forge--self-蒸馏自己-blue.svg)
![forge-persona](https://img.shields.io/badge/forge--persona-蒸馏他人-orange.svg)
![Privacy](https://img.shields.io/badge/数据-本地处理-green.svg)

Forge 是一个 **local-first 的 Claude Code 人格引擎**。  
它做两件事：

- **forge-self**：蒸馏你自己的说话方式、决策模式和盲区，生成一个能帮你重新看清自己的数字替身。
- **forge-persona**：从聊天记录、记忆和描述中蒸馏他人的语气、习惯和互动方式，让 ta 的腔调被近似保留下来。

所有数据都保留在本地，不依赖服务器。

> ⚠️ 本项目仅用于个人记忆与情感疗愈。严禁用于骚扰、跟踪或侵犯他人隐私。

---

## 为什么做 Forge

> “师傅，这样怎么做我还是没有学会。”  
> “宝贝，我陪你一辈子。”  
> “妈妈，我已经可以独当一面了。”

有些话，来不及说完。  
有些人，不在了。

我们不会对一块土有感情，也不会对一块电子屏幕有感情。  
但屏幕那一边，可能有我们爱过的人、依赖过的人、想念的人。

Forge 做的不是复活谁，也不是替代谁。  
它只是试着用聊天记录、说话习惯、互动痕迹，拼出一个大概。  
起码，留住 ta 说话的腔调。

还有另一种孤独：你看不清自己。

很多时候，我们不是缺一个“最佳答案”。  
我们知道什么更健康，什么更长期正确，什么更值得坚持。  
但知道，不等于做得到。

所以人更常缺的，不是建议，  
而是一个能把自己照出来的镜子。

Forge 就是这个镜子。  
一个锻造人格的工具。蒸馏自己，也蒸馏身边的人。

---

## Forge 能做什么

### 1. forge-self —— 蒸馏自己

从这些材料中提取你的“人格底座”：

- 引导式对话
- 日记 / 笔记
- 聊天记录
- 社交媒体内容

然后把这些人格信息用于：

- 自我反思
- 决策辅助
- 多变体替身会议
- 盲区暴露与代价分析

适合这样的场景：

- “我明明知道什么是对的，但还是做不出决定。”
- “我想知道自己为什么总会在某类问题上卡住。”
- “我不想听建议，我想更清楚地看见自己。”

---

### 2. forge-persona —— 蒸馏他人

从这些材料中提取 ta 的人格轮廓：

- 微信聊天记录
- 文本导出
- 社交媒体内容
- 你对 ta 的描述和记忆

然后近似还原：

- ta 的说话风格
- ta 的口头禅和语气
- ta 和你互动的方式
- ta 的边界和典型回应模式

适合这样的场景：

- 留住老朋友的腔调
- 保留导师 / 同事 / 前任 boss 的沟通方式
- 记住一个离开的人曾经怎样回应你
- 让 agent 在角色扮演时更像“这个人”而不是泛泛的模仿

---

### 3. use-self —— 替身会议

Forge 不只是让你“拥有一个更像自己的 AI”。  
它还会在一个具体决策场景中，生成多个参数不同的你：

- 更稳健的你
- 更果断的你
- 更看长期的你
- 更重关系的你

它们不会替你做决定。  
它们会把：

- 你的真实在意点
- 每个选择的代价
- 你忽略的盲区
- 你自我矛盾的地方

一起摊开来看。

你得到的不是“最优解”，而是 **清晰度**。

---

### 4. use-persona —— 以 ta 的方式和你说话

载入蒸馏好的人格档案后，Forge 可以让 Claude：

- 用 ta 的消息长度回你
- 用 ta 的口头禅说话
- 按 ta 的互动习惯回应你
- 保留 ta 的边界和禁区

这不是复活，也不是替代。  
而是一种近似的、带着记忆痕迹的重现。

---

## 核心理念

不管你蒸馏的是：

- 朋友
- 前任 boss
- 导师
- 同事
- 爱人
- 还是你自己

本质上都在做同一件事：

**怎么把“人格”变成 agent 真正能调用的东西。**

Forge 是我对这个问题的回答。

---

## 它是怎么工作的

Forge 把“人格构建”和“人格使用”拆成了两件事。

### Step 1：Forge 阶段
收集并提炼这些信号：

- 对话
- 聊天记录
- 日记
- 社交媒体
- 用户纠正反馈

然后把它们整理成结构化的人格档案。

### Step 2：Use 阶段
这些人格档案随后可以被用于两种方向：

- **use-self**：作为决策镜子
- **use-persona**：作为记忆驱动的角色对话

### Step 3：本地优先
所有解析和人格生成都在本地完成。  
你的聊天记录和记忆不需要离开你的机器。

---

## 为什么 forge-self 有意义

我们从来不是差那个“最佳答案”。

你知道高油高盐不健康，但偶尔吃一次真的开心。  
你知道坚持锻炼很好，但偷懒一次也确实舒服。  
你知道长期正确的事情重要，但未必每次都做得到。

所以 forge-self 不是替你做决定。  
它做的是：把你的说话方式、思考方式、决策模式提炼出来，  
变成几个参数不同的你，帮你从第三视角重新看自己。

不是为了自恋。  
是为了在局中时，仍然有一面镜子。

---

## 为什么 forge-persona 有意义

有些人不会一直在。

朋友会走远，同事会离开，爱的人可能有一天不在了。  
记忆会模糊，但 ta 说话的腔调、回应你的方式、你们之间那些固定的小梗，不该那么快消失。

forge-persona 不是复活，不是替代，也不是欺骗。  
它只是试着用 ta 留下的痕迹，拼出一个大概。

至少，留住 ta 的腔调。

---

## 特性

- 本地人格蒸馏（local-first persona distillation）
- 微信聊天记录解析
- 自我反思与决策辅助
- 记忆驱动的角色扮演
- 多 Agent / 多变体辩论式 use-self
- 结构化人格档案
- 纠正层与迭代修正
- 无需服务器

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

---

## 可用命令

```bash
/forge-self              # 蒸馏自己
/forge-persona 小明      # 蒸馏"小明"
/use-self                # 召唤替身决策会议
/use-persona 小明        # 以小明的方式和你对话
```

---

## 使用示例

### 示例 1：蒸馏自己（forge-self）

在 Claude Code 中输入 `/forge-self`，Forge 会启动四轮对话来采集你的人格信息：

```
> /forge-self

Forge: 让我们开始蒸馏你的人格底座。先聊聊基本情况——
      你现在做什么工作？处于人生的什么阶段？
      如果用一句话介绍自己，你会怎么说？

You:  我是CS学生，20岁，还在摸索方向。一句话的话："什么都想试，什么都还没定。"

Forge: 你身边的人怎么评价你？跟你自己的感觉有差别吗？

You:  朋友说我挺随和的，但我觉得自己其实很有主见，只是不太表达。

     ... (4 轮对话，约 15-20 分钟)

Forge: 你的人格底座已生成 ✅
      保存在: personas/self/阿然/persona.md
      核心发现:
      - 决策风格: 直觉先行 (risk_appetite: 7/10)
      - 价值排序: 自由 > 亲密 > 快乐 > 安全 > 成长
      - 盲区: "懒" 不是全局的——在关系中你很主动
```

你还可以导入聊天记录来交叉验证：

```
You:  我有一段微信聊天记录，帮我分析一下

Forge: 好的，请把聊天记录文件发给我。支持 .txt 和 .html 格式。
      （分析完成后会自动与对话数据交叉验证，标注置信度）
```

### 示例 2：蒸馏他人（forge-persona）

```
> /forge-persona 小美

Forge: 我来帮你蒸馏"小美"的人格。先跟我聊聊——
      小美是你的什么人？你们的关系大概是什么样的？

You:  她是我女朋友。日常互动模式是她说了算，我执行。

Forge: 她平时怎么说话？消息一般多长？爱用什么口头禅？

You:  超级短，一般1-3个字一条，而且拆成很多条发。
      口头禅有"行吧""对啊""不然留着过年吗"。
      生气不会爆发，而是突然变冷——句号变多，"嗯"变多。

     ... (收集说话风格、互动模式、关键场景)

Forge: 小美的人格轮廓已生成 ✅
      保存在: personas/others/小美/persona.md
      关键特征:
      - 消息风格: 极短拆条，冷淡时省句号
      - 互动模式: 霸道女友 / 固定梗"试用期/转正/offer"
      - 核心口头禅: 行吧、对啊、嗯哼、不然留着过年吗
```

### 示例 3：替身决策会议（use-self）

```
> /use-self

Forge: 说说你在纠结什么吧。越具体越好。

You:  收到一个外地的offer，薪资翻倍，但意味着要跟女朋友异地。

Forge: 生成替身阵容:
      🔵 稳健的你 — 安全优先，不冒不必要的险
      🟢 成长的你 — 机会难得，该冲就冲
      🟡 关系优先的你 — 亲密关系是底线
      🔴 三年后的你 — 站在未来回头看

      [Phase 1: 各替身独立分析...]
      [Phase 2: 替身互相质询盲区...]
      [Phase 3: 综合报告]

      共识: 都认为需要跟女朋友认真谈一次
      核心分歧: 是否值得用关系风险换职业跳板
      你没注意到的: 你的 time_horizon 偏短期(3/10)，
                    但这次决定本质上是长期的
```

### 示例 4：角色对话（use-persona）

```
> /use-persona 小美

小美: 干嘛

You:  今天加班好累

小美: 行吧
      那你吃了吗

You:  还没

小美: 不会吧
      这都几点了
      外卖点了没

You:  你关心我啊

小美: 关心个鬼
      我怕你饿死了我没秘书用
```

---

## 项目结构

```
forge-skill/
├── forge-self/                # /forge-self 蒸馏自己
│   ├── SKILL.md
│   └── prompts/               # 四轮采集 + 人格构建 prompt
├── forge-persona/             # /forge-persona 蒸馏他人
│   ├── SKILL.md
│   └── prompts/               # 素材优先采集 + 人格构建 prompt
├── use-self/                  # /use-self 替身决策会议
│   ├── SKILL.md
│   └── prompts/               # 多 agent 辩论引擎
├── use-persona/               # /use-persona 角色对话
│   ├── SKILL.md
│   └── prompts/               # 角色扮演引擎
├── tools/                     # Python 工具
│   ├── persona_schema.py      # 人格 JSON Schema 定义
│   ├── persona_validator.py   # 人格档案校验器
│   ├── persona_runtime_loader.py  # 运行时上下文卡片生成
│   ├── skill_writer.py        # 人格文件读写
│   ├── version_manager.py     # 版本存档与 diff
│   ├── decision_logger.py     # 决策记录与追踪
│   ├── wechat_parser.py       # 微信聊天记录解析
│   ├── diary_parser.py        # 日记/笔记解析
│   ├── social_parser.py       # 社交媒体解析
│   └── journal_analyzer.py    # 多源交叉分析
├── templates/                 # 决策场景快启模板
├── personas/                  # 人格档案存储 (gitignored)
├── tests/                     # 单元测试
│   ├── test_persona_schema.py
│   ├── test_persona_validator.py
│   ├── test_runtime_loader.py
│   ├── test_skill_writer.py
│   ├── test_version_manager.py
│   ├── test_decision_logger.py
│   └── test_parsers.py
├── evals/                     # 效果评测
├── docs/                      # 文档
│   ├── PRD.md
│   └── persona_schema.md
└── requirements.txt
```

---

## 测试

运行全部测试：

```bash
cd forge-skill
pip install pytest
pytest tests/ -v
```

测试覆盖：

| 模块 | 测试文件 | 覆盖内容 |
|------|----------|----------|
| persona_schema | test_persona_schema.py | 实例化、序列化、反序列化、参数校验 |
| persona_validator | test_persona_validator.py | 结构校验、参数范围、证据覆盖率、缺失字段检测 |
| persona_runtime_loader | test_runtime_loader.py | chat/decision/variant 三种卡片生成、字段完整性 |
| skill_writer | test_skill_writer.py | MD/JSON 读写、版本管理、纠正追加、名称清洗 |
| version_manager | test_version_manager.py | diff 生成、快照存档、版本列表 |
| decision_logger | test_decision_logger.py | 决策记录、结果回填、列表查询 |
| parsers | test_parsers.py | 模块导入、数据结构、基本解析 |

---

## 隐私

所有数据本地处理，人格档案本地存储（`personas/` 已 gitignore），不依赖远程服务器。原始聊天记录和记忆不会离开你的机器。素材解析器只提取人格信号（说话风格、情绪模式、决策习惯），不存储原始内容。

---

## 搜索关键词

人格蒸馏、数字替身、自我反思、决策辅助、聊天记录人格提取、微信聊天记录分析、Claude Code Skill、local-first AI、persona distillation、digital persona、self-reflection、decision support、roleplay agent、memory-based roleplay、multi-agent debate

---

## 路线图

- 更丰富的数据源支持（QQ、钉钉、飞书、Telegram）
- 更强的多 agent 辩论调度
- 角色扮演 anti-drift 强化
- 决策追踪闭环与参数反哺
- 怀念故人应用（基于 forge-persona 的情感向产品）
- 更稳定的人格一致性，让替身更像"ta"
- 更轻量的启动方式，降低上手门槛
- 替身决策会议的可视化报告
- Web UI（让不会 CLI 的人也能用）

---

## 致谢

设计灵感来自 [ex-skill](https://github.com/therealXiaomanChu/ex-skill) 和 [colleague-skill](https://github.com/titanwings/colleague-skill)。

---

## License

MIT
