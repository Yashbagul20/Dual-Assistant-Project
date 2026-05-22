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
st.write("assignment demo — streamlit UI, shared memory + basic safety filters")

tab1, tab2, tab3 = st.tabs(["chat", "eval", "deploy notes"])


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
    st.write("runs 9 fixed prompts on both bots, saves csv + chart to eval_results/")
    use_judge = st.checkbox("use groq as judge", value=True)
    if st.button("run eval"):
        try:
            oss = OSSAssistant()
            fr = FrontierAssistant()
        except ValueError as err:
            st.error(str(err))
            st.stop()
        with st.spinner("this takes a minute..."):
            df = run_evaluation(oss, fr, root / "eval_results", use_llm_judge=use_judge)
            chart = plot_comparison(df, root / "eval_results" / "comparison_chart.png")
        st.success("done")
        st.dataframe(df, use_container_width=True)
        st.image(str(chart))
        st.download_button("csv", df.to_csv(index=False), "results.csv")

with tab3:
    st.markdown("""
**OSS hosting options** (from assignment bonus section)

| where | speed | cost |
|-------|-------|------|
| local qwen | slow on cpu | free |
| groq llama 3.1 | fast | free tier |
| hf space | medium | ~free tier |

logs go to `logs/assistant.jsonl` if you need to debug weird replies.
    """)
