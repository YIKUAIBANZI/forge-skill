"""
角色扮演一致性测试 (Persona Consistency Test)

对 use-persona 场景进行自动评测：给定 persona + 10 个对话场景，
让 Claude 生成角色扮演回复，再用 Claude 按 5 个维度评分。

用法：
    python evals/persona_consistency_test.py --persona personas/others/小美/persona.json
    python evals/persona_consistency_test.py --persona personas/others/小美/persona.json --cases evals/test_cases/persona_consistency_cases.yaml
"""

import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).parent.parent))
from tools.persona_runtime_loader import load_card


# ---------------------------------------------------------------------------
# 评分维度定义
# ---------------------------------------------------------------------------

SCORING_DIMENSIONS = [
    {
        "id": "message_length",
        "name": "消息长度一致性",
        "weight": 20,
        "prompt_fragment": (
            "回复的长度是否符合 persona 的 L2.message_habits 描述？"
            "如果 persona 是短消息风格，给长篇回复就应扣分。"
        ),
    },
    {
        "id": "signature_phrases",
        "name": "口头禅命中率",
        "weight": 20,
        "prompt_fragment": (
            "回复中是否自然出现了 persona 的 L2.signature_phrases 中的词或句式？"
            "不需要每条都用，但完全没有应扣分。"
        ),
    },
    {
        "id": "punctuation_style",
        "name": "标点风格一致性",
        "weight": 20,
        "prompt_fragment": (
            "标点和语气是否符合 persona 的风格描述？"
            "比如 persona 几乎不用句号，但回复全是句号结尾，应扣分。"
        ),
    },
    {
        "id": "interaction_pattern",
        "name": "互动模式一致性",
        "weight": 20,
        "prompt_fragment": (
            "在这个具体场景下，回复的互动模式是否符合 persona 的 L4.scene_responses？"
            "比如面对倾诉时的反应、被问建议时的典型答法是否对上。"
        ),
    },
    {
        "id": "hard_traits",
        "name": "边界遵守",
        "weight": 20,
        "prompt_fragment": (
            "回复有没有违反 persona 的 L0 硬性特征？"
            "如果 L0 说'ta 绝对不会...'，但回复中出现了这个行为，应严重扣分。"
        ),
    },
]


# ---------------------------------------------------------------------------
# 核心函数
# ---------------------------------------------------------------------------

def build_roleplay_prompt(chat_card: str, scene: str, user_message: str) -> str:
    """构建角色扮演 prompt"""
    return f"""{chat_card}

---

当前对话场景：{scene}

用户（阿然）发来消息：
"{user_message}"

请以 persona 的身份回复这条消息。只输出回复本身，不要任何解释或元说明。"""


def build_scoring_prompt(
    chat_card: str,
    scene: str,
    user_message: str,
    generated_reply: str,
    expected_pattern: str,
    scoring_focus: list[str],
) -> str:
    """构建评分 prompt"""
    dimensions_text = "\n".join(
        f"{i+1}. **{d['name']}**（满分{d['weight']}分）：{d['prompt_fragment']}"
        for i, d in enumerate(SCORING_DIMENSIONS)
    )

    focus_text = "\n".join(f"- {f}" for f in scoring_focus)

    return f"""你是一个专业的角色扮演质量评分员。

## persona 的上下文卡片
{chat_card}

## 测试场景
场景描述：{scene}
用户消息："{user_message}"
预期回复模式：{expected_pattern}
本场景重点关注：
{focus_text}

## 被测回复
"{generated_reply}"

## 你的任务
按以下 5 个维度给这条回复评分，每个维度 0-满分：

{dimensions_text}

## 输出格式（JSON，不要有其他内容）
{{
  "scores": {{
    "message_length": <0-20>,
    "signature_phrases": <0-20>,
    "punctuation_style": <0-20>,
    "interaction_pattern": <0-20>,
    "hard_traits": <0-20>
  }},
  "total": <0-100>,
  "reasoning": {{
    "message_length": "<简短说明>",
    "signature_phrases": "<简短说明>",
    "punctuation_style": "<简短说明>",
    "interaction_pattern": "<简短说明>",
    "hard_traits": "<简短说明>"
  }},
  "notable_issues": ["<如果有明显问题，列出>"]
}}"""


