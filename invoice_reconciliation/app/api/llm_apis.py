from fastapi import APIRouter
from app.schemas.llm_config import LLMConfig
from app.utils.active_llm import ACTIVE_LLM

router = APIRouter(prefix="/api/v1/llm", tags=["LLM"])


@router.post("/", response_model=LLMConfig)
async def add_llm_config(config: LLMConfig):
    await config.insert()
    return config


@router.get("/", response_model=list[LLMConfig])
async def list_llms():
    return await LLMConfig.find_all().to_list()


@router.get("/test")
async def test_llm(prompt: str = "Hello, how are you?"):

    if not ACTIVE_LLM.llm:
        return {"error": "❌ LLM not initialized"}

    try:
        response_text = await ACTIVE_LLM.invoke(prompt)
        return {
            "prompt": prompt,
            "response": response_text,
            "active_llm": ACTIVE_LLM.llm_name
        }
    except Exception as e:
        return {"error": f"LLM invocation failed: {str(e)}"}
