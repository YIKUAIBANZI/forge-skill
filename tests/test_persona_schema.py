"""
persona_schema.py 的单元测试
覆盖：dataclass 实例化、序列化、反序列化、参数校验
"""
import sys, os, json, pytest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools"))

from persona_schema import (
    Trait, PersonaMeta, SelfPersona, OthersPersona,
    MessageHabits, PersonaMessageHabits, DecisionParam,
    L0HardOverride, L1Identity, L2Expression,
    L3DecisionParams, L3ThinkingStyle,
    L4Values, L4InteractionPatterns, SceneResponse,
    L5Correction,
    to_dict, from_dict_self, validate_params,
)


# ─── 基本实例化 ─────────────────────────────────────────────────

class TestInstantiation:
    def test_self_persona_default(self):
        p = SelfPersona()
        assert p.meta.name == ""
        assert p.meta.type == "self"
        assert len(p.L3_decision_params.parameters) == 8

    def test_others_persona_default(self):
        p = OthersPersona()
        assert p.meta.name == ""
        assert p.meta.type == "self"  # default, should be overridden

    def test_self_persona_with_name(self):
        p = SelfPersona(meta=PersonaMeta(name="阿然", type="self"))
        assert p.meta.name == "阿然"

    def test_trait_with_evidence(self):
        t = Trait(trait="嘴硬", evidence="她从不当面承认", source="wechat", confidence="high")
        assert t.confidence == "high"
        assert t.source == "wechat"

    def test_persona_message_habits_extends(self):
        h = PersonaMessageHabits()
        assert hasattr(h, "multi_send_pattern")
        assert hasattr(h, "coldness_markers")
        assert hasattr(h, "avg_length")  # inherited from MessageHabits

    def test_decision_param_defaults(self):
        dp = DecisionParam()
        assert dp.score == 5
        assert dp.confidence == "medium"

    def test_l5_correction(self):
        c = L5Correction(date="2026-04-05", layer="L3", field="risk_appetite",
                         before="5", after="7", reason="新证据",
                         user_original_words="其实我挺冒险的")
        assert c.layer == "L3"

    def test_scene_response(self):
        sr = SceneResponse(scene="对方倾诉时", typical_response="先听完再说",
                           evidence="多次聊天记录显示")
        assert sr.scene == "对方倾诉时"


# ─── 序列化 ──────────────────────────────────────────────────────

class TestSerialization:
    def test_to_dict_self_persona(self):
        p = SelfPersona(meta=PersonaMeta(name="测试"))
        d = to_dict(p)
        assert isinstance(d, dict)
        assert d["meta"]["name"] == "测试"
        assert "L3_decision_params" in d
        assert "parameters" in d["L3_decision_params"]

    def test_to_dict_others_persona(self):
        p = OthersPersona(meta=PersonaMeta(name="小美", type="persona"))
        d = to_dict(p)
        assert d["meta"]["type"] == "persona"
        assert "L4_interaction_patterns" in d

    def test_to_dict_with_traits(self):
        p = SelfPersona()
        p.L0_hard_override.will = [
            Trait(trait="给别人机会", evidence="从不一次性否定", source="conversation")
        ]
        d = to_dict(p)
        assert len(d["L0_hard_override"]["will"]) == 1
        assert d["L0_hard_override"]["will"][0]["trait"] == "给别人机会"

    def test_to_dict_json_serializable(self):
        p = SelfPersona(meta=PersonaMeta(name="JSON测试"))
        d = to_dict(p)
        json_str = json.dumps(d, ensure_ascii=False)
        assert "JSON测试" in json_str

    def test_roundtrip_self(self):
        """序列化后反序列化，关键字段不丢失"""
        original = SelfPersona(meta=PersonaMeta(name="往返测试", type="self"))
        original.L4_values.ranking = ["自由", "亲密", "快乐"]
        d = to_dict(original)
        restored = from_dict_self(d)
        assert restored.meta.name == "往返测试"
        assert restored.L4_values.ranking == ["自由", "亲密", "快乐"]


# ─── 反序列化 ────────────────────────────────────────────────────

class TestDeserialization:
    def test_from_dict_self_basic(self):
        data = {
            "meta": {"name": "测试", "type": "self", "version": "v1.0"},
            "L3_decision_params": {
                "parameters": {
                    "risk_appetite": {"score": 7, "evidence": "创业经历", "confidence": "high"}
                },
                "decision_process": "直觉先行",
                "past_decisions": [],
            },
            "L4_values": {"ranking": ["自由", "亲密"]},
        }
        p = from_dict_self(data)
        assert p.meta.name == "测试"
        assert p.L3_decision_params.parameters["risk_appetite"]["score"] == 7

    def test_from_dict_self_missing_fields(self):
        """缺少的字段不报错，使用默认值"""
        p = from_dict_self({"meta": {"name": "最小"}})
        assert p.meta.name == "最小"
        assert p.L3_decision_params.decision_process == ""


# ─── 参数校验 ────────────────────────────────────────────────────

class TestValidateParams:
    def test_valid_params(self):
        params = {
            "risk_appetite": {"score": 7, "evidence": "", "confidence": "high"},
            "time_horizon": {"score": 3, "evidence": "", "confidence": "medium"},
        }
        errors = validate_params(params)
        assert len(errors) == 0

    def test_score_out_of_range(self):
        params = {
            "risk_appetite": {"score": 15, "evidence": "", "confidence": "high"},
            "time_horizon": {"score": 0, "evidence": "", "confidence": "medium"},
        }
        errors = validate_params(params)
        assert len(errors) == 2

    def test_score_non_numeric(self):
        params = {"risk_appetite": {"score": "高", "evidence": "", "confidence": "high"}}
        errors = validate_params(params)
        assert len(errors) == 1
