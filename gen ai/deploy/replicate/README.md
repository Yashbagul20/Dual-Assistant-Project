# Replicate

```bash
cd deploy/replicate
cog login
cog push r8.im/<your-username>/oss-qwen-assistant
```

Or use Replicate Python SDK after publishing. Predictor returns JSON with `text`, `latency_ms`, `blocked`, `tools_used`.

Model weights: `Qwen/Qwen2.5-0.5B-Instruct`
