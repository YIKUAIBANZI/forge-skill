"""
Persona 校验器 (Persona Validator) — P0-2

在生成后、使用前对 persona.json 做自动校验。
检查结构完整性、类型正确性、重复/矛盾、证据覆盖率。
"""

import json
from pathlib import Path
from dataclasses import dataclass, field


@dataclass
class ValidationError:
    level: str      # "error" | "warning"
    layer: str      # "L0" ~ "L5" | "meta"
    field: str
    message: str


@dataclass
class ValidationResult:
    valid: bool = True
    errors: list = field(default_factory=list)   # list[ValidationError]
    stats: dict = field(default_factory=dict)


def validate(persona_data: dict) -> ValidationResult:
    """主校验入口，返回 ValidationResult"""
    result = ValidationResult()
    result.stats = {
        "total_traits": 0,
        "with_evidence": 0,
        "high_confidence": 0,
        "contradictions_found": 0,
    }

    ptype = persona_data.get("meta", {}).get("type", "self")

    _check_meta(persona_data, result)
    _check_L0(persona_data, result, ptype)
    _check_L1(persona_data, result)
    _check_L2(persona_data, result)

    if ptype == "self":
        _check_L3_self(persona_data, result)
        _check_L4_self(persona_data, result)
    else:
        _check_L3_persona(persona_data, result)
        _check_L4_persona(persona_data, result)

    _check_evidence_coverage(persona_data, result)
    _check_contradictions(persona_data, result, ptype)

    # 有 error 级别则标记 valid=False
    if any(e.level == "error" for e in result.errors):
        result.valid = False

    return result


# ─── 各层校验 ─────────────────────────────────────────────────

def _check_meta(data: dict, r: ValidationResult):
    meta = data.get("meta")
    if not meta:
        r.errors.append(ValidationError("error", "meta", "meta", "meta 字段缺失"))
        return

    for required in ("name", "type", "version", "created"):
        if not meta.get(required):
            r.errors.append(ValidationError(
                "warning", "meta", required, f"meta.{required} 为空"
            ))

    if meta.get("type") not in ("self", "persona"):
        r.errors.append(ValidationError(
            "error", "meta", "type", f"meta.type 必须是 'self' 或 'persona'，当前值：{meta.get('type')}"
        ))

    if not meta.get("data_sources"):
        r.errors.append(ValidationError(
            "warning", "meta", "data_sources", "meta.data_sources 为空，建议标注数据来源"
        ))


def _check_L0(data: dict, r: ValidationResult, ptype: str):
    key = "L0_hard_override" if ptype == "self" else "L0_hard_traits"
    L0 = data.get(key)
    if not L0:
        r.errors.append(ValidationError("warning", "L0", key, f"{key} 层缺失"))
        return

    for subkey in ("will", "wont", "bottom_line"):
        items = L0.get(subkey, [])
        for item in items:
            _count_trait(item, r)
            if not item.get("trait"):
                r.errors.append(ValidationError("error", "L0", subkey, "trait 字段为空"))

    # 检查 will 和 wont 是否有明显矛盾
    will_traits = [i.get("trait", "").lower() for i in L0.get("will", [])]
    wont_traits = [i.get("trait", "").lower() for i in L0.get("wont", [])]
    for w in will_traits:
        for wo in wont_traits:
            if _semantic_overlap(w, wo):
                r.errors.append(ValidationError(
                    "warning", "L0", "will/wont",
                    f"L0 疑似矛盾：will 有「{w}」，wont 有「{wo}」"
                ))
                r.stats["contradictions_found"] += 1


def _check_L1(data: dict, r: ValidationResult):
    L1 = data.get("L1_identity")
    if not L1:
        r.errors.append(ValidationError("warning", "L1", "L1_identity", "L1 层缺失"))
        return
    if not L1.get("basic_info"):
        r.errors.append(ValidationError("warning", "L1", "basic_info", "L1.basic_info 为空"))


def _check_L2(data: dict, r: ValidationResult):
    L2 = data.get("L2_expression")
    if not L2:
        r.errors.append(ValidationError("error", "L2", "L2_expression", "L2 层缺失（表达风格是核心层）"))
        return
    if not L2.get("language_style"):
        r.errors.append(ValidationError("warning", "L2", "language_style", "L2.language_style 为空"))

    habits = L2.get("message_habits", {})
    if not habits.get("avg_length") and not habits.get("signature_phrases"):
        r.errors.append(ValidationError(
            "warning", "L2", "message_habits", "L2.message_habits 关键字段为空（avg_length 和 signature_phrases）"
        ))


def _check_L3_self(data: dict, r: ValidationResult):
    L3 = data.get("L3_decision_params")
    if not L3:
        r.errors.append(ValidationError("error", "L3", "L3_decision_params", "L3 层缺失（决策参数是核心层）"))
        return

    params = L3.get("parameters", {})
    expected_params = ["risk_appetite", "time_horizon", "emotion_weight", "social_reference",
                       "action_bias", "control_need", "novelty_seeking", "conflict_style"]

    for param in expected_params:
        if param not in params:
            r.errors.append(ValidationError("warning", "L3", param, f"L3.parameters.{param} 缺失"))
            continue

        score = params[param].get("score", 0)
        if not isinstance(score, (int, float)) or not (1 <= score <= 10):
            r.errors.append(ValidationError(
                "error", "L3", param, f"L3.parameters.{param}.score = {score}，应在 1-10 范围内"
            ))

        _count_trait(params[param], r)


