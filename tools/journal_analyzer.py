"""
综合分析器 (Journal Analyzer)

跨数据源交叉验证，综合对话采集和素材分析结果，
输出供 AI 生成 persona.md 的完整分析报告。
"""

import json
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class TraitEvidence:
    """单条特征的证据结构"""
    trait: str                  # 特征描述
    evidence: str               # 原话或行为实例（不是 AI 概括）
    source: str                 # conversation | wechat | diary | social
    confidence: str             # high | medium | low
    cross_sources: list = field(default_factory=list)  # 其他验证来源

    def to_dict(self):
        return {
            "trait": self.trait,
            "evidence": self.evidence,
            "source": self.source,
            "confidence": self.confidence,
            "cross_sources": self.cross_sources,
        }


@dataclass
class CrossValidationResult:
    """交叉验证结果"""
    high_confidence: list = field(default_factory=list)    # TraitEvidence 列表（多源一致）
    medium_confidence: list = field(default_factory=list)  # TraitEvidence 列表（部分来源）
    contradictions: list = field(default_factory=list)     # 不同来源的矛盾点（dict 含两侧证据）
    new_findings: list = field(default_factory=list)       # 仅在素材中发现、对话未提到（TraitEvidence）


class JournalAnalyzer:
    """综合分析器：整合多个数据源，输出完整的人格分析报告"""

    def __init__(self):
        self.conversation_data: dict = {}     # 对话采集结果
        self.wechat_data: Optional[dict] = None
        self.social_data: Optional[dict] = None
        self.diary_data: Optional[dict] = None

    def load_conversation(self, data: dict):
        """加载对话采集结果（由 AI 整理的结构化数据）"""
        self.conversation_data = data

    def load_parsed_data(self, source_type: str, data: dict):
        """加载解析器输出"""
        if source_type == "wechat":
            self.wechat_data = data
        elif source_type == "social":
            self.social_data = data
        elif source_type == "diary":
            self.diary_data = data

    def load_from_files(self, parsed_files: list[str]):
        """从已有的解析结果 JSON 文件加载"""
        for file_path in parsed_files:
            p = Path(file_path)
            if not p.exists():
                continue
            data = json.loads(p.read_text(encoding="utf-8"))
            source = data.get("source", "")
            if source == "wechat":
                self.wechat_data = data
            elif source == "social_media":
                self.social_data = data
            elif source == "diary":
                self.diary_data = data

    def analyze(self) -> dict:
        """执行综合分析，返回完整报告"""
        cv = CrossValidationResult()
        personality_signals = {}

        # 1. 表达风格综合
        self._analyze_expression_style(cv, personality_signals)

        # 2. 决策模式综合
        self._analyze_decision_patterns(cv, personality_signals)

        # 3. 价值观综合
        self._analyze_values(cv, personality_signals)

        # 4. 情绪模式综合
        self._analyze_emotional_patterns(cv, personality_signals)

        # 5. 自我认知综合
        self._analyze_self_perception(cv, personality_signals)

        return {
            "cross_validation": {
                "high_confidence": [
                    t.to_dict() if isinstance(t, TraitEvidence) else {"trait": t, "evidence": "", "source": "unknown", "confidence": "low"}
                    for t in cv.high_confidence
                ],
                "medium_confidence": [
                    t.to_dict() if isinstance(t, TraitEvidence) else {"trait": t, "evidence": "", "source": "unknown", "confidence": "medium"}
                    for t in cv.medium_confidence
                ],
                "contradictions": cv.contradictions,
                "new_findings": [
                    t.to_dict() if isinstance(t, TraitEvidence) else {"trait": t, "evidence": "", "source": "unknown", "confidence": "low"}
                    for t in cv.new_findings
                ],
            },
            "personality_signals": personality_signals,
            "data_sources_used": self._list_sources(),
            "analysis_confidence": self._calculate_confidence(),
            "ai_prompt": self._generate_ai_prompt(cv, personality_signals),
        }

    def _analyze_expression_style(self, cv: CrossValidationResult, signals: dict):
        """整合表达风格数据"""
        style_data = {}

        if self.wechat_data:
            wc_signals = self.wechat_data.get("signals", {})
            avg_len = wc_signals.get("avg_message_length", 0)
            style_data["message_length"] = {
                "value": avg_len,
                "interpretation": "简短直接" if avg_len < 20 else "中等" if avg_len < 80 else "喜欢详细表达",
                "source": "wechat"
            }
            emoji_rate = wc_signals.get("emoji_usage_rate", 0)
            style_data["emoji_usage"] = {
                "value": emoji_rate,
                "interpretation": "频繁使用表情" if emoji_rate > 20 else "偶尔使用" if emoji_rate > 5 else "很少使用",
                "source": "wechat"
            }
            common_phrases = wc_signals.get("common_phrases", [])
            if common_phrases:
                style_data["common_phrases"] = {
                    "value": common_phrases,
                    "source": "wechat"
                }

        if self.social_data:
            social_signals = self.social_data.get("signals", {})
            presentation = social_signals.get("presentation_style", "")
            if presentation:
                style_data["public_presentation"] = {
                    "value": presentation,
                    "source": "social_media"
                }

        if self.diary_data:
            diary_signals = self.diary_data.get("signals", {})
            narrative = diary_signals.get("narrative_style", "")
            if narrative:
                style_data["private_narrative"] = {
                    "value": narrative,
                    "source": "diary"
                }
                # 检查公私差距
                if self.social_data:
                    social_style = self.social_data.get("signals", {}).get("presentation_style", "")
                    if social_style and social_style != narrative:
                        cv.new_findings.append(TraitEvidence(
                            trait="公私表达差距",
                            evidence=f"社交媒体上是「{social_style}」，私下日记里是「{narrative}」",
                            source="diary",
                            confidence="medium",
                            cross_sources=["social_media"],
                        ))

        signals["expression_style"] = style_data

    def _analyze_decision_patterns(self, cv: CrossValidationResult, signals: dict):
        """整合决策模式数据"""
        decision_data = {}

        # 从对话采集中获取
        conv_decisions = self.conversation_data.get("decision_params", {})
        if conv_decisions:
            decision_data["self_reported"] = conv_decisions

        # 从日记中补充
        if self.diary_data:
            diary_signals = self.diary_data.get("signals", {})
            attribution = diary_signals.get("attribution_style", "")
            if attribution:
                decision_data["attribution_style"] = {
                    "value": attribution,
                    "source": "diary"
                }

            decision_records = diary_signals.get("decision_records", [])
            if decision_records:
                decision_data["recorded_decisions"] = {
                    "value": decision_records,
                    "source": "diary",
                    "note": "从日记中发现的实际决策记录"
                }

        signals["decision_patterns"] = decision_data

    def _analyze_values(self, cv: CrossValidationResult, signals: dict):
        """整合价值观数据"""
        values_data = {}

        # 对话采集的价值排序
        conv_values = self.conversation_data.get("core_values", [])
        if conv_values:
            values_data["stated_values"] = {
                "value": conv_values,
                "source": "conversation",
                "note": "用户自述的价值排序"
            }

        # 社交媒体推断的价值观
        if self.social_data:
            inferred = self.social_data.get("signals", {}).get("inferred_values", [])
            if inferred:
                values_data["inferred_from_social"] = {
                    "value": inferred,
                    "source": "social_media",
                    "note": "从社交媒体内容推断"
                }
                # 交叉验证
                if conv_values:
                    agreed = [v for v in inferred if any(cv_val in v or v in cv_val for cv_val in conv_values)]
                    disagreed = [v for v in inferred if v not in agreed]
                    if agreed:
                        cv.high_confidence.extend([
                            TraitEvidence(
                                trait=f"价值观-{v}",
                                evidence=f"用户自述「{v}」，社交媒体内容同样体现此倾向",
                                source="conversation",
                                confidence="high",
                                cross_sources=["social_media"],
                            ) for v in agreed
                        ])
                    if disagreed:
                        cv.new_findings.extend([
                            TraitEvidence(
                                trait=f"价值观发现-{v}",
                                evidence=f"社交媒体显示「{v}」，但用户未在对话中提及",
                                source="social_media",
                                confidence="medium",
                                cross_sources=[],
                            ) for v in disagreed
                        ])

        # 日记中的价值主题
        if self.diary_data:
            themes = self.diary_data.get("signals", {}).get("recurring_themes", [])
            if themes:
                values_data["diary_themes"] = {
                    "value": themes,
                    "source": "diary",
                    "note": "日记中反复出现的主题，反映深层关切"
                }

        signals["values"] = values_data

    def _analyze_emotional_patterns(self, cv: CrossValidationResult, signals: dict):
        """整合情绪模式数据"""
        emotion_data = {}

        if self.wechat_data:
            wc_signals = self.wechat_data.get("signals", {})
            positive_markers = wc_signals.get("positive_emotion_markers", [])
            negative_markers = wc_signals.get("negative_emotion_markers", [])
            emotion_data["wechat_emotion"] = {
                "positive_expressions": positive_markers,
                "negative_expressions": negative_markers,
                "source": "wechat"
            }

        if self.social_data:
            social_signals = self.social_data.get("signals", {})
            tone = social_signals.get("emotional_tone", "")
            venting = social_signals.get("venting_ratio", 0)
            if tone:
                emotion_data["public_emotional_tone"] = {
                    "value": tone,
                    "venting_ratio": venting,
                    "source": "social_media"
                }

        if self.diary_data:
            diary_signals = self.diary_data.get("signals", {})
            self_eval = diary_signals.get("self_evaluation_tone", "")
            if self_eval:
                emotion_data["private_self_talk"] = {
                    "value": self_eval,
                    "source": "diary"
                }
                # 检查公私差距
                if self.social_data:
                    public_tone = self.social_data.get("signals", {}).get("emotional_tone", "")
                    if "积极" in public_tone and "苛责" in self_eval:
                        cv.contradictions.append({
                            "trait": "情绪表达矛盾",
                            "side_a": {
                                "evidence": f"社交媒体呈现积极情绪（{public_tone}）",
                                "source": "social_media",
                            },
                            "side_b": {
                                "evidence": f"私下日记中对自己有较多苛责（{self_eval}）",
                                "source": "diary",
                            },
                            "confidence": "medium",
                        })

        signals["emotional_patterns"] = emotion_data

    def _analyze_self_perception(self, cv: CrossValidationResult, signals: dict):
        """整合自我认知数据"""
        self_data = {}

        # 对话中的自我描述
        conv_self = self.conversation_data.get("self_description", {})
        if conv_self:
            self_data["stated_self"] = conv_self

        if self.diary_data:
            diary_signals = self.diary_data.get("signals", {})
            self_data["diary_self_perception"] = {
                "temporal_orientation": diary_signals.get("future_orientation", ""),
                "attribution": diary_signals.get("attribution_style", ""),
                "narrative_style": diary_signals.get("narrative_style", ""),
                "source": "diary"
            }

            # 日记的自我评价与对话自述的差距
            conv_strengths = self.conversation_data.get("stated_strengths", [])
            diary_themes = diary_signals.get("recurring_themes", [])
            if conv_strengths and diary_themes:
                gaps = [t for t in diary_themes if not any(s in t for s in conv_strengths)]
                if gaps:
                    cv.new_findings.append(TraitEvidence(
                        trait="自我认知盲区",
                        evidence=f"日记中频繁出现但对话中未提及的关切：{', '.join(gaps[:3])}",
                        source="diary",
                        confidence="medium",
                        cross_sources=["conversation"],
                    ))

        signals["self_perception"] = self_data

    def _list_sources(self) -> list[str]:
        sources = ["conversation"]
        if self.wechat_data:
            sources.append("wechat_chat")
        if self.social_data:
            sources.append("social_media")
        if self.diary_data:
            sources.append("diary_notes")
        return sources

    def _calculate_confidence(self) -> str:
        source_count = len(self._list_sources())
        if source_count >= 3:
            return "高（多源交叉验证）"
        elif source_count == 2:
            return "中（有部分素材补充）"
        else:
            return "低（仅基于对话采集，建议导入更多素材）"

    def _generate_ai_prompt(self, cv: CrossValidationResult, signals: dict) -> str:
        """生成给 AI 的分析报告摘要，用于生成 persona.md"""
        parts = []
        parts.append("=== 综合分析报告（供生成人格底座使用）===\n")

        parts.append("【高置信度特征】")
        if cv.high_confidence:
            for item in cv.high_confidence:
                if isinstance(item, TraitEvidence):
                    parts.append(f"  - {item.trait}（{item.confidence}置信度）")
                    parts.append(f"    evidence: {item.evidence}")
                    parts.append(f"    source: {item.source}" + (f" + {', '.join(item.cross_sources)}" if item.cross_sources else ""))
                else:
                    parts.append(f"  - {item}")
        else:
            parts.append("  （无多源验证的高置信特征，建议导入更多素材）")

        parts.append("\n【数据矛盾点（需用户确认）】")
        if cv.contradictions:
            for item in cv.contradictions:
                if isinstance(item, dict) and "side_a" in item:
                    parts.append(f"  ⚠️ {item.get('trait', '矛盾')}")
                    parts.append(f"     A面：{item['side_a']['evidence']}（来源：{item['side_a']['source']}）")
                    parts.append(f"     B面：{item['side_b']['evidence']}（来源：{item['side_b']['source']}）")
                else:
                    parts.append(f"  ⚠️ {item}")
        else:
            parts.append("  （未发现显著矛盾）")

        parts.append("\n【新发现（对话未提及，但从素材中发现）】")
        if cv.new_findings:
            for item in cv.new_findings:
                if isinstance(item, TraitEvidence):
                    parts.append(f"  🔍 {item.trait}：{item.evidence}（来源：{item.source}，置信度：{item.confidence}）")
                else:
                    parts.append(f"  🔍 {item}")

        parts.append(f"\n【分析置信度】{self._calculate_confidence()}")
        parts.append(f"【数据来源】{', '.join(self._list_sources())}")

        return "\n".join(parts)


def analyze_all(
    conversation_data: dict,
    parsed_files: list[str] = None
) -> dict:
    """对外接口：传入对话数据和已解析的素材文件路径"""
    analyzer = JournalAnalyzer()
    analyzer.load_conversation(conversation_data)
    if parsed_files:
        analyzer.load_from_files(parsed_files)
    return analyzer.analyze()


if __name__ == "__main__":
    import sys
    # 测试用：传入示例数据
    sample_conv = {
        "core_values": ["安全感", "成长", "自由"],
        "decision_params": {"risk_appetite": 4, "time_horizon": 6},
        "self_description": {"strengths": ["认真", "负责"], "weaknesses": ["容易焦虑"]},
    }
    result = analyze_all(sample_conv, sys.argv[1:])
    print(json.dumps(result, ensure_ascii=False, indent=2))
