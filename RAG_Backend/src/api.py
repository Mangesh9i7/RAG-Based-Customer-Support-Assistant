from dotenv import load_dotenv
load_dotenv() 

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from src.graph import app as rag_chain

api = FastAPI()


# Allow React frontend to call this API
api.add_middleware(CORSMiddleware, allow_origins=["http://localhost:5173"], allow_methods=["*"], allow_headers=["*"])

class Query(BaseModel):
    question: str

@api.post("/chat")
async def chat(query: Query):
    def stream():
        for chunk in rag_chain.stream(query.question):
            yield chunk
    return StreamingResponse(stream(), media_type="text/plain")

@api.get("/health")
def health():
    return {"status": "ok"}