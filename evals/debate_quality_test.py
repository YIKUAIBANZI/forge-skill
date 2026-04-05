"""
辩论质量测试 (Debate Quality Test)

对 use-self 替身会议进行自动评测：给定 persona + 3 个决策场景，
模拟完整三阶段辩论流程（Phase 1 独立分析 → Phase 2 质询 → Phase 3 综合），
用 Claude 按 5 个维度评分。

用法：
    python evals/debate_quality_test.py --persona personas/self/阿然/persona.json
    python evals/debate_quality_test.py --persona personas/self/阿然/persona.json --cases evals/test_cases/debate_quality_cases.yaml
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
# 评分维度
# ---------------------------------------------------------------------------

SCORING_DIMENSIONS = [
    {
        "id": "variant_differentiation",
        "name": "变体区分度",
        "weight": 20,
        "prompt_fragment": (
            "Phase 1 的各变体立场是否有实质性差异？"
            "如果所有变体都说'两边各有优缺点'，得 0 分。"
            "如果每个变体有明确不同的立场且理由具体，得满分。"
        ),
    },
    {
        "id": "challenge_depth",
        "name": "质询深度",
        "weight": 20,
        "prompt_fragment": (
            "Phase 2 的质询是否指出了具体的假设和盲区？"
            "泛泛的'你没考虑到...'得低分。"
            "能具体指出'你说的X假设了Y，但Y并不成立，因为Z'得高分。"
        ),
    },
    {
        "id": "param_consistency",
        "name": "参数一致性",
        "weight": 20,
        "prompt_fragment": (
            "各变体的发言是否与其偏移后的参数一致？"
            "比如'稳健的你'风险偏好应该明显低，如果它的发言和'冒险的你'一样激进，应扣分。"
        ),
    },
    {
        "id": "synthesis_coverage",
        "name": "综合覆盖度",
        "weight": 20,
        "prompt_fragment": (
            "Phase 3 是否涵盖了所有关键分歧？"
            "代价清单是否具体？是否提出了做决定前需要搞清楚的具体问题？"
            "如果综合只是 Phase 1 的复述，应扣分。"
        ),
    },
    {
        "id": "language_style",
        "name": "用户语言风格",
        "weight": 20,
        "prompt_fragment": (
            "所有输出（Phase 1/2/3）的语气和用词是否符合 persona 的 L2 语言风格？"
            "替身说话要像用户，不像顾问。出现'综上所述'、'建议您'等顾问句式应扣分。"
        ),
    },
]


# ---------------------------------------------------------------------------
# 模拟各阶段 prompt
# ---------------------------------------------------------------------------

def build_phase1_prompt(decision_card: str, scenario: str, variant_params: dict) -> str:
    """构建 Phase 1 单变体 prompt（简化版，用于评测）"""
    shifts_text = "\n".join(
        f"  - {k}：基础值 ±{v:+d}（{'更高' if v > 0 else '更低'}）"
        for k, v in variant_params.get("shifts", {}).items()
    )
    return f"""你是用户本人的一个版本。

## 你的人格底座（决策相关部分）
{decision_card}

## 你这个变体的参数偏移
名称：{variant_params['name']} —— {variant_params['tagline']}
参数调整：
{shifts_text}

## 当前决策场景
{scenario}

---

基于你的参数倾向，**独立**分析这个决策。用第一人称"我"，用用户自己的语言风格。

输出格式：
【我的判断】
（一句话，明确表态，不能说"两边都有道理"）

【为什么】
（不超过 3 个具体理由，贴合这个处境，不讲大道理）

【我最担心的是】
（具体的最坏情况）

【我最期待的是】
（具体的最好结果）

【我想问自己】
（一个没想清楚这个这个决定就是悬空的问题）"""


def build_phase2_prompt(decision_card: str, phase1_outputs: list[dict], blind_spots: list) -> str:
    """构建 Phase 2 质询 prompt"""
    variants_text = "\n\n".join(
        f"### {v['name']}\n{v['output']}"
        for v in phase1_outputs
    )
    blind_text = "\n".join(f"- {b}" for b in blind_spots) if blind_spots else "（暂无记录）"

    return f"""你是一个质询者。找出每个变体观点里藏着的问题。

## 用户已知盲区
{blind_text}

## 所有变体的 Phase 1 输出
{variants_text}

---

### Step 1：为每个变体找出最尖锐的质疑
对每个变体：它的判断建立在什么**隐含假设**上？它说的担忧/期待是真实的还是幻觉？

### Step 2：识别跨变体矛盾
如果两个变体的前提相互冲突，点出来。

