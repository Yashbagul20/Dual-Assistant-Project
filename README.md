### Things I’d improve next

1. **Real moderation layer**  
   Right now the safety checks are still pretty lightweight. I’d replace most of the regex-based filtering with something stronger like Llama Guard or a hosted moderation API so the assistants can better detect harmful or unsafe prompts.

2. **Add RAG for factual answers**  
   Smaller open-source models sometimes hallucinate on factual questions. Adding a Retrieval-Augmented Generation (RAG) pipeline with a small document store would help ground responses in real sources instead of relying only on model memory.

3. **Cleaner tool calling system**  
   The current version uses simple intent checks (for example, detecting keywords like “calculate”). A better setup would be proper function/tool calling so the assistants can reliably trigger calculators, search tools, or external APIs.

4. **Larger evaluation benchmark**  
   The evaluation set is still small. Next step would be running a broader benchmark using slices from TruthfulQA, toxicity/harm datasets, and storing all experiment runs in SQLite for easier comparison and tracking.

5. **Public OSS deployment**  
   I started setting up deployment in `deploy/hf_space/`, but it still needs cleanup. I’d like to finish the Hugging Face Space deployment with proper cold-start handling, usage notes, and a simple cost/performance comparison table.

6. **Separate judge model**  
   Using the same provider for both generation and evaluation can introduce bias. A better approach would be evaluating with a different model/provider to make scoring more balanced.

7. **Add automated tests**  
   The project could use proper pytest coverage for guardrails, prompt formatting, and a few fixed “golden” evaluation examples so future refactors don’t accidentally break scores.

---

### Notes from development

Some additional implementation notes, failed experiments, and debugging observations are written in `NOTES.txt`.

---

## Evaluation Report

A short summary report with charts and comparison results is available in:

`EVALUATION_REPORT.md`

---

## Repository Structure

| Path | Purpose |
|------|---------|
| `app/streamlit_app.py` | Main demo application |
| `scripts/run_eval.py` | Evaluation runner script |
| `eval_results/` | Stores CSV results, JSON summaries, and generated charts |
| `deploy/hf_space/` | Hugging Face Space deployment files |
| `.env.example` | Environment variable template |

---

## Security Notes

- API keys are stored through environment variables only.
- `.env` is excluded using `.gitignore`.
- If a key is accidentally exposed (screenshots, commits, chats, etc.), rotate it immediately.
