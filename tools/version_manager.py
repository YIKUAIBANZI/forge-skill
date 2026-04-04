"""
版本管理器 (Version Manager)

负责：
- 在更新前存档当前版本
- 版本历史查看
- 版本回滚
"""

import re
import shutil
from pathlib import Path
from datetime import datetime


PERSONAS_DIR = Path(__file__).parent.parent / "personas"


def _get_persona_path(name: str, persona_type: str = "self") -> Path:
    base = PERSONAS_DIR / persona_type
    return base / _sanitize_name(name) / "persona.md"


def archive_before_update(name: str, persona_type: str = "self") -> Path:
    """更新前创建当前版本快照，返回存档路径"""
    persona_path = _get_persona_path(name, persona_type)
    if not persona_path.exists():
        return None

    history_dir = persona_path.parent / "history"
    history_dir.mkdir(exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_path = history_dir / f"persona_{timestamp}.md"
    shutil.copy2(persona_path, archive_path)
    return archive_path


def list_versions(name: str, persona_type: str = "self") -> list[dict]:
    """列出历史版本"""
    history_dir = _get_persona_path(name, persona_type).parent / "history"
    if not history_dir.exists():
        return []

    versions = []
    for f in sorted(history_dir.glob("persona_*.md"), reverse=True):
        ts_str = f.stem.replace("persona_", "")
        try:
            ts = datetime.strptime(ts_str, "%Y%m%d_%H%M%S")
            formatted = ts.strftime("%Y-%m-%d %H:%M")
        except ValueError:
            formatted = ts_str
        versions.append({"file": f.name, "path": str(f), "saved_at": formatted})

    return versions


def rollback(name: str, version_file: str, persona_type: str = "self") -> bool:
    """回滚到指定历史版本"""
    persona_path = _get_persona_path(name, persona_type)
    history_dir = persona_path.parent / "history"
    archive_path = history_dir / version_file

    if not archive_path.exists():
        return False

    archive_before_update(name, persona_type)
    shutil.copy2(archive_path, persona_path)
    return True


def cleanup_old_versions(name: str, persona_type: str = "self", keep_count: int = 10):
    """清理旧版本，只保留最近 N 个"""
    history_dir = _get_persona_path(name, persona_type).parent / "history"
    if not history_dir.exists():
        return
    versions = sorted(history_dir.glob("persona_*.md"))
    for f in versions[:-keep_count]:
        f.unlink()


def _sanitize_name(name: str) -> str:
    return re.sub(r'[^\w\u4e00-\u9fff-]', '_', name)[:50]


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("用法: python version_manager.py <名称> [self|others] [list|rollback <版本文件>]")
        sys.exit(1)

    name = sys.argv[1]
    persona_type = sys.argv[2] if len(sys.argv) > 2 and sys.argv[2] in ("self", "others") else "self"
    action = sys.argv[3] if len(sys.argv) > 3 else "list"

    if action == "list":
        versions = list_versions(name, persona_type)
        if versions:
            print(f"{name} ({persona_type}) 的历史版本：")
            for v in versions:
                print(f"  [{v['saved_at']}] {v['file']}")
        else:
            print("没有历史版本")
    elif action == "rollback" and len(sys.argv) > 4:
        if rollback(name, sys.argv[4], persona_type):
            print(f"已回滚到：{sys.argv[4]}")
        else:
            print(f"回滚失败：找不到该版本")