### Step 3：用已知盲区做最后一击
从盲区列表里找最相关的一条，直接点。

输出格式：
## 质询报告

### 对 [变体名] 的质疑
（具体的尖锐质疑，落地到这个具体决策）

...（每个变体都要有）

### 跨变体矛盾
（如果有，列出）

### 盲区质询
（基于已知盲区的最后一问）"""


def build_phase3_scoring_prompt(
    decision_card: str,
    scenario: str,
    phase1_outputs: list[dict],
    phase2_output: str,
    phase3_output: str,
    expected_stances: list[str],
    evaluation_criteria: dict,
) -> str:
    """构建 Phase 3 质量评分 prompt"""
    variants_summary = "\n".join(
        f"- {v['name']}：{v['output'][:200]}..."
        for v in phase1_outputs
    )
    expected_text = "\n".join(f"- {s}" for s in expected_stances)
    criteria_text = json.dumps(evaluation_criteria, ensure_ascii=False, indent=2)

    dimensions_text = "\n".join(
        f"{i+1}. **{d['name']}**（满分{d['weight']}分）：{d['prompt_fragment']}"
        for i, d in enumerate(SCORING_DIMENSIONS)
    )

    return f"""你是一个替身会议质量评分员。

## 用户的决策 persona（关键部分）
{decision_card}

## 决策场景
{scenario}

## Phase 1 输出摘要
{variants_summary}

## Phase 2 质询输出
{phase2_output[:1000]}

## Phase 3 综合输出
{phase3_output[:1500]}

## 预期各变体立场
{expected_text}

## 本场景评估标准
{criteria_text}

---

按以下 5 个维度评分：

{dimensions_text}

## 输出格式（JSON，不要有其他内容）
{{
  "scores": {{
    "variant_differentiation": <0-20>,
    "challenge_depth": <0-20>,
    "param_consistency": <0-20>,
    "synthesis_coverage": <0-20>,
    "language_style": <0-20>
  }},
  "total": <0-100>,
  "reasoning": {{
    "variant_differentiation": "<简短说明>",
    "challenge_depth": "<简短说明>",
    "param_consistency": "<简短说明>",
    "synthesis_coverage": "<简短说明>",
    "language_style": "<简短说明>"
  }},
  "notable_issues": ["<主要问题>"],
  "notable_strengths": ["<做得好的地方>"]
}}"""


# ---------------------------------------------------------------------------
# 辩论流程模拟
# ---------------------------------------------------------------------------

def simulate_debate(client, model: str, decision_card: str, scenario: str, blind_spots: list) -> dict:
    """模拟三阶段辩论，返回各阶段输出"""

    # 生成固定的 3 个变体参数（评测用，不动态生成）
    variant_configs = [
        {
            "name": "稳健的你",
            "tagline": "先确保不输，再想怎么赢",
            "shifts": {"risk_appetite": -3, "action_bias": -2, "loss_aversion": 2},
        },
        {
            "name": "果断的你",
            "tagline": "窗口期有限，想太多不如先干",
            "shifts": {"risk_appetite": 3, "action_bias": 3, "information_need": -2},
        },
        {
            "name": "长线的你",
            "tagline": "三年后的你会希望今天怎么选",
            "shifts": {"time_horizon": 4, "loss_aversion": -2, "action_bias": 1},
        },
    ]

    # Phase 1：并行（串行模拟）
    phase1_outputs = []
    for variant in variant_configs:
        prompt = build_phase1_prompt(decision_card, scenario, variant)
        resp = client.messages.create(
            model=model,
            max_tokens=600,
            messages=[{"role": "user", "content": prompt}],
        )
        phase1_outputs.append({
            "name": variant["name"],
            "output": resp.content[0].text.strip(),
        })

    # Phase 2：质询
    phase2_prompt = build_phase2_prompt(decision_card, phase1_outputs, blind_spots)
    phase2_resp = client.messages.create(
        model=model,
        max_tokens=800,
        messages=[{"role": "user", "content": phase2_prompt}],
    )
    phase2_output = phase2_resp.content[0].text.strip()

    # Phase 3：综合（简化版，直接让模型基于前两阶段输出综合）
    phase3_prompt = f"""{decision_card}

你收到了所有替身的分析和质询报告。

## 各替身发言（Phase 1）
{chr(10).join(f'### {v["name"]}{chr(10)}{v["output"]}' for v in phase1_outputs)}

## 质询报告（Phase 2）
{phase2_output}

---

现在生成综合报告。用用户自己的语言风格（来自上面的 decision-card）。

