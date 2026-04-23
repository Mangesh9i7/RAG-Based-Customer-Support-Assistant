from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from src.config import PDF_FILE_PATH

def load_and_chunk_pdf():
    print(f"Loading PDF from {PDF_FILE_PATH}...")
    loader = PyPDFLoader(PDF_FILE_PATH)
    docs = loader.load()
    
    print("Chunking document...")
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, 
        chunk_overlap=200
    )
    splits = text_splitter.split_documents(docs)
    
    return splits