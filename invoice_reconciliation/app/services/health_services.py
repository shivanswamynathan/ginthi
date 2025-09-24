# app/services/health_service.py
from app.core import health as health_core
from app.utils.active_llm import ACTIVE_LLM


async def get_health_status() -> dict:
    """
    Basic health status for API, DB, and LLM (without test query).
    """
    database_status = await health_core.check_database()
    llm_status = "ok" if ACTIVE_LLM.llm else "not initialized"

    return {
        "api": "ok",
        "database": database_status,
        "llm": llm_status
    }


async def get_readiness_status() -> dict:
    """
    Full readiness status including LLM test query.
    """
    database_status = await health_core.check_database()
    llm_status = await health_core.check_llm()

    return {
        "api": "ok",
        "database": database_status,
        "llm": "ok" if ACTIVE_LLM.llm else "not initialized",
        "llm_response": llm_status
    }
