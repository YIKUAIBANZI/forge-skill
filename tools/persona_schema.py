"""
Persona JSON Schema 定义 (Persona Schema)

persona.json 是所有程序调用的 single source of truth。
persona.md 保留供人阅读。两者通过 skill_writer 保持同步。

支持两种类型：
  type="self"    — forge-self 生成，核心层是 L3 决策参数 + L4 价值观
  type="persona" — forge-persona 生成，核心层是 L2 表达风格 + L4 互动模式
"""

from dataclasses import dataclass, field
from typing import Literal, Optional
import json


# ─── 通用子结构 ────────────────────────────────────────────────

@dataclass
class Trait:
    """带证据的人格特征条目（通用）"""
    trait: str
    evidence: str = ""          # 用户原话或行为实例
    source: str = ""            # conversation | wechat | diary | social | correction
    confidence: str = "medium"  # high | medium | low


# ─── Meta ─────────────────────────────────────────────────────

@dataclass
class PersonaMeta:
    name: str
    type: str = "self"          # self | persona
    version: str = "v1.0"
    created: str = ""
    last_updated: str = ""
    data_sources: list = field(default_factory=list)   # conversation/wechat/diary/social
    confidence_overall: str = "medium"                  # high | medium | low


# ─── L0 ───────────────────────────────────────────────────────

@dataclass
class L0HardOverride:
    will: list = field(default_factory=list)         # list[Trait]
    wont: list = field(default_factory=list)         # list[Trait]
    bottom_line: list = field(default_factory=list)  # list[Trait]


# ─── L1 ───────────────────────────────────────────────────────

@dataclass
class L1Identity:
    basic_info: str = ""          # 年龄段/职业/人生阶段
    self_perception: str = ""     # 用户自述的自我认知
    others_perception: str = ""   # 他人评价
    labels: list = field(default_factory=list)            # 自我标签
    identity_conflicts: list = field(default_factory=list)  # 身份张力


# ─── L2 ───────────────────────────────────────────────────────

@dataclass
class MessageHabits:
    avg_length: str = ""         # 短/中/长，或字数描述
    punctuation: str = ""        # 标点习惯
    emoji_usage: str = ""        # 表情使用频率和风格
    signature_phrases: list = field(default_factory=list)  # 口头禅原话列表


@dataclass
class L2Expression:
    language_style: str = ""     # 综合语言风格描述
    message_habits: MessageHabits = field(default_factory=MessageHabits)
    communication_mode: str = "" # 说话顺序/思维方式
    emotion_expression: str = "" # 情绪表达方式
    under_pressure: str = ""     # 压力下的变化


# ─── L2 (persona 专用扩展) ─────────────────────────────────────

@dataclass
class PersonaMessageHabits(MessageHabits):
    """forge-persona 专用：更细颗粒度的消息习惯"""
    multi_send_pattern: str = ""    # 拆多条发还是一条发完
    coldness_markers: list = field(default_factory=list)   # 冷漠/距离感的表达方式
    warmth_markers: list = field(default_factory=list)     # 温暖/亲近的表达方式
    humor_style: str = ""           # 幽默方式
    fixed_phrases: list = field(default_factory=list)      # 固定句式，每项带 evidence


# ─── L3 (self 专用) ───────────────────────────────────────────

@dataclass
class DecisionParam:
    score: int = 5               # 1-10
    evidence: str = ""
    confidence: str = "medium"  # high | medium | low


@dataclass
class PastDecision:
    scenario: str = ""
    choice: str = ""
    outcome: str = ""


