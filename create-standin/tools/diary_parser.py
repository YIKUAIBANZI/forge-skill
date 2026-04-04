"""
日记/笔记解析器 (Diary Parser)

支持格式：
- 纯文本 txt
- Markdown (md)
- Notion 导出（md / html）
- Day One 导出（txt / JSON）
- 任意格式的个人文字记录

从私人写作中提取最真实的自我认知数据。
"""

import re
import json
from pathlib import Path
from datetime import datetime
from collections import Counter
from dataclasses import dataclass, field, asdict
from typing import Optional


@dataclass
class DiaryEntry:
    date: str
    title: str
    content: str
    word_count: int = 0
    tags: list = field(default_factory=list)


@dataclass
class DiarySignal:
    """从日记/笔记中提取的人格信号"""
    # 写作模式
    total_entries: int = 0
    avg_entry_length: float = 0.0
    writing_frequency: str = ""       # 高频/中频/低频
    active_periods: list = field(default_factory=list)  # 哪些月份/情境下写得更多

    # 思维模式
    narrative_style: str = ""          # 叙事风格：事件驱动/情感驱动/分析驱动
    attribution_style: str = ""        # 归因：内归因/外归因/混合
    self_evaluation_tone: str = ""     # 自我评价：苛责/中性/温和

    # 深层关切
    recurring_themes: list = field(default_factory=list)    # 反复出现的主题
    recurring_worries: list = field(default_factory=list)   # 反复出现的焦虑
    recurring_aspirations: list = field(default_factory=list)  # 反复出现的渴望

    # 自我对话
    self_talk_patterns: list = field(default_factory=list)  # 对自己说话的方式
    future_orientation: str = ""  # 未来导向/当下导向/过去导向

    # 关键事件
    significant_events: list = field(default_factory=list)  # 被反复提及的重要事件
    decision_records: list = field(default_factory=list)    # 记录过的重大决定


