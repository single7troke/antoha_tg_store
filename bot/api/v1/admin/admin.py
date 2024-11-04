import json
import logging
import pickle
import time

from aiogram import types, Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile

from core import *
from core.utils import bytes_to_user
from db.redis import get_redis_db, RedisDB


router = Router()
config = get_config()

logger = logging.getLogger(__name__)


@router.message(Command(commands=('admin',)))
async def main_menu(message: types.Message):
    logger.info(f'Admin menu. '
                f'user_id: {message.from_user.id}, '
                f'user_name: {message.from_user.username}')
    response = await message.bot.send_message(
        chat_id=message.chat.id,
        text='admin menu',
        reply_markup=kb.admin_main_menu_keyboard()
    )
    await utils.clear_messages(message.bot, message.chat.id, response.message_id - 1)


@router.callback_query(cb.AdminMainMenuCallback.filter(F.data == 'user'))
async def user_id_form(
        callback: types.CallbackQuery,
        callback_data: cb.MainMenuCallback,
        state: FSMContext
):
    await state.clear()
    await state.set_state(form.UserId.user_id)
    await callback.message.edit_text(
        text='Enter user id',
        reply_markup=kb.back_button('admin_main_menu')
    )


@router.message(form.UserId.user_id)
async def get_user(message: types.Message, state: FSMContext):
    user_id = message.text
    await state.clear()
    cache: RedisDB = get_redis_db()
    user = message.from_user
    data_from_cache = await cache.get(CacheKeyConstructor.user(user_id=user_id))
    user_from_cache = utils.bytes_to_user(data_from_cache) if data_from_cache else None

    if user_from_cache:
        text = (f'id: {user_from_cache.tg_user_data["id"]}'
                f'\nfirst name: {user_from_cache.tg_user_data["first_name"]}'
                f'\nlast name: {user_from_cache.tg_user_data["last_name"]}'
                f'\nusername: {user_from_cache.tg_user_data["username"]}'
                f'\nemail: {user_from_cache.email}'
                f'\nCourse type: {user_from_cache.courses[1001].paid}'
                f'\nPromo access: {user_from_cache.courses[1001].promo_access}'
                f'\nPayments: {user_from_cache.courses[1001].payment_ids}')
    else:
        text = 'User not found'

    response = await message.bot.send_message(
        chat_id=message.chat.id,
        text=text,
        reply_markup=kb.back_button('admin_main_menu')
    )

    await utils.clear_messages(message.bot, message.chat.id, response.message_id - 1)


@router.callback_query(cb.AdminMainMenuCallback.filter(F.data == 'user_list'))
async def user_list(
        callback: types.CallbackQuery,
        callback_data: cb.MainMenuCallback,
):
    cache: RedisDB = get_redis_db()
    user_keys = await cache.find_all_with('user')
    text = ''
    for key in user_keys:
        user = await cache.get(key)
        user = bytes_to_user(user)
        text += f'id: {CacheKeyConstructor.extract_user_id(key.decode())}, username: {user.tg_user_data["username"]}\n'

    response = await callback.bot.send_message(
        chat_id=callback.message.chat.id,
        text=text,
        reply_markup=kb.back_button('admin_main_menu')
    )

    await utils.clear_messages(callback.bot, callback.message.chat.id, response.message_id - 1)


@router.callback_query(cb.AdminMainMenuCallback.filter(F.data == 'payment'))
async def payment_id_form(
        callback: types.CallbackQuery,
        callback_data: cb.MainMenuCallback,
        state: FSMContext
):
    await state.clear()
    await state.set_state(form.PaymentId.payment_id)
    await callback.message.edit_text(
        text='Enter payment id',
        reply_markup=kb.back_button('admin_main_menu')
    )


@router.message(form.PaymentId.payment_id)
async def get_payment_handler(message: types.Message, state: FSMContext):
    payment_id = message.text
    await state.clear()
    payment = json.loads(get_payment(payment_id).json())

    if payment:
        text = json.dumps(payment, indent=4)

    else:
        text = 'Payment not found'

    response = await message.bot.send_message(
        chat_id=message.chat.id,
        text=text,
        reply_markup=kb.back_button('admin_main_menu')
    )

    await utils.clear_messages(message.bot, message.chat.id, response.message_id - 1)


@router.callback_query(cb.BackButtonCallback.filter(F.data == 'admin_main_menu'))
async def admin_back_button_callback(
        callback: types.CallbackQuery,
        callback_data: cb.BackButtonCallback,
        state: FSMContext
):
    await callback.message.edit_text(text='admin menu', reply_markup=kb.admin_main_menu_keyboard())
    await utils.clear_messages(callback.bot, callback.message.chat.id, callback.message.message_id - 1)
