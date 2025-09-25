import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
import logging
from app.db.mongodb import init_db
from app.api import llm_apis, health, ocr_api
from app.utils.active_llm import ACTIVE_LLM
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.gzip import GZipMiddleware

import logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


@asynccontextmanager
async def lifespan(app: FastAPI):

    await init_db()
    print("MongoDB initialized")

    await ACTIVE_LLM.init()
    if ACTIVE_LLM.llm:
        print(f"Active LLM in use: {ACTIVE_LLM.llm_name}")
    else:
        print(" No active LLM configured in DB")

    yield
    print("Application shutting down")


app = FastAPI(
    title="Ginthi Invoice Reconciliation API's",
    lifespan=lifespan
)


# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # update with allowed domains in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Compress large responses
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Add routers
app.include_router(llm_apis.router, prefix="/api/v1/llm")
app.include_router(ocr_api.router)
app.include_router(health.router, prefix="/api/v1")



if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",   # accessible from anywhere
        port=8000,
        reload=True,      # auto-reload on code changes (dev mode)
        workers=1
    )
