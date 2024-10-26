import os.path
import pickle
import time

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse

from db.redis import get_redis_db, RedisDB
from core.config import get_config
from core.utils import decrypt, get_data_from_link_key
from core.cache_key_constructor import CacheKeyConstructor
from models.models import User, UserCourse

router = APIRouter()
config = get_config()


@router.get('/{secret_str}', response_class=FileResponse)
async def get(secret_str: str, cache: RedisDB = Depends(get_redis_db)):
    # TODO проверяем есть ли запись в редис и не вышло ли время.
    # TODO делать ли фронт??? и нужно локально уже сделать nginx
    # TODO настроить ngrok чтоб настроить колбек от телеги
    # TODO 1. nginx 2. callback 3. доделать этот хендлер.
    link_key = decrypt(secret_str)
    link_info = await cache.get(link_key)
    if not link_info:
        raise HTTPException(status_code=404, detail='File not found')

    link_info = pickle.loads(link_info)
    if time.time() - link_info['created'] > 24 * 60 * 60:
        raise HTTPException(status_code=403, detail='The link expired')

    user_id, course_id, part_id = get_data_from_link_key(link_key)
    file_name = f'part_{part_id}.zip'
    file_path = os.path.join(config.path_to_files, course_id, file_name)
    if os.path.isfile(file_path):
        return FileResponse(status_code=200, path=file_path, filename=file_name)

    raise HTTPException(status_code=404, detail='File not found')
