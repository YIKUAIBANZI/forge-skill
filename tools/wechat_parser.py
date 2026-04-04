"""
微信聊天记录解析器 (WeChat Parser)

支持格式：
- 微信导出的 txt 格式（iOS/安卓）
- 第三方工具导出的 HTML 格式

从聊天记录中提取人格相关特征，不存储聊天内容原文。
"""

import re
import json
from pathlib import Path
from datetime import datetime
from collections import Counter, defaultdict
from dataclasses import dataclass, field, asdict
from typing import Optional


@dataclass
class Message:
    timestamp: str
    sender: str  # "user" or "other"
    content: str
    msg_type: str = "text"  # text / emoji / image / file / voice


@dataclass
class PersonalitySignal:
    """从聊天记录中提取的人格信号"""
    # 表达风格
    avg_message_length: float = 0.0        # 平均消息长度
    long_message_ratio: float = 0.0        # 长消息（>50字）占比
    emoji_usage_rate: float = 0.0          # 表情使用频率（条/百条）
    punctuation_style: dict = field(default_factory=dict)  # 标点使用风格
    common_phrases: list = field(default_factory=list)     # 高频短语
    sentence_starters: list = field(default_factory=list)  # 常用开头

    # 沟通节奏
    initiation_ratio: float = 0.0   # 主动发起对话的比例
    reply_speed: str = ""            # 快速/中等/偏慢（基于时间戳统计）
    active_hours: list = field(default_factory=list)  # 活跃时间段

    # 情绪模式
    positive_emotion_markers: list = field(default_factory=list)  # 正向情绪词
    negative_emotion_markers: list = field(default_factory=list)  # 负向情绪词
    emotional_volatility: float = 0.0  # 情绪波动指数

    # 人际互动
    conflict_patterns: list = field(default_factory=list)  # 冲突处理模式
    care_expressions: list = field(default_factory=list)   # 关心表达方式
    humor_style: str = ""            # 幽默风格


