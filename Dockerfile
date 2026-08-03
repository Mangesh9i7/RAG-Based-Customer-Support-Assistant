# Stage 1: Build the React Frontend
FROM node:20-alpine AS frontend-builder
WORKDIR /client
COPY client/package*.json ./
RUN npm ci
COPY client/ ./
RUN npm run build

# Stage 2: Set up Python Backend & Serve
FROM python:3.10-slim
WORKDIR /app

# Hugging Face requires user ID 1000
RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:$PATH"

# Copy and install Python dependencies
COPY --chown=user RAG_Backend/requirements.txt /app/RAG_Backend/
RUN pip install --no-cache-dir -r /app/RAG_Backend/requirements.txt

# Copy built frontend assets from Stage 1
COPY --from=frontend-builder --chown=user /client/dist /app/client/dist

# Copy backend application files
COPY --chown=user RAG_Backend/ /app/RAG_Backend/

# Expose default Hugging Face port
EXPOSE 7860

WORKDIR /app/RAG_Backend

# Run Uvicorn using 'api' as the object name
CMD ["uvicorn", "src.api:api", "--host", "0.0.0.0", "--port", "7860"]