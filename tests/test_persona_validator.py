"""
persona_validator.py 的单元测试
覆盖：结构校验、参数范围、证据覆盖率、矛盾检测
"""
import sys, os, pytest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools"))

from persona_validator import validate, ValidationResult


# ─── 辅助 ────────────────────────────────────────────────────────

def _minimal_self_persona():
    """最小合法 self persona"""
    return {
        "meta": {"name": "测试", "type": "self", "version": "v1.0",
                 "created": "2026-04-05", "data_sources": ["conversation"],
                 "confidence_overall": "medium"},
        "L0_hard_override": {
            "will": [{"trait": "给机会", "evidence": "多次表现", "source": "conversation", "confidence": "high"}],
            "wont": [], "bottom_line": []
        },
        "L1_identity": {"basic_info": "20岁CS学生"},
        "L2_expression": {"language_style": "简短直接"},
        "L3_decision_params": {
            "parameters": {
                "risk_appetite": {"score": 7, "evidence": "创业经历", "confidence": "high"},
                "time_horizon": {"score": 3, "evidence": "短期优先", "confidence": "medium"},
                "emotion_weight": {"score": 6, "evidence": "感情决策占比高", "confidence": "medium"},
                "social_reference": {"score": 3, "evidence": "不太在意他人看法", "confidence": "low"},
                "action_bias": {"score": 6, "evidence": "小事快大事慢", "confidence": "medium"},
                "control_need": {"score": 4, "evidence": "顺其自然偏多", "confidence": "medium"},
                "novelty_seeking": {"score": 7, "evidence": "喜欢尝试新东西", "confidence": "medium"},
                "conflict_style": {"score": 5, "evidence": "视情况而定", "confidence": "medium"},
            }
        },
        "L4_values": {"ranking": ["自由", "亲密", "快乐"]},
        "L5_corrections": [],
    }


def _minimal_persona():
    """最小合法 persona (他人)"""
    return {
        "meta": {"name": "小美", "type": "persona", "version": "v1.0",
                 "created": "2026-04-05", "data_sources": ["wechat"],
                 "confidence_overall": "medium"},
        "L0_hard_traits": {
            "will": [{"trait": "说一次不重复", "evidence": "聊天记录", "source": "wechat", "confidence": "high"}],
            "wont": [], "bottom_line": []
        },
        "L1_identity": {"basic_info": "20岁办公室职员"},
        "L2_expression": {
            "language_style": "极短消息",
            "message_habits": {"signature_phrases": ["行吧", "对啊", "嗯哼"]}
        },
        "L3_thinking_style": {"summary": "结论先行"},
        "L4_interaction_patterns": {
            "power_dynamic": "霸道女友",
            "scene_responses": [
                {"scene": "被夸", "typical_response": "先否认再接受", "evidence": "多次出现"}
            ]
        },
        "L5_corrections": [],
    }


# ─── 合法数据测试 ────────────────────────────────────────────────

class TestValidInput:
    def test_valid_self_persona(self):
        result = validate(_minimal_self_persona())
        assert isinstance(result, ValidationResult)
        # 不应该有 error 级别的问题
        errors = [e for e in result.errors if e.level == "error"]
        assert len(errors) == 0

    def test_valid_others_persona(self):
        result = validate(_minimal_persona())
        errors = [e for e in result.errors if e.level == "error"]
        assert len(errors) == 0


# ─── 缺失字段检测 ────────────────────────────────────────────────

class TestMissingFields:
    def test_missing_meta(self):
        data = _minimal_self_persona()
        del data["meta"]
        result = validate(data)
        errors = [e for e in result.errors if e.level == "error"]
        assert len(errors) > 0

    def test_missing_meta_name(self):
        data = _minimal_self_persona()
        data["meta"]["name"] = ""
        result = validate(data)
        # 空 name 应该至少产生一个 error 或 warning
        assert len(result.errors) > 0

    def test_missing_L3_for_self(self):
        data = _minimal_self_persona()
        del data["L3_decision_params"]
        result = validate(data)
        has_l3_error = any("L3" in e.layer or "L3" in e.message for e in result.errors)
        assert has_l3_error


# ─── 参数范围检测 ────────────────────────────────────────────────

class TestParamValidation:
    def test_score_out_of_range(self):
        data = _minimal_self_persona()
        data["L3_decision_params"]["parameters"]["risk_appetite"]["score"] = 15
        result = validate(data)
        has_range_error = any("1-10" in e.message or "范围" in e.message or "score" in e.message.lower()
                             for e in result.errors)
        assert has_range_error

    def test_score_zero(self):
        data = _minimal_self_persona()
        data["L3_decision_params"]["parameters"]["risk_appetite"]["score"] = 0
        result = validate(data)
        has_range_error = any("score" in e.message.lower() or "范围" in e.message
                             for e in result.errors)
        assert has_range_error


# ─── 统计数据 ────────────────────────────────────────────────────

class TestStats:
    def test_stats_structure(self):
        result = validate(_minimal_self_persona())
        assert "total_traits" in result.stats
        assert "with_evidence" in result.stats
        assert isinstance(result.stats["total_traits"], int)

    def test_stats_count(self):
        result = validate(_minimal_self_persona())
        assert result.stats["total_traits"] >= 1  # 至少有 L0 的一个 trait
