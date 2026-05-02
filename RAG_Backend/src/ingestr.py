import os
from langchain_community.document_loaders import PyPDFLoader, TextLoader, UnstructuredWordDocumentLoader, CSVLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.config import DATA_FILE_PATH

def load_and_chunk_data():
    ext = os.path.splitext(DATA_FILE_PATH)[1].lower()

    if ext == ".pdf":
        loader = PyPDFLoader(DATA_FILE_PATH)
    elif ext == ".txt":
        loader = TextLoader(DATA_FILE_PATH, encoding="utf-8") 
    elif ext in [".doc", ".docx"]:
        loader = UnstructuredWordDocumentLoader(DATA_FILE_PATH)
    elif ext == ".csv":
        loader = CSVLoader(DATA_FILE_PATH, encoding="utf-8")
    else:
        raise ValueError(f"Unsupported file format: {ext}")

    print(f"Loading data from {DATA_FILE_PATH}...")
    docs = loader.load()

    print("Chunking document...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200
    )
    splits = text_splitter.split_documents(docs)

    return splits