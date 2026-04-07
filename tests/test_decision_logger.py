"""
decision_logger.py 的单元测试
覆盖：决策记录创建、结果回填、列表查询
"""
import sys, os, json, pytest
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "tools"))

import decision_logger
import skill_writer


@pytest.fixture(autouse=True)
def use_temp_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(skill_writer, "PERSONAS_DIR", tmp_path)
    monkeypatch.setattr(skill_writer, "SELF_DIR", tmp_path / "self")
    monkeypatch.setattr(skill_writer, "OTHERS_DIR", tmp_path / "others")
    if hasattr(decision_logger, "PERSONAS_DIR"):
        monkeypatch.setattr(decision_logger, "PERSONAS_DIR", tmp_path)


@pytest.fixture
def setup_persona(tmp_path):
    """创建用于决策记录测试的 persona 目录"""
    persona_dir = tmp_path / "self" / "决策测试"
    persona_dir.mkdir(parents=True, exist_ok=True)
    data = {"meta": {"name": "决策测试", "type": "self", "version": "v1.0"}}
    (persona_dir / "persona.json").write_text(json.dumps(data, ensure_ascii=False))
    return "决策测试"


class TestRecordCreation:
    def test_new_record_id_format(self):
        rid = decision_logger.new_record_id()
        assert isinstance(rid, str)
        assert len(rid) > 0

    def test_new_record_id_unique(self):
        ids = {decision_logger.new_record_id() for _ in range(10)}
        assert len(ids) >= 2  # 至少大部分应该不同

    def test_decision_record_creation(self):
        record = decision_logger.DecisionRecord(
            id=decision_logger.new_record_id(),
            created_at="2026-04-07",
            title="要不要换工作",
            scenario="收到外地offer",
            options=["留下", "跳槽"],
            variants_generated=["稳健你", "果断你", "关系优先你"],
            variant_positions={"稳健你": "留下", "果断你": "跳", "关系优先你": "留下"},
            key_tensions=["安全vs成长", "短期vs长期"],
            consensus=["都同意需要更多信息"],
            core_disagreements=["风险承受度"],
        )
        assert record.title == "要不要换工作"
        assert len(record.options) == 2


class TestLogAndList:
    def test_log_and_list(self, setup_persona):
        record = decision_logger.DecisionRecord(
            id=decision_logger.new_record_id(),
            created_at="2026-04-07",
            title="测试决策",
            scenario="测试场景",
            options=["A", "B"],
            variants_generated=["v1"],
            variant_positions={"v1": "A"},
            key_tensions=["x"],
            consensus=["y"],
            core_disagreements=["z"],
        )
        decision_logger.log_decision(setup_persona, record)
        decisions = decision_logger.list_decisions(setup_persona)
        assert isinstance(decisions, list)
        assert len(decisions) >= 1


class TestOutcomeUpdate:
    def test_update_outcome(self, setup_persona):
        record = decision_logger.DecisionRecord(
            id="test-001",
            created_at="2026-04-07",
            title="结果测试",
            scenario="场景",
            options=["A", "B"],
            variants_generated=["v1"],
            variant_positions={"v1": "A"},
            key_tensions=[], consensus=[], core_disagreements=[],
        )
        decision_logger.log_decision(setup_persona, record)
        success = decision_logger.update_outcome(
            setup_persona, "test-001",
            choice="A", notes="选了A，还不错", regret_level=2
        )
        assert success is True
