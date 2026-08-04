import os
from dotenv import load_dotenv

load_dotenv()

from langchain_groq import ChatGroq
from langchain_core.runnables import RunnablePassthrough, RunnableLambda
from langchain_core.output_parsers import StrOutputParser
from src.vector_store import get_retriever
from src.prompts import rag_prompt
from src.config import GROQ_MODEL_NAME

# 1. Initialize the free Groq LLM (lightweight — just an HTTP client, no local weights)
llm = ChatGroq(
    model=GROQ_MODEL_NAME,
    api_key=os.environ.get("GROQ_API_KEY")
)


def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)


def retrieve_and_format(question):

    retriever = get_retriever()
    docs = retriever.invoke(question)
    return format_docs(docs)


# 2. Build the LangChain executable app (retrieval is now lazy, see above)
app = (
    {"context": RunnableLambda(retrieve_and_format), "question": RunnablePassthrough()}
    | rag_prompt
    | llm
    | StrOutputParser()
)
