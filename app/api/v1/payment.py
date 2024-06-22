from http import HTTPStatus
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, Request
from aioredis.exceptions import ConnectionError

from db import get_redis_db, RedisDB
# from models.models import BasicUser, CreateUser

router = APIRouter()


@router.post("", description="Return user's role if user exists, else False")
async def get_user(data: Dict[Any, Any]):
    print(data)
    return {'status': 'ok'}


@router.get("", description="Return user's role if user exists, else False")
async def get_user(request: Request):
    return {'qwer': request.headers,
            'body': await request.body(),
            'items': request.items}
