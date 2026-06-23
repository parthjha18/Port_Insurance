from fastapi import APIRouter

router = APIRouter(prefix="/chat", tags=["chat"])


@router.post("")
async def chat():
    # Implemented in feat/api branch
    raise NotImplementedError