class DiaryParser:
    # 思维模式关键词
    EMOTION_WORDS = ["感觉", "觉得", "心情", "情绪", "难受", "开心", "焦虑", "担心", "害怕", "期待"]
    ANALYSIS_WORDS = ["因为", "所以", "原因", "分析", "总结", "反思", "复盘", "推断", "判断"]
    EVENT_WORDS = ["今天", "昨天", "这周", "发生了", "遇到了", "完成了", "失败了"]

    # 归因模式
    INTERNAL_ATTRIBUTION = ["是我的问题", "我不够", "我应该", "我没有", "我太", "我的错", "怪我"]
    EXTERNAL_ATTRIBUTION = ["是因为", "都是", "让我", "导致", "影响了", "没想到"]

    # 自我评价语气
    HARSH_SELF_TALK = ["我怎么这么", "我真的好烂", "为什么我总是", "我太差了", "我不行"]
    GENTLE_SELF_TALK = ["也已经很好了", "没关系", "下次会好的", "尽力了", "慢慢来"]

    # 反复出现的主题词组
    THEME_KEYWORDS = {
        "职业/方向感": ["方向", "未来", "职业", "工作", "目标", "不知道要", "迷茫"],
        "人际关系": ["关系", "朋友", "家人", "边界", "相处", "孤独", "连接"],
        "自我价值感": ["值得", "够好", "认可", "成就", "证明", "我到底", "有什么用"],
        "时间与效率": ["时间", "效率", "拖延", "浪费", "来不及", "又是一天"],
        "金钱/安全感": ["钱", "存款", "稳定", "安全感", "焦虑", "够不够"],
        "身体/健康": ["身体", "睡眠", "状态", "疲惫", "生病", "锻炼"],
        "情感/亲密": ["爱", "被爱", "孤独", "陪伴", "理解", "被理解"],
        "自由/掌控": ["自由", "选择", "掌控", "被迫", "没得选", "想要"],
    }

    def __init__(self, file_path: str):
        self.file_path = Path(file_path)
        self.entries: list[DiaryEntry] = []
        self.signals = DiarySignal()

    def parse(self) -> dict:
        content = self.file_path.read_text(encoding="utf-8", errors="ignore")
        suffix = self.file_path.suffix.lower()

        if suffix == ".json":
            self._parse_json(content)
        elif suffix in (".md", ".markdown"):
            self._parse_markdown(content)
        else:
            self._parse_plain_text(content)

        self._analyze()
        return self._format_output()

    def _parse_markdown(self, content: str):
        """解析 Markdown 格式（Notion/Obsidian/Bear 导出）"""
        # 按 # 标题分割
        sections = re.split(r'\n(?=#{1,3}\s)', content)
        for section in sections:
            if not section.strip():
                continue

            # 提取标题
            title_match = re.match(r'#{1,3}\s+(.+)', section)
            title = title_match.group(1).strip() if title_match else ""

            # 提取日期（从标题或内容中）
            date = self._extract_date(title + " " + section[:200])

            # 提取标签
            tags = re.findall(r'#(\w+)', section)

            # 内容（去掉标题行）
            body = re.sub(r'^#{1,3}\s+.+\n?', '', section).strip()
            # 去掉 Notion 的属性块
            body = re.sub(r'^[\w\s]+::.+\n?', '', body, flags=re.MULTILINE).strip()

            if len(body) > 20:
                self.entries.append(DiaryEntry(
                    date=date,
                    title=title,
                    content=body,
                    word_count=len(body),
                    tags=tags,
                ))

    def _parse_plain_text(self, content: str):
        """解析纯文本日记"""
        # 按日期行或分隔线分割
        blocks = re.split(r'\n{3,}|(?=\d{4}[-/年]\d{1,2}[-/月]\d{1,2})', content)

        for block in blocks:
            block = block.strip()
            if len(block) < 30:
                continue

            date = self._extract_date(block[:100])
            # 提取日期后的内容作为 body
            body = re.sub(r'^\d{4}[-/年]\d{1,2}[-/月]\d{1,2}[日\s]*[\w\s]*\n?', '', block).strip()
            if not body:
                body = block

            if len(body) > 20:
                self.entries.append(DiaryEntry(
                    date=date,
                    title="",
                    content=body,
                    word_count=len(body),
                ))

    def _parse_json(self, content: str):
        """解析 JSON 格式（Day One 等）"""
        try:
            data = json.loads(content)
            entries = data if isinstance(data, list) else data.get("entries", data.get("data", []))
            for item in entries:
                text = item.get("text", item.get("content", item.get("body", "")))
                date = item.get("creationDate", item.get("date", item.get("created_at", "")))
                tags = item.get("tags", [])
                if isinstance(tags, list):
                    tags = [t if isinstance(t, str) else t.get("name", "") for t in tags]

                if text:
                    self.entries.append(DiaryEntry(
                        date=str(date)[:10],
                        title=item.get("title", ""),
                        content=text,
                        word_count=len(text),
                        tags=tags,
                    ))
        except (json.JSONDecodeError, KeyError):
            self._parse_plain_text(content)

    def _extract_date(self, text: str) -> str:
        """从文本中提取日期"""
        patterns = [
            r'(\d{4})[-/年](\d{1,2})[-/月](\d{1,2})',
            r'(\d{4})-(\d{2})-(\d{2})',
        ]
        for p in patterns:
            m = re.search(p, text)
            if m:
                return m.group(0)[:10]
        return ""

    def _analyze(self):
        """执行所有分析"""
        if not self.entries:
            return

        all_text = " ".join(e.content for e in self.entries)
        self.signals.total_entries = len(self.entries)

        lengths = [e.word_count for e in self.entries]
        self.signals.avg_entry_length = sum(lengths) / len(lengths)

        if self.signals.avg_entry_length > 500:
            self.signals.writing_frequency = "深度写作型（文章较长，可能频率不高但内容充实）"
        elif len(self.entries) > 100:
            self.signals.writing_frequency = "高频写作（记录频繁）"
        elif len(self.entries) > 30:
            self.signals.writing_frequency = "中频写作"
        else:
            self.signals.writing_frequency = "低频写作（或数据不完整）"

        self._analyze_narrative_style(all_text)
        self._analyze_attribution(all_text)
        self._analyze_self_talk(all_text)
        self._analyze_themes(all_text)
        self._analyze_temporal_orientation(all_text)
        self._extract_significant_patterns(all_text)

    def _analyze_narrative_style(self, all_text: str):
        emotion_score = sum(all_text.count(w) for w in self.EMOTION_WORDS)
        analysis_score = sum(all_text.count(w) for w in self.ANALYSIS_WORDS)
        event_score = sum(all_text.count(w) for w in self.EVENT_WORDS)

        scores = {"情感驱动": emotion_score, "分析驱动": analysis_score, "事件驱动": event_score}
        dominant = max(scores, key=scores.get)

        if max(scores.values()) > sum(scores.values()) * 0.5:
            self.signals.narrative_style = f"以{dominant}为主"
        else:
            self.signals.narrative_style = "混合型（情感、分析、事件记录并重）"

    def _analyze_attribution(self, all_text: str):
        internal = sum(all_text.count(m) for m in self.INTERNAL_ATTRIBUTION)
        external = sum(all_text.count(m) for m in self.EXTERNAL_ATTRIBUTION)

        if internal > external * 1.5:
            self.signals.attribution_style = "偏内归因（倾向于从自身找原因）"
        elif external > internal * 1.5:
            self.signals.attribution_style = "偏外归因（倾向于从环境找原因）"
        else:
            self.signals.attribution_style = "内外归因均衡"

    def _analyze_self_talk(self, all_text: str):
        harsh = sum(all_text.count(m) for m in self.HARSH_SELF_TALK)
        gentle = sum(all_text.count(m) for m in self.GENTLE_SELF_TALK)

        if harsh > gentle * 1.5:
            self.signals.self_evaluation_tone = "偏自我苛责（对自己要求高，容易自我批评）"
        elif gentle > harsh * 1.5:
            self.signals.self_evaluation_tone = "偏温和自我对话"
        else:
            self.signals.self_evaluation_tone = "自我评价态度较为中性"

    def _analyze_themes(self, all_text: str):
        theme_scores = {}
        for theme, keywords in self.THEME_KEYWORDS.items():
            score = sum(all_text.count(kw) for kw in keywords)
            if score > 1:
                theme_scores[theme] = score

        self.signals.recurring_themes = [
            t for t, _ in sorted(theme_scores.items(), key=lambda x: x[1], reverse=True)[:5]
        ]

    def _analyze_temporal_orientation(self, all_text: str):
        past_words = ["当时", "以前", "从前", "之前", "那时候", "记得", "曾经"]
        future_words = ["以后", "将来", "未来", "打算", "计划", "希望", "想要做", "目标"]
        present_words = ["现在", "今天", "此刻", "当下", "最近", "这段时间"]

        past_score = sum(all_text.count(w) for w in past_words)
        future_score = sum(all_text.count(w) for w in future_words)
        present_score = sum(all_text.count(w) for w in present_words)

        scores = {"过去导向": past_score, "未来导向": future_score, "当下导向": present_score}
        dominant = max(scores, key=scores.get)
        self.signals.future_orientation = dominant

    def _extract_significant_patterns(self, all_text: str):
        """提取决策记录和重大事件信号"""
        decision_markers = ["决定了", "我决定", "最终选择", "选择了", "最后还是", "做了决定"]
        for marker in decision_markers:
            indices = [m.start() for m in re.finditer(re.escape(marker), all_text)]
            for idx in indices[:5]:  # 最多取5个
                snippet = all_text[max(0, idx-20):idx+80].strip()
                if snippet:
                    self.signals.decision_records.append(snippet)

    def _format_output(self) -> dict:
        return {
            "source": "diary",
            "total_entries": len(self.entries),
            "time_range": {
                "start": self.entries[0].date if self.entries else "",
                "end": self.entries[-1].date if self.entries else "",
            },
            "signals": asdict(self.signals),
            "raw_sample": [e.content[:300] for e in self.entries[:10]],  # 前10条摘录
        }


def parse_diary(file_path: str) -> dict:
    parser = DiaryParser(file_path)
    return parser.parse()


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("用法: python diary_parser.py <日记文件路径>")
        sys.exit(1)
    result = parse_diary(sys.argv[1])
    print(json.dumps(result, ensure_ascii=False, indent=2))
