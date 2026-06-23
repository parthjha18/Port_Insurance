from fastapi import APIRouter

router = APIRouter(prefix="/upload", tags=["upload"])


@router.post("")
async def upload_policy():
    # Implemented in feat/api branch
    raise NotImplementedError
