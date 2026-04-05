# Forge Skill

> Tools for forging personalities. Distill yourself, and the people around you.

---

## Two Modes

### `/forge-self` — Distill Yourself

When you can't see yourself clearly, your digital stand-ins help you look again.

Through guided conversation and imported materials (chat logs, journals, social posts), Forge builds a five-layer personality foundation. When you face a real decision, it spawns multiple versions of you — each with different parameters — to analyze the situation from angles you can't see from inside.

**Use with**: `/use-self` (stand-in decision meeting)

---

### `/forge-persona [name]` — Distill Someone Else

Preserve someone in your life — a friend, family member, ex, someone who's gone — in the way they actually talked.

Using their chat records, social media, and your descriptions, Forge reconstructs how they communicated: their message rhythm, their catchphrases (verbatim), their patterns with you specifically.

**Use with**: `/use-persona [name]` (conversation in their voice)

---

## How the Stand-in Meeting Works

This isn't one Claude pretending to be multiple people. It's a genuine multi-agent architecture:

```
Moderator analyzes tension axes → generates 3-4 variant parameter sets
                ↓
Phase 1: Parallel variant agents (information-isolated from each other)
         Each takes a clear stance, gives reasons, names fears and hopes
                ↓
Phase 2: Challenger agent receives all Phase 1 outputs
         Finds hidden assumptions, cross-variant contradictions, blind spots
                ↓
Phase 3: Synthesis report
         ├─ Position distribution
         ├─ Consensus zone
         ├─ Core disagreements (what trade-off they represent)
         ├─ Cost manifest ("if you choose A, you need to accept...")
         └─ Things to clarify before deciding
```

Variants aren't fixed "conservative/aggressive" presets. They're generated dynamically based on the **tension axes in your specific situation**. No optimal answer is given — only clarity.

---

## Personality Layer Design

| Layer | forge-self | forge-persona |
|-------|-----------|---------------|
| L0 | Hard overrides (non-negotiables) | Hard traits (most stable behaviors) |
| L1 | Identity | Background + relationship context |
| L2 | Expression style | **Expression style (core layer, must have verbatim evidence)** |
| L3 | **Decision parameters (8 dimensions, 1-10 scored)** | Thinking style |
| L4 | **Values & blind spots** | **Interaction patterns (relationship-specific layer)** |
| L5 | Correction layer | Correction layer |

Every trait must carry `evidence`, `source`, and `confidence` fields — traits without evidence are flagged as low confidence rather than invented.

---

## Installation

```bash
git clone https://github.com/YIKUAIBANZI/forge-skill.git
cd forge-skill

# Optional: material parsing tools (WeChat / social / diary)
pip install -r requirements.txt

# Register Skills
claude skill add ./forge-self
claude skill add ./forge-persona
claude skill add ./use-self
claude skill add ./use-persona
```

## Commands

```
/forge-self              # Start distilling yourself
/forge-persona 小明      # Start distilling "Xiao Ming"
/use-self                # Start a stand-in decision meeting
/use-persona 小明        # Chat with Xiao Ming in their voice

/eval-consistency        # Test role-play consistency (auto-scored)
/eval-debate             # Test debate quality (auto-scored)
```

---

## Material Sources

| Source | Formats | Tool |
|--------|---------|------|
| WeChat chat logs | txt / html (auto-detects format) | `tools/wechat_parser.py` |
| Social media | json / txt | `tools/social_parser.py` |
| Diary / notes | md / txt / json | `tools/diary_parser.py` |
| Cross-source synthesis | — | `tools/journal_analyzer.py` |

When parsing fails, an LLM parsing prompt is generated — paste it to Claude to handle non-standard formats.

---

## Project Structure

```
forge-skill/
├── forge-self/               # /forge-self Skill
├── forge-persona/            # /forge-persona Skill
├── use-self/                 # /use-self Skill (stand-in meeting)
│   └── prompts/
│       ├── moderator.md          # Orchestrator for multi-agent flow
│       ├── variant_generator.md  # Variant param generation (JSON output)
│       ├── phase1_independent.md # Variant agent prompt (isolated)
│       ├── phase2_challenge.md   # Challenger agent prompt
│       ├── phase3_synthesis.md   # Synthesis report prompt
│       ├── template_loader.md    # Scene template matching
│       └── follow_up.md          # Decision tracking & follow-up
├── use-persona/              # /use-persona Skill (role-play chat)
│   └── prompts/
│       └── chat_engine.md        # Per-round check + every-5-round calibration
├── tools/
│   ├── persona_schema.py         # Data structure definitions
│   ├── persona_validator.py      # Validator (structure, evidence, contradictions)
│   ├── persona_runtime_loader.py # Context card generator (chat/decision/variant)
│   ├── skill_writer.py           # Persona read/write
│   ├── version_manager.py        # Versioning (field-level diff + field rollback)
│   ├── wechat_parser.py          # WeChat log parser
│   ├── social_parser.py          # Social media parser
│   ├── diary_parser.py           # Diary/notes parser
│   └── journal_analyzer.py       # Cross-source synthesis
├── templates/                # Scene templates (structured tension axes + variant hints)
│   ├── job_change.md
│   ├── relationship.md
│   ├── investment.md
│   └── life_change.md
├── evals/                    # Evaluation framework (no API key needed)
│   ├── eval-consistency/     # /eval-consistency Skill
│   └── eval-debate/          # /eval-debate Skill
├── docs/
│   ├── persona_schema.md     # Persona data schema (shared contract)
│   └── OPTIMIZATION_TASKS.md
└── personas/                 # Generated personas (local, gitignored)
```

---

## Privacy

- All data processed locally — nothing uploaded
- `personas/` is gitignored by default
- Parsing tools extract personality signals only; raw chat content is not stored
- `decisions.json` decision logs are also gitignored

---

## Credits

Inspired by [ex-skill](https://github.com/therealXiaomanChu/ex-skill) and [colleague-skill](https://github.com/titanwings/colleague-skill).

---

MIT License
