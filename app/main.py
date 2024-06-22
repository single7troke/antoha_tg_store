import aioredis
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
import uvicorn

from api.v1 import payment
from core import Config
from db import redis

config = Config()

app = FastAPI(
    title=config.app.name,
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
    default_response_class=ORJSONResponse,
)


@app.on_event('startup')
async def startup():
    redis = await aioredis.from_url(
        url=f"redis://{config.cache.host}:{config.cache.port}",
        encoding="utf-8",
        decode_responses=True
    )

app.include_router(payment.router, prefix="/api/v1/payments", tags=["payments"])
if __name__ == "__main__":
    uvicorn.run(
        app="main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )
