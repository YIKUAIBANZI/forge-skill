"""
微信聊天记录解析器 (WeChat Parser)

支持格式：
- 微信导出的多种 txt 格式（iOS/安卓/不同版本）
- 第三方工具导出的 HTML 格式

从聊天记录中提取人格相关特征，不存储聊天内容原文。

增强特性（P2-1）：
- 格式自动检测：读取前 20 行判断格式类型
- 启发式分段：先按时间戳定位边界，再识别发言人
- 多时间戳格式支持（6 种常见微信导出格式）
- LLM 回退：正则全部失败时，生成结构化解析 prompt 交给 Claude 处理
"""

import re
import json
from pathlib import Path
from datetime import datetime
from collections import Counter, defaultdict
from dataclasses import dataclass, field, asdict
from typing import Optional


# ---------------------------------------------------------------------------
# 数据结构
# ---------------------------------------------------------------------------

@dataclass
class Message:
    timestamp: str
    sender: str   # "user" or "other"
    content: str
    msg_type: str = "text"  # text / emoji / image / file / voice


@dataclass
class PersonalitySignal:
    """从聊天记录中提取的人格信号"""
    avg_message_length: float = 0.0
    long_message_ratio: float = 0.0
    emoji_usage_rate: float = 0.0
    punctuation_style: dict = field(default_factory=dict)
    common_phrases: list = field(default_factory=list)
    sentence_starters: list = field(default_factory=list)

    initiation_ratio: float = 0.0
    reply_speed: str = ""
    active_hours: list = field(default_factory=list)

    positive_emotion_markers: list = field(default_factory=list)
    negative_emotion_markers: list = field(default_factory=list)
    emotional_volatility: float = 0.0

    conflict_patterns: list = field(default_factory=list)
    care_expressions: list = field(default_factory=list)
    humor_style: str = ""


# ---------------------------------------------------------------------------
# 格式检测
# ---------------------------------------------------------------------------

# 多种时间戳模式，按优先级排列
TIMESTAMP_PATTERNS = [
    # 格式1: 2024-01-01 12:00:00（最常见）
    (r'\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}', "fmt1_dash_full"),
    # 格式2: 2024/01/01 12:00:00
    (r'\d{4}/\d{2}/\d{2}\s+\d{2}:\d{2}:\d{2}', "fmt2_slash_full"),
    # 格式3: 01/01/2024 12:00（月/日/年）
    (r'\d{2}/\d{2}/\d{4}\s+\d{2}:\d{2}', "fmt3_us_date"),
    # 格式4: 2024年01月01日 12:00（中文日期）
    (r'\d{4}年\d{2}月\d{2}日\s+\d{2}:\d{2}', "fmt4_chinese"),
    # 格式5: 2024-01-01（仅日期，有些导出是分开的）
    (r'\d{4}-\d{2}-\d{2}', "fmt5_date_only"),
    # 格式6: 12:00（仅时间，部分格式时间戳独占一行）
    (r'^\s*\d{1,2}:\d{2}(:\d{2})?\s*$', "fmt6_time_only"),
]

def detect_format(lines: list[str]) -> dict:
    """
    读取前 20 行，判断文件格式类型。

    返回：
    {
      "type": "txt_standard" | "txt_compact" | "html" | "unknown",
      "timestamp_pattern": (regex_str, fmt_name),
      "sample_lines": [...],
    }
    """
    sample = lines[:20]
    sample_text = "\n".join(sample)

    # HTML 检测
    if "<html" in sample_text.lower() or "<div" in sample_text.lower():
        return {"type": "html", "timestamp_pattern": None, "sample_lines": sample}

    # 按 TIMESTAMP_PATTERNS 检测哪种时间戳格式出现频率最高
    pattern_hits = {}
    for pattern, fmt_name in TIMESTAMP_PATTERNS:
        count = sum(1 for line in lines[:50] if re.search(pattern, line))
        if count > 0:
            pattern_hits[fmt_name] = (count, pattern, fmt_name)

    if not pattern_hits:
        return {"type": "unknown", "timestamp_pattern": None, "sample_lines": sample}

    # 选命中最多的格式
    best = max(pattern_hits.values(), key=lambda x: x[0])
    fmt_type = "txt_compact" if "time_only" in best[2] else "txt_standard"

    return {
        "type": fmt_type,
        "timestamp_pattern": (best[1], best[2]),
        "sample_lines": sample,
    }


# ---------------------------------------------------------------------------
# 核心解析器
# ---------------------------------------------------------------------------

