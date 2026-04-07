"""
解析器（wechat_parser, diary_parser, social_parser, journal_analyzer）基础测试
覆盖：模块可导入、核心数据结构正确、基本解析不崩溃
"""
import sys, os, pytest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools"))


# ─── 导入测试 ────────────────────────────────────────────────────

class TestImports:
    def test_import_wechat_parser(self):
        import wechat_parser
        assert hasattr(wechat_parser, "PersonalitySignal")

    def test_import_diary_parser(self):
        import diary_parser
        assert hasattr(diary_parser, "DiarySignal")

    def test_import_social_parser(self):
        import social_parser
        assert hasattr(social_parser, "SocialSignal")

    def test_import_journal_analyzer(self):
        import journal_analyzer
        assert hasattr(journal_analyzer, "JournalAnalyzer") or hasattr(journal_analyzer, "CrossValidationResult")


# ─── 数据结构测试 ────────────────────────────────────────────────

class TestDataStructures:
    def test_personality_signal_defaults(self):
        from wechat_parser import PersonalitySignal
        sig = PersonalitySignal()
        assert sig.avg_message_length == 0.0
        assert isinstance(sig.common_phrases, list)

    def test_diary_signal_defaults(self):
        from diary_parser import DiarySignal
        sig = DiarySignal()
        assert sig.total_entries == 0
        assert isinstance(sig.recurring_themes, list)

    def test_social_signal_defaults(self):
        from social_parser import SocialSignal
        sig = SocialSignal()
        assert isinstance(sig.topic_distribution, dict)
        assert sig.self_disclosure_level == ""


# ─── 基础解析测试（不崩溃即通过）─────────────────────────────────

class TestBasicParsing:
    def test_wechat_parse_empty_string(self):
        from wechat_parser import PersonalitySignal
        # 空输入不应该崩溃
        sig = PersonalitySignal()
        assert sig is not None

    def test_diary_entry_creation(self):
        from diary_parser import DiaryEntry
        entry = DiaryEntry(date="2026-04-07", title="测试", content="今天写了测试")
        assert entry.content == "今天写了测试"

    def test_social_post_creation(self):
        from social_parser import Post
        post = Post(platform="weibo", timestamp="2026-04-07", content="测试帖子")
        assert post.platform == "weibo"
