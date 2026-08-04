import os
from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.config import DATA_FILE_PATH


def load_and_chunk_data():
    if not DATA_FILE_PATH:
        raise FileNotFoundError(
            "No supported file found in data/. Add a .pdf, .txt, .docx or .csv file."
        )

    ext = os.path.splitext(DATA_FILE_PATH)[1].lower()


    if ext == ".pdf":
        from langchain_community.document_loaders import PyPDFLoader
        loader = PyPDFLoader(DATA_FILE_PATH)
    elif ext == ".txt":
        from langchain_community.document_loaders import TextLoader
        loader = TextLoader(DATA_FILE_PATH, encoding="utf-8")
    elif ext in (".doc", ".docx"):
        from langchain_community.document_loaders import UnstructuredWordDocumentLoader
        loader = UnstructuredWordDocumentLoader(DATA_FILE_PATH)
    elif ext == ".csv":
        from langchain_community.document_loaders import CSVLoader
        loader = CSVLoader(DATA_FILE_PATH, encoding="utf-8")
    else:
        raise ValueError(f"Unsupported file format: {ext}")

    print(f"Loading data from {DATA_FILE_PATH}...")
    docs = loader.load()

    print("Chunking document...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=150
    )
    splits = text_splitter.split_documents(docs)

    return splits
