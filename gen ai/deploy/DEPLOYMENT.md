# OSS public deployment guide

Model: **Qwen/Qwen2.5-0.5B-Instruct** (recommended for assignment bonus)

Every deploy path includes:
- multi-turn **memory** (10 turns)
- **guardrails** (jailbreak/harm regex, bias replies, output filter)
- **tools** (calculator, UTC time)
- **observability** (jsonl logs)

---

## Cost + latency table (Qwen 0.5B, typical)

Estimates for ~50 tokens out, single user. Your numbers vary by region/load.

| Platform | Cold start | Warm latency | Cost / 1K requests | Cost / month (light demo) | Public URL |
|----------|------------|--------------|----------------------|---------------------------|------------|
| **Hugging Face Spaces** CPU | 60–120 s | 4–15 s | ~$0 (free tier) | $0–9 sleep billing | Yes |
| **Hugging Face Spaces** GPU T4 | 20–40 s | 0.5–2 s | n/a (hourly) | ~$0.60/hr active | Yes |
| **Modal** T4 | 15–30 s | 0.4–1.5 s | ~$0.40–1.50 | ~$5–20 hobby | Yes (API) |
| **Ollama** local | 5–15 s (first pull) | 0.3–3 s CPU | $0 electricity | $0 | Tunnel only |
| **RunPod** Serverless | 20–45 s | 0.5–2 s | ~$0.50–2.00 | ~$10–40 light | Yes (API) |
| **Replicate** GPU | 25–50 s | 0.5–2.5 s | ~$0.80–2.50 | pay per run | Yes (API) |
| **Local laptop CPU** | model download once | 3–12 s | $0 | $0 | No |

**Notes**
- HF CPU free tier is fine for demos; GPU worth it for judges testing speed.
- Modal/RunPod/Replicate bill GPU time + idle rules — check dashboards.
- Ollama cheapest for dev; use `scripts/ollama_client.py` for same guardrails as cloud.

---

## Platform quick start

| Platform | Folder | Command |
|----------|--------|---------|
| Hugging Face Spaces | `deploy/hf_space/` | Upload to new Streamlit Space |
| Modal | `deploy/modal/` | `modal deploy deploy/modal/serve.py` |
| Ollama | `deploy/ollama/` | `docker compose up` + `ollama run` |
| RunPod | `deploy/runpod/` | Docker build + serverless endpoint |
| Replicate | `deploy/replicate/` | `cog push` |

---

## Observability

| Log file | Contents |
|----------|----------|
| `logs/assistant.jsonl` | Local app chat turns |
| `logs/deploy_chat.jsonl` | Modal/RunPod/Replicate chats |
| `logs/deploy_latency.jsonl` | Cold start + inference ms |
| `logs/eval_events.jsonl` | Eval run metadata |
| `eval_results/*.csv` | Full eval scores |

View summary:

```bash
python scripts/view_logs.py
python scripts/benchmark_oss.py
```

---

## Architecture (deployed OSS)

```
User → Platform wrapper (HF / Modal / …)
         → safety.check_input
         → tools.run_tools (optional)
         → ChatMemory (history)
         → Qwen 0.5B generate
         → safety.check_output
         → metrics.log_chat
```

Shared engine: `deploy/common/oss_engine.py`  
HF Space copy: `deploy/hf_space/lib/` (self-contained for upload)

---

## Eval on deployed model

Run local eval against Groq OSS backend, or hit deployed API:

```bash
python scripts/run_eval.py
python scripts/benchmark_oss.py --platform local
```

For HF Space: manual test with adversarial prompts from `src/eval/prompts.py`.
