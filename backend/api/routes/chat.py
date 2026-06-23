from __future__ import annotations

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from pathlib import Path

from backend.core import rag_pipeline, benefit_extractor, llm_client
from backend.models.schemas import ChatRequest, ChatResponse

router = APIRouter(prefix="/chat", tags=["chat"])

UPLOAD_DIR = Path("backend/uploads")
DEMO_COLLECTION_ID = "demo-mode-no-collection"


def _has_collection(collection_id: str) -> bool:
    """Return True if this collection has a document on disk (or in ChromaDB)."""
    if collection_id == DEMO_COLLECTION_ID:
        return False
    chunks_file = UPLOAD_DIR / f"{collection_id}.chunks.json"
    return chunks_file.exists()


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Multi-turn Q&A against an uploaded policy document.
    In demo mode (no real collection), answers from general IRDAI knowledge.
    """
    if not request.messages:
        raise HTTPException(status_code=400, detail="At least one message is required.")

    persona_context = ""
    if request.persona_id:
        try:
            from backend.core.persona_loader import get_persona_context
            persona_context = get_persona_context(request.persona_id)
        except Exception:
            pass

    last_user_message = next(
        (m.content for m in reversed(request.messages) if m.role == "user"),
        None,
    )
    if not last_user_message:
        raise HTTPException(status_code=400, detail="No user message found in conversation.")

    try:
        if _has_collection(request.collection_id):
            # Normal RAG path: retrieve relevant chunks, then answer
            result = rag_pipeline.answer_query(
                query=last_user_message,
                collection_id=request.collection_id,
                persona_context=persona_context,
            )
        else:
            # Demo / no-document path: answer from general IRDAI knowledge
            result = rag_pipeline.answer_general(
                query=last_user_message,
                persona_context=persona_context,
            )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(exc)}")

    return ChatResponse(
        answer=result["answer"],
        sources=result.get("sources", []),
    )


@router.post("/stream")
async def chat_stream(request: ChatRequest) -> StreamingResponse:
    """
    Streaming version of the chat endpoint.
    Yields text chunks as Server-Sent Events (SSE).
    """

    persona_context = ""
    if request.persona_id:
        try:
            from backend.core.persona_loader import get_persona_context
            persona_context = get_persona_context(request.persona_id)
        except Exception:
            pass

    last_user_message = next(
        (m.content for m in reversed(request.messages) if m.role == "user"),
        "",
    )

    if _has_collection(request.collection_id):
        chunks = rag_pipeline.retrieve_context(request.collection_id, last_user_message)
    else:
        chunks = []
    context = "\n\n".join(chunks)
    prompt = benefit_extractor.build_chat_prompt(last_user_message, context, persona_context)
    system = benefit_extractor.build_system_prompt(persona_context)

    def _generate():
        for token in llm_client.stream(prompt, system=system):
            yield f"data: {token}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(_generate(), media_type="text/event-stream")
