FROM python:3.10-slim

WORKDIR /app

# Copy and install Python dependencies first (better layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the backend (main.py, src/, data/, docs/, vector_db/)
# venv/, __pycache__/, .env, .git/ etc. are excluded via .dockerignore
COPY . .

EXPOSE 5000

# FastAPI object is named "api" inside src/api.py -> FastAPI()
CMD ["uvicorn", "src.api:api", "--host", "0.0.0.0", "--port", "5000"]
