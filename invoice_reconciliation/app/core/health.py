# app/core/health.py
from app.db.mongodb import get_db
from app.utils.active_llm import ACTIVE_LLM
import asyncio


async def check_database() -> str:
    """
    Ping the MongoDB database to ensure it is alive.
    Returns "ok" or error message.
    """
    try:
        db = await get_db()
        if db is None:
            raise Exception("Database not initialized")
        await db.command("ping")
        return "ok"
    except Exception as e:
        return f"error: {str(e)}"


async def check_llm(test_prompt: str = "ping") -> str:
    """
    Check if LLM is initialized and responds to a simple test prompt.
    Returns "ok" or error message.
    """
    if not ACTIVE_LLM.llm:
        return "not initialized"
    try:
        response = await asyncio.wait_for(ACTIVE_LLM.invoke(test_prompt), timeout=5)
        if response:
            return {
                "test_prompt": test_prompt,
                "response": response,
                "active_llm": ACTIVE_LLM.llm_name
            }
        else:
            return "empty response"
    except Exception as e:
        return f"error: {str(e)}"
