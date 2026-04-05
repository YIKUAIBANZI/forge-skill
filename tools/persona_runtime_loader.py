"""
运行时加载器 (Persona Runtime Loader) — P0-3

根据使用场景，从完整 persona.json 中生成精简的"上下文卡片"。
避免每次把整份 persona 全塞给模型（token 浪费、长对话容易飘）。

三种卡片模式：
  chat-card     给 use-persona，聚焦表达风格和互动模式
  decision-card 给 use-self，聚焦决策参数和价值观
  variant-card  给 use-self 的每个变体 agent，参数已偏移
"""

import json
from pathlib import Path
from typing import Literal


CardType = Literal["chat", "decision", "variant"]


def load_card(
    persona_data: dict,
    card_type: CardType,
    variant_params: dict = None,
    variant_meta: dict = None,
    scene_summary: str = "",
) -> str:
    """
    生成上下文卡片（Markdown 格式，直接注入 prompt）

    persona_data: read_persona_json() 的返回值
    card_type: "chat" | "decision" | "variant"
    variant_params: variant-card 专用，偏移后的 L3 参数 dict
    variant_meta: variant-card 专用，{"name": "稳健的你", "tagline": "...", "shifts": {...}}
    scene_summary: variant-card 专用，用户的决策场景摘要
    """
    if card_type == "chat":
        return _build_chat_card(persona_data)
    elif card_type == "decision":
        return _build_decision_card(persona_data)
    elif card_type == "variant":
        return _build_variant_card(persona_data, variant_params, variant_meta, scene_summary)
    else:
        raise ValueError(f"未知 card_type: {card_type}")


# ─── chat-card（给 use-persona）──────────────────────────────

def _build_chat_card(data: dict) -> str:
    """
    抽取：L0 全部 + L1 basic_info + L2 全部 + L4 interaction_patterns
    目标 token：原 persona 的 40-50%
    """
    meta = data.get("meta", {})
    sections = [
        f"# 角色卡：{meta.get('name', '未命名')}",
        f"关系：{data.get('L1_identity', {}).get('basic_info', '')}",
        "",
    ]

    # L0：边界不能省
    L0 = data.get("L0_hard_traits") or data.get("L0_hard_override", {})
    if L0:
        sections.append("## 硬性特征（不可违反）")
        for item in L0.get("will", []):
            sections.append(f"- ✅ 一定会：{item.get('trait', '')}")
        for item in L0.get("wont", []):
            sections.append(f"- ❌ 绝对不会：{item.get('trait', '')}")
        sections.append("")

    # L2：角色扮演核心
    L2 = data.get("L2_expression", {})
    sections.append("## 表达风格")
    sections.append(f"总体：{L2.get('language_style', '')}")
    habits = L2.get("message_habits", {})
    if habits.get("avg_length"):
        sections.append(f"消息长度：{habits['avg_length']}")
    if habits.get("punctuation"):
        sections.append(f"标点习惯：{habits['punctuation']}")
    if habits.get("emoji_usage"):
        sections.append(f"表情：{habits['emoji_usage']}")
    if habits.get("signature_phrases"):
        sections.append(f"口头禅：{' / '.join(habits['signature_phrases'])}")

    # persona 专用扩展字段
    for field_name in ("multi_send_pattern", "humor_style"):
        val = habits.get(field_name)
        if val:
            sections.append(f"{field_name}：{val}")

    for label, key in [("冷漠信号", "coldness_markers"), ("温暖信号", "warmth_markers")]:
        markers = habits.get(key, [])
        if markers:
            sections.append(f"{label}：{' / '.join(str(m) for m in markers[:3])}")

    if L2.get("emotion_expression"):
        sections.append(f"情绪表达：{L2['emotion_expression']}")
    if L2.get("under_pressure"):
        sections.append(f"压力下：{L2['under_pressure']}")
    sections.append("")

    # L4 互动模式
    L4 = data.get("L4_interaction_patterns", {})
    if L4:
        sections.append("## 互动模式")
        if L4.get("power_dynamic"):
            sections.append(f"关系基调：{L4['power_dynamic']}")
        if L4.get("relationship_context"):
            sections.append(f"关系背景：{L4['relationship_context']}")

        scene_responses = L4.get("scene_responses", [])
        if scene_responses:
            sections.append("关键场景反应：")
            for sr in scene_responses:
                scene = sr.get("scene", "")
                resp = sr.get("typical_response", "")
                if scene and resp:
                    sections.append(f"  - {scene} → {resp}")

        fixed_memes = L4.get("fixed_memes", [])
        if fixed_memes:
            meme_list = [m if isinstance(m, str) else m.get("trait", "") for m in fixed_memes[:3]]
            sections.append(f"固定梗：{' / '.join(meme_list)}")

        boundaries = L4.get("boundaries", [])
        if boundaries:
            sections.append("禁区：")
            for b in boundaries:
                trait = b if isinstance(b, str) else b.get("trait", "")
                sections.append(f"  - {trait}")

    return "\n".join(sections)


# ─── decision-card（给 use-self）────────────────────────────

