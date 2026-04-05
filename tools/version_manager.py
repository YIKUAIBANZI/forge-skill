"""
版本管理器 (Version Manager)

负责：
- 更新前存档当前版本（persona.json 全量快照）
- 字段级 diff 生成与记录（changelog.json）
- 按字段回滚（不影响其他字段）
- 全量版本回滚
- 版本历史查看
"""

import json
import re
import shutil
from datetime import datetime
from pathlib import Path


PERSONAS_DIR = Path(__file__).parent.parent / "personas"


# ---------------------------------------------------------------------------
# 路径工具
# ---------------------------------------------------------------------------

def _sanitize_name(name: str) -> str:
    return re.sub(r'[^\w\u4e00-\u9fff-]', '_', name)[:50]


def _persona_dir(name: str, persona_type: str = "self") -> Path:
    return PERSONAS_DIR / persona_type / _sanitize_name(name)


def _json_path(name: str, persona_type: str = "self") -> Path:
    return _persona_dir(name, persona_type) / "persona.json"


def _history_dir(name: str, persona_type: str = "self") -> Path:
    d = _persona_dir(name, persona_type) / "history"
    d.mkdir(parents=True, exist_ok=True)
    return d


def _changelog_path(name: str, persona_type: str = "self") -> Path:
    return _history_dir(name, persona_type) / "changelog.json"


# ---------------------------------------------------------------------------
# 全量快照（已有功能，扩展为支持 json）
# ---------------------------------------------------------------------------

def archive_before_update(name: str, persona_type: str = "self") -> Path | None:
    """更新前创建当前版本快照（json），返回存档路径"""
    src = _json_path(name, persona_type)
    if not src.exists():
        # 兼容旧版：如果只有 md，快照 md
        md = _persona_dir(name, persona_type) / "persona.md"
        if not md.exists():
            return None
        src = md

    hist = _history_dir(name, persona_type)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    suffix = src.suffix
    dest = hist / f"persona_{ts}{suffix}"
    shutil.copy2(src, dest)
    return dest


def list_versions(name: str, persona_type: str = "self") -> list[dict]:
    """列出历史快照版本"""
    hist = _history_dir(name, persona_type)
    versions = []
    for f in sorted(hist.glob("persona_*"), reverse=True):
        if f.name == "changelog.json":
            continue
        ts_str = f.stem.replace("persona_", "")
        try:
            ts = datetime.strptime(ts_str, "%Y%m%d_%H%M%S")
            formatted = ts.strftime("%Y-%m-%d %H:%M:%S")
        except ValueError:
            formatted = ts_str
        versions.append({"file": f.name, "path": str(f), "saved_at": formatted})
    return versions


def rollback(name: str, version_file: str, persona_type: str = "self") -> bool:
    """全量回滚到指定历史版本"""
    dest = _json_path(name, persona_type)
    hist = _history_dir(name, persona_type)
    src = hist / version_file

    if not src.exists():
        return False

    archive_before_update(name, persona_type)
    shutil.copy2(src, dest)
    return True


def cleanup_old_versions(name: str, persona_type: str = "self", keep_count: int = 10):
    """清理旧版本快照，只保留最近 N 个"""
    hist = _history_dir(name, persona_type)
    files = sorted([f for f in hist.glob("persona_*") if f.name != "changelog.json"])
    for f in files[:-keep_count]:
        f.unlink()


# ---------------------------------------------------------------------------
# 字段级 Diff
# ---------------------------------------------------------------------------

