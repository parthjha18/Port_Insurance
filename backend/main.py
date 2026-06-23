from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s — %(message)s",
)

from backend.api.routes import upload, analyze, chat, personas


@asynccontextmanager
async def lifespan(app: FastAPI):
    Path("backend/uploads").mkdir(parents=True, exist_ok=True)
    yield


app = FastAPI(
    title="Insurance Port Assistant",
    description="AI-powered health insurance portability advisor for India",
    version="1.0.0",
    lifespan=lifespan,
)

frontend_url = os.environ.get("FRONTEND_URL", "http://localhost:5173")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_url, "http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router)
app.include_router(analyze.router)
app.include_router(chat.router)
app.include_router(personas.router)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logging.getLogger("uvicorn.error").exception(
        "Unhandled error on %s %s", request.method, request.url
    )
    return JSONResponse(status_code=500, content={"detail": str(exc)})


@app.get("/health", tags=["health"])
async def health_check():
    return {
        "status": "ok",
        "service": "insurance-port-assistant",
        "model": os.environ.get("LLM_MODEL", "openai/gpt-4o-mini"),
    }