@dataclass
class L3DecisionParams:
    """forge-self 专用"""
    parameters: dict = field(default_factory=lambda: {
        "risk_appetite":   {"score": 5, "evidence": "", "confidence": "medium"},
        "time_horizon":    {"score": 5, "evidence": "", "confidence": "medium"},
        "emotion_weight":  {"score": 5, "evidence": "", "confidence": "medium"},
        "social_reference":{"score": 5, "evidence": "", "confidence": "medium"},
        "action_bias":     {"score": 5, "evidence": "", "confidence": "medium"},
        "control_need":    {"score": 5, "evidence": "", "confidence": "medium"},
        "novelty_seeking": {"score": 5, "evidence": "", "confidence": "medium"},
        "conflict_style":  {"score": 5, "evidence": "", "confidence": "medium"},
    })
    decision_process: str = ""   # 决策过程描述
    past_decisions: list = field(default_factory=list)  # list[PastDecision]


@dataclass
class L3ThinkingStyle:
    """forge-persona 专用：简化版，非参数化"""
    summary: str = ""            # 综合描述
    advice_giving: str = ""      # 给建议的方式
    info_preference: str = ""    # 倾向听细节还是结论
    decision_speed: str = ""     # 决策速度描述


# ─── L4 (self 专用) ───────────────────────────────────────────

@dataclass
class L4Values:
    """forge-self 专用"""
    ranking: list = field(default_factory=list)              # 价值观排序，字符串列表
    suppressed_value: str = ""                               # 压抑的价值
    blind_spots: list = field(default_factory=list)          # list[Trait]
    emotional_triggers: list = field(default_factory=list)   # list[Trait]
    self_contradictions: list = field(default_factory=list)  # list[Trait]


# ─── L4 (persona 专用) ────────────────────────────────────────

@dataclass
class SceneResponse:
    scene: str = ""              # 场景描述（如"对方倾诉时"）
    typical_response: str = ""  # 典型反应（带 evidence）
    evidence: str = ""


@dataclass
class L4InteractionPatterns:
    """forge-persona 专用"""
    power_dynamic: str = ""      # 关系中的权力/亲密动态
    fixed_memes: list = field(default_factory=list)     # 固定梗，每项带 evidence
    daily_topics: list = field(default_factory=list)    # 固定话题
    scene_responses: list = field(default_factory=list) # list[SceneResponse]
    boundaries: list = field(default_factory=list)      # 禁区，list[Trait]
    relationship_context: str = ""  # 与用户的关系特征（角色扮演的核心参考）


# ─── L5 ───────────────────────────────────────────────────────

@dataclass
class L5Correction:
    date: str = ""
    layer: str = ""       # L0 | L1 | L2 | L3 | L4
    field: str = ""
    before: str = ""
    after: str = ""
    reason: str = ""
    user_original_words: str = ""


# ─── 完整 Persona ─────────────────────────────────────────────

@dataclass
class SelfPersona:
    """forge-self 生成的 persona"""
    meta: PersonaMeta = field(default_factory=PersonaMeta)
    L0_hard_override: L0HardOverride = field(default_factory=L0HardOverride)
    L1_identity: L1Identity = field(default_factory=L1Identity)
    L2_expression: L2Expression = field(default_factory=L2Expression)
    L3_decision_params: L3DecisionParams = field(default_factory=L3DecisionParams)
    L4_values: L4Values = field(default_factory=L4Values)
    L5_corrections: list = field(default_factory=list)  # list[L5Correction]


@dataclass
class OthersPersona:
    """forge-persona 生成的 persona"""
    meta: PersonaMeta = field(default_factory=PersonaMeta)
    L0_hard_traits: L0HardOverride = field(default_factory=L0HardOverride)
    L1_identity: L1Identity = field(default_factory=L1Identity)
    L2_expression: L2Expression = field(default_factory=L2Expression)       # 使用 PersonaMessageHabits
    L3_thinking_style: L3ThinkingStyle = field(default_factory=L3ThinkingStyle)
    L4_interaction_patterns: L4InteractionPatterns = field(default_factory=L4InteractionPatterns)
    L5_corrections: list = field(default_factory=list)  # list[L5Correction]


# ─── 序列化工具 ───────────────────────────────────────────────

