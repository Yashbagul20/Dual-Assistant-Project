# Modal

```bash
pip install modal
modal token new
modal deploy deploy/modal/serve.py
```

Call the endpoint from Modal dashboard or:

```python
import modal
fn = modal.Cls.lookup("oss-qwen-assistant", "QwenOSS")
print(fn().chat.remote("what is 2+2"))
```

Uses GPU T4. Includes memory, guardrails, tools via `deploy/common/oss_engine.py`.
