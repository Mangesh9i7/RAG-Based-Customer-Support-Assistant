# ==========================================
# Stage 1: Build the React Frontend
# ==========================================
FROM node:20-alpine AS frontend-builder
WORKDIR /app/client

# Install dependencies
COPY client/package*.json ./
RUN npm install

# Copy frontend source and build
COPY client/ ./
RUN npm run build

# ==========================================
# Stage 2: Build the FastAPI Backend & Serve
# ==========================================
FROM python:3.10-slim
WORKDIR /app

# Install system dependencies (needed for some Python packages)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python requirements
COPY RAG_Backend/requirements.txt ./RAG_Backend/
RUN pip install --no-cache-dir -r RAG_Backend/requirements.txt

# Copy Backend source code
COPY RAG_Backend/ ./RAG_Backend/

# Copy the built React assets from Stage 1 into the folder api.py expects
COPY --from=frontend-builder /app/client/dist ./client/dist

# Switch to backend directory so relative paths in Python work correctly
WORKDIR /app/RAG_Backend

# Render dynamically assigns a PORT environment variable (default 10000)
EXPOSE 10000

# Start Uvicorn, binding to 0.0.0.0 and the Render-provided PORT
CMD ["sh", "-c", "uvicorn src.api:api --host 0.0.0.0 --port ${PORT:-10000}"]