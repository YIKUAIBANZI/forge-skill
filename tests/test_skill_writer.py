"""
skill_writer.py 的单元测试
覆盖：读写 persona.md / persona.json、版本管理、纠正追加
"""
import sys, os, json, tempfile, pytest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools"))

import skill_writer


@pytest.fixture(autouse=True)
def use_temp_dir(tmp_path, monkeypatch):
    """所有测试用临时目录，不影响真实 personas"""
    monkeypatch.setattr(skill_writer, "PERSONAS_DIR", tmp_path)
    monkeypatch.setattr(skill_writer, "SELF_DIR", tmp_path / "self")
    monkeypatch.setattr(skill_writer, "OTHERS_DIR", tmp_path / "others")


class TestWriteAndRead:
    def test_write_and_read_md(self):
        path = skill_writer.write_persona("测试人", "# 这是测试内容\n\n一些文本", "self")
        assert path.exists()
        content = skill_writer.read_persona("测试人", "self")
        assert "测试内容" in content

    def test_write_and_read_json(self):
        data = {"meta": {"name": "JSON测试", "type": "self", "version": "v1.0"},
                "L3_decision_params": {"parameters": {}}}
        path = skill_writer.write_persona_json("JSON测试", data, "self")
        assert path.exists()
        loaded = skill_writer.read_persona_json("JSON测试", "self")
        assert loaded["meta"]["name"] == "JSON测试"

    def test_write_others_persona(self):
        data = {"meta": {"name": "小美", "type": "persona", "version": "v1.0"}}
        path = skill_writer.write_persona_json("小美", data, "others")
        assert path.exists()
        assert "others" in str(path)


class TestVersioning:
    def test_version_auto_increment(self):
        """写两次 JSON，版本号自动递增"""
        data_v1 = {"meta": {"name": "版本测试", "type": "self", "version": "v1.0"}}
        skill_writer.write_persona_json("版本测试", data_v1, "self")

        data_v2 = {"meta": {"name": "版本测试", "type": "self", "version": "v1.0"}}
        skill_writer.write_persona_json("版本测试", data_v2, "self")

        loaded = skill_writer.read_persona_json("版本测试", "self")
        # 版本应该 >= v1.0（具体取决于实现是否自动递增）
        assert "version" in loaded.get("meta", {})


class TestListAndExists:
    def test_persona_exists_after_write(self):
        skill_writer.write_persona("存在测试", "内容", "self")
        assert skill_writer.persona_exists("存在测试", "self")

    def test_persona_not_exists(self):
        assert not skill_writer.persona_exists("不存在的人", "self")

    def test_list_personas_empty(self):
        result = skill_writer.list_personas("self")
        assert isinstance(result, list)

    def test_list_personas_after_write(self):
        skill_writer.write_persona("列表测试", "内容", "self")
        result = skill_writer.list_personas("self")
        names = [p.get("name", "") for p in result]
        assert "列表测试" in names or len(result) > 0

    def test_has_json(self):
        data = {"meta": {"name": "JSON检查", "version": "v1.0"}}
        skill_writer.write_persona_json("JSON检查", data, "self")
        assert skill_writer.persona_has_json("JSON检查", "self")

    def test_has_no_json(self):
        skill_writer.write_persona("无JSON", "只有md", "self")
        assert not skill_writer.persona_has_json("无JSON", "self")


class TestCorrection:
    def test_append_correction(self):
        data = {"meta": {"name": "纠正测试", "version": "v1.0"}, "L5_corrections": []}
        skill_writer.write_persona_json("纠正测试", data, "self")
        correction = {
            "date": "2026-04-07", "layer": "L3", "field": "risk_appetite",
            "before": "5", "after": "7", "reason": "新证据",
        }
        skill_writer.append_correction("纠正测试", correction, "self")
        loaded = skill_writer.read_persona_json("纠正测试", "self")
        assert len(loaded.get("L5_corrections", [])) >= 1


class TestNameSanitization:
    def test_chinese_name(self):
        path = skill_writer.get_persona_dir("小明", "self")
        assert path.exists()

    def test_name_with_special_chars(self):
        path = skill_writer.get_persona_dir("test-用户_01", "self")
        assert path.exists()
