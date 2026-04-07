# Forge Skill

> 蒸馏自己，看清自己。
> 蒸馏亲友，留住他们的余温与回声
> 让 AI 不再是冰冷的吐字机器。


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

## 隐私

- 所有数据本地处理
- 人格档案本地存储
- 不依赖远程服务器
- 原始聊天记录和记忆不会离开你的机器

---

## 搜索关键词

人格蒸馏、数字替身、自我反思、决策辅助、聊天记录人格提取、微信聊天记录分析、Claude Code Skill、local-first AI、persona distillation、digital persona、self-reflection、decision support、roleplay agent、memory-based roleplay、multi-agent debate

---

## 路线图

- 怀念故人应用（基于 forge-persona 的情感向产品）
- 支持更多聊天记录格式（QQ、Telegram）
- 更稳定的人格一致性，让替身更像"ta"
- 更轻量的启动方式，降低上手门槛
- 替身决策会议的可视化报告
- 更强的多 agent 调度

---

## License

MIT