def _check_L3_persona(data: dict, r: ValidationResult):
    L3 = data.get("L3_thinking_style")
    if not L3:
        r.errors.append(ValidationError("warning", "L3", "L3_thinking_style", "L3 层缺失"))
        return
    if not L3.get("summary"):
        r.errors.append(ValidationError("warning", "L3", "summary", "L3.summary 为空"))


def _check_L4_self(data: dict, r: ValidationResult):
    L4 = data.get("L4_values")
    if not L4:
        r.errors.append(ValidationError("error", "L4", "L4_values", "L4 层缺失（价值观是核心层）"))
        return
    if not L4.get("ranking"):
        r.errors.append(ValidationError("warning", "L4", "ranking", "L4.ranking 为空，建议补充价值观排序"))

    for subkey in ("blind_spots", "emotional_triggers", "self_contradictions"):
        for item in L4.get(subkey, []):
            _count_trait(item, r)


def _check_L4_persona(data: dict, r: ValidationResult):
    L4 = data.get("L4_interaction_patterns")
    if not L4:
        r.errors.append(ValidationError("error", "L4", "L4_interaction_patterns", "L4 层缺失（互动模式是核心层）"))
        return
    if not L4.get("scene_responses"):
        r.errors.append(ValidationError("warning", "L4", "scene_responses", "L4.scene_responses 为空，建议补充关键场景反应"))
    if not L4.get("relationship_context"):
        r.errors.append(ValidationError("warning", "L4", "relationship_context", "L4.relationship_context 为空"))


def _check_evidence_coverage(data: dict, r: ValidationResult):
    """检查整体证据覆盖率"""
    total = r.stats["total_traits"]
    with_evidence = r.stats["with_evidence"]
    if total == 0:
        return

    coverage = with_evidence / total
    if coverage < 0.5:
        r.errors.append(ValidationError(
            "error", "global", "evidence_coverage",
            f"证据覆盖率过低：{with_evidence}/{total}（{coverage:.0%}），目标 > 80%"
        ))
    elif coverage < 0.8:
        r.errors.append(ValidationError(
            "warning", "global", "evidence_coverage",
            f"证据覆盖率偏低：{coverage:.0%}，目标 > 80%"
        ))


def _check_contradictions(data: dict, r: ValidationResult, ptype: str):
    """检查 L3 参数极端值之间的潜在矛盾"""
    if ptype != "self":
        return

    params = data.get("L3_decision_params", {}).get("parameters", {})
    if not params:
        return

    def score(p): return params.get(p, {}).get("score", 5)

    # 风险偏好极低 + 行动倾向极高 → 可疑
    if score("risk_appetite") <= 2 and score("action_bias") >= 8:
        r.errors.append(ValidationError(
            "warning", "L3", "risk_appetite/action_bias",
            "risk_appetite=低 但 action_bias=高，两者通常相关，请确认数据"
        ))
        r.stats["contradictions_found"] += 1

    # 掌控需求极高 + 随遇而安描述 → 可疑
    if score("control_need") >= 9 and score("novelty_seeking") >= 8:
        r.errors.append(ValidationError(
            "warning", "L3", "control_need/novelty_seeking",
            "control_need=极高 且 novelty_seeking=极高，两者有时矛盾，请确认"
        ))
        r.stats["contradictions_found"] += 1


# ─── 工具函数 ─────────────────────────────────────────────────

def _count_trait(item: dict, r: ValidationResult):
    """统计 trait 的证据覆盖"""
    r.stats["total_traits"] += 1
    if item.get("evidence"):
        r.stats["with_evidence"] += 1
    if item.get("confidence") == "high":
        r.stats["high_confidence"] += 1


def _semantic_overlap(a: str, b: str) -> bool:
    """简单语义重叠检测（基于关键词，非完整NLP）"""
    a_words = set(a.split())
    b_words = set(b.split())
    return len(a_words & b_words) >= 2


# ─── 格式化输出 ───────────────────────────────────────────────

def format_report(result: ValidationResult) -> str:
    lines = []
    status = "✅ 通过" if result.valid else "❌ 未通过"
    lines.append(f"校验结果：{status}")
    lines.append("")

    errors = [e for e in result.errors if e.level == "error"]
    warnings = [e for e in result.errors if e.level == "warning"]

    if errors:
        lines.append(f"🚨 错误（{len(errors)} 条）")
        for e in errors:
            lines.append(f"  [{e.layer}] {e.field}: {e.message}")

    if warnings:
        lines.append(f"⚠️  警告（{len(warnings)} 条）")
        for w in warnings:
            lines.append(f"  [{w.layer}] {w.field}: {w.message}")

    lines.append("")
    lines.append("统计：")
    for k, v in result.stats.items():
        lines.append(f"  {k}: {v}")

    return "\n".join(lines)


def validate_file(json_path: str) -> ValidationResult:
    """从文件路径校验"""
    data = json.loads(Path(json_path).read_text(encoding="utf-8"))
    return validate(data)


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("用法: python persona_validator.py <persona.json 路径>")
        sys.exit(1)
    result = validate_file(sys.argv[1])
    print(format_report(result))
    sys.exit(0 if result.valid else 1)