def generate_diff(old_data: dict, new_data: dict, path: str = "") -> list[dict]:
    """
    递归生成字段级 diff。

    返回 list[dict]，每项格式：
    {
      "field_path": "L3_decision_params.parameters.risk_appetite.score",
      "before": 5,
      "after": 7,
      "change_type": "modified" | "added" | "removed"
    }
    """
    changes = []

    all_keys = set(old_data.keys()) | set(new_data.keys()) if isinstance(old_data, dict) else set()

    for key in all_keys:
        field_path = f"{path}.{key}" if path else key
        old_val = old_data.get(key) if isinstance(old_data, dict) else None
        new_val = new_data.get(key) if isinstance(new_data, dict) else None

        if key not in old_data:
            changes.append({"field_path": field_path, "before": None, "after": new_val, "change_type": "added"})
        elif key not in new_data:
            changes.append({"field_path": field_path, "before": old_val, "after": None, "change_type": "removed"})
        elif isinstance(old_val, dict) and isinstance(new_val, dict):
            changes.extend(generate_diff(old_val, new_val, field_path))
        elif isinstance(old_val, list) and isinstance(new_val, list):
            # 列表：只比较整体是否变化，不做元素级 diff（避免过度细化）
            if old_val != new_val:
                changes.append({"field_path": field_path, "before": old_val, "after": new_val, "change_type": "modified"})
        elif old_val != new_val:
            changes.append({"field_path": field_path, "before": old_val, "after": new_val, "change_type": "modified"})

    return changes


def save_changelog_entry(
    name: str,
    persona_type: str,
    changes: list[dict],
    reason: str,
    user_words: str = "",
) -> None:
    """
    将一次修改的 diff 追加写入 changelog.json。

    changelog.json 结构：
    [
      {
        "version": "1.0 → 1.1",
        "date": "ISO date",
        "reason": "...",
        "user_words": "...",
        "changes": [ {...}, ... ]
      },
      ...
    ]
    """
    changelog_path = _changelog_path(name, persona_type)

    # 读取现有 changelog
    if changelog_path.exists():
        try:
            entries = json.loads(changelog_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, IOError):
            entries = []
    else:
        entries = []

    # 确定版本号
    persona_data = {}
    json_file = _json_path(name, persona_type)
    if json_file.exists():
        try:
            persona_data = json.loads(json_file.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, IOError):
            pass

    current_version = persona_data.get("meta", {}).get("version", "unknown")
    prev_version = entries[-1].get("version", "").split(" → ")[-1] if entries else "0.0"

    entry = {
        "version": f"{prev_version} → {current_version}",
        "date": datetime.now().isoformat(),
        "reason": reason,
        "user_words": user_words,
        "changes": changes,
    }
    entries.append(entry)
    changelog_path.write_text(json.dumps(entries, ensure_ascii=False, indent=2), encoding="utf-8")


# ---------------------------------------------------------------------------
# 字段级回滚
# ---------------------------------------------------------------------------

def _get_nested(data: dict, field_path: str):
    """按路径读取嵌套字段，如 'L3_decision_params.parameters.risk_appetite.score'"""
    keys = field_path.split(".")
    cur = data
    for k in keys:
        if not isinstance(cur, dict) or k not in cur:
            raise KeyError(f"字段路径不存在：{field_path}")
        cur = cur[k]
    return cur


def _set_nested(data: dict, field_path: str, value) -> dict:
    """按路径写入嵌套字段，返回修改后的 data（in-place 修改）"""
    keys = field_path.split(".")
    cur = data
    for k in keys[:-1]:
        if k not in cur or not isinstance(cur[k], dict):
            cur[k] = {}
        cur = cur[k]
    cur[keys[-1]] = value
    return data


