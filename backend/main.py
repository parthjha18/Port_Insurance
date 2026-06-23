from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.api.routes import upload, analyze, chat, personas

app = FastAPI(
    title="Insurance Port Assistant",
    description="AI-powered health insurance portability advisor for India",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router)
app.include_router(analyze.router)
app.include_router(chat.router)
app.include_router(personas.router)


@app.get("/health", tags=["health"])
async def health_check():
    return {"status": "ok", "service": "insurance-port-assistant"}
