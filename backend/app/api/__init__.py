from fastapi import APIRouter

router = APIRouter()

from .gemini import router as gemini_router

router.include_router(gemini_router)