from typing import Optional
from langchain_openai import ChatOpenAI
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.schema import HumanMessage, AIMessage
from app.schemas.llm_config import LLMConfig
import asyncio


class ActiveLLM:
    """
    Singleton class to hold the currently active LLM.
    Initialize at startup with LLMConfig where is_use=True.
    Use `invoke(prompt)` to send prompts safely.
    """
    _instance: Optional["ActiveLLM"] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.llm = None
            cls._instance.llm_name = None
            cls._instance.is_async = True
        return cls._instance

    async def init(self):
        """
        Initialize the active LLM from the DB where is_use=True.
        Supports 'openai' and 'gemini'.
        """
        active_configs = await LLMConfig.find_many({"is_use": True}).to_list()
        if not active_configs:
            print("⚠️ No active LLM found in DB")
            return

        config = active_configs[0]  # Take the first active LLM
        provider = config.provider.lower()

        if provider == "openai":
            self.llm = ChatOpenAI(
                openai_api_key=config.api_key,
                temperature=0.2,
                model_name=config.model_type or "gpt-3.5-turbo",
                streaming=False
            )
            self.llm_name = "OpenAI"
            self.is_async = True

        elif provider == "gemini":
            self.llm = ChatGoogleGenerativeAI(
                api_key=config.api_key,
                model=config.model_type or "gemini-pro",
                temperature=0.2
            )
            self.llm_name = "Google GenAI"
            self.is_async = False  # Gemini client is sync
        else:
            print(f"⚠️ Unsupported LLM provider: {provider}")
            self.llm = None
            self.llm_name = None

        if self.llm:
            print(f"✅ Active LLM initialized: {self.llm_name}")

    async def invoke(self, prompt: str) -> str:
        """
        Send a prompt to the active LLM and return the response as string.
        Handles both sync and async LLMs.
        """
        if not self.llm:
            raise ValueError("Active LLM not initialized")

        message = HumanMessage(content=prompt)

        if self.is_async:
            response = await self.llm.ainvoke([message])
        else:
            # Run sync Gemini in a thread so it doesn’t block FastAPI loop
            response = await asyncio.to_thread(self.llm.invoke, [message])

        # Ensure we always return plain text
        if isinstance(response, AIMessage):
            return response.content
        elif hasattr(response, "content"):
            return response.content
        elif hasattr(response, "text"):
            return response.text
        return str(response)


# Singleton instance to import anywhere
ACTIVE_LLM = ActiveLLM()
