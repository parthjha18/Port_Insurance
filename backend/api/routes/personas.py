from fastapi import APIRouter

router = APIRouter(prefix="/personas", tags=["personas"])


@router.get("/demo")
async def get_demo_personas():
    # Implemented in feat/personas branch
    raise NotImplementedError
