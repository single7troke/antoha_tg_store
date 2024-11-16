import aioredis
from fastapi import FastAPI
from fastapi.responses import ORJSONResponse
import uvicorn

from api.v1 import payments, files, user
from core.config import get_config
from db import redis

config = get_config()

app = FastAPI(
    title=config.name,
    docs_url="/api/openapi",
    openapi_url="/api/openapi.json",
    default_response_class=ORJSONResponse,
)
# TODO по хорошему, нужно перенести всю бизнес логику в это приложение(создание/сохранение/редактирование юзера/платежа всяческие проверки и тд)
#  бот должен просто обращаться к этой апишке и получать нужные данные а то в итоге получилась кучу дублированного кода.
#  + к юкассе лучше обращаться не через их библотеку(она синхронная) а напрямую запросом к API

@app.on_event('startup')
async def startup():
    redis.redis = await aioredis.from_url(
        url=f"redis://{config.cache.host}:{config.cache.port}",
        encoding="utf-8",
        # decode_responses=True
    )

app.include_router(payments.router, prefix="/api/v1/payments", tags=["payments"])
app.include_router(files.router, prefix="/api/v1/files", tags=["files"])
app.include_router(user.router, prefix="/api/v1/user", tags=["user"])

if __name__ == "__main__":
    uvicorn.run(
        app="main:app",
        host="0.0.0.0",
        port=8000,
        reload=config.dev_mode
    )
