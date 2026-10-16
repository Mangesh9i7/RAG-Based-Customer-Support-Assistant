import logging
import os
import threading
import time
from collections import deque
from pathlib import Path
from typing import Annotated

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, StringConstraints
from starlette.types import ASGIApp, Receive, Scope, Send
from src.graph import app as rag_chain

logger = logging.getLogger(__name__)
api = FastAPI()


class ChatRequestSizeLimitMiddleware:
    def __init__(self, app: ASGIApp, max_body_bytes: int) -> None:
        self.app = app
        self.max_body_bytes = max_body_bytes

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if (
            scope["type"] != "http"
            or scope["method"] != "POST"
            or scope["path"] != "/chat"
        ):
            await self.app(scope, receive, send)
            return

        content_length = next(
            (
                value.decode("latin-1")
                for name, value in scope["headers"]
                if name.lower() == b"content-length"
            ),
            None,
        )
        if content_length is not None:
            try:
                if int(content_length) > self.max_body_bytes:
                    await self._reject(scope, receive, send)
                    return
            except ValueError:
                await self._reject(scope, receive, send)
                return

        messages = []
        received_bytes = 0
        while True:
            message = await receive()
            if message["type"] == "http.disconnect":
                messages.append(message)
                break
            if message["type"] != "http.request":
                continue
            received_bytes += len(message.get("body", b""))
            if received_bytes > self.max_body_bytes:
                await self._reject(scope, receive, send)
                return
            messages.append(message)
            if not message.get("more_body", False):
                break

        message_index = 0

        async def replay_receive() -> dict:
            nonlocal message_index
            if message_index < len(messages):
                message = messages[message_index]
                message_index += 1
                return message
            return await receive()

        await self.app(scope, replay_receive, send)

    async def _reject(
        self, scope: Scope, receive: Receive, send: Send
    ) -> None:
        response = JSONResponse(
            status_code=413, content={"detail": "Request body is too large."}
        )
        await response(scope, receive, send)


api.add_middleware(ChatRequestSizeLimitMiddleware, max_body_bytes=8192)

allowed_origins = [
    origin.strip()
    for origin in os.environ.get(
        "ALLOWED_ORIGIN", "http://localhost:5173"
    ).split(",")
    if origin.strip()
]
api.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

_RATE_LIMIT_REQUESTS = 20
_RATE_LIMIT_WINDOW_SECONDS = 60
_MAX_RATE_LIMIT_CLIENTS = 4096
_MAX_CONCURRENT_GENERATIONS = 4
_rate_limit_lock = threading.Lock()
_rate_limit_events: dict[str, deque[float]] = {}
_generation_slots = threading.BoundedSemaphore(_MAX_CONCURRENT_GENERATIONS)


QuestionText = Annotated[
    str, StringConstraints(strip_whitespace=True, min_length=1, max_length=1500)
]


class Query(BaseModel):
    model_config = ConfigDict(extra="forbid")

    question: QuestionText


@api.post("/chat")
async def chat(query: Query, request: Request):
    client_ip = request.client.host if request.client else "unknown"
    now = time.monotonic()
    with _rate_limit_lock:
        expired_clients = [
            key
            for key, events in _rate_limit_events.items()
            if not events or now - events[-1] >= _RATE_LIMIT_WINDOW_SECONDS
        ]
        for key in expired_clients:
            del _rate_limit_events[key]

        events = _rate_limit_events.get(client_ip)
        if events is None:
            if len(_rate_limit_events) >= _MAX_RATE_LIMIT_CLIENTS:
                raise HTTPException(status_code=503, detail="Rate limiting is busy.")
            events = _rate_limit_events[client_ip] = deque()
        while events and now - events[0] >= _RATE_LIMIT_WINDOW_SECONDS:
            events.popleft()
        if len(events) >= _RATE_LIMIT_REQUESTS:
            retry_after = max(
                1, int(_RATE_LIMIT_WINDOW_SECONDS - (now - events[0]))
            )
            raise HTTPException(
                status_code=429,
                detail="Too many chat requests. Please try again shortly.",
                headers={"Retry-After": str(retry_after)},
            )
        events.append(now)

    if not _generation_slots.acquire(blocking=False):
        raise HTTPException(
            status_code=503,
            detail="The assistant is busy. Please try again shortly.",
            headers={"Retry-After": "5"},
        )

    def stream():
        try:
            yield from rag_chain.stream(query.question)
        except Exception:
            logger.exception("Chat generation failed.")
            raise
        finally:
            _generation_slots.release()

    return StreamingResponse(
        stream(),
        media_type="text/plain; charset=utf-8",
        headers={
            "Cache-Control": "no-cache, no-transform",
            "X-Content-Type-Options": "nosniff",
        },
    )


@api.get("/health")
def health():
    return {"status": "ok"}

ui_dir = Path(__file__).resolve().parents[2] / "client" / "dist"
assets_dir = ui_dir / "assets"

if ui_dir.is_dir():
    if assets_dir.is_dir():
        api.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @api.get("/{full_path:path}")
    async def serve_react_app(full_path: str):
        file_path = (ui_dir / full_path).resolve()
        if file_path.is_relative_to(ui_dir) and file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(ui_dir / "index.html")