import os
from dotenv import load_dotenv

# Load environment variables before accessing them
load_dotenv()

from langchain_groq import ChatGroq
from langchain_core.runnables import RunnablePassthrough
from langchain_core.output_parsers import StrOutputParser
from src.vector_store import get_retriever
from src.prompts import rag_prompt
from src.config import GROQ_MODEL_NAME

# 1. Initialize the free Groq LLM
llm = ChatGroq(
    model=GROQ_MODEL_NAME,
    api_key=os.environ.get("GROQ_API_KEY")
)

# 2. Get the database retriever
retriever = get_retriever()

# Helper function to combine retrieved documents into a single string
def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

# 3. Build the LangChain executable app
app = (
    {"context": retriever | format_docs, "question": RunnablePassthrough()}
    | rag_prompt
    | llm
    | StrOutputParser()
)