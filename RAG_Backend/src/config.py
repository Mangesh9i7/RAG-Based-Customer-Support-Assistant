import os

# Base paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VECTOR_DB_DIR = os.path.join(BASE_DIR, "vector_db")
VECTOR_STORE_DIR = VECTOR_DB_DIR  
RAW_DATA_DIR = os.path.join(BASE_DIR, "data", "raw")


def _find_data_file():
    """Pick the first supported file in data/raw instead of hardcoding a filename.
    Your folder structure has support_kb.pdf, but the old code pointed at
    customer_support_tickets.csv, which doesn't exist -> ingestion would crash.
    """
    if not os.path.isdir(RAW_DATA_DIR):
        return None
    supported = (".pdf", ".txt", ".docx", ".doc", ".csv")
    for fname in sorted(os.listdir(RAW_DATA_DIR)):
        if fname.lower().endswith(supported):
            return os.path.join(RAW_DATA_DIR, fname)
    return None


DATA_FILE_PATH = _find_data_file()

# Model configurations
RETRIEVER_K = 3
GROQ_MODEL_NAME = "llama-3.1-8b-instant"
EMBEDDING_MODEL_NAME = "all-MiniLM-L6-v2"


