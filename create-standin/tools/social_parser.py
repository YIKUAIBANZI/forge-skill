"""
社交媒体内容解析器 (Social Parser)

支持来源：
- 微博（导出 JSON 或 txt）
- 小红书（导出文本/截图文字）
- 朋友圈（通过第三方工具导出的 txt/JSON）

从公开社交内容中提取自我呈现方式、关注领域、价值倾向。
"""

import re
import json
from pathlib import Path
from collections import Counter
from dataclasses import dataclass, field, asdict
from typing import Optional


@dataclass
class Post:
    platform: str
    timestamp: str
    content: str
    likes: int = 0
    comments: int = 0
    reposts: int = 0


@dataclass
class SocialSignal:
    """从社交媒体中提取的人格信号"""
    # 内容主题分布
    topic_distribution: dict = field(default_factory=dict)  # 主题→比例
    top_topics: list = field(default_factory=list)           # 前5主题

    # 自我呈现
    self_disclosure_level: str = ""   # 分享深度：浅层/中等/深度
    presentation_style: str = ""       # 展示风格：记录生活/分享观点/情绪表达/知识输出
    public_persona: list = field(default_factory=list)  # 公开形象关键词

    # 表达特征
    avg_post_length: float = 0.0
    uses_hashtags: bool = False
    image_heavy: bool = False  # 是否以图片为主

    # 情感基调
    emotional_tone: str = ""  # 积极/消极/中性/混合
    venting_ratio: float = 0.0  # 发泄性内容占比
    positive_ratio: float = 0.0  # 正向内容占比

    # 价值倾向（从内容推断）
    inferred_values: list = field(default_factory=list)

    # 私人vs公开的差距感知
    public_private_gap: str = ""  # 社交媒体内容与对话采集的差距描述


