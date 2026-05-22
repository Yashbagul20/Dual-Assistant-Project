FROM runpod/pytorch:2.1.0-py3.10-cuda11.8.0-devel-ubuntu22.04

WORKDIR /app
COPY deploy/runpod/handler.py /app/handler.py
COPY deploy/common /app/deploy/common

RUN pip install --no-cache-dir runpod transformers accelerate torch sentencepiece

ENV OSS_MODEL_ID=Qwen/Qwen2.5-0.5B-Instruct
CMD python -u handler.py