def _build_decision_card(data: dict) -> str:
    """
    抽取：L0.bottom_line + L1.basic_info + L2.language_style + L3 全部 + L4 全部
    目标 token：原 persona 的 50-60%
    """
    meta = data.get("meta", {})
    sections = [
        f"# 决策底座：{meta.get('name', '未命名')}",
        "",
    ]

    # L0 底线
    L0 = data.get("L0_hard_override", {})
    bottom_lines = L0.get("bottom_line", [])
    if bottom_lines:
        sections.append("## 决策底线")
        for item in bottom_lines:
            sections.append(f"- {item.get('trait', '')}")
        sections.append("")

    # L1
    L1 = data.get("L1_identity", {})
    if L1.get("basic_info"):
        sections.append(f"**身份**：{L1['basic_info']}")
        sections.append("")

    # L2 语言风格（变体说话时需要）
    L2 = data.get("L2_expression", {})
    sections.append("## 语言风格（变体说话时使用）")
    sections.append(L2.get("language_style", ""))
    habits = L2.get("message_habits", {})
    if habits.get("signature_phrases"):
        sections.append(f"口头禅：{' / '.join(habits['signature_phrases'])}")
    sections.append("")

    # L3 决策参数（核心）
    L3 = data.get("L3_decision_params", {})
    params = L3.get("parameters", {})
    if params:
        sections.append("## 决策参数 (L3)")
        param_labels = {
            "risk_appetite": "风险偏好",
            "time_horizon": "时间偏好",
            "emotion_weight": "情感权重",
            "social_reference": "社会参照",
            "action_bias": "行动倾向",
            "control_need": "掌控需求",
            "novelty_seeking": "新奇追求",
            "conflict_style": "冲突风格",
        }
        for key, label in param_labels.items():
            if key in params:
                p = params[key]
                score = p.get("score", "?")
                conf = p.get("confidence", "medium")
                evidence = p.get("evidence", "")
                ev_str = f"（{evidence}）" if evidence else ""
                sections.append(f"- {label}：{score}/10 [{conf}]{ev_str}")

    if L3.get("decision_process"):
        sections.append(f"\n决策过程：{L3['decision_process']}")
    sections.append("")

    # L4 价值观（核心）
    L4 = data.get("L4_values", {})
    if L4:
        sections.append("## 价值观 (L4)")
        if L4.get("ranking"):
            sections.append(f"价值排序：{' > '.join(L4['ranking'])}")
        if L4.get("suppressed_value"):
            sections.append(f"被压抑的价值：{L4['suppressed_value']}")

        blind_spots = L4.get("blind_spots", [])
        if blind_spots:
            sections.append("已知盲区：")
            for b in blind_spots[:3]:
                sections.append(f"  - {b.get('trait', '')}")

        triggers = L4.get("emotional_triggers", [])
        if triggers:
            sections.append("情绪触发：")
            for t in triggers[:3]:
                sections.append(f"  - {t.get('trait', '')}")

        contradictions = L4.get("self_contradictions", [])
        if contradictions:
            sections.append("自我矛盾：")
            for c in contradictions[:2]:
                sections.append(f"  - {c.get('trait', '')}")

    return "\n".join(sections)


# ─── variant-card（给 use-self 每个变体 agent）──────────────

def _build_variant_card(
    data: dict,
    variant_params: dict,
    variant_meta: dict,
    scene_summary: str,
) -> str:
    """
    基于 decision-card，替换 L3 参数为偏移后的值，附加变体身份和场景。
    """
    if not variant_params:
        variant_params = {}
    if not variant_meta:
        variant_meta = {}

    # 先生成 decision-card 基础
    base = _build_decision_card(data)

    sections = [base, ""]
    sections.append("─" * 40)
    sections.append(f"## 你是：{variant_meta.get('name', '变体')}")
    sections.append(f"标签：{variant_meta.get('tagline', '')}")

    shifts = variant_meta.get("shifts", {})
    if shifts:
        sections.append("参数偏移（相对于底座）：")
        param_labels = {
            "risk_appetite": "风险偏好",
            "time_horizon": "时间偏好",
            "emotion_weight": "情感权重",
            "action_bias": "行动倾向",
            "control_need": "掌控需求",
            "conflict_style": "冲突风格",
        }
        for key, delta in shifts.items():
            label = param_labels.get(key, key)
            sign = "+" if delta > 0 else ""
            base_score = data.get("L3_decision_params", {}).get("parameters", {}).get(key, {}).get("score", 5)
            new_score = max(1, min(10, base_score + delta))
            sections.append(f"  - {label}：{base_score} → {new_score}（{sign}{delta}）")

    if scene_summary:
        sections.append("")
        sections.append("## 当前决策场景")
        sections.append(scene_summary)

    sections.append("")
    sections.append("**以第一人称"我"说话，用上面的语言风格和口头禅。**")

    return "\n".join(sections)


# ─── 对外便捷接口 ─────────────────────────────────────────────

def load_chat_card(name: str, persona_type: str = "others") -> str:
    """便捷接口：从文件加载并生成 chat-card"""
    from skill_writer import read_persona_json
    data = read_persona_json(name, persona_type)
    return load_card(data, "chat")


def load_decision_card(name: str) -> str:
    """便捷接口：从文件加载并生成 decision-card"""
    from skill_writer import read_persona_json
    data = read_persona_json(name, "self")
    return load_card(data, "decision")


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("用法: python persona_runtime_loader.py <persona.json> <chat|decision>")
        sys.exit(1)

    data = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    card = load_card(data, sys.argv[2])
    print(card)
    print(f"\n--- 字符数：{len(card)} ---")