def to_dict(obj) -> dict:
    """递归将 dataclass 转为 dict"""
    if hasattr(obj, '__dataclass_fields__'):
        return {k: to_dict(v) for k, v in obj.__dict__.items()}
    elif isinstance(obj, list):
        return [to_dict(i) for i in obj]
    else:
        return obj


def from_dict_self(data: dict) -> SelfPersona:
    """从 dict 反序列化 SelfPersona（浅层，不递归）"""
    p = SelfPersona()
    if "meta" in data:
        p.meta = PersonaMeta(**{k: v for k, v in data["meta"].items()
                                if k in PersonaMeta.__dataclass_fields__})
    if "L1_identity" in data:
        p.L1_identity = L1Identity(**{k: v for k, v in data["L1_identity"].items()
                                      if k in L1Identity.__dataclass_fields__})
    if "L3_decision_params" in data:
        d = data["L3_decision_params"]
        p.L3_decision_params = L3DecisionParams(
            parameters=d.get("parameters", {}),
            decision_process=d.get("decision_process", ""),
            past_decisions=d.get("past_decisions", []),
        )
    if "L4_values" in data:
        p.L4_values = L4Values(**{k: v for k, v in data["L4_values"].items()
                                  if k in L4Values.__dataclass_fields__})
    if "L5_corrections" in data:
        p.L5_corrections = data["L5_corrections"]
    return p


def validate_params(params: dict) -> list[str]:
    """校验 L3 参数分值，返回错误列表"""
    errors = []
    for param_name, param_data in params.items():
        score = param_data.get("score", 5)
        if not isinstance(score, (int, float)) or not (1 <= score <= 10):
            errors.append(f"L3.parameters.{param_name}.score = {score}，应在 1-10 范围内")
    return errors


# ─── Schema 文档生成 ──────────────────────────────────────────

SCHEMA_SUMMARY = {
    "self": {
        "meta": "基本信息、版本、数据来源、置信度",
        "L0_hard_override": "will(一定会) + wont(绝对不会) + bottom_line(底线)，每项带 evidence",
        "L1_identity": "basic_info / self_perception / others_perception / labels / identity_conflicts",
        "L2_expression": "language_style / message_habits / communication_mode / emotion_expression / under_pressure",
        "L3_decision_params": "8维参数(risk_appetite/time_horizon/.../conflict_style)，每维带 score+evidence+confidence；decision_process；past_decisions",
        "L4_values": "ranking(价值排序) / suppressed_value / blind_spots / emotional_triggers / self_contradictions",
        "L5_corrections": "每次修正记录：date / layer / field / before / after / reason / user_original_words",
    },
    "persona": {
        "meta": "同 self，type='persona'，新增 relationship 字段",
        "L0_hard_traits": "最稳定的行为特征",
        "L1_identity": "同 self，增加关系信息",
        "L2_expression": "同 self + PersonaMessageHabits 扩展：multi_send_pattern / coldness_markers / warmth_markers / humor_style / fixed_phrases",
        "L3_thinking_style": "非参数化，纯描述：summary / advice_giving / info_preference / decision_speed",
        "L4_interaction_patterns": "power_dynamic / fixed_memes / daily_topics / scene_responses / boundaries / relationship_context",
        "L5_corrections": "同 self",
    }
}


if __name__ == "__main__":
    # 输出 schema 摘要
    import json
    print("=== Self Persona Schema ===")
    print(json.dumps(SCHEMA_SUMMARY["self"], ensure_ascii=False, indent=2))
    print("\n=== Others Persona Schema ===")
    print(json.dumps(SCHEMA_SUMMARY["persona"], ensure_ascii=False, indent=2))

    # 输出示例空结构
    print("\n=== 空 SelfPersona 示例 ===")
    p = SelfPersona()
    p.meta.name = "示例"
    p.meta.type = "self"
    print(json.dumps(to_dict(p), ensure_ascii=False, indent=2))
