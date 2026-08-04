import os
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from src.graph import app as rag_chain

load_dotenv()
api = FastAPI()

allowed_origin = os.environ.get("ALLOWED_ORIGIN", "*")
api.add_middleware(
    CORSMiddleware,
    allow_origins=[allowed_origin] if allowed_origin != "*" else ["*"],
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

ui_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "client", "dist"))

if os.path.exists(ui_dir):
    api.mount("/assets", StaticFiles(directory=os.path.join(ui_dir, "assets")), name="assets")

    @api.get("/{full_path:path}")
    async def serve_react_app(full_path: str):
        file_path = os.path.join(ui_dir, full_path)
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(ui_dir, "index.html"))