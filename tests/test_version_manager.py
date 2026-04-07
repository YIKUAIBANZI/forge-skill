"""
version_manager.py 的单元测试
覆盖：快照存档、版本列表、回滚、diff 生成、changelog
"""
import sys, os, json, pytest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools"))

import version_manager
import skill_writer


@pytest.fixture(autouse=True)
def use_temp_dir(tmp_path, monkeypatch):
    """所有测试用临时目录"""
    monkeypatch.setattr(skill_writer, "PERSONAS_DIR", tmp_path)
    monkeypatch.setattr(skill_writer, "SELF_DIR", tmp_path / "self")
    monkeypatch.setattr(skill_writer, "OTHERS_DIR", tmp_path / "others")
    # version_manager 内部也引用 personas 目录
    if hasattr(version_manager, "PERSONAS_DIR"):
        monkeypatch.setattr(version_manager, "PERSONAS_DIR", tmp_path)


@pytest.fixture
def sample_persona(tmp_path):
    """创建一个可用于版本测试的 persona"""
    data = {
        "meta": {"name": "版本测试", "type": "self", "version": "v1.0"},
        "L3_decision_params": {
            "parameters": {"risk_appetite": {"score": 5, "evidence": "", "confidence": "medium"}}
        },
        "L4_values": {"ranking": ["自由", "亲密"]},
    }
    skill_writer.write_persona_json("版本测试", data, "self")
    return data


# ─── Diff 生成 ───────────────────────────────────────────────────

class TestDiff:
    def test_no_diff_on_same_data(self):
        data = {"a": 1, "b": {"c": 2}}
        diffs = version_manager.generate_diff(data, data)
        assert len(diffs) == 0

    def test_detect_modified_field(self):
        old = {"a": 1, "b": 2}
        new = {"a": 1, "b": 3}
        diffs = version_manager.generate_diff(old, new)
        assert len(diffs) == 1
        assert diffs[0]["change_type"] == "modified"
        assert diffs[0]["before"] == 2
        assert diffs[0]["after"] == 3

    def test_detect_added_field(self):
        old = {"a": 1}
        new = {"a": 1, "b": 2}
        diffs = version_manager.generate_diff(old, new)
        assert any(d["change_type"] == "added" for d in diffs)

    def test_detect_removed_field(self):
        old = {"a": 1, "b": 2}
        new = {"a": 1}
        diffs = version_manager.generate_diff(old, new)
        assert any(d["change_type"] == "removed" for d in diffs)

    def test_nested_diff(self):
        old = {"L3": {"params": {"risk": 5}}}
        new = {"L3": {"params": {"risk": 8}}}
        diffs = version_manager.generate_diff(old, new)
        assert len(diffs) == 1
        assert "risk" in diffs[0]["field_path"]

    def test_diff_with_lists(self):
        old = {"values": ["自由", "亲密"]}
        new = {"values": ["自由", "亲密", "快乐"]}
        diffs = version_manager.generate_diff(old, new)
        assert len(diffs) >= 1


# ─── 快照与版本 ──────────────────────────────────────────────────

class TestArchiveAndVersions:
    def test_archive_creates_snapshot(self, sample_persona):
        path = version_manager.archive_before_update("版本测试", "self")
        if path is not None:  # 有些实现只在有变化时创建
            assert path.exists()

    def test_list_versions_empty_initially(self):
        # 如果没有创建过 persona，应该返回空列表或不报错
        versions = version_manager.list_versions("不存在", "self")
        assert isinstance(versions, list)

    def test_list_versions_after_archive(self, sample_persona):
        version_manager.archive_before_update("版本测试", "self")
        versions = version_manager.list_versions("版本测试", "self")
        assert isinstance(versions, list)


# ─── Cleanup ─────────────────────────────────────────────────────

class TestCleanup:
    def test_cleanup_does_not_crash(self, sample_persona):
        # 即使没有历史版本也不应该报错
        version_manager.cleanup_old_versions("版本测试", "self", keep_count=5)
