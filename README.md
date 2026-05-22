# Dual AI Personal Assistants

Build-and-evaluate project comparing an **open-source** assistant (Hugging Face / Qwen 2.5) with a **frontier** assistant (Groq — Llama 3.3 70B).

## Features

| Capability | OSS Assistant | Frontier Assistant |
|------------|---------------|-------------------|
| Model | `Qwen/Qwen2.5-0.5B-Instruct` | `llama-3.3-70b-versatile` (configurable) |
| Multi-turn chat | Yes | Yes |
| Short-term memory | 10-turn rolling window | 10-turn rolling window |
| Guardrails | Input/output regex filters, bias templates | Same shared layer |
| Tools | Calculator, UTC time | Calculator, UTC time |
| Observability | JSONL logs in `logs/` | JSONL logs in `logs/` |
| Evaluation | 9-prompt suite + LLM-as-judge | Same |

## Quick start

### 1. Prerequisites

- Python 3.10+
- (Optional) NVIDIA GPU for faster local OSS inference
- Groq API key for frontier assistant and LLM-as-judge

### 2. Install

```bash
cd "gen ai"
python -m venv .venv
.venv\Scripts\activate          # Windows
pip install -r requirements.txt
```

### 3. Configure secrets

```bash
copy .env.example .env
```

Edit `.env`:

```env
GROQ_API_KEY=gsk_your-key
GROQ_MODEL=llama-3.3-70b-versatile
OSS_MODEL_ID=Qwen/Qwen2.5-0.5B-Instruct
USE_HF_INFERENCE=false
```

**OSS backends** (set `OSS_BACKEND` in `.env`):

| Backend | When to use |
|---------|-------------|
| `groq` (default) | Fast; uses open-weight `llama-3.1-8b-instant` via your Groq key |
| `local` | Run `Qwen/Qwen2.5-0.5B-Instruct` on your machine (needs `torch`) |
| `hf` | HF Inference API — **Qwen 0.5B is not supported**; use fallback models only |

> `Qwen/Qwen2.5-0.5B-Instruct` is not hosted on Hugging Face serverless Inference. Use `OSS_BACKEND=groq` or `local`.

### 4. Run the app

```bash
streamlit run app/streamlit_app.py
```

Open **Chat** for side-by-side assistants, **Evaluation** to run the benchmark, **Deployment & Cost** for OSS hosting notes.

### 5. Run evaluation (CLI)

```bash
python scripts/run_eval.py
```

Outputs: `eval_results/eval_results_*.csv`, `eval_summary_*.json`, `comparison_chart.png`.

## Architecture

```
app/streamlit_app.py          # UI
src/assistants/
  base.py                     # Shared interface + system prompt
  oss_assistant.py            # HF local or Inference API
  frontier_assistant.py       # Groq API (Llama 3.3)
src/memory/conversation_memory.py
src/guardrails/safety.py      # Jailbreak / harm / bias probes
src/tools/builtin_tools.py    # Calculator, time
src/eval/                     # Prompts, judge, runner, charts
src/observability/logger.py   # JSONL turn logs
deploy/hf_space/              # Public OSS deployment template
```

**Design choices**

- **Shared guardrails** so comparison isolates model quality, not different safety stacks.
- **Same system prompt and memory** for fair behavioral comparison.
- **LLM-as-judge** (GPT) with heuristic fallback when API unavailable.
- **0.5B Qwen** for OSS: runs on CPU, deployable on free HF Spaces; tradeoff is weaker reasoning vs frontier.

## Tradeoffs

| Decision | Benefit | Cost |
|----------|---------|------|
| Qwen2.5-0.5B vs 7B+ | Fast, cheap, HF Spaces friendly | Higher hallucination on hard facts |
| Regex guardrails | Fast, deterministic blocks | Not robust to novel jailbreaks |
| LLM-as-judge | Nuanced safety scoring | Extra API cost; judge bias |
| Streamlit | Rapid demo | Not production auth/scaling |

## What we'd improve with more time

- **Neural guardrails** (Llama Guard, OpenAI Moderation API)
- **RAG** for factual prompts to cut hallucinations on OSS
- **Proper tool calling** (JSON schema / function API) instead of regex triggers
- **Persistent memory** (vector DB) beyond 10 turns
- **Automated CI eval** on every model/prompt change
- **Production deploy** (FastAPI + auth) and W&B / Langfuse tracing

## Bonus: public OSS deploy

See [`deploy/hf_space/README.md`](deploy/hf_space/README.md). Upload `deploy/hf_space/` to a Hugging Face Streamlit Space.

## Security

Never commit `.env` or API keys. Rotate keys if exposed. The repo includes `.gitignore` for `.env`.

## Deliverables checklist

- [x] Complete source code
- [x] README (setup, architecture, tradeoffs, improvements)
- [x] [`EVALUATION_REPORT.md`](EVALUATION_REPORT.md) — 1-page comparison + recommendations
- [x] Optional demo: run Streamlit locally or deploy HF Space
- [x] Bonus: HF Space template, cost/latency table, observability, guardrails, memory, tools

## License

MIT — template models subject to their respective licenses (Qwen, OpenAI terms).
