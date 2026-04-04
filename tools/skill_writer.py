"""
Skill 文件管理器 (Skill Writer)

负责：
- 创建和更新 persona 目录结构
- 写入和读取 persona.md
- 管理元信息（版本、更新时间等）

目录结构：
  personas/self/{name}/persona.md    — forge-self 生成的自我替身
  personas/others/{name}/persona.md  — forge-persona 生成的他人档案
"""

import re
from pathlib import Path
from datetime import datetime


PERSONAS_DIR = Path(__file__).parent.parent / "personas"
SELF_DIR = PERSONAS_DIR / "self"
OTHERS_DIR = PERSONAS_DIR / "others"


def get_persona_dir(name: str, persona_type: str = "self") -> Path:
    """获取 persona 目录，不存在则创建

    persona_type: "self" | "others"
    """
    base = SELF_DIR if persona_type == "self" else OTHERS_DIR
    persona_dir = base / _sanitize_name(name)
    persona_dir.mkdir(parents=True, exist_ok=True)
    return persona_dir


def write_persona(name: str, content: str, persona_type: str = "self", version: str = None) -> Path:
    """写入 persona.md 文件"""
    persona_dir = get_persona_dir(name, persona_type)
    persona_path = persona_dir / "persona.md"

    now = datetime.now().strftime("%Y-%m-%d")
    if version is None:
        version = _get_next_version(persona_path)

    content = _update_frontmatter(content, {
        "last_updated": now,
        "version": version,
        "type": persona_type,
    })

    persona_path.write_text(content, encoding="utf-8")
    return persona_path


def read_persona(name: str, persona_type: str = "self") -> str:
    """读取 persona.md 内容"""
    base = SELF_DIR if persona_type == "self" else OTHERS_DIR
    persona_path = base / _sanitize_name(name) / "persona.md"
    if not persona_path.exists():
        hint = "/forge-self" if persona_type == "self" else "/forge-persona"
        raise FileNotFoundError(f"未找到 {persona_type} persona：{name}，请先运行 {hint} 创建")
    return persona_path.read_text(encoding="utf-8")


def list_personas(persona_type: str = "self") -> list[dict]:
    """列出已创建的 persona"""
    base = SELF_DIR if persona_type == "self" else OTHERS_DIR
    if not base.exists():
        return []

    result = []
    for d in base.iterdir():
        if d.is_dir() and (d / "persona.md").exists():
            meta = _read_frontmatter(d / "persona.md")
            result.append({
                "directory": d.name,
                "name": meta.get("name", d.name),
                "type": persona_type,
                "version": meta.get("version", "v1.0"),
                "last_updated": meta.get("last_updated", ""),
                "data_sources": meta.get("data_sources", ""),
            })
    return result


def persona_exists(name: str, persona_type: str = "self") -> bool:
    """检查 persona 是否已存在"""
    base = SELF_DIR if persona_type == "self" else OTHERS_DIR
    return (base / _sanitize_name(name) / "persona.md").exists()


def append_correction(name: str, correction_text: str, persona_type: str = "self"):
    """向 L5 纠正层追加一条纠正记录"""
    content = read_persona(name, persona_type)
    now = datetime.now().strftime("%Y-%m-%d")
    correction_entry = f"\n- [{now}] {correction_text}"

    if "## L5: 纠正层" in content:
        content = content.replace(
            "### 纠正记录",
            f"### 纠正记录{correction_entry}",
            1
        )
    else:
        content += f"\n\n## L5: 纠正层\n\n### 纠正记录{correction_entry}"

    write_persona(name, content, persona_type)


def _sanitize_name(name: str) -> str:
    safe = re.sub(r'[^\w\u4e00-\u9fff-]', '_', name)
    return safe[:50]


def _get_next_version(persona_path: Path) -> str:
    if not persona_path.exists():
        return "v1.0"
    meta = _read_frontmatter(persona_path)
    current = meta.get("version", "v1.0")
    match = re.match(r'v(\d+)\.(\d+)', current)
    if match:
        major, minor = int(match.group(1)), int(match.group(2))
        return f"v{major}.{minor + 1}"
    return "v1.1"


def _read_frontmatter(persona_path: Path) -> dict:
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
    for ptype in ("self", "others"):
        personas = list_personas(ptype)
        if personas:
            print(f"\n[{ptype}]")
            for p in personas:
                print(f"  - {p['name']} ({p['version']}, 更新于 {p['last_updated']})")
    if not list_personas("self") and not list_personas("others"):
        print("还没有任何 persona。运行 /forge-self 或 /forge-persona [name] 开始创建。")
