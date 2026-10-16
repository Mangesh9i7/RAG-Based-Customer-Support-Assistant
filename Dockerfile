# ==========================================
# Stage 1: Build the React Frontend
# ==========================================
FROM node:20-alpine AS frontend-builder
WORKDIR /app/client

# Install dependencies
COPY client/package*.json ./
RUN npm ci

# Copy frontend source and build
COPY client/ ./
RUN npm run build

# ==========================================
# Stage 2: Build the FastAPI Backend & Serve
# ==========================================
FROM python:3.10-slim
WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    OMP_NUM_THREADS=1 \
    OPENBLAS_NUM_THREADS=1 \
    MKL_NUM_THREADS=1 \
    TOKENIZERS_PARALLELISM=false \
    EMBEDDING_MODEL_PATH=/opt/models/all-MiniLM-L6-v2

# Install Python requirements
COPY RAG_Backend/requirements.txt ./RAG_Backend/
RUN pip install --no-cache-dir -r RAG_Backend/requirements.txt
RUN python -c "from huggingface_hub import snapshot_download; snapshot_download(repo_id='sentence-transformers/all-MiniLM-L6-v2', revision='1110a243fdf4706b3f48f1d95db1a4f5529b4d41', local_dir='/opt/models/all-MiniLM-L6-v2', allow_patterns=['onnx/model.onnx', 'config.json', 'tokenizer.json', 'tokenizer_config.json', 'special_tokens_map.json'])"

# Copy Backend source code
COPY RAG_Backend/ ./RAG_Backend/

# Copy the built React assets from Stage 1 into the folder api.py expects
COPY --from=frontend-builder /app/client/dist ./client/dist

# Switch to backend directory so relative paths in Python work correctly
WORKDIR /app/RAG_Backend

# Render dynamically assigns a PORT environment variable (default 10000)
EXPOSE 10000

CMD ["sh", "-c", "exec uvicorn src.api:api --host 0.0.0.0 --port ${PORT:-10000} --workers 1 --limit-concurrency 16 --timeout-keep-alive 5 --proxy-headers --forwarded-allow-ips='*'"]