"""
版本管理器 (Version Manager)

负责：
- 在更新前存档当前版本
- 版本历史查看
- 版本回滚
"""

import shutil
from pathlib import Path
from datetime import datetime


STANDINS_DIR = Path(__file__).parent.parent.parent / "standins"


def archive_before_update(name: str) -> Path:
    """更新前创建当前版本快照，返回存档路径"""
    standin_dir = STANDINS_DIR / _sanitize_name(name)
    persona_path = standin_dir / "persona.md"

    if not persona_path.exists():
        return None

    # 创建 history 目录
    history_dir = standin_dir / "history"
    history_dir.mkdir(exist_ok=True)

    # 以时间戳命名存档
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_path = history_dir / f"persona_{timestamp}.md"
    shutil.copy2(persona_path, archive_path)

    return archive_path


def list_versions(name: str) -> list[dict]:
    """列出某个替身的所有历史版本"""
    standin_dir = STANDINS_DIR / _sanitize_name(name)
    history_dir = standin_dir / "history"

    if not history_dir.exists():
        return []

    versions = []
    for f in sorted(history_dir.glob("persona_*.md"), reverse=True):
        # 从文件名解析时间戳
        ts_str = f.stem.replace("persona_", "")
        try:
            ts = datetime.strptime(ts_str, "%Y%m%d_%H%M%S")
            formatted = ts.strftime("%Y-%m-%d %H:%M")
        except ValueError:
            formatted = ts_str

        versions.append({
            "file": f.name,
            "path": str(f),
            "saved_at": formatted,
        })

    return versions


def rollback(name: str, version_file: str) -> bool:
    """回滚到指定历史版本"""
    standin_dir = STANDINS_DIR / _sanitize_name(name)
    history_dir = standin_dir / "history"
    persona_path = standin_dir / "persona.md"

    archive_path = history_dir / version_file
    if not archive_path.exists():
        return False

    # 先把当前版本存档
    archive_before_update(name)

    # 回滚
    shutil.copy2(archive_path, persona_path)
    return True


def cleanup_old_versions(name: str, keep_count: int = 10):
    """清理旧版本，只保留最近 N 个"""
    standin_dir = STANDINS_DIR / _sanitize_name(name)
    history_dir = standin_dir / "history"

    if not history_dir.exists():
        return

    versions = sorted(history_dir.glob("persona_*.md"))
    to_delete = versions[:-keep_count] if len(versions) > keep_count else []
    for f in to_delete:
        f.unlink()


def _sanitize_name(name: str) -> str:
    import re
    return re.sub(r'[^\w\u4e00-\u9fff-]', '_', name)[:50]


if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("用法: python version_manager.py <替身名称> [list|rollback <版本文件>]")
        sys.exit(1)

    name = sys.argv[1]
    action = sys.argv[2] if len(sys.argv) > 2 else "list"

    if action == "list":
        versions = list_versions(name)
        if versions:
            print(f"{name} 的历史版本：")
            for v in versions:
                print(f"  [{v['saved_at']}] {v['file']}")
        else:
            print("没有历史版本")

    elif action == "rollback" and len(sys.argv) > 3:
        version_file = sys.argv[3]
        if rollback(name, version_file):
            print(f"已回滚到：{version_file}")
        else:
            print(f"回滚失败：找不到版本 {version_file}")
