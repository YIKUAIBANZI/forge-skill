# Stand-in (替身)

> When you can't see yourself clearly, let your digital stand-ins help you look again.

---

## Why This Exists

Most difficult personal decisions aren't hard because you lack information or wisdom. They're hard because:

- You're **inside the situation**, and emotions distort judgment
- Your current environment **hijacks your thinking**
- External advice, though correct in principle, **doesn't fit your actual circumstances**

**Stand-in is not about finding a "smarter person" to advise you.**

It's about distilling your own personality into a foundation, then generating multiple versions of yourself with different parameter settings — and letting those stand-ins collectively analyze your decision from angles you can't see from inside the situation.

---

## Core Design

### Distilling Yourself, Not Someone Else

| | ex-skill / colleague-skill | Stand-in |
|--|--|--|
| Distillation target | Others (ex / colleague) | Yourself |
| Output | 1 persona | N variants |
| Use case | Companionship / work continuity | Personal decision support |
| Core value | Recreate someone else | Help you see yourself clearly |

### Multiple Variants, Not Multiple "Experts"

This isn't "invite three thought leaders to analyze your situation objectively." Instead, it generates multiple versions of you from the same personality foundation — with different parameters dialed up or down:

- Variants are generated based on the **tension axes in your specific decision** (not fixed "conservative/aggressive" templates)
- Each variant **is still you** — just with certain tendencies amplified
- Stand-ins speak in **your own voice and style**

### Progressive Discussion, Not Direct Answers

```
Phase 1: Independent Analysis (each stand-in states their position + reasoning)
    ↓
Phase 2: Cross-Examination (stand-ins challenge each other's blind spots)
    ↓
Phase 3: Synthesis (consensus, core disagreements, cost breakdown per option)
```

---

## Installation

### Requirements

- Claude Code (desktop or CLI)
- Python 3.10+ (only needed for material parsing tools)

### Setup

```bash
git clone https://github.com/your-username/forge-skill.git
cd forge-skill
pip install -r requirements.txt  # optional, for material parsing

claude skill add ./create-standin
claude skill add ./use-standin
```

### Step 1: Create Your Stand-in

In Claude Code, type:
```
创建替身
```
*(or: "create my stand-in")*

Claude will guide you through four rounds of intake conversation to build your personality foundation.

### Step 2: Use Your Stand-in for Decisions

In Claude Code, type:
```
替身会议
```
*(or: "stand-in session")*

Describe what you're wrestling with. Your stand-ins will run through the three-phase discussion and help you see what you can't see from inside.

---

## Privacy

- All data is processed locally — nothing is uploaded
- Parsing tools extract personality signals only; raw chat content is not stored
- `standins/` is gitignored by default

---

## License

MIT
