# RunPod Serverless

1. Build image from repo root: `docker build -f deploy/runpod/Dockerfile -t oss-qwen .`
2. Push to registry, create Serverless endpoint on RunPod
3. POST input: `{"input": {"message": "hi", "session_id": "user1"}}`

Per-session memory via `session_id`. Guardrails + tools included in handler.

See cost table in `../DEPLOYMENT.md`.