包含：
1. 立场分布（各变体倾向哪边）
2. 共识区（所有变体都同意的点）
3. 核心分歧（背后是什么取舍）
4. 代价清单（选A需要接受什么，选B需要接受什么）
5. 做决定前先想清楚这几件事（基于质询点）
6. 一个观察（不是建议，是一个你可能忽略了的东西）

不说"你应该"，不给最优解。"""

    phase3_resp = client.messages.create(
        model=model,
        max_tokens=1200,
        messages=[{"role": "user", "content": phase3_prompt}],
    )
    phase3_output = phase3_resp.content[0].text.strip()

    return {
        "phase1": phase1_outputs,
        "phase2": phase2_output,
        "phase3": phase3_output,
    }


# ---------------------------------------------------------------------------
# 核心函数
# ---------------------------------------------------------------------------

def run_test(persona_path: str, cases_path: str, output_dir: str = "evals/results") -> dict:
    """运行辩论质量测试"""
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
    decision_card = load_card(persona_data, "decision")

    # 提取盲区
    l4 = persona_data.get("L4_values", {})
    blind_spots = [b.get("trait", "") for b in l4.get("blind_spots", [])]

    # 加载测试用例
    with open(cases_path, "r", encoding="utf-8") as f:
        cases_data = yaml.safe_load(f)
    cases = cases_data["cases"]

    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    model = "claude-sonnet-4-6"

    results = []
    total_score = 0

    print(f"\n{'='*60}")
    print(f"辩论质量测试 — {cases_data.get('persona_name', 'unknown')}")
    print(f"{'='*60}\n")

    for case in cases:
        print(f"\n[{case['id']}] {case['title']}")
        print(f"  运行三阶段辩论...")

        # 模拟辩论
        debate_result = simulate_debate(
            client, model, decision_card, case["scenario"], blind_spots
        )

        print(f"  Phase 1 完成（{len(debate_result['phase1'])} 个变体）")
        print(f"  Phase 2 完成（质询报告）")
        print(f"  Phase 3 完成（综合报告）")
        print(f"  评分中...")

        # 评分
        scoring_prompt = build_phase3_scoring_prompt(
            decision_card,
            case["scenario"],
            debate_result["phase1"],
            debate_result["phase2"],
            debate_result["phase3"],
            case.get("expected_variant_stances", []),
            case.get("evaluation_criteria", {}),
        )
        scoring_resp = client.messages.create(
            model=model,
            max_tokens=1024,
            messages=[{"role": "user", "content": scoring_prompt}],
        )
        scoring_text = scoring_resp.content[0].text.strip()

        try:
            if "```" in scoring_text:
                scoring_text = scoring_text.split("```")[1]
                if scoring_text.startswith("json"):
                    scoring_text = scoring_text[4:]
            score_data = json.loads(scoring_text)
        except json.JSONDecodeError:
            print(f"  ⚠️  评分解析失败")
            score_data = {"total": 0, "scores": {}, "reasoning": {}, "notable_issues": ["评分解析失败"]}

        case_score = score_data.get("total", 0)
        total_score += case_score
        print(f"  得分：{case_score}/100")

        for strength in score_data.get("notable_strengths", []):
            print(f"  ✅ {strength}")
        for issue in score_data.get("notable_issues", []):
            print(f"  ⚠️  {issue}")

        results.append({
            "case_id": case["id"],
            "title": case["title"],
            "debate": debate_result,
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
        "baseline": True,  # 首次运行标记为基线
        "results": results,
    }

    # 打印汇总
    print(f"\n{'='*60}")
    print(f"测试完成")
    print(f"{'='*60}")
    print(f"平均分：{avg_score:.1f}/100")
    print(f"\n各维度平均：")
    for dim in SCORING_DIMENSIONS:
        avg = dimension_avgs[dim["id"]]
        bar = "█" * int(avg / 20 * 10)
        print(f"  {dim['name']:<12} {avg:>5.1f}/{dim['weight']}  {bar}")

    # 保存结果
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    result_file = output_path / f"debate_{ts}.json"
    result_file.write_text(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"\n结果已保存至：{result_file}")
    print("（首次运行已标记为基线数据，后续优化可对比）")

    return summary


# ---------------------------------------------------------------------------
# CLI 入口
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="辩论质量测试")
    parser.add_argument(
        "--persona",
        required=True,
        help="persona.json 路径，如 personas/self/阿然/persona.json",
    )
    parser.add_argument(
        "--cases",
        default="evals/test_cases/debate_quality_cases.yaml",
        help="测试用例 YAML 路径",
    )
    parser.add_argument(
        "--output",
        default="evals/results",
        help="结果输出目录",
    )
    args = parser.parse_args()

    run_test(args.persona, args.cases, args.output)
