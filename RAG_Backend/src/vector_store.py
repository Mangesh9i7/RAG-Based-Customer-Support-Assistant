import os
from dotenv import load_dotenv
# Load environment variables before accessing them
load_dotenv()
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import Chroma
from src.config import VECTOR_DB_DIR, RETRIEVER_K, EMBEDDING_MODEL_NAME
from src.ingestr import load_and_chunk_data

def get_retriever():
    # Free local embeddings
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL_NAME)
    
    if os.path.exists(VECTOR_DB_DIR) and os.listdir(VECTOR_DB_DIR):
        print("Loading existing vector database...")
        vectorstore = Chroma(
            persist_directory=VECTOR_DB_DIR, 
            embedding_function=embeddings
        )
    else:
        print("Vector database not found. Creating a new one...")
        splits = load_and_chunk_data()
        vectorstore = Chroma.from_documents(
            documents=splits, 
            embedding=embeddings,
            persist_directory=VECTOR_DB_DIR
        )
        print(f"Vector database saved to {VECTOR_DB_DIR}.")
        
    return vectorstore.as_retriever(search_kwargs={"k": RETRIEVER_K})