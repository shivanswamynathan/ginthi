from beanie import Document


class LLMConfig(Document):
    provider: str
    api_key: str
    model_type: str
    is_active: bool = True
    is_use: bool = False

    class Settings:
        name = "llm_config"
