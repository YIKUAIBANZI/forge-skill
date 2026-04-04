"""
Skill 文件管理器 (Skill Writer)

负责：
- 创建和更新 standin 目录结构
- 写入和读取 persona.md
- 管理元信息（版本、更新时间等）
"""

import json
import re
from pathlib import Path
from datetime import datetime


STANDINS_DIR = Path(__file__).parent.parent.parent / "standins"


def get_standin_dir(name: str) -> Path:
    """获取替身目录，不存在则创建"""
    standin_dir = STANDINS_DIR / _sanitize_name(name)
    standin_dir.mkdir(parents=True, exist_ok=True)
    return standin_dir


def write_persona(name: str, content: str, version: str = None) -> Path:
    """写入 persona.md 文件"""
    standin_dir = get_standin_dir(name)
    persona_path = standin_dir / "persona.md"

    # 更新元信息中的 last_updated 和 version
    now = datetime.now().strftime("%Y-%m-%d")
    if version is None:
        # 自动递增版本号
        version = _get_next_version(persona_path)

    # 更新 frontmatter 中的日期和版本
    content = _update_frontmatter(content, {
        "last_updated": now,
        "version": version,
    })

    persona_path.write_text(content, encoding="utf-8")
    return persona_path


def read_persona(name: str) -> str:
    """读取 persona.md 内容"""
    persona_path = STANDINS_DIR / _sanitize_name(name) / "persona.md"
    if not persona_path.exists():
        raise FileNotFoundError(f"未找到替身：{name}，请先运行 create-standin 创建")
    return persona_path.read_text(encoding="utf-8")


def list_standins() -> list[dict]:
    """列出所有已创建的替身"""
    if not STANDINS_DIR.exists():
        return []

    standins = []
    for d in STANDINS_DIR.iterdir():
        if d.is_dir() and (d / "persona.md").exists():
            meta = _read_frontmatter(d / "persona.md")
            standins.append({
                "directory": d.name,
                "name": meta.get("name", d.name),
                "version": meta.get("version", "v1.0"),
                "last_updated": meta.get("last_updated", ""),
                "data_sources": meta.get("data_sources", ""),
            })
    return standins


def standin_exists(name: str) -> bool:
    """检查替身是否已存在"""
    return (STANDINS_DIR / _sanitize_name(name) / "persona.md").exists()


def append_correction(name: str, correction_text: str):
    """向 L5 纠正层追加一条纠正记录"""
    content = read_persona(name)
    now = datetime.now().strftime("%Y-%m-%d")

    correction_entry = f"\n- [{now}] {correction_text}"

    if "## L5: 纠正层" in content:
        # 在纠正层末尾追加
        content = content.replace(
            "### 纠正记录",
            f"### 纠正记录{correction_entry}",
            1
        )
    else:
        # 没有纠正层则新增
        content += f"\n\n## L5: 纠正层\n\n### 纠正记录{correction_entry}"

    write_persona(name, content)


def _sanitize_name(name: str) -> str:
    """将名称转为安全的目录名"""
    # 只保留字母、数字、中文、连字符
    safe = re.sub(r'[^\w\u4e00-\u9fff-]', '_', name)
    return safe[:50]  # 限制长度


def _get_next_version(persona_path: Path) -> str:
    """从现有文件读取版本号并递增"""
    if not persona_path.exists():
        return "v1.0"

    meta = _read_frontmatter(persona_path)
    current = meta.get("version", "v1.0")

    # 解析 v1.0 格式
    match = re.match(r'v(\d+)\.(\d+)', current)
    if match:
        major, minor = int(match.group(1)), int(match.group(2))
        return f"v{major}.{minor + 1}"
    return "v1.1"


def _read_frontmatter(persona_path: Path) -> dict:
    """读取 YAML frontmatter"""
    content = persona_path.read_text(encoding="utf-8")
    match = re.match(r'^---\n([\s\S]+?)\n---', content)
    if not match:
        return {}

    meta = {}
    for line in match.group(1).split('\n'):
        if ':' in line:
            key, _, value = line.partition(':')
            meta[key.strip()] = value.strip()
    return meta


def _update_frontmatter(content: str, updates: dict) -> str:
    """更新 frontmatter 中的指定字段"""
    match = re.match(r'^(---\n)([\s\S]+?)(\n---)', content)
    if not match:
        return content

    frontmatter = match.group(2)
    for key, value in updates.items():
        if re.search(rf'^{key}:', frontmatter, re.MULTILINE):
            frontmatter = re.sub(rf'^{key}:.*', f'{key}: {value}', frontmatter, flags=re.MULTILINE)
        else:
            frontmatter += f'\n{key}: {value}'

    return content[:match.start(2)] + frontmatter + content[match.end(2):]


if __name__ == "__main__":
    # 测试
    standins = list_standins()
    if standins:
        print("已有替身：")
        for s in standins:
            print(f"  - {s['name']} ({s['version']}, 更新于 {s['last_updated']})")
    else:
        print("还没有创建任何替身。运行 create-standin 开始创建。")
