from fastapi import APIRouter

router = APIRouter(prefix="/api/ps-write", tags=["ps-write"])

@router.get("/test")
async def test_endpoint():
    return {"message": "PS写作API测试端点"}