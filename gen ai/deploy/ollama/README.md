# Ollama (local public via tunnel)

```bash
# start server
docker compose -f deploy/ollama/docker-compose.yml up -d

# pull + create model
ollama pull qwen2.5:0.5b-instruct
ollama create qwen-assistant -f deploy/ollama/Modelfile

# chat
ollama run qwen-assistant
```

Use our wrapper with guardrails + memory + tools:

```bash
python scripts/ollama_client.py
```

Expose publicly with ngrok/cloudflare tunnel on port 11434 if needed for demo.
