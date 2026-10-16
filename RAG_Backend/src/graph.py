import os
from dotenv import load_dotenv

load_dotenv()

from langchain_groq import ChatGroq
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from src.vector_store import get_retriever
from src.prompts import rag_prompt
from src.config import GROQ_MODEL_NAME

groq_api_key = os.environ.get("GROQ_API_KEY")
if not groq_api_key:
    raise RuntimeError("GROQ_API_KEY must be configured before starting the API.")

llm = ChatGroq(
    model=GROQ_MODEL_NAME,
    api_key=groq_api_key,
    max_tokens=512,
    temperature=0,
    timeout=30,
    max_retries=2,
)


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


def retrieve_and_format(question):
    retriever = get_retriever()
    docs = retriever.invoke(question)
    return format_docs(docs)


app = (
    {"context": RunnableLambda(retrieve_and_format), "question": RunnablePassthrough()}
    | rag_prompt
    | llm
    | StrOutputParser()
)
