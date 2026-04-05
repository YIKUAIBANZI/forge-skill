# Forge-Skill 执行清单（给 Claude Code）

> 按顺序执行。每个任务标注了具体文件、行号、改法。不要跳步。

---

## 第一批：修 Bug（不修后面全跑不通）

### BUG-1：`tools/persona_schema.py` — SelfPersona() 无法实例化

**问题**：`PersonaMeta.name` 是必填参数（无默认值），但 `SelfPersona` 的 `meta` 字段用 `default_factory=PersonaMeta`，调用 `PersonaMeta()` 时缺少 `name` 参数，直接报 TypeError。

**文件**：`tools/persona_schema.py` 第 32 行

**修法**：给 `PersonaMeta.name` 加默认值：
```python
# 第 32 行，改为：
name: str = ""
```

**验证**：
```bash
cd tools && python3 -c "from persona_schema import SelfPersona, OthersPersona; SelfPersona(); OthersPersona(); print('OK')"
```

---

### BUG-2：`tools/persona_runtime_loader.py` — 第 278 行语法错误

**问题**：第 278 行的中文引号 `"我"` 实际上是 ASCII 双引号 `"我"`，和外层字符串定界符冲突，导致 SyntaxError。

**文件**：`tools/persona_runtime_loader.py` 第 278 行

**修法**：把外层引号改成单引号：
```python
# 第 278 行，改为：
sections.append('**以第一人称"我"说话，用上面的语言风格和口头禅。**')
```

**同时检查整个文件中是否有其他类似的引号嵌套问题**。

**验证**：
```bash
cd tools && python3 -c "import persona_runtime_loader; print('OK')"
```

---

## 第二批：数据落地（schema 定义好了但没有真实 JSON）

### DATA-1：迁移阿然的 persona 到 JSON

**目标**：基于 `personas/self/阿然/persona.md` 生成 `personas/self/阿然/persona.json`

**方法**：
1. 读取 `persona.md` 的全部内容
2. 按照 `tools/persona_schema.py` 中 `SelfPersona` 的结构，提取各层数据填入
3. 关键映射：
   - YAML frontmatter → `meta`
   - L0 的 ✅/❌/⚠️ 条目 → `L0_hard_override.will/wont/bottom_line`，每条转为 `{"trait": "...", "evidence": "...", "source": "...", "confidence": "..."}`
   - L3 决策参数表 → `L3_decision_params.parameters`，每个参数带 `score`/`evidence`/`confidence`
   - L4 价值排序 → `L4_values.ranking` 数组
   - L5 修正记录 → `L5_corrections` 数组
4. 用 `persona_schema.to_dict()` 序列化为 JSON
5. 写入 `personas/self/阿然/persona.json`

**验证**：
```bash
cd tools && python3 -c "
from persona_schema import from_dict_self, to_dict
import json
with open('../personas/self/阿然/persona.json') as f:
    data = json.load(f)
p = from_dict_self(data)
print(f'Name: {p.meta.name}')
print(f'L3 params: {len(p.L3_decision_params.parameters)} dimensions')
print(f'L4 values: {p.L4_values.ranking}')
print('OK')
"
```

---

### DATA-2：迁移小美的 persona 到 JSON

**目标**：基于 `personas/others/小美/persona.md` 生成 `personas/others/小美/persona.json`

**方法**：同 DATA-1，但使用 `OthersPersona` 的结构：
- L2 用 `PersonaMessageHabits`（展开：`multi_send_pattern`, `coldness_markers`, `warmth_markers`, `humor_style`, `fixed_phrases`）
- L3 用 `L3ThinkingStyle`（非参数化）
- L4 用 `L4InteractionPatterns`（`power_dynamic`, `fixed_memes`, `daily_topics`, `scene_responses`, `boundaries`, `relationship_context`）

**特别注意**：小美的 L2 是核心层，`fixed_phrases` 每项必须从聊天记录中找到 evidence 原文。

**验证**：
```bash
cd tools && python3 -c "
import json
with open('../personas/others/小美/persona.json') as f:
    data = json.load(f)
print(f'Name: {data[\"meta\"][\"name\"]}')
print(f'L2 fixed_phrases count: {len(data.get(\"L2_expression\",{}).get(\"message_habits\",{}).get(\"fixed_phrases\",[]))}')
print(f'L4 scene_responses count: {len(data.get(\"L4_interaction_patterns\",{}).get(\"scene_responses\",[]))}')
print('OK')
"
```

---

## 第三批：打通链路（让 forge → json → loader → use 能跑通）

### LINK-1：`use-self/SKILL.md` 数据源统一

**问题**：Step 0（第 30 行）写的是"加载 persona.md，解析五层结构"，但 Step 2&3 引用 runtime_loader 从 persona.json 加载。前后矛盾。

**文件**：`use-self/SKILL.md`

**改动**：Step 0 改为：
```markdown
### Step 0: 加载人格底座
1. 读取 `personas/self/` 目录，检查是否有已创建的替身
2. 如无替身，提示用户先运行 `/forge-self`
3. 加载 `persona.json`（single source of truth）
4. 通过 `tools/persona_runtime_loader.py` 生成 `decision-card`（精简版上下文）
```

---

### LINK-2：`use-persona/SKILL.md` 数据源统一

**文件**：`use-persona/SKILL.md`

**改动**：把所有"读取 persona.md"的描述改为"读取 persona.json，通过 runtime_loader 生成 chat-card"。persona.md 只在"展示给用户确认"时使用。

---

### LINK-3：`use-self/SKILL.md` 补充 Agent 工具声明

