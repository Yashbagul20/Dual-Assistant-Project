# Public OSS deploy — Hugging Face Spaces (Streamlit)
# Upload this whole hf_space folder. Model: Qwen2.5-0.5B-Instruct
import os
import streamlit as st

from lib.oss_engine import OSSChatEngine

MODEL = os.getenv("OSS_MODEL_ID", "Qwen/Qwen2.5-0.5B-Instruct")

st.set_page_config(page_title="OSS Assistant", layout="centered")
st.title("Open Source Personal Assistant")
st.caption(f"Model: {MODEL} · memory · guardrails · tools (calc/time)")

st.markdown(
    "Try: `what time is it` · `calculate 15 * 4` · normal chat. "
    "Jailbreak prompts should get blocked."
)

if "engine" not in st.session_state:
    st.session_state.engine = OSSChatEngine(MODEL, max_turns=10)
if "ui_msgs" not in st.session_state:
    st.session_state.ui_msgs = []

engine = st.session_state.engine

for m in st.session_state.ui_msgs:
    with st.chat_message(m["role"]):
        st.write(m["content"])
        if m.get("meta"):
            st.caption(m["meta"])

if prompt := st.chat_input("Message"):
    st.session_state.ui_msgs.append({"role": "user", "content": prompt})
    with st.spinner("generating..."):
        text, ms, blocked, tool = engine.chat(prompt)
    meta = f"{ms:.0f} ms"
    if blocked:
        meta += " · safety block"
    if tool:
        meta += " · tool used"
    st.session_state.ui_msgs.append({"role": "assistant", "content": text, "meta": meta})
    st.rerun()

if st.button("clear chat"):
    engine.memory.clear()
    st.session_state.ui_msgs = []
    st.rerun()

with st.expander("features on this deployment"):
    st.markdown("""
- **Memory:** last 10 turns  
- **Guardrails:** regex jailbreak/harm + bias canned replies  
- **Tools:** calculator, UTC time  
- **Observability:** logs under `/tmp/oss_logs/chat.jsonl` on the Space container  
    """)
