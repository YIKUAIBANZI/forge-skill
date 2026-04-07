"""
决策日志管理器 (Decision Logger)

记录用户的决策过程和结果，随时间积累后反哺人格参数准确度。

存储路径：personas/self/{name}/decisions/
每条决策一个 JSON 文件：{timestamp}_{slug}.json
"""

import json
import re
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, field, asdict
from typing import Optional


PERSONAS_DIR = Path(__file__).parent.parent / "personas"


@dataclass
class DecisionRecord:
    id: str                          # 唯一ID，时间戳生成
    created_at: str                  # 创建时间
    title: str                       # 决策简标题（如"要不要跳槽去B公司"）
    scenario: str                    # 用户描述的完整场景
    options: list                    # 选项列表
    variants_generated: list         # 本次生成的替身变体
    variant_positions: dict          # 各变体的倾向（变体名 → 倾向选项）
    key_tensions: list               # 识别出的矛盾轴
    consensus: list                  # 所有变体的共识点
    core_disagreements: list         # 核心分歧点
    user_initial_lean: str = ""      # 用户开始时的倾向
    user_final_choice: str = ""      # 用户最终选择（事后填写）
    outcome_notes: str = ""          # 结果复盘（事后填写）
    outcome_date: str = ""           # 结果发生时间
    regret_level: int = -1           # 后悔程度 1-10（-1=未填写）
    params_feedback: dict = field(default_factory=dict)  # 对人格参数的反馈


def _decisions_dir(persona_name: str) -> Path:
    d = PERSONAS_DIR / "self" / _sanitize(persona_name) / "decisions"
    d.mkdir(parents=True, exist_ok=True)
    return d


def log_decision(persona_name: str, record: DecisionRecord) -> Path:
    """保存一条决策记录"""
    decisions_dir = _decisions_dir(persona_name)
    slug = re.sub(r'[^\w\u4e00-\u9fff]', '_', record.title)[:20]
    filename = f"{record.id}_{slug}.json"
    path = decisions_dir / filename
    path.write_text(json.dumps(asdict(record), ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def update_outcome(persona_name: str, decision_id: str, choice: str,
                   notes: str = "", regret_level: int = -1) -> bool:
    """事后更新决策结果"""
    decisions_dir = _decisions_dir(persona_name)
    for f in decisions_dir.glob(f"{decision_id}_*.json"):
        data = json.loads(f.read_text(encoding="utf-8"))
        data["user_final_choice"] = choice
        data["outcome_notes"] = notes
        data["outcome_date"] = datetime.now().strftime("%Y-%m-%d")
        if regret_level >= 0:
            data["regret_level"] = regret_level
        f.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        return True
    return False


def list_decisions(persona_name: str, pending_only: bool = False) -> list[dict]:
    """列出决策记录"""
    decisions_dir = _decisions_dir(persona_name)
    records = []
    for f in sorted(decisions_dir.glob("*.json"), reverse=True):
        data = json.loads(f.read_text(encoding="utf-8"))
        if pending_only and data.get("user_final_choice"):
            continue
        records.append({
            "id": data["id"],
            "title": data["title"],
            "created_at": data["created_at"],
            "final_choice": data.get("user_final_choice", ""),
            "has_outcome": bool(data.get("outcome_notes")),
            "regret_level": data.get("regret_level", -1),
        })
    return records


def generate_params_feedback(persona_name: str) -> dict:
    """
    分析历史决策记录，生成对 L3 决策参数的调整建议。

    逻辑：
    - 如果用户多次选择了"激进变体"的方向 → 风险偏好可能被低估
    - 如果用户后悔程度高的决定都是"冲动型" → action_bias 可能偏高
    - 如果实际选择和"自然的你"变体一致率高 → 参数准确
    """
    decisions_dir = _decisions_dir(persona_name)
    records = []
    for f in decisions_dir.glob("*.json"):
        data = json.loads(f.read_text(encoding="utf-8"))
        if data.get("user_final_choice"):
            records.append(data)

    if len(records) < 3:
        return {"message": "还不够3条有结果的决策，先积累数据再分析"}

    feedback = {}

    # 分析后悔模式
    regret_records = [r for r in records if r.get("regret_level", -1) >= 7]
    no_regret_records = [r for r in records if 0 <= r.get("regret_level", -1) <= 3]

    if regret_records:
        feedback["regret_pattern"] = {
            "high_regret_count": len(regret_records),
            "titles": [r["title"] for r in regret_records],
            "note": "这些决策后悔程度较高，可以复盘当时替身讨论的倾向和实际选择的差距"
        }

    # 分析变体一致性
    variant_alignment = []
    for r in records:
        positions = r.get("variant_positions", {})
        choice = r.get("user_final_choice", "")
        if positions and choice:
            aligned = [v for v, pos in positions.items() if pos == choice]
            variant_alignment.append(len(aligned) / max(len(positions), 1))

    if variant_alignment:
        avg_alignment = sum(variant_alignment) / len(variant_alignment)
        if avg_alignment > 0.7:
            feedback["variant_accuracy"] = "变体预测准确率较高，人格底座参数基本准确"
        elif avg_alignment < 0.4:
            feedback["variant_accuracy"] = "实际选择经常偏离所有变体预测，建议重新校准 L3 参数"
        else:
            feedback["variant_accuracy"] = f"变体预测准确率中等（{avg_alignment:.0%}），部分参数可能需要调整"

    feedback["total_decisions"] = len(records)
    feedback["decisions_with_outcome"] = len(records)
    return feedback


def new_record_id() -> str:
    return datetime.now().strftime("%Y%m%d%H%M%S%f")


def _sanitize(name: str) -> str:
    return re.sub(r'[^\w\u4e00-\u9fff-]', '_', name)[:50]


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("用法: python decision_logger.py <persona名称> [list|feedback]")
        sys.exit(1)

    name = sys.argv[1]
    action = sys.argv[2] if len(sys.argv) > 2 else "list"

    if action == "list":
        records = list_decisions(name)
        if records:
            print(f"{name} 的决策记录：")
            for r in records:
                status = f"→ {r['final_choice']}" if r['final_choice'] else "（待结果）"
                print(f"  [{r['created_at'][:10]}] {r['title']} {status}")
        else:
            print("还没有决策记录")

    elif action == "feedback":
        fb = generate_params_feedback(name)
        print(json.dumps(fb, ensure_ascii=False, indent=2))
