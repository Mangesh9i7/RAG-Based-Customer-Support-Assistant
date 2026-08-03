from dotenv import load_dotenv
load_dotenv() 

import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from src.graph import app as rag_chain

api = FastAPI()

# Allow frontend requests in both dev and production
api.add_middleware(
    CORSMiddleware, 
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"]
)

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

# --- Frontend Serving Logic ---
# Locate client/dist relative to RAG_Backend/src/api.py
ui_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "client", "dist"))

if os.path.exists(ui_dir):
    # Serve static assets (JS, CSS, images)
    api.mount("/assets", StaticFiles(directory=os.path.join(ui_dir, "assets")), name="assets")

    # Catch-all route to serve index.html for React Router routes (e.g. / and /chat)
    @api.get("/{full_path:path}")
    async def serve_react_app(full_path: str):
        file_path = os.path.join(ui_dir, full_path)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(ui_dir, "index.html"))