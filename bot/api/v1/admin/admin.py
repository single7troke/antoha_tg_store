import json
import logging
import pickle
from collections import defaultdict
from datetime import datetime, timedelta, timezone

from aiogram import types, Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

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


@router.callback_query(cb.AdminMainMenuCallback.filter(F.data == 'extended_buyers'))
async def extended_buyers(
        callback: types.CallbackQuery,
        callback_data: cb.MainMenuCallback,
):
    cache: RedisDB = get_redis_db()
    user_keys = await cache.find_all_with('user')
    text = ''
    for key in user_keys:
        user = await cache.get(key)
        user = bytes_to_user(user)
        if user.courses[1001].paid == 'extended':
            text += (f'id: {CacheKeyConstructor.extract_user_id(key.decode())}, '
                     f'username: {user.tg_user_data["username"]}\n'
                     f'paid: {user.courses[1001].paid}, access: {user.courses[1001].promo_access}\n\n')

    response = await callback.bot.send_message(
        chat_id=callback.message.chat.id,
        text=text if text else '-',
        reply_markup=kb.back_button('admin_main_menu')
    )

    await utils.clear_messages(callback.bot, callback.message.chat.id, response.message_id - 1)


@router.callback_query(cb.AdminMainMenuCallback.filter(F.data == 'basic_buyers'))
async def basic_buyers(
        callback: types.CallbackQuery,
        callback_data: cb.MainMenuCallback,
):
    cache: RedisDB = get_redis_db()
    user_keys = await cache.find_all_with('user')
    text = ''
    for key in user_keys:
        user = await cache.get(key)
        user = bytes_to_user(user)
        if user.courses[1001].paid == 'basic':
            text += (f'id: {CacheKeyConstructor.extract_user_id(key.decode())}, '
                     f'username: {user.tg_user_data["username"]}\n'
                     f'paid: {user.courses[1001].paid}, access: {user.courses[1001].promo_access}\n\n')

    response = await callback.bot.send_message(
        chat_id=callback.message.chat.id,
        text=text if text else '-',
        reply_markup=kb.back_button('admin_main_menu')
    )

    await utils.clear_messages(callback.bot, callback.message.chat.id, response.message_id - 1)


@router.callback_query(cb.AdminMainMenuCallback.filter(F.data == 'stats'))
async def user_stats(
        callback: types.CallbackQuery,
        callback_data: cb.MainMenuCallback,
):
    cache: RedisDB = get_redis_db()
    user_keys = await cache.find_all_with('user')
    data = defaultdict(int)
    for key in user_keys:
        user = await cache.get(key)
        user = bytes_to_user(user)
        if user.courses[1001].paid == 'extended':
            data['extended'] += 1
        elif user.courses[1001].paid == 'basic':
            data['basic'] += 1
        elif user.courses[1001].promo_access:
            data['promo'] += 1

    text = '\n'.join(f'{key} - {value}' for key, value in data.items())

    response = await callback.bot.send_message(
        chat_id=callback.message.chat.id,
        text=text if text else '-',
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


@router.callback_query(cb.AdminMainMenuCallback.filter(F.data == 'grant_access'))
async def grant_access_form(
        callback: types.CallbackQuery,
        callback_data: cb.MainMenuCallback,
        state: FSMContext
):
    await state.clear()
    await state.set_state(form.GrantAccessToUser.user_id)
    await callback.message.edit_text(
        text='Enter user id, to grant access',
        reply_markup=kb.back_button('admin_main_menu')
    )


@router.message(form.GrantAccessToUser.user_id)
async def grant_access_to_user(message: types.Message, state: FSMContext):
    user_id = message.text
    await state.clear()
    cache: RedisDB = get_redis_db()
    user = message.from_user
    data_from_cache = await cache.get(CacheKeyConstructor.user(user_id=user_id))
    user_from_cache = utils.bytes_to_user(data_from_cache) if data_from_cache else None

    if user_from_cache:
        if not user_from_cache.courses[1001].paid:
            user_from_cache.courses[1001].promo_access = True
            user_from_cache.courses[1001].captured_at = datetime.now(timezone.utc).isoformat()
            await cache.update(
                CacheKeyConstructor.user(user_id),
                pickle.dumps(user_from_cache)
            )
            text = f'Access granted to user with id: {user_id}'
        else:
            text = 'User has already purchased the course'

    else:
        text = 'User not found'

    response = await message.bot.send_message(
        chat_id=message.chat.id,
        text=text,
        reply_markup=kb.back_button('admin_main_menu')
    )

    await utils.clear_messages(message.bot, message.chat.id, response.message_id - 1)


@router.callback_query(cb.AdminMainMenuCallback.filter(F.data == 'extend_access'))
async def extend_access_to_the_course(
        callback: types.CallbackQuery,
        callback_data: cb.MainMenuCallback,
        state: FSMContext
):
    await state.clear()
    await state.set_state(form.ExtendAccessToUser.user_id)
    await callback.message.edit_text(
        text='Enter user id, to extend access',
        reply_markup=kb.back_button('admin_main_menu')
    )


@router.message(form.ExtendAccessToUser.user_id)
async def grant_access_to_user(message: types.Message, state: FSMContext):
    user_id = message.text
    await state.clear()
    cache: RedisDB = get_redis_db()
    data_from_cache = await cache.get(CacheKeyConstructor.user(user_id=user_id))
    user_from_cache = utils.bytes_to_user(data_from_cache) if data_from_cache else None

    if user_from_cache:
        if user_from_cache.courses[1001].paid or user_from_cache.courses[1001].promo_access:
            captured_at = user_from_cache.courses[1001].captured_at
            updated_captured_at = datetime.fromisoformat(
                captured_at.replace("Z", "+00:00")
            ) + timedelta(days=1)

            user_from_cache.courses[1001].captured_at = updated_captured_at.replace(tzinfo=timezone.utc).isoformat()
            await cache.update(
                CacheKeyConstructor.user(user_id),
                pickle.dumps(user_from_cache)
            )
            text = f'Access extended to user with id: {user_id}'
        else:
            text = 'User has not access to the course'

    else:
        text = 'User not found'

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