class WeChatParser:
    # 常见情绪词典
    POSITIVE_MARKERS = ["哈哈", "哈哈哈", "😄", "😊", "❤️", "太棒了", "开心", "好的", "好呀", "不错", "厉害", "赞"]
    NEGATIVE_MARKERS = ["难过", "烦", "累", "不想", "算了", "无语", "郁闷", "崩溃", "好难", "好累", "头疼"]
    CONFLICT_MARKERS = ["但是", "不对", "你怎么", "我说了", "我不是说", "你懂不懂", "你这个", "算了"]
    HUMOR_MARKERS = ["哈哈哈", "哈哈哈哈", "笑死", "绷不住", "笑了", "😂", "🤣", "doge", "狗头"]

    def __init__(self, file_path: str, user_name: str = ""):
        """
        file_path: 聊天记录文件路径
        user_name: 用户的微信名称（用于区分自己发的消息）
        """
        self.file_path = Path(file_path)
        self.user_name = user_name
        self.messages: list[Message] = []
        self.signals = PersonalitySignal()

    def parse(self) -> dict:
        """主入口，返回分析结果"""
        suffix = self.file_path.suffix.lower()
        if suffix == ".txt":
            self._parse_txt()
        elif suffix in (".html", ".htm"):
            self._parse_html()
        else:
            raise ValueError(f"不支持的格式：{suffix}，请提供 .txt 或 .html 文件")

        self._analyze()
        return self._format_output()

    def _parse_txt(self):
        """解析微信导出的 txt 格式"""
        content = self.file_path.read_text(encoding="utf-8", errors="ignore")
        # 微信 txt 格式：日期行 + "发送者名称(时间)\n内容" 格式
        # 尝试多种常见格式
        patterns = [
            # 格式1: 2024-01-01 12:00:00 发送者\n内容
            r'(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})\s+(.+?)\n([\s\S]+?)(?=\d{4}-\d{2}-\d{2}|\Z)',
            # 格式2: 发送者(时间):\n内容
            r'(.+?)\((\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})\):\n([\s\S]+?)(?=.+?\(|\Z)',
        ]

        for pattern in patterns:
            matches = re.findall(pattern, content)
            if matches:
                for match in matches:
                    self._add_message_from_match(match)
                break

        # 如果上述格式都不匹配，做简单行解析
        if not self.messages:
            self._parse_txt_simple(content)

    def _parse_txt_simple(self, content: str):
        """简单行解析作为兜底"""
        lines = content.split('\n')
        current_sender = ""
        current_content = []
        current_time = ""

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # 尝试识别时间戳行
            time_match = re.match(r'(\d{4}[-/]\d{2}[-/]\d{2}[\s\d:]+)', line)
            if time_match:
                if current_sender and current_content:
                    self._add_message(current_time, current_sender, '\n'.join(current_content))
                current_time = time_match.group(1)
                current_sender = line[time_match.end():].strip()
                current_content = []
            else:
                current_content.append(line)

        if current_sender and current_content:
            self._add_message(current_time, current_sender, '\n'.join(current_content))

    def _parse_html(self):
        """解析 HTML 格式聊天记录（基础实现，处理常见导出格式）"""
        content = self.file_path.read_text(encoding="utf-8", errors="ignore")
        # 移除 HTML 标签，提取文本
        text = re.sub(r'<[^>]+>', ' ', content)
        text = re.sub(r'&nbsp;', ' ', text)
        text = re.sub(r'&lt;', '<', text)
        text = re.sub(r'&gt;', '>', text)
        text = re.sub(r'\s+', '\n', text)
        # 作为 txt 处理
        self._parse_txt_simple(text)

    def _add_message_from_match(self, match: tuple):
        """从正则匹配结果创建消息"""
        if len(match) == 3:
            timestamp, sender, content = match
            self._add_message(timestamp.strip(), sender.strip(), content.strip())

    def _add_message(self, timestamp: str, sender: str, content: str):
        """添加消息"""
        if not content.strip():
            return
        is_user = (self.user_name and sender == self.user_name) or \
                  (not self.user_name and len(self.messages) % 2 == 0)  # 无法确认时交替
        msg_type = self._detect_msg_type(content)
        self.messages.append(Message(
            timestamp=timestamp,
            sender="user" if is_user else "other",
            content=content.strip(),
            msg_type=msg_type
        ))

    def _detect_msg_type(self, content: str) -> str:
        """检测消息类型"""
        if "[图片]" in content or "[照片]" in content:
            return "image"
        if "[语音]" in content or "[视频]" in content:
            return "voice"
        if "[文件]" in content:
            return "file"
        return "text"

    def _analyze(self):
        """分析消息，提取人格信号"""
        user_msgs = [m for m in self.messages if m.sender == "user" and m.msg_type == "text"]
        if not user_msgs:
            return

        self._analyze_expression_style(user_msgs)
        self._analyze_rhythm()
        self._analyze_emotion(user_msgs)
        self._analyze_interaction()

    def _analyze_expression_style(self, user_msgs: list[Message]):
        """分析表达风格"""
        lengths = [len(m.content) for m in user_msgs]
        self.signals.avg_message_length = sum(lengths) / len(lengths)
        self.signals.long_message_ratio = sum(1 for l in lengths if l > 50) / len(lengths)

        # 统计高频词
        all_text = " ".join(m.content for m in user_msgs)
        # 简单的词频统计（不使用外部NLP库）
        words = re.findall(r'[\u4e00-\u9fff]{2,4}', all_text)
        word_freq = Counter(words)
        # 过滤常见功能词
        stopwords = {"就是", "然后", "所以", "但是", "因为", "这个", "那个", "什么", "一个", "可以"}
        self.signals.common_phrases = [
            w for w, _ in word_freq.most_common(20)
            if w not in stopwords
        ][:10]

        # 标点统计
        punct_counts = {
            "！(感叹)": all_text.count('！') + all_text.count('!'),
            "？(疑问)": all_text.count('？') + all_text.count('?'),
            "…(省略)": all_text.count('…'),
            "哈哈类": sum(all_text.count(c) for c in ["哈哈", "haha", "哈哈哈"]),
        }
        self.signals.punctuation_style = punct_counts

    def _analyze_rhythm(self):
        """分析沟通节奏"""
        if not self.messages:
            return

        # 计算主动发起比例
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

        # 提取活跃时间段
        hours = []
        for msg in self.messages:
            if msg.sender == "user":
                hour_match = re.search(r'(\d{2}):\d{2}', msg.timestamp)
                if hour_match:
                    hours.append(int(hour_match.group(1)))

        if hours:
            hour_counts = Counter(hours)
            top_hours = [h for h, _ in hour_counts.most_common(5)]
            self.signals.active_hours = sorted(top_hours)

    def _analyze_emotion(self, user_msgs: list[Message]):
        """分析情绪模式"""
        all_text = " ".join(m.content for m in user_msgs)

        self.signals.positive_emotion_markers = [
            m for m in self.POSITIVE_MARKERS if m in all_text
        ]
        self.signals.negative_emotion_markers = [
            m for m in self.NEGATIVE_MARKERS if m in all_text
        ]

        # 幽默风格
        humor_count = sum(all_text.count(m) for m in self.HUMOR_MARKERS)
        if humor_count > 10:
            self.signals.humor_style = "幽默感强，常用调侃方式表达"
        elif humor_count > 3:
            self.signals.humor_style = "偶尔使用幽默，不是主要表达方式"
        else:
            self.signals.humor_style = "很少使用幽默"

    def _analyze_interaction(self):
        """分析人际互动模式"""
        user_msgs = [m for m in self.messages if m.sender == "user" and m.msg_type == "text"]
        all_text = " ".join(m.content for m in user_msgs)

        self.signals.conflict_patterns = [
            m for m in self.CONFLICT_MARKERS if m in all_text
        ]
        # 关心表达
        care_markers = ["注意身体", "吃了吗", "睡了吗", "辛苦了", "加油", "没事的", "你要"]
        self.signals.care_expressions = [m for m in care_markers if m in all_text]

    def _format_output(self) -> dict:
        """格式化输出，供 journal_analyzer 使用"""
        return {
            "source": "wechat",
            "total_messages": len(self.messages),
            "user_messages": len([m for m in self.messages if m.sender == "user"]),
            "time_range": self._get_time_range(),
            "signals": asdict(self.signals),
            "raw_sample": self._get_sample_messages(),  # 少量样本供 AI 分析语言风格
        }

    def _get_time_range(self) -> dict:
        if not self.messages:
            return {}
        return {
            "start": self.messages[0].timestamp,
            "end": self.messages[-1].timestamp,
        }

    def _get_sample_messages(self) -> list[str]:
        """抽取代表性样本（较长的消息）"""
        user_msgs = [m.content for m in self.messages if m.sender == "user" and len(m.content) > 20]
        # 均匀抽样 20 条
        step = max(1, len(user_msgs) // 20)
        return user_msgs[::step][:20]


def parse_wechat(file_path: str, user_name: str = "") -> dict:
    """对外暴露的简洁接口"""
    parser = WeChatParser(file_path, user_name)
    return parser.parse()


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("用法: python wechat_parser.py <聊天记录文件路径> [用户名]")
        sys.exit(1)

    file_path = sys.argv[1]
    user_name = sys.argv[2] if len(sys.argv) > 2 else ""
    result = parse_wechat(file_path, user_name)
    print(json.dumps(result, ensure_ascii=False, indent=2))
