import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path

import pandas as pd

from src.eval.judge import heuristic_scores, llm_judge
from src.eval.prompts import EVAL_PROMPTS


@dataclass
class EvalRow:
    assistant: str
    prompt_id: str
    category: str
    prompt: str
    response: str
    blocked: bool
    latency_ms: float
    hallucination_risk: float
    bias_harm: float
    safety_refusal: float
    judge_notes: str


def run_evaluation(oss, frontier, output_dir: Path, use_llm_judge=True):
    output_dir.mkdir(parents=True, exist_ok=True)
    rows = []

    for label, bot in [("oss", oss), ("frontier", frontier)]:
        bot.reset()
        for p in EVAL_PROMPTS:
            resp = bot.chat(p.text)
            scores = llm_judge(p, resp.text, resp.blocked) if use_llm_judge else heuristic_scores(p, resp.text, resp.blocked)
            rows.append(EvalRow(
                label, p.id, p.category, p.text, resp.text, resp.blocked, resp.latency_ms,
                scores.hallucination_risk, scores.bias_harm, scores.safety_refusal, scores.notes,
            ))

    df = pd.DataFrame([asdict(r) for r in rows])
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    df.to_csv(output_dir / f"eval_results_{stamp}.csv", index=False)

    summary = {"at": datetime.now(timezone.utc).isoformat(), "assistants": {}}
    for name, g in df.groupby("assistant"):
        summary["assistants"][name] = {
            "hallucination": round(g.hallucination_risk.mean(), 3),
            "bias": round(g.bias_harm.mean(), 3),
            "safety": round(g.safety_refusal.mean(), 3),
            "latency_ms": round(g.latency_ms.mean(), 1),
        }
    (output_dir / f"eval_summary_{stamp}.json").write_text(json.dumps(summary, indent=2))
    return df
