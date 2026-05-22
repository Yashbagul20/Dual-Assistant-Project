# Hugging Face Spaces deploy

1. Create Space → **Streamlit** SDK  
2. Upload files from this folder (`app.py`, `lib/`, `requirements.txt`)  
3. Hardware: **CPU basic** (free, slow) or **GPU** (faster, may cost)  
4. Optional secret: `OSS_MODEL_ID` (default `Qwen/Qwen2.5-0.5B-Instruct`)

First visitor waits for model download (~1GB). Public URL looks like:  
`https://huggingface.co/spaces/<user>/<space-name>`

See `../DEPLOYMENT.md` for cost/latency table.