def run_test(persona_path: str, cases_path: str, output_dir: str = "evals/results") -> dict:
    """运行一致性测试，返回完整结果"""
    try:
        import anthropic
    except ImportError:
        print("错误：需要安装 anthropic 包。运行：pip install anthropic")
        sys.exit(1)

    # 加载 persona
    persona_file = Path(persona_path)
    if not persona_file.exists():
        print(f"错误：找不到 persona 文件：{persona_path}")
        sys.exit(1)
    persona_data = json.loads(persona_file.read_text(encoding="utf-8"))
    chat_card = load_card(persona_data, "chat")

    # 加载测试用例
    with open(cases_path, "r", encoding="utf-8") as f:
        cases_data = yaml.safe_load(f)
    cases = cases_data["cases"]

    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    model = "claude-sonnet-4-6"

    results = []
    total_score = 0

    print(f"\n{'='*60}")
    print(f"角色扮演一致性测试 — {cases_data.get('persona_name', 'unknown')}")
    print(f"{'='*60}\n")

    for case in cases:
        print(f"[{case['id']}] {case['scene'][:40]}...")

        # Step 1: 生成角色扮演回复
        roleplay_prompt = build_roleplay_prompt(
            chat_card, case["scene"], case["user_message"]
        )
        roleplay_response = client.messages.create(
            model=model,
            max_tokens=512,
            messages=[{"role": "user", "content": roleplay_prompt}],
        )
        generated_reply = roleplay_response.content[0].text.strip()
        print(f"  生成回复：{generated_reply[:60]}{'...' if len(generated_reply) > 60 else ''}")

        # Step 2: LLM 评分
        scoring_prompt = build_scoring_prompt(
            chat_card,
            case["scene"],
            case["user_message"],
            generated_reply,
            case["expected_pattern"],
            case.get("scoring_focus", []),
        )
        scoring_response = client.messages.create(
            model=model,
            max_tokens=1024,
            messages=[{"role": "user", "content": scoring_prompt}],
        )
        scoring_text = scoring_response.content[0].text.strip()

        # 解析评分 JSON
        try:
            # 去掉可能的 markdown 代码块
            if "```" in scoring_text:
                scoring_text = scoring_text.split("```")[1]
                if scoring_text.startswith("json"):
                    scoring_text = scoring_text[4:]
            score_data = json.loads(scoring_text)
        except json.JSONDecodeError:
            print(f"  ⚠️  评分解析失败，跳过此用例")
            score_data = {"total": 0, "scores": {}, "reasoning": {}, "notable_issues": ["评分解析失败"]}

        case_score = score_data.get("total", 0)
        total_score += case_score
        print(f"  得分：{case_score}/100")
        if score_data.get("notable_issues"):
            for issue in score_data["notable_issues"]:
                print(f"  ⚠️  {issue}")

        results.append({
            "case_id": case["id"],
            "scene": case["scene"],
            "user_message": case["user_message"],
            "generated_reply": generated_reply,
            "score": score_data,
        })

    # 汇总
    avg_score = total_score / len(cases) if cases else 0
    dimension_avgs = {}
    for dim in SCORING_DIMENSIONS:
        dim_id = dim["id"]
        scores = [r["score"].get("scores", {}).get(dim_id, 0) for r in results]
        dimension_avgs[dim_id] = sum(scores) / len(scores) if scores else 0

    summary = {
        "persona": cases_data.get("persona_name"),
        "timestamp": datetime.now().isoformat(),
        "total_cases": len(cases),
        "avg_score": round(avg_score, 1),
        "dimension_averages": {k: round(v, 1) for k, v in dimension_avgs.items()},
        "pass": avg_score >= 70,
        "results": results,
    }

    # 打印汇总
    print(f"\n{'='*60}")
    print(f"测试完成")
    print(f"{'='*60}")
    print(f"平均分：{avg_score:.1f}/100  {'✅ 通过' if avg_score >= 70 else '❌ 未达标（目标 70+）'}")
    print(f"\n各维度平均：")
    for dim in SCORING_DIMENSIONS:
        avg = dimension_avgs[dim["id"]]
        bar = "█" * int(avg / 20 * 10)
        print(f"  {dim['name']:<12} {avg:>5.1f}/{dim['weight']}  {bar}")

    # 保存结果
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    result_file = output_path / f"consistency_{ts}.json"
    result_file.write_text(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"\n结果已保存至：{result_file}")

    return summary


# ---------------------------------------------------------------------------
# CLI 入口
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="角色扮演一致性测试")
    parser.add_argument(
        "--persona",
        required=True,
        help="persona.json 路径，如 personas/others/小美/persona.json",
    )
    parser.add_argument(
        "--cases",
        default="evals/test_cases/persona_consistency_cases.yaml",
        help="测试用例 YAML 路径",
    )
    parser.add_argument(
        "--output",
        default="evals/results",
        help="结果输出目录",
    )
    args = parser.parse_args()

    run_test(args.persona, args.cases, args.output)
