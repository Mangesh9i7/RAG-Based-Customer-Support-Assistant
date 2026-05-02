import os

# Base paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VECTOR_DB_DIR = os.path.join(BASE_DIR, "vector_db")
RAW_DATA_DIR = os.path.join(BASE_DIR, "data", "raw")
DATA_FILE_PATH = os.path.join(RAW_DATA_DIR, "customer_support_tickets.csv")

# Model configurations
RETRIEVER_K = 3
GROQ_MODEL_NAME = "llama-3.1-8b-instant"
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"