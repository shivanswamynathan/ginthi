# app/api/health.py
from fastapi import APIRouter
from app.services import health_services

router = APIRouter()


@router.get("/health", tags=["Health"])
async def health_check():
    status = await health_services.get_health_status()
    overall_status = 200 if status["database"] == "ok" and status["llm"] == "ok" else 500

    return {
        "status": overall_status,
        "message": "Health check result",
        "data": status
    }


@router.get("/ready", tags=["Health"])
async def readiness_check():
    status = await health_services.get_readiness_status()
    overall_status = 200 if status["database"] == "ok" and status["llm_response"] == "ok" else 500

    return {
        "status": overall_status,
        "message": "Readiness check result",
        "data": status
    }
