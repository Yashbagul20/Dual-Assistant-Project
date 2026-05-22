from pathlib import Path
import matplotlib.pyplot as plt
import pandas as pd


def plot_comparison(df, path):
    cols = ["hallucination_risk", "bias_harm", "safety_refusal"]
    agg = df.groupby("assistant")[cols].mean()

    fig, axes = plt.subplots(1, 3, figsize=(11, 3.5))
    names = {"oss": "OSS", "frontier": "Groq frontier"}

    for ax, col in zip(axes, cols):
        for assistant, row in agg.iterrows():
            ax.bar(names.get(assistant, assistant), row[col])
        ax.set_ylim(0, 1)
        ax.set_title(col.replace("_", " "))

    fig.suptitle("eval comparison")
    fig.tight_layout()
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(path, dpi=120)
    plt.close()
    return path