def rollback_field(
    name: str,
    persona_type: str,
    field_path: str,
    version_file: str,
) -> dict:
    """
    将 persona.json 中的单个字段回滚到指定历史版本的值。
    其他字段不受影响。

    返回：{ "success": bool, "field_path": str, "before": ..., "after": ..., "message": str }
    """
    hist = _history_dir(name, persona_type)
    snapshot_path = hist / version_file

    if not snapshot_path.exists():
        return {"success": False, "message": f"找不到历史版本：{version_file}"}

    # 只支持 json 快照的字段回滚
    if not version_file.endswith(".json"):
        return {"success": False, "message": "字段回滚仅支持 .json 快照文件"}

    try:
        snapshot_data = json.loads(snapshot_path.read_text(encoding="utf-8"))
        historical_value = _get_nested(snapshot_data, field_path)
    except KeyError:
        return {"success": False, "message": f"历史版本中不存在该字段：{field_path}"}
    except (json.JSONDecodeError, IOError) as e:
        return {"success": False, "message": f"读取历史版本失败：{e}"}

    # 读取当前 persona
    current_path = _json_path(name, persona_type)
    if not current_path.exists():
        return {"success": False, "message": "当前 persona.json 不存在"}

    current_data = json.loads(current_path.read_text(encoding="utf-8"))

    try:
        current_value = _get_nested(current_data, field_path)
    except KeyError:
        current_value = None

    # 先存档当前版本
    archive_before_update(name, persona_type)

    # 回滚字段
    _set_nested(current_data, field_path, historical_value)
    current_path.write_text(json.dumps(current_data, ensure_ascii=False, indent=2), encoding="utf-8")

    # 记录到 changelog
    save_changelog_entry(
        name, persona_type,
        changes=[{
            "field_path": field_path,
            "before": current_value,
            "after": historical_value,
            "change_type": "modified",
        }],
        reason=f"字段回滚：从 {version_file} 恢复",
        user_words="",
    )

    return {
        "success": True,
        "field_path": field_path,
        "before": current_value,
        "after": historical_value,
        "message": f"已将 {field_path} 回滚到 {version_file} 的值",
    }


# ---------------------------------------------------------------------------
# CLI 入口
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import sys

    def usage():
        print("用法：")
        print("  python version_manager.py <名称> [self|others] list")
        print("  python version_manager.py <名称> [self|others] rollback <版本文件>")
        print("  python version_manager.py <名称> [self|others] rollback-field <字段路径> <版本文件>")
        print("  python version_manager.py <名称> [self|others] changelog")
        sys.exit(1)

    if len(sys.argv) < 3:
        usage()

    name = sys.argv[1]
    persona_type = sys.argv[2] if sys.argv[2] in ("self", "others") else "self"
    action = sys.argv[3] if len(sys.argv) > 3 else "list"

    if action == "list":
        versions = list_versions(name, persona_type)
        if versions:
            print(f"{name} ({persona_type}) 的历史快照：")
            for v in versions:
                print(f"  [{v['saved_at']}] {v['file']}")
        else:
            print("没有历史快照")

    elif action == "rollback":
        if len(sys.argv) < 5:
            print("缺少版本文件参数")
            usage()
        if rollback(name, sys.argv[4], persona_type):
            print(f"已全量回滚到：{sys.argv[4]}")
        else:
            print("回滚失败：找不到该版本")

    elif action == "rollback-field":
        if len(sys.argv) < 6:
            print("缺少参数，需要：<字段路径> <版本文件>")
            usage()
        result = rollback_field(name, persona_type, sys.argv[4], sys.argv[5])
        if result["success"]:
            print(result["message"])
            print(f"  修改前：{result['before']}")
            print(f"  修改后：{result['after']}")
        else:
            print(f"失败：{result['message']}")

    elif action == "changelog":
        cp = _changelog_path(name, persona_type)
        if not cp.exists():
            print("暂无变更记录")
        else:
            entries = json.loads(cp.read_text(encoding="utf-8"))
            for e in entries:
                print(f"\n[{e['date'][:10]}] {e['version']} — {e['reason']}")
                if e.get("user_words"):
                    print(f"  用户原话：{e['user_words']}")
                for c in e.get("changes", []):
                    arrow = "→" if c["change_type"] == "modified" else ("+" if c["change_type"] == "added" else "-")
                    print(f"  {arrow} {c['field_path']}: {c['before']} → {c['after']}")

    else:
        usage()
