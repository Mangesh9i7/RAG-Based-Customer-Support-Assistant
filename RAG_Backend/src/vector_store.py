import os
from dotenv import load_dotenv
from langchain_community.embeddings import HuggingFaceInferenceAPIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEndpointEmbeddings
from src.config import VECTOR_STORE_DIR, RETRIEVER_K, EMBEDDING_MODEL_NAME

load_dotenv()

_retriever = None  


def get_retriever():
    global _retriever
    if _retriever is not None:
        return _retriever

    # embeddings = HuggingFaceInferenceAPIEmbeddings(
    #     api_key=os.environ.get("HF_TOKEN"),  
    #     model_name=f"sentence-transformers/{EMBEDDING_MODEL_NAME}"
    # )
    embeddings = HuggingFaceEndpointEmbeddings(
        model=f"sentence-transformers/{EMBEDDING_MODEL_NAME}",
        task="feature-extraction",
        huggingfacehub_api_token=os.environ.get("HF_TOKEN"),
    )

    index_path = os.path.join(VECTOR_STORE_DIR, "index.faiss")

    if os.path.exists(index_path):
        vectorstore = FAISS.load_local(
            folder_path=VECTOR_STORE_DIR,
            embeddings=embeddings,
            allow_dangerous_deserialization=True
        )
    else:
        print("FAISS index not found. Creating a new one...")
        from src.ingestr import load_and_chunk_data
        splits = load_and_chunk_data()

        vectorstore = FAISS.from_documents(
            documents=splits,
            embedding=embeddings
        )

        os.makedirs(VECTOR_STORE_DIR, exist_ok=True)
        vectorstore.save_local(folder_path=VECTOR_STORE_DIR)
        print(f"FAISS vector store saved to {VECTOR_STORE_DIR}.")

    _retriever = vectorstore.as_retriever(search_kwargs={"k": RETRIEVER_K})
    return _retriever
