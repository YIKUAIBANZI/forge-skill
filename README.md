# 替身 (Stand-in)

> 当你看不清自己时，用数字替身帮你重新看清自己。

---

## 为什么要做这个

很多私人决策之所以难，不是因为缺少道理，而是因为：

- 人身处局中，情绪干扰判断
- 当前环境会绑架思路  
- 很多建议虽然正确，但脱离实际处境

**替身不是找一个"更聪明的人"给建议。**

替身是基于你自己的人格底座，生成多个参数不同的自己——然后让这些替身同时参与分析，帮你做更贴近自己处境的私人决策。

---

## 核心设计

### 蒸馏自己，不是蒸馏别人

| 对比 | ex-skill / colleague-skill | 替身 (Stand-in) |
|------|---------------------------|-----------------|
| 蒸馏对象 | 别人（前任/同事） | 你自己 |
| 生成物 | 1个人格 | N个变体 |
| 用途 | 陪伴/工作延续 | 私人决策辅助 |
| 核心价值 | 复现他人 | 帮你看清自己 |

### 多个变体，不是多个"专家"

不是"请三个思想家来做客观分析"，而是基于同一个人格底座，调整参数生成多个版本的你：

- 根据**具体决策场景中的矛盾轴**自动生成（不是固定的"保守/激进"）
- 每个变体都是你，只是某些倾向被放大或调低
- 替身们用**你自己的语言风格**说话，不是用"专家口吻"

### 渐进式讨论，不是直接给答案

```
Phase 1: 独立分析（每个替身各自表态，给理由）
    ↓
Phase 2: 交叉质疑（替身们互相挑战对方的盲区）
    ↓
Phase 3: 综合呈现（共识、分歧、代价清单）
```

---

## 安装与使用

### 前置要求

- Claude Code（桌面版或 CLI）
- Python 3.10+（用于素材解析工具，对话采集模式不需要）

### 安装

```bash
# 克隆仓库
git clone https://github.com/your-username/standin-skill.git
cd standin-skill

# 安装依赖（仅素材解析功能需要）
pip install -r requirements.txt
```

在 Claude Code 中注册 Skill：

```bash
claude skill add ./create-standin
claude skill add ./use-standin
```

### Step 1: 创建你的替身

在 Claude Code 中输入：

```
创建替身
```

Claude 会开始四轮对话采集：
1. **基础画像**：你是谁，人生什么阶段
2. **决策风格**：通过具体场景而非抽象问题来了解你
3. **价值观探测**：你真正在意什么，怕什么，后悔过什么
4. **素材导入**（可选）：微信聊天记录、日记、社交媒体内容

采集完成后生成你的人格底座文件 `standins/{你的名字}/persona.md`。

### Step 2: 使用替身做决策

在 Claude Code 中输入：

```
替身会议
```

描述你在纠结的事情，替身们会用渐进式讨论帮你分析。

---

## 素材导入

素材不是必须的，但质量越高，替身越准确。

### 支持的格式

| 素材类型 | 格式 | 提取内容 |
|----------|------|----------|
| 微信聊天记录 | `.txt` / `.html` | 说话风格、情绪模式、人际互动 |
| 社交媒体 | `.json` / `.txt` | 公开表达风格、价值倾向 |
| 日记/笔记 | `.md` / `.txt` / `.json` | 内心独白、深层思考、决策记录 |

### 如何导出

**微信聊天记录**：手机 → 微信 → 聊天记录 → 聊天记录迁移 → 导出到电脑

**日记**：支持 Obsidian/Notion/Day One/纸质日记拍照识别

**朋友圈**：需要第三方工具导出，推荐 WeChatExporter

---

## 隐私说明

- 所有数据只在本地处理，不上传任何服务器
- 素材解析工具只提取人格特征信号，不存储原始聊天内容
- `standins/` 目录已在 `.gitignore` 中，不会被意外提交

---

## 项目结构

```
standin-skill/
├── create-standin/           # 创建替身 Skill
│   ├── SKILL.md
│   ├── prompts/
│   │   ├── intake.md         # 四轮对话采集
│   │   ├── self_analyzer.md  # 素材人格提取
│   │   ├── value_mapper.md   # 价值观参数提取
│   │   ├── persona_builder.md # 五层人格底座模板
│   │   ├── variant_generator.md # 变体生成（在 use-standin 中使用）
│   │   ├── merger.md         # 增量更新
│   │   └── correction_handler.md # 纠正处理
│   └── tools/
│       ├── wechat_parser.py
│       ├── social_parser.py
│       ├── diary_parser.py
│       ├── journal_analyzer.py
│       ├── skill_writer.py
│       └── version_manager.py
├── use-standin/              # 使用替身决策 Skill
│   ├── SKILL.md
│   └── prompts/
│       ├── variant_generator.md # 情境自动变体生成
│       └── debate_engine.md     # 渐进式讨论引擎
├── standins/                 # 你的替身数据（本地，不提交）
├── docs/
│   └── PRD.md
├── requirements.txt
├── LICENSE
└── README.md
```

---

## 致谢

设计灵感来自：
- [ex-skill](https://github.com/therealXiaomanChu/ex-skill)：蒸馏人格类 Skill 的开创性工作
- [colleague-skill](https://github.com/titanwings/colleague-skill)：五层人格结构的工程实践

---

## License

MIT