class SocialParser:
    TOPIC_KEYWORDS = {
        "工作/职场": ["工作", "项目", "开会", "deadline", "加班", "同事", "上班", "职场", "跳槽", "升职"],
        "情感/关系": ["朋友", "男友", "女友", "家人", "爱", "感情", "分手", "结婚", "约会", "思念"],
        "生活/日常": ["吃饭", "睡觉", "今天", "周末", "好累", "好开心", "日常", "打卡", "记录"],
        "旅行/探索": ["旅行", "出发", "打卡", "风景", "美食", "探店", "城市", "景点"],
        "学习/成长": ["学习", "读书", "课程", "思考", "感悟", "复盘", "进步", "成长"],
        "健康/运动": ["健身", "跑步", "运动", "减肥", "饮食", "身体", "打球"],
        "兴趣/爱好": ["音乐", "电影", "游戏", "追剧", "看书", "画画", "摄影", "手作"],
        "社会/观点": ["感觉", "觉得", "其实", "想说", "分享", "观点", "问题", "现象"],
    }

    SELF_DISCLOSURE_DEEP = ["我其实", "说真的", "真实想法", "不太敢说", "很少人知道", "内心深处"]
    SELF_DISCLOSURE_SHALLOW = ["今天", "打卡", "记录一下", "分享", "推荐"]

    POSITIVE_WORDS = ["开心", "快乐", "幸福", "太棒了", "❤️", "😊", "好爱", "感谢", "感动", "惊喜"]
    NEGATIVE_WORDS = ["难过", "崩溃", "好累", "太难了", "委屈", "烦", "想哭", "郁闷", "无语"]

    def __init__(self, file_path: str, platform: str = "auto"):
        self.file_path = Path(file_path)
        self.platform = platform
        self.posts: list[Post] = []
        self.signals = SocialSignal()

    def parse(self) -> dict:
        """主入口"""
        content = self.file_path.read_text(encoding="utf-8", errors="ignore")

        # 自动检测格式
        if self.file_path.suffix == ".json":
            self._parse_json(content)
        else:
            self._parse_text(content)

        self._analyze()
        return self._format_output()

    def _parse_json(self, content: str):
        """解析 JSON 格式"""
        try:
            data = json.loads(content)
            # 尝试多种 JSON 结构
            if isinstance(data, list):
                for item in data:
                    self._extract_post_from_dict(item)
            elif isinstance(data, dict):
                # 可能有 posts/data 等字段
                for key in ["posts", "data", "items", "content"]:
                    if key in data and isinstance(data[key], list):
                        for item in data[key]:
                            self._extract_post_from_dict(item)
                        break
        except json.JSONDecodeError:
            # JSON 解析失败，当 txt 处理
            self._parse_text(content)

    def _extract_post_from_dict(self, item: dict):
        """从字典中提取帖子"""
        content = ""
        for key in ["content", "text", "body", "post", "message", "weibo_cont", "note_content"]:
            if key in item and item[key]:
                content = str(item[key])
                break

        timestamp = ""
        for key in ["created_at", "timestamp", "time", "date", "created_time"]:
            if key in item:
                timestamp = str(item[key])
                break

        if content:
            self.posts.append(Post(
                platform=self.platform,
                timestamp=timestamp,
                content=content,
                likes=int(item.get("likes_count", item.get("like_count", 0))),
                comments=int(item.get("comments_count", item.get("comment_count", 0))),
                reposts=int(item.get("reposts_count", item.get("repost_count", 0))),
            ))

    def _parse_text(self, content: str):
        """解析文本格式"""
        # 按常见分隔符拆分
        blocks = re.split(r'\n{2,}|={3,}|-{3,}', content)
        for block in blocks:
            block = block.strip()
            if len(block) < 10:  # 过短的块跳过
                continue

            # 尝试提取时间戳
            time_match = re.search(r'(\d{4}[-/]\d{2}[-/]\d{2})', block)
            timestamp = time_match.group(1) if time_match else ""

            # 清理时间戳行，保留内容
            clean_content = re.sub(r'\d{4}[-/]\d{2}[-/]\d{2}[\s\d:]*', '', block).strip()
            if clean_content:
                self.posts.append(Post(
                    platform=self.platform or "unknown",
                    timestamp=timestamp,
                    content=clean_content,
                ))

    def _analyze(self):
        """分析所有帖子"""
        if not self.posts:
            return

        all_text = " ".join(p.content for p in self.posts)
        self._analyze_topics(all_text)
        self._analyze_presentation(all_text)
        self._analyze_emotion(all_text)
        self._infer_values(all_text)

    def _analyze_topics(self, all_text: str):
        """分析主题分布"""
        topic_scores = {}
        for topic, keywords in self.TOPIC_KEYWORDS.items():
            score = sum(all_text.count(kw) for kw in keywords)
            if score > 0:
                topic_scores[topic] = score

        total = sum(topic_scores.values()) or 1
        self.signals.topic_distribution = {
            topic: round(score / total, 2)
            for topic, score in topic_scores.items()
        }
        self.signals.top_topics = [
            t for t, _ in sorted(topic_scores.items(), key=lambda x: x[1], reverse=True)[:5]
        ]

    def _analyze_presentation(self, all_text: str):
        """分析自我呈现风格"""
        # 分享深度
        deep_count = sum(all_text.count(m) for m in self.SELF_DISCLOSURE_DEEP)
        shallow_count = sum(all_text.count(m) for m in self.SELF_DISCLOSURE_SHALLOW)

        if deep_count > 5:
            self.signals.self_disclosure_level = "深度分享，倾向于表达内心真实想法"
        elif shallow_count > deep_count * 2:
            self.signals.self_disclosure_level = "浅层记录为主，较少分享内心世界"
        else:
            self.signals.self_disclosure_level = "中等深度，偶尔分享真实感受"

        # 帖子长度
        lengths = [len(p.content) for p in self.posts]
        self.signals.avg_post_length = sum(lengths) / len(lengths)

        # 展示风格推断
        if "觉得" in all_text or "其实" in all_text or "想说" in all_text:
            self.signals.presentation_style = "观点输出型"
        elif self.signals.avg_post_length < 50:
            self.signals.presentation_style = "生活记录型"
        else:
            self.signals.presentation_style = "情绪表达型"

    def _analyze_emotion(self, all_text: str):
        """分析情感基调"""
        positive_count = sum(all_text.count(w) for w in self.POSITIVE_WORDS)
        negative_count = sum(all_text.count(w) for w in self.NEGATIVE_WORDS)
        total = positive_count + negative_count or 1

        self.signals.positive_ratio = positive_count / total
        self.signals.venting_ratio = negative_count / total

        if self.signals.positive_ratio > 0.7:
            self.signals.emotional_tone = "偏积极，公开场合展示正面情绪为主"
        elif self.signals.venting_ratio > 0.4:
            self.signals.emotional_tone = "偏消极，会在社交媒体发泄情绪"
        else:
            self.signals.emotional_tone = "情绪基调较为平衡"

    def _infer_values(self, all_text: str):
        """从内容推断价值倾向"""
        value_keywords = {
            "重视关系": ["朋友", "家人", "爱", "陪伴", "珍惜"],
            "追求成长": ["学习", "进步", "成长", "目标", "计划"],
            "在意自由": ["自由", "随心", "想做就做", "不将就"],
            "注重体验": ["体验", "感受", "当下", "活在", "享受"],
            "追求认可": ["终于", "被夸", "好评", "认可", "获奖"],
            "注重公平": ["公平", "凭什么", "应该", "本来"],
        }

        for value, keywords in value_keywords.items():
            if sum(all_text.count(k) for k in keywords) > 2:
                self.signals.inferred_values.append(value)

    def _format_output(self) -> dict:
        return {
            "source": "social_media",
            "platform": self.platform,
            "total_posts": len(self.posts),
            "time_range": {
                "start": self.posts[0].timestamp if self.posts else "",
                "end": self.posts[-1].timestamp if self.posts else "",
            },
            "signals": asdict(self.signals),
            "raw_sample": [p.content for p in self.posts[:15]],  # 样本供 AI 分析
        }


def parse_social(file_path: str, platform: str = "auto") -> dict:
    parser = SocialParser(file_path, platform)
    return parser.parse()


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("用法: python social_parser.py <文件路径> [platform: weibo/xiaohongshu/moments]")
        sys.exit(1)
    result = parse_social(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else "auto")
    print(json.dumps(result, ensure_ascii=False, indent=2))