class WeChatParser:
    POSITIVE_MARKERS = ["哈哈", "哈哈哈", "😄", "😊", "❤️", "太棒了", "开心", "好的", "好呀", "不错", "厉害", "赞"]
    NEGATIVE_MARKERS = ["难过", "烦", "累", "不想", "算了", "无语", "郁闷", "崩溃", "好难", "好累", "头疼"]
    CONFLICT_MARKERS = ["但是", "不对", "你怎么", "我说了", "我不是说", "你懂不懂", "你这个", "算了"]
    HUMOR_MARKERS = ["哈哈哈", "哈哈哈哈", "笑死", "绷不住", "笑了", "😂", "🤣", "doge", "狗头"]

    def __init__(self, file_path: str, user_name: str = ""):
        self.file_path = Path(file_path)
        self.user_name = user_name
        self.messages: list[Message] = []
        self.signals = PersonalitySignal()
        self._parse_succeeded = False

    def parse(self) -> dict:
        """主入口"""
        suffix = self.file_path.suffix.lower()
        raw = self.file_path.read_text(encoding="utf-8", errors="ignore")
        lines = raw.splitlines()

        if suffix in (".html", ".htm"):
            self._parse_html(raw)
        else:
            fmt_info = detect_format(lines)
            if fmt_info["type"] == "html":
                self._parse_html(raw)
            elif fmt_info["type"] in ("txt_standard", "txt_compact") and fmt_info["timestamp_pattern"]:
                self._parse_with_detected_format(lines, fmt_info["timestamp_pattern"][0])
            else:
                # 启发式兜底
                self._parse_heuristic(lines)

        if not self.messages:
            # 所有正则失败，生成 LLM 回退建议
            return self._llm_fallback_result(raw)

        self._parse_succeeded = True
        self._analyze()
        return self._format_output()

    # ------------------------------------------------------------------
    # 格式化解析（已知时间戳 pattern）
    # ------------------------------------------------------------------

    def _parse_with_detected_format(self, lines: list[str], ts_pattern: str):
        """
        启发式分段：
        1. 扫描所有行，找到时间戳行的位置
        2. 时间戳行 + 下一行 = 发言人信息
        3. 两个时间戳之间的行 = 消息内容
        """
        segments = []  # (timestamp, sender_raw, content_lines)
        current_ts = ""
        current_sender = ""
        current_content: list[str] = []

        i = 0
        while i < len(lines):
            line = lines[i]
            ts_match = re.search(ts_pattern, line)

            if ts_match:
                # 保存上一条消息
                if current_sender and current_content:
                    segments.append((current_ts, current_sender, "\n".join(current_content).strip()))

                current_ts = ts_match.group(0)
                # 发言人可能在同一行（时间戳后面），也可能在下一行
                after_ts = line[ts_match.end():].strip()
                if after_ts:
                    current_sender = after_ts
                elif i + 1 < len(lines):
                    i += 1
                    current_sender = lines[i].strip()
                current_content = []
            else:
                if current_sender:
                    current_content.append(line)
            i += 1

        if current_sender and current_content:
            segments.append((current_ts, current_sender, "\n".join(current_content).strip()))

        for ts, sender_raw, content in segments:
            if content:
                self._add_message(ts, sender_raw, content)

    # ------------------------------------------------------------------
    # 启发式兜底（格式未知时）
    # ------------------------------------------------------------------

    def _parse_heuristic(self, lines: list[str]):
        """
        当格式无法确定时，尝试所有已知 timestamp 模式逐行扫描。
        取命中最多的模式，然后调用 _parse_with_detected_format。
        """
        best_pattern = None
        best_count = 0

        for pattern, _ in TIMESTAMP_PATTERNS:
            count = sum(1 for l in lines if re.search(pattern, l))
            if count > best_count:
                best_count = count
                best_pattern = pattern

        if best_pattern and best_count >= 3:
            self._parse_with_detected_format(lines, best_pattern)
        else:
            # 最后的兜底：逐行识别，发现时间戳+冒号模式就切
            self._parse_line_by_line(lines)

    def _parse_line_by_line(self, lines: list[str]):
        """最后兜底：按"含时间且后面有冒号/名字"的行切分"""
        general_ts = re.compile(r'\d{1,4}[-/年]\d{1,2}[-/月]\d{1,2}')
        time_only = re.compile(r'\b\d{1,2}:\d{2}\b')

        current_sender = ""
        current_ts = ""
        current_content: list[str] = []

        for line in lines:
            stripped = line.strip()
            if not stripped:
                continue
            is_ts_line = bool(general_ts.search(stripped)) or bool(time_only.match(stripped))
            if is_ts_line and len(stripped) < 80:
                if current_sender and current_content:
                    self._add_message(current_ts, current_sender, "\n".join(current_content).strip())
                current_ts = stripped
                current_sender = stripped  # 先用整行当发言人
                current_content = []
            else:
                current_content.append(stripped)

        if current_sender and current_content:
            self._add_message(current_ts, current_sender, "\n".join(current_content).strip())

    # ------------------------------------------------------------------
    # HTML 解析
    # ------------------------------------------------------------------

    def _parse_html(self, content: str):
        """解析 HTML 格式（支持常见导出工具的结构）"""
        # 尝试提取结构化 HTML（div.message 类结构）
        msg_pattern = re.compile(
            r'<[^>]*(?:class|id)[^>]*(?:msg|message|bubble|chat)[^>]*>.*?</[^>]+>',
            re.IGNORECASE | re.DOTALL
        )
        matches = msg_pattern.findall(content)
        if matches:
            for block in matches:
                text = re.sub(r'<[^>]+>', ' ', block)
                text = re.sub(r'&nbsp;', ' ', text)
                text = re.sub(r'\s+', ' ', text).strip()
                if text:
                    self._add_message("", "unknown", text)
            if self.messages:
                return

        # 降级：剥离所有标签后当 txt 处理
        text = re.sub(r'<[^>]+>', '\n', content)
        text = re.sub(r'&nbsp;', ' ', text)
        text = re.sub(r'&lt;', '<', text)
        text = re.sub(r'&gt;', '>', text)
        self._parse_heuristic(text.splitlines())

    # ------------------------------------------------------------------
    # LLM 回退
    # ------------------------------------------------------------------

    def _llm_fallback_result(self, raw_content: str) -> dict:
        """
        所有解析方式全部失败时，生成一个 LLM 解析 prompt，
        让用户把这个 prompt 交给 Claude 来做结构化提取。
        """
        sample = "\n".join(raw_content.splitlines()[:40])
        llm_prompt = f"""以下是一段微信聊天记录，格式无法被自动识别。请帮我把它解析成结构化格式。

---聊天记录开始---
{sample}
---聊天记录结束（仅展示前 40 行）---

请输出 JSON 数组，每条消息格式：
{{
  "timestamp": "时间字符串",
  "sender": "发言人名称",
  "content": "消息内容"
}}

注意：
- 只输出 JSON，不要其他说明
- 如果无法确定发言人，用 "unknown"
- 语音/图片/视频消息保留，content 填 "[语音]"/"[图片]"/"[视频]"
"""

        return {
            "source": "wechat",
            "parse_status": "failed",
            "total_messages": 0,
            "user_messages": 0,
            "signals": asdict(PersonalitySignal()),
            "llm_fallback": {
                "message": (
                    "自动解析失败：未能识别聊天记录格式。\n"
                    "请把下方 prompt 复制给 Claude，让它帮你提取结构化数据，"
                    "然后把结果保存为 JSON 文件，再传给解析器。"
                ),
                "prompt": llm_prompt,
            }
        }

    # ------------------------------------------------------------------
    # 消息处理
    # ------------------------------------------------------------------

    def _add_message(self, timestamp: str, sender_raw: str, content: str):
        if not content.strip():
            return
        is_user = (
            (self.user_name and self.user_name in sender_raw) or
            (not self.user_name and len(self.messages) % 2 == 0)
        )
        msg_type = self._detect_msg_type(content)
        self.messages.append(Message(
            timestamp=timestamp,
            sender="user" if is_user else "other",
            content=content.strip(),
            msg_type=msg_type,
        ))

    def _detect_msg_type(self, content: str) -> str:
        lower = content.lower()
        if any(k in lower for k in ["[图片]", "[照片]", "[photo]"]):
            return "image"
        if any(k in lower for k in ["[语音]", "[voice]", "[视频]", "[video]"]):
            return "voice"
        if "[文件]" in lower or "[file]" in lower:
            return "file"
        return "text"

    # ------------------------------------------------------------------
    # 分析
    # ------------------------------------------------------------------

    def _analyze(self):
        user_msgs = [m for m in self.messages if m.sender == "user" and m.msg_type == "text"]
        if not user_msgs:
            return
        self._analyze_expression_style(user_msgs)
        self._analyze_rhythm()
        self._analyze_emotion(user_msgs)
        self._analyze_interaction()

    def _analyze_expression_style(self, user_msgs: list[Message]):
        lengths = [len(m.content) for m in user_msgs]
        self.signals.avg_message_length = sum(lengths) / len(lengths)
        self.signals.long_message_ratio = sum(1 for l in lengths if l > 50) / len(lengths)

        all_text = " ".join(m.content for m in user_msgs)
        words = re.findall(r'[\u4e00-\u9fff]{2,4}', all_text)
        word_freq = Counter(words)
        stopwords = {"就是", "然后", "所以", "但是", "因为", "这个", "那个", "什么", "一个", "可以", "觉得", "感觉"}
        self.signals.common_phrases = [
            w for w, _ in word_freq.most_common(20) if w not in stopwords
        ][:10]

        self.signals.punctuation_style = {
            "！(感叹)": all_text.count('！') + all_text.count('!'),
            "？(疑问)": all_text.count('？') + all_text.count('?'),
            "…(省略)": all_text.count('…'),
            "哈哈类": sum(all_text.count(c) for c in ["哈哈", "haha", "哈哈哈"]),
            "句号": all_text.count('。') + all_text.count('.'),
        }

        # 常用开头词
        starters = []
        for m in user_msgs[:200]:
            first_word = re.match(r'[\u4e00-\u9fff]{1,3}', m.content)
            if first_word:
                starters.append(first_word.group(0))
        starter_freq = Counter(starters)
        self.signals.sentence_starters = [w for w, _ in starter_freq.most_common(5)]

    def _analyze_rhythm(self):
        if not self.messages:
            return

        initiations = 0
        total_conversations = 0
        prev_sender = None
        for msg in self.messages:
            if prev_sender != "user" and msg.sender == "user":
                initiations += 1
                total_conversations += 1
            elif prev_sender != "other" and msg.sender == "other":
                total_conversations += 1
            prev_sender = msg.sender

        if total_conversations > 0:
            self.signals.initiation_ratio = initiations / total_conversations

        hours = []
        for msg in self.messages:
            if msg.sender == "user":
                hour_match = re.search(r'(\d{1,2}):\d{2}', msg.timestamp)
                if hour_match:
                    h = int(hour_match.group(1))
                    if 0 <= h <= 23:
                        hours.append(h)

        if hours:
            hour_counts = Counter(hours)
            self.signals.active_hours = sorted([h for h, _ in hour_counts.most_common(5)])

    def _analyze_emotion(self, user_msgs: list[Message]):
        all_text = " ".join(m.content for m in user_msgs)
        self.signals.positive_emotion_markers = [m for m in self.POSITIVE_MARKERS if m in all_text]
        self.signals.negative_emotion_markers = [m for m in self.NEGATIVE_MARKERS if m in all_text]

        humor_count = sum(all_text.count(m) for m in self.HUMOR_MARKERS)
        if humor_count > 10:
            self.signals.humor_style = "幽默感强，常用调侃方式表达"
        elif humor_count > 3:
            self.signals.humor_style = "偶尔使用幽默，不是主要表达方式"
        else:
            self.signals.humor_style = "很少使用幽默"

    def _analyze_interaction(self):
        user_msgs = [m for m in self.messages if m.sender == "user" and m.msg_type == "text"]
        all_text = " ".join(m.content for m in user_msgs)
        self.signals.conflict_patterns = [m for m in self.CONFLICT_MARKERS if m in all_text]
        care_markers = ["注意身体", "吃了吗", "睡了吗", "辛苦了", "加油", "没事的", "你要"]
        self.signals.care_expressions = [m for m in care_markers if m in all_text]

    # ------------------------------------------------------------------
    # 输出
    # ------------------------------------------------------------------

    def _format_output(self) -> dict:
        return {
            "source": "wechat",
            "parse_status": "success",
            "total_messages": len(self.messages),
            "user_messages": len([m for m in self.messages if m.sender == "user"]),
            "time_range": self._get_time_range(),
            "signals": asdict(self.signals),
            "raw_sample": self._get_sample_messages(),
        }

    def _get_time_range(self) -> dict:
        if not self.messages:
            return {}
        return {"start": self.messages[0].timestamp, "end": self.messages[-1].timestamp}

    def _get_sample_messages(self) -> list[str]:
        """抽取代表性样本（较长的用户消息，均匀采样 20 条）"""
        user_msgs = [m.content for m in self.messages if m.sender == "user" and len(m.content) > 15]
        step = max(1, len(user_msgs) // 20)
        return user_msgs[::step][:20]


# ---------------------------------------------------------------------------
# 公开接口
# ---------------------------------------------------------------------------

def parse_wechat(file_path: str, user_name: str = "") -> dict:
    """对外暴露的简洁接口"""
    return WeChatParser(file_path, user_name).parse()


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("用法: python wechat_parser.py <聊天记录文件路径> [用户名]")
        sys.exit(1)

    result = parse_wechat(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "")

    if result.get("parse_status") == "failed":
        print(result["llm_fallback"]["message"])
        print("\n--- LLM 解析 Prompt ---")
        print(result["llm_fallback"]["prompt"])
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))
