"""
Skill 文件管理器 (Skill Writer)

负责：
- 创建和更新 persona 目录结构
- 写入和读取 persona.md（人读）和 persona.json（程序调用）
- 两者保持同步，persona.json 是 single source of truth

目录结构：
  personas/self/{name}/persona.md     — 人读版本
  personas/self/{name}/persona.json   — 结构化版本（程序调用）
  personas/others/{name}/persona.md
  personas/others/{name}/persona.json
"""

import json
import re
from pathlib import Path
from datetime import datetime


PERSONAS_DIR = Path(__file__).parent.parent / "personas"
SELF_DIR = PERSONAS_DIR / "self"
OTHERS_DIR = PERSONAS_DIR / "others"


def get_persona_dir(name: str, persona_type: str = "self") -> Path:
    """获取 persona 目录，不存在则创建"""
    base = SELF_DIR if persona_type == "self" else OTHERS_DIR
    persona_dir = base / _sanitize_name(name)
    persona_dir.mkdir(parents=True, exist_ok=True)
    return persona_dir


# ─── persona.md（人读版）─────────────────────────────────────

def write_persona(name: str, content: str, persona_type: str = "self", version: str = None) -> Path:
    """写入 persona.md"""
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
    """读取 persona.md"""
    base = SELF_DIR if persona_type == "self" else OTHERS_DIR
    persona_path = base / _sanitize_name(name) / "persona.md"
    if not persona_path.exists():
        hint = "/forge-self" if persona_type == "self" else "/forge-persona"
        raise FileNotFoundError(f"未找到 {persona_type} persona：{name}，请先运行 {hint} 创建")
    return persona_path.read_text(encoding="utf-8")


# ─── persona.json（程序调用版）──────────────────────────────

def write_persona_json(name: str, data: dict, persona_type: str = "self") -> Path:
    """写入 persona.json（结构化数据）

    data 应符合 persona_schema.py 中定义的 SelfPersona 或 OthersPersona 结构。
    会自动更新 meta.last_updated 和 meta.version。
    """
    persona_dir = get_persona_dir(name, persona_type)
    json_path = persona_dir / "persona.json"

    now = datetime.now().strftime("%Y-%m-%d")

    # 更新 meta
    if "meta" not in data:
        data["meta"] = {}
    data["meta"]["last_updated"] = now
    data["meta"]["name"] = data["meta"].get("name", name)
    data["meta"]["type"] = persona_type

    # 自动递增版本
    if json_path.exists():
        try:
            existing = json.loads(json_path.read_text(encoding="utf-8"))
            current_version = existing.get("meta", {}).get("version", "v1.0")
            data["meta"]["version"] = _increment_version(current_version)
        except Exception:
            data["meta"]["version"] = data["meta"].get("version", "v1.0")
    else:
        data["meta"]["version"] = data["meta"].get("version", "v1.0")

    json_path.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    return json_path


def read_persona_json(name: str, persona_type: str = "self") -> dict:
    """读取 persona.json，返回 dict

    优先读 json，如果 json 不存在但 md 存在，返回空骨架并提示迁移。
    """
    base = SELF_DIR if persona_type == "self" else OTHERS_DIR
    json_path = base / _sanitize_name(name) / "persona.json"
    md_path = base / _sanitize_name(name) / "persona.md"

    if json_path.exists():
        return json.loads(json_path.read_text(encoding="utf-8"))

    if md_path.exists():
        raise FileNotFoundError(
            f"{name} 的 persona.json 不存在，但 persona.md 存在。\n"
            f"请运行迁移工具：python tools/migrate_to_json.py {name} {persona_type}"
        )

    hint = "/forge-self" if persona_type == "self" else "/forge-persona"
    raise FileNotFoundError(f"未找到 {persona_type} persona：{name}，请先运行 {hint} 创建")


def persona_has_json(name: str, persona_type: str = "self") -> bool:
    """检查是否已有 persona.json"""
    base = SELF_DIR if persona_type == "self" else OTHERS_DIR
    return (base / _sanitize_name(name) / "persona.json").exists()


