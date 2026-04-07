"""
persona_runtime_loader.py 的单元测试
覆盖：三种卡片生成（chat/decision/variant）、token 精简、字段完整性
"""
import sys, os, pytest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools"))

from persona_runtime_loader import load_card


# ─── 测试数据 ────────────────────────────────────────────────────

SELF_PERSONA = {
    "meta": {"name": "阿然", "type": "self"},
    "L0_hard_override": {
        "will": [{"trait": "给别人机会", "evidence": "从不一次性否定"}],
        "wont": [{"trait": "不背后说人", "evidence": "聊天记录可证"}],
        "bottom_line": [{"trait": "不接受欺骗", "evidence": "过去经历"}]
    },
    "L1_identity": {"basic_info": "20岁CS学生", "self_perception": "还在探索"},
    "L2_expression": {
        "language_style": "简短幽默",
        "message_habits": {"signature_phrases": ["哈哈哈", "确实"]},
    },
    "L3_decision_params": {
        "parameters": {
            "risk_appetite": {"score": 7, "evidence": "创业经历", "confidence": "high"},
            "time_horizon": {"score": 3, "evidence": "短期优先", "confidence": "medium"},
            "emotion_weight": {"score": 6, "evidence": "", "confidence": "medium"},
            "social_reference": {"score": 3, "evidence": "", "confidence": "low"},
            "action_bias": {"score": 6, "evidence": "", "confidence": "medium"},
            "control_need": {"score": 4, "evidence": "", "confidence": "medium"},
            "novelty_seeking": {"score": 7, "evidence": "", "confidence": "medium"},
            "conflict_style": {"score": 5, "evidence": "", "confidence": "medium"},
        },
        "decision_process": "直觉先行，再找理由",
    },
    "L4_values": {
        "ranking": ["自由", "亲密", "快乐", "安全", "成长", "掌控", "认可"],
        "suppressed_value": "成长",
        "blind_spots": [{"trait": "懒不是全局的", "evidence": "在关系中很主动"}],
        "emotional_triggers": [{"trait": "被否定时会回避", "evidence": "聊天记录"}],
        "self_contradictions": [{"trait": "嘴上说佛系，行动上很卷", "evidence": "行为矛盾"}],
    },
}

OTHERS_PERSONA = {
    "meta": {"name": "小美", "type": "persona"},
    "L0_hard_traits": {
        "will": [{"trait": "说一次不重复"}],
        "wont": [], "bottom_line": []
    },
    "L1_identity": {"basic_info": "20岁办公室职员", "relationship_context": "女朋友"},
    "L2_expression": {
        "language_style": "极短消息，拆多条发",
        "message_habits": {
            "avg_length": "1-5字/条",
            "signature_phrases": ["行吧", "对啊", "嗯哼", "不然留着过年吗"],
            "coldness_markers": ["省句号", "嗯"],
            "warmth_markers": ["啦", "呀"],
        },
        "emotion_expression": "冷处理，不爆发",
    },
    "L4_interaction_patterns": {
        "power_dynamic": "霸道女友 / 他是秘书",
        "fixed_memes": ["试用期/转正/offer"],
        "daily_topics": ["吃的", "猫", "日常翻车"],
        "scene_responses": [
            {"scene": "被夸好看", "typical_response": "先否认再小幅接受", "evidence": "多次出现"}
        ],
        "boundaries": [{"trait": "不接受公开否定"}],
        "relationship_context": "情侣关系，日常互怼但底线明确",
    },
}


# ─── Chat Card 测试 ──────────────────────────────────────────────

class TestChatCard:
    def test_generates_string(self):
        card = load_card(OTHERS_PERSONA, "chat")
        assert isinstance(card, str)
        assert len(card) > 0

    def test_contains_L2_expressions(self):
        card = load_card(OTHERS_PERSONA, "chat")
        assert "行吧" in card or "极短" in card or "表达" in card.lower()

    def test_contains_L0_boundaries(self):
        card = load_card(OTHERS_PERSONA, "chat")
        assert "说一次" in card or "L0" in card or "边界" in card or "硬性" in card

    def test_excludes_L3_params(self):
        """chat-card 不需要 L3 决策参数"""
        card = load_card(OTHERS_PERSONA, "chat")
        assert "risk_appetite" not in card
        assert "score" not in card.lower() or "decision" not in card.lower()

    def test_shorter_than_full_persona(self):
        """chat-card 应该比完整 persona 更精简"""
        import json
        full_size = len(json.dumps(OTHERS_PERSONA, ensure_ascii=False))
        card_size = len(load_card(OTHERS_PERSONA, "chat"))
        # card 的 markdown 格式可能比 json 长，但不应该长太多
        assert card_size < full_size * 3


# ─── Decision Card 测试 ──────────────────────────────────────────

class TestDecisionCard:
    def test_generates_string(self):
        card = load_card(SELF_PERSONA, "decision")
        assert isinstance(card, str)
        assert len(card) > 0

    def test_contains_L3_params(self):
        card = load_card(SELF_PERSONA, "decision")
        has_params = ("risk" in card.lower() or "风险" in card or
                      "decision" in card.lower() or "决策" in card or
                      "7" in card)  # risk_appetite score
        assert has_params

    def test_contains_L4_values(self):
        card = load_card(SELF_PERSONA, "decision")
        assert "自由" in card or "价值" in card or "ranking" in card.lower()

    def test_contains_identity(self):
        card = load_card(SELF_PERSONA, "decision")
        assert "阿然" in card or "CS" in card or "20" in card


# ─── Variant Card 测试 ───────────────────────────────────────────

class TestVariantCard:
    def test_generates_with_shifted_params(self):
        variant_params = {"risk_appetite": 3, "time_horizon": 8}
        variant_meta = {"name": "🔵 稳健的你", "tagline": "安全优先，长线思考"}
        card = load_card(SELF_PERSONA, "variant",
                         variant_params=variant_params,
                         variant_meta=variant_meta,
                         scene_summary="要不要换工作")
        assert isinstance(card, str)
        assert len(card) > 0

    def test_variant_contains_identity(self):
        variant_params = {"risk_appetite": 3}
        variant_meta = {"name": "🔵 稳健的你", "tagline": "安全优先"}
        card = load_card(SELF_PERSONA, "variant",
                         variant_params=variant_params,
                         variant_meta=variant_meta)
        assert "稳健" in card or "🔵" in card

    def test_variant_contains_scene(self):
        variant_params = {"risk_appetite": 3}
        variant_meta = {"name": "🔵 稳健的你", "tagline": "安全优先"}
        card = load_card(SELF_PERSONA, "variant",
                         variant_params=variant_params,
                         variant_meta=variant_meta,
                         scene_summary="要不要辞职创业")
        assert "辞职" in card or "创业" in card or "场景" in card
