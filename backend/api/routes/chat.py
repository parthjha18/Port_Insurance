from __future__ import annotations

from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse

from backend.core import rag_pipeline, vector_store, benefit_extractor, llm_client
from backend.models.schemas import ChatRequest, ChatResponse

router = APIRouter(prefix="/chat", tags=["chat"])


def _require_collection(collection_id: str) -> None:
    if not vector_store.collection_exists(collection_id):
        raise HTTPException(
            status_code=404,
            detail=f"Collection '{collection_id}' not found. Upload a PDF first.",
        )


@router.post("", response_model=ChatResponse)
async def chat(request: ChatRequest) -> ChatResponse:
    """
    Multi-turn Q&A against an uploaded policy document.
    Returns a grounded answer with source excerpts.
    """
    _require_collection(request.collection_id)

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
        result = rag_pipeline.answer_query(
            query=last_user_message,
            collection_id=request.collection_id,
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
    _require_collection(request.collection_id)

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

    chunks = rag_pipeline.retrieve_context(request.collection_id, last_user_message)
    context = "\n\n".join(chunks)
    prompt = benefit_extractor.build_chat_prompt(last_user_message, context, persona_context)
    system = benefit_extractor.build_system_prompt(persona_context)

    def _generate():
        for token in llm_client.stream(prompt, system=system):
            yield f"data: {token}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(_generate(), media_type="text/event-stream")
