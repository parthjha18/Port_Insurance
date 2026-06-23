from fastapi import APIRouter

router = APIRouter(prefix="/analyze", tags=["analyze"])


@router.post("")
async def analyze_policy():
    # Implemented in feat/api branch
    raise NotImplementedError


@router.post("/compare")
async def compare_policies():
    # Implemented in feat/api branch
    raise NotImplementedError
