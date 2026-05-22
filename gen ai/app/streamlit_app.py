import sys
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(root))
load_dotenv(root / ".env")

from src.assistants.frontier_assistant import FrontierAssistant
from src.assistants.oss_assistant import OSSAssistant
from src.eval.runner import run_evaluation
from src.eval.visualize import plot_comparison

st.set_page_config(page_title="assistant compare", layout="wide")
st.title("OSS vs frontier assistants")
st.write("assignment demo — memory, guardrails, tools, evals, public OSS deploy configs")

tab1, tab2, tab3 = st.tabs(["chat", "eval", "OSS deploy"])


@st.cache_resource
def load_oss():
    return OSSAssistant()


@st.cache_resource
def load_frontier():
    return FrontierAssistant()


def chat_panel(title, key, factory):
    st.subheader(title)
    if key not in st.session_state:
        st.session_state[key] = {"msgs": [], "bot": factory()}

    box = st.session_state[key]
    bot = box["bot"]

    for m in box["msgs"]:
        with st.chat_message(m["role"]):
            st.write(m["text"])

    if q := st.chat_input("ask " + title, key="in_" + key):
        box["msgs"].append({"role": "user", "text": q})
        with st.chat_message("user"):
            st.write(q)
        with st.spinner("..."):
            ans = bot.chat(q)
        box["msgs"].append({"role": "assistant", "text": ans.text})
        with st.chat_message("assistant"):
            st.write(ans.text)
            extra = f"{ans.latency_ms:.0f}ms · {ans.model_id}"
            if ans.blocked:
                extra += " · blocked"
            st.caption(extra)

    if st.button("clear", key="clr_" + key):
        bot.reset()
        box["msgs"] = []
        st.rerun()


with tab1:
    c1, c2 = st.columns(2)
    with c1:
        chat_panel("OSS side", "oss", load_oss)
    with c2:
        try:
            chat_panel("frontier (groq)", "frontier", load_frontier)
        except ValueError as err:
            st.error(str(err))
            st.caption("put GROQ_API_KEY in .env")

with tab2:
    st.write("9 prompts (factual / jailbreak / bias). logs → `logs/eval_events.jsonl`")
    use_judge = st.checkbox("use groq as judge", value=True)
    if st.button("run eval"):
        try:
            oss = OSSAssistant()
            fr = FrontierAssistant()
        except ValueError as err:
            st.error(str(err))
            st.stop()
        with st.spinner("running..."):
            df = run_evaluation(oss, fr, root / "eval_results", use_llm_judge=use_judge)
            chart = plot_comparison(df, root / "eval_results" / "comparison_chart.png")
        st.success("done")
        st.dataframe(df, use_container_width=True)
        st.image(str(chart))
        st.download_button("csv", df.to_csv(index=False), "results.csv")

with tab3:
    st.markdown("### Public OSS deploy (Qwen2.5-0.5B)")
    st.markdown("Full guide: **`deploy/DEPLOYMENT.md`**")

    st.markdown("""
| Platform | Cold start | Warm latency | ~Cost / 1K req | Public |
|----------|------------|--------------|----------------|--------|
| HF Spaces CPU | 60–120s | 4–15s | $0 free tier | Yes |
| HF Spaces GPU | 20–40s | 0.5–2s | hourly | Yes |
| Modal T4 | 15–30s | 0.4–1.5s | $0.40–1.50 | API |
| Ollama local | 5–15s | 0.3–3s | $0 | tunnel |
| RunPod | 20–45s | 0.5–2s | $0.50–2.00 | API |
| Replicate | 25–50s | 0.5–2.5s | $0.80–2.50 | API |
    """)

    st.markdown("""
**Included on every deploy:** memory (10 turns) · guardrails · tools (calc/time) · jsonl observability

| Folder | Use |
|--------|-----|
| `deploy/hf_space/` | Upload to Hugging Face Space |
| `deploy/modal/` | `modal deploy` |
| `deploy/ollama/` | Docker + Modelfile |
| `deploy/runpod/` | Serverless handler |
| `deploy/replicate/` | `cog push` |

```bash
python scripts/benchmark_oss.py
python scripts/view_logs.py
```
    """)