**问题**：frontmatter 的 `tools` 列表只有 Read/Write/Glob/Bash/AskUserQuestion，但 Step 2&3 需要 spawn subagent。

**文件**：`use-self/SKILL.md` 第 5-10 行

**改动**：在 tools 列表中增加 `Agent`：
```yaml
tools:
  - Read
  - Write
  - Glob
  - Bash
  - AskUserQuestion
  - Agent
```

---

### LINK-4：同步 `.claude/skills/` 目录

**问题**：`.claude/skills/use-self/prompts/` 只有旧的 `debate_engine.md` 和 `variant_generator.md`，缺少新增的 `moderator.md`、`phase1_independent.md`、`phase2_challenge.md`、`phase3_synthesis.md`、`emotion_detector.md`、`template_loader.md`、`follow_up.md`、`decision_logger.md`、`time_compare.md`。

**改动方案（二选一）**：
- 方案 A（推荐）：在根目录的每个 skill 的 SKILL.md 中，明确所有 prompt 引用用相对路径 `./prompts/xxx.md`。`.claude/skills/` 下的 SKILL.md 也用绝对路径指向根目录的 prompts。这样只维护一份 prompt。
- 方案 B：写一个同步脚本，每次修改后自动将根目录 prompt 复制到 `.claude/skills/` 对应位置。

**不管选哪个方案**，至少要：
1. 删除 `.claude/skills/use-self/prompts/debate_engine.md`（已拆分，不再使用）
2. 确保 `.claude/skills/` 下的 SKILL.md 和根目录的 SKILL.md 内容一致

---

### LINK-5：`tools/skill_writer.py` 确认 JSON 读写能力

**检查**：`skill_writer.py` 是否有 `write_persona_json()` 和 `read_persona_json()` 方法？

**如果没有，新增**：
```python
def write_persona_json(name: str, data: dict, persona_type: str = "self") -> str:
    """将 persona dict 写入 JSON 文件"""
    base = "self" if persona_type == "self" else "others"
    dir_path = os.path.join(PERSONAS_DIR, base, name)
    os.makedirs(dir_path, exist_ok=True)
    path = os.path.join(dir_path, "persona.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return path

def read_persona_json(name: str, persona_type: str = "self") -> dict:
    """读取 persona JSON 文件"""
    base = "self" if persona_type == "self" else "others"
    path = os.path.join(PERSONAS_DIR, base, name, "persona.json")
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
```

**验证**：
```bash
cd tools && python3 -c "
from skill_writer import write_persona_json, read_persona_json
print('write_persona_json:', callable(write_persona_json))
print('read_persona_json:', callable(read_persona_json))
print('OK')
"
```

---

## 第四批：验证器接入工作流

### VALID-1：`forge-self/SKILL.md` 接入 validator

**改动**：在 persona 生成完毕后（Phase 4 或 5），增加验证步骤：

```markdown
### Phase X: 自动校验
生成 persona.json 后，运行 `tools/persona_validator.py` 校验：
- 结构完整性（L0-L5 全部存在）
- 参数合法性（L3 scores 在 1-10）
- 证据覆盖率（> 80% 的 trait 有 evidence）
- 矛盾检测

如有 error 级问题，自动修正后重新生成。
如有 warning 级问题，展示给用户确认。
```

### VALID-2：`forge-persona/SKILL.md` 同样接入 validator

---

## 第五批：端到端验证

### E2E-1：跑通 forge-self → persona.json → validator → runtime_loader

**步骤**：
```bash
cd tools

# 1. 验证 schema
python3 -c "from persona_schema import SelfPersona; SelfPersona(); print('schema OK')"

# 2. 验证 JSON 存在
python3 -c "import json; json.load(open('../personas/self/阿然/persona.json')); print('json OK')"

# 3. 验证 validator
python3 -c "
from persona_validator import validate_persona
import json
with open('../personas/self/阿然/persona.json') as f:
    data = json.load(f)
result = validate_persona(data)
print(f'Valid: {result}')
"

# 4. 验证 runtime loader
python3 -c "
from persona_runtime_loader import load_decision_card
print('loader OK')
"
```

### E2E-2：跑通 forge-persona → persona.json → validator → chat-card

**同上，但使用小美的数据和 `load_chat_card`。**

---

## 第六批：评测基线

### EVAL-1：确认评测用例文件存在且格式正确

**检查**：
- `evals/test_cases/persona_consistency_cases.yaml` — 是否有 10 个场景，每个有 `scene` 和 `expected_pattern`
- `evals/test_cases/debate_quality_cases.yaml` — 是否有 3 个场景，每个有 `scenario` 和 `tension_axes`

### EVAL-2：跑一次 consistency eval（手动或脚本）

用小美的 persona + 3 个测试场景，生成回复，人工评估是否"像"。记录基线分数。

### EVAL-3：跑一次 debate eval（手动或脚本）

用阿然的 persona + 1 个测试场景，走完 Phase 1-3，人工评估变体区分度。记录基线分数。

---

## 执行顺序总结

```
BUG-1 + BUG-2           （10 分钟，修两个 bug）
    ↓
DATA-1 + DATA-2          （30 分钟，迁移两份 persona 到 JSON）
    ↓
LINK-1 ~ LINK-5          （20 分钟，统一数据源引用 + 同步文件）
    ↓
VALID-1 + VALID-2        （10 分钟，接入 validator）
    ↓
E2E-1 + E2E-2            （15 分钟，端到端验证）
    ↓
EVAL-1 ~ EVAL-3          （30 分钟，建立基线）
```

全部做完后，`forge → json → validate → load → use` 这条链就真正跑通了。
后续的多 agent 辩论优化、anti-drift、decision tracking 都建立在这个基础上。