# ─── 列表和检查 ───────────────────────────────────────────────

def list_personas(persona_type: str = "self") -> list[dict]:
    """列出已创建的 persona"""
    base = SELF_DIR if persona_type == "self" else OTHERS_DIR
    if not base.exists():
        return []

    result = []
    for d in base.iterdir():
        if not d.is_dir():
            continue
        json_path = d / "persona.json"
        md_path = d / "persona.md"

        if json_path.exists():
            try:
                data = json.loads(json_path.read_text(encoding="utf-8"))
                meta = data.get("meta", {})
                result.append({
                    "directory": d.name,
                    "name": meta.get("name", d.name),
                    "type": persona_type,
                    "version": meta.get("version", "v1.0"),
                    "last_updated": meta.get("last_updated", ""),
                    "data_sources": meta.get("data_sources", []),
                    "has_json": True,
                })
                continue
            except Exception:
                pass

        if md_path.exists():
            meta = _read_frontmatter(md_path)
            result.append({
                "directory": d.name,
                "name": meta.get("name", d.name),
                "type": persona_type,
                "version": meta.get("version", "v1.0"),
                "last_updated": meta.get("last_updated", ""),
                "data_sources": meta.get("data_sources", ""),
                "has_json": False,  # 标注：尚未迁移
            })

    return result


def persona_exists(name: str, persona_type: str = "self") -> bool:
    """检查 persona 是否已存在（md 或 json 任一存在即可）"""
    base = SELF_DIR if persona_type == "self" else OTHERS_DIR
    safe = _sanitize_name(name)
    return (base / safe / "persona.md").exists() or (base / safe / "persona.json").exists()


# ─── 纠正追加 ─────────────────────────────────────────────────

def append_correction(name: str, correction: dict, persona_type: str = "self"):
    """向 L5 追加纠正记录（同时更新 json 和 md）

    correction 格式：
    {
        "layer": "L3",
        "field": "parameters.risk_appetite.score",
        "before": "4",
        "after": "7",
        "reason": "用户反馈",
        "user_original_words": "其实我骨子里还是挺冒险的"
    }
    """
    now = datetime.now().strftime("%Y-%m-%d")
    correction["date"] = now

    # 更新 json
    if persona_has_json(name, persona_type):
        data = read_persona_json(name, persona_type)
        if "L5_corrections" not in data:
            data["L5_corrections"] = []
        data["L5_corrections"].append(correction)
        write_persona_json(name, data, persona_type)

    # 更新 md（追加到 L5 纠正层）
    try:
        content = read_persona(name, persona_type)
        entry = f"\n- [{now}] [{correction.get('layer', '')}] {correction.get('field', '')}: {correction.get('before', '')} → {correction.get('after', '')}（{correction.get('reason', '')}）"
        if "## L5: 纠正层" in content:
            content = content.replace("### 纠正记录", f"### 纠正记录{entry}", 1)
        else:
            content += f"\n\n## L5: 纠正层\n\n### 纠正记录{entry}"
        write_persona(name, content, persona_type)
    except FileNotFoundError:
        pass  # 只有 json 没有 md，跳过


# ─── 内部工具 ─────────────────────────────────────────────────

def _sanitize_name(name: str) -> str:
    return re.sub(r'[^\w\u4e00-\u9fff-]', '_', name)[:50]


def _increment_version(version: str) -> str:
    match = re.match(r'v(\d+)\.(\d+)', version)
    if match:
        return f"v{match.group(1)}.{int(match.group(2)) + 1}"
    return "v1.1"


def _get_next_version(persona_path: Path) -> str:
    if not persona_path.exists():
        return "v1.0"
    meta = _read_frontmatter(persona_path)
    return _increment_version(meta.get("version", "v1.0"))


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
                json_flag = "✅ json" if p.get("has_json") else "⚠️  仅md"
                print(f"  {json_flag} {p['name']} ({p['version']}, {p['last_updated']})")
    if not list_personas("self") and not list_personas("others"):
        print("还没有任何 persona。运行 /forge-self 或 /forge-persona [name] 开始创建。")
