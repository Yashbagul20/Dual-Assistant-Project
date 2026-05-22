# run from project root: python scripts/run_eval.py
import sys
from pathlib import Path

from dotenv import load_dotenv

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root))
load_dotenv(root / ".env")

from src.assistants.frontier_assistant import FrontierAssistant
from src.assistants.oss_assistant import OSSAssistant
from src.eval.runner import run_evaluation
from src.eval.visualize import plot_comparison

if __name__ == "__main__":
    print("starting eval...")
    df = run_evaluation(OSSAssistant(), FrontierAssistant(), root / "eval_results")
    plot_comparison(df, root / "eval_results" / "comparison_chart.png")
    print(df.groupby("assistant")[["hallucination_risk", "bias_harm", "safety_refusal"]].mean())
    print("wrote files under eval_results/")
