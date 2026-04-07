# Forge Skill

> Distill yourself. Find clarity.
> Distill those you love. Keep their warmth. Keep their echo.
> Make AI less of a cold word machine.


![License](https://img.shields.io/badge/License-MIT-yellow.svg)
![Claude Code](https://img.shields.io/badge/Claude_Code-Skill-purple.svg)
![forge-self](https://img.shields.io/badge/forge--self-蒸馏自己-blue.svg)
![forge-persona](https://img.shields.io/badge/forge--persona-蒸馏他人-orange.svg)
![Privacy](https://img.shields.io/badge/数据-本地处理-green.svg)

Forge is a **local-first persona engine for Claude Code**.

It does two things:

- **forge-self**: distills your own speaking style, decision patterns, and blind spots into a digital stand-in that helps you see yourself more clearly.
- **forge-persona**: distills someone else's tone, habits, and interaction patterns from chat logs and memories, so their way of speaking can be approximately preserved.

All data stays local. No server required.

> ⚠️ This project is intended solely for personal memory and emotional healing. It must not be used for harassment, stalking, or invasion of privacy.

---

## Why Forge exists

> “Master, I still haven't learned how to do this.”  
> “Baby, I'll stay with you for life.”  
> “Mom, I can handle things on my own now.”

Some words never get fully said.  
Some people are no longer here.

We do not love a pile of dirt, and we do not love a glowing screen.  
But on the other side of that screen, there may be someone we once loved, relied on, or still miss.

Forge is not trying to bring anyone back.  
It is not trying to replace anyone either.  
It simply tries to use traces — chat logs, phrasing, habits, interaction patterns — to reconstruct an approximation.

At the very least, it tries to preserve their tone.

There is another kind of loneliness too: not being able to see yourself clearly.

Most of the time, we are not missing the “best answer.”  
We already know what is healthier, what is more disciplined, what is more correct in the long term.  
But knowing is not the same as being able to live it.

What people often lack is not advice,  
but a mirror that reflects them honestly.

Forge is that mirror.  
A tool for forging personality — your own, and the people around you.

---

## What Forge can do

### 1. forge-self — Distill yourself

Build a personality foundation from:

- guided conversation
- journals / notes
- chat logs
- social media posts

Then use it for:

- self-reflection
- decision support
- multi-variant stand-in meetings
- blind-spot exposure and tradeoff analysis

Good for situations like:

- “I know what's right, but I still can't decide.”
- “I want to understand why I always get stuck in the same kind of problem.”
- “I don't want advice. I want a clearer view of myself.”

---

### 2. forge-persona — Distill someone else

Build a persona profile from:

- WeChat chat logs
- exported text conversations
- social media content
- your own memories and descriptions

Then approximate:

- their speaking style
- their signature phrases and tone
- the way they interact with you
- their boundaries and typical responses

Good for situations like:

- preserving an old friend's tone
- keeping a mentor's or ex-boss's communication style
- remembering how someone who left used to respond to you
- making an agent feel more like *this person* instead of a generic imitation

---

### 3. use-self — Stand-in meeting

Forge does not just give you “an AI version of yourself.”  
It creates multiple parameter-shifted versions of you for a concrete decision:

- the more cautious you
- the more decisive you
- the long-term you
- the relationship-first you

They do not decide for you.  
They help surface:

- what you actually care about
- the cost of each option
- what blind spots you are ignoring
- where your internal contradictions are

What you get is not “the optimal answer,” but **clarity**.

---

### 4. use-persona — Talk in their tone

Once a persona is distilled, Forge can let Claude respond:

- with their message length
- with their signature phrases
- with their interaction habits
- with their emotional rhythm
- with their boundaries

This is not resurrection.  
It is not replacement.  
It is an approximation shaped by memory traces.

---

## Core idea

Whether you want to distill:

- a friend
- an ex-boss
- a mentor
- a colleague
- a partner
- or yourself

The underlying problem is the same:

**How do we turn personality into something an agent can actually use?**

Forge is my answer to that question.

---

## How it works

Forge separates **persona building** from **persona usage**.

### Step 1: Forge phase
Collect and distill signals from:

- conversation
- chat logs
- journals
- social posts
- user corrections

Then turn them into a structured persona profile.

### Step 2: Use phase
That profile can then be used in two directions:

- **use-self**: as a decision mirror
- **use-persona**: as a memory-driven roleplay layer

### Step 3: Local-first
All parsing and persona generation happen locally.  
Your memories and chat logs do not need to leave your machine.

---

## Why forge-self matters

We are not always missing the “best answer.”

You know greasy food is unhealthy, but eating it once feels great.  
You know consistent exercise is better, but skipping one day feels easier.  
You know long-term discipline matters, but that does not mean you can always follow through.

So forge-self does not make decisions for you.  
It extracts the way you speak, think, and decide,  
and turns that into several parameter-shifted versions of you, so you can examine yourself from a third-person angle.

Not for narcissism.  
For perspective.

---

## Why forge-persona matters

Some people do not stay forever.

Friends drift away. Colleagues leave. Someone you love may one day be gone.  
Memory blurs, but their tone, their way of responding, and the private little patterns between you should not disappear that quickly.

forge-persona is not resurrection, replacement, or deception.  
It is only an attempt to reconstruct an approximation from what they left behind.

At the very least, it preserves their tone.

---

## Features

- local-first persona distillation
- WeChat chat log parsing
- self-reflection and decision support
- memory-based roleplay
- multi-agent / multi-variant `use-self`
- structured persona profiles
- correction layer and iterative refinement
- no server required

---

## Install

### Global install (works across all projects)

```bash
git clone https://github.com/YIKUAIBANZI/forge-skill.git ~/.claude/skills/forge-skill
```

### Project-level install (run in your git repo root)

```bash
mkdir -p .claude/skills
git clone https://github.com/YIKUAIBANZI/forge-skill.git .claude/skills/forge-skill
```

Restart Claude Code after installation. All 4 skills are auto-discovered — no extra configuration needed.

Optional: install parsers for WeChat / social media / journal files

```bash
pip install -r ~/.claude/skills/forge-skill/requirements.txt
```

---

## Commands

```bash
/forge-self              # distill yourself
/forge-persona Xiaoming  # distill someone named Xiaoming
/use-self                # run a stand-in decision meeting
/use-persona Xiaoming    # talk with Xiaoming's tone
```

---

## Privacy

- all data is processed locally
- persona profiles are stored locally
- no remote server is required
- raw memories and chat logs stay on your machine

---

## Search keywords

persona distillation, digital persona, digital stand-in, self-reflection, decision support, roleplay agent, local-first AI, Claude Code skill, WeChat chat log parser, personality simulation, memory-based roleplay, multi-agent debate

---

## Roadmap

- Memorial app — an emotional product built on forge-persona
- Support for more chat formats (QQ, Telegram)
- Stronger persona consistency — make the stand-in feel more like *them*
- Lighter setup experience, lower barrier to entry
- Visual reports for use-self decision meetings
- stronger multi-agent orchestration

---

## 致谢

Design inspiration from [ex-skill](https://github.com/therealXiaomanChu/ex-skill) and [colleague-skill](https://github.com/titanwings/colleague-skill)。

---

## License

MIT
