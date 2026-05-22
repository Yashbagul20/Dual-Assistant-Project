# minimal HF space for qwen — upload this folder as streamlit space
import os
import time
import streamlit as st
from transformers import pipeline

MODEL = os.getenv("OSS_MODEL_ID", "Qwen/Qwen2.5-0.5B-Instruct")

st.title("OSS chatbot")
st.caption(MODEL)

@st.cache_resource
def get_pipe():
    return pipeline("text-generation", model=MODEL, device_map="auto")

if "hist" not in st.session_state:
    st.session_state.hist = []

pipe = get_pipe()

for h in st.session_state.hist:
    with st.chat_message(h["role"]):
        st.write(h["text"])

if p := st.chat_input("message"):
    st.session_state.hist.append({"role": "user", "text": p})
    ctx = "\n".join(f"{x['role']}: {x['text']}" for x in st.session_state.hist[-6:])
    prompt = f"System: helpful assistant.\n{ctx}\nassistant:"
    t0 = time.perf_counter()
    out = pipe(prompt, max_new_tokens=180, do_sample=True, temperature=0.7, return_full_text=False)
    reply = out[0]["generated_text"].strip()
    st.session_state.hist.append({"role": "assistant", "text": reply})
    with st.chat_message("assistant"):
        st.write(reply)
        st.caption(f"{(time.perf_counter()-t0)*1000:.0f} ms")
