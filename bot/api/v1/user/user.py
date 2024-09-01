import logging
import pickle
import time

from aiogram import types, Router, Bot
from aiogram.filters import Command

from core import *
from db.redis import get_redis_db, RedisDB
from models import User, UserCourse

router = Router()
config = get_config()


@router.message(Command(commands=('menu',)))
async def main_menu(message: types.Message, bot: Bot):
    response = await message.answer(
        text=texts.menu,
        reply_markup=kb.user_main_menu_keyboard()
    )
    await bot.delete_message(message.chat.id, response.message_id - 1)
    await bot.delete_message(message.chat.id, response.message_id - 2)


@router.callback_query(cb.MainMenuCallback.filter())
async def main_menu_callback_handler(callback: types.CallbackQuery, callback_data: cb.MainMenuCallback):
    if callback_data.data == 'about':
        await about(callback.message)


@router.callback_query(cb.CourseCallback.filter())
async def selected_course_callback(
        callback: types.CallbackQuery,
        callback_data: cb.CourseCallback,
):
    cache: RedisDB = get_redis_db()
    user = callback.from_user

    data_from_cache = await cache.get(CacheKeyConstructor.user(user_id=user.id))
    user_from_cache = utils.bytes_to_user(data_from_cache) if data_from_cache else None
    if user_from_cache:
        user_course = user_from_cache.courses.get(callback_data.data)
        if user_course.payed:
            print('Оплачен')
            text = texts.course_part_list.format(course_name=user_course.course.name)
            keyboard = kb.payed_course_keyboard(user_course.course)
        else:
            print('Еще не оплачен')
            text = texts.course_description.format(description=user_course.course.description)
            keyboard = kb.course_keyboard()
    else:
        course = utils.COURSE
        print(str(callback_data.data) + '---------------------------------------')
        print('Вообще новый юзер')
        data_to_cache = User(
            courses={course.id: UserCourse(course=course)}
        )
        await cache.create(
            CacheKeyConstructor.user(user_id=user.id),
            pickle.dumps(data_to_cache)
        )
        text = texts.course_description.format(description=course.description)
        keyboard = kb.course_keyboard()

    await callback.message.edit_text(
        text=text,
        reply_markup=keyboard
    )


@router.callback_query(cb.CoursePricesCallback.filter())
async def selected_course_prices_callback(
        callback: types.CallbackQuery,
        callback_data: cb.CoursePricesCallback,
):
    await callback.message.edit_text(
        text=texts.prices_description.format(
            basic_price=utils.COURSE.prices['basic'][:-3],
            extended_price=utils.COURSE.prices['extended'][:-3]
        ),
        reply_markup=kb.selected_course_prices_keyboard(utils.COURSE.prices)
    )


@router.callback_query(cb.PayButtonCallback.filter())  # TODO отслеживать время создания платежа и создавать новый если время вышло
async def pay_button_callback(
        callback: types.CallbackQuery,
        callback_data: cb.CoursePartCallback
):
    cache: RedisDB = get_redis_db()
    price_type = callback_data.data
    user = callback.from_user

    data_from_cache = await cache.get(CacheKeyConstructor.user(user_id=user.id))
    user_from_cache = utils.bytes_to_user(data_from_cache) if data_from_cache else None

    if payment_data := user_from_cache.courses.get(utils.COURSE.id).payments_data.get(price_type, False) == 'canceled':
        user_payment_problems = await cache.get(CacheKeyConstructor.payment_issues(user_id=user.id))
        user_payment_problems = pickle.loads(user_from_cache) if user_payment_problems else list()
        user_payment_problems.append(payment_data)
        await cache.create(
            CacheKeyConstructor.payment_issues(user_id=user.id),
            pickle.dumps(user_payment_problems)
        )
        payment_info = create_payment(user.id, utils.COURSE, price_type)
        payment_link = payment_info.confirmation.confirmation_url

        user_from_cache.courses.get(utils.COURSE.id).payments_data[price_type] = None
        user_from_cache.courses.get(utils.COURSE.id).payment_links[price_type] = payment_link
        await cache.create(
            CacheKeyConstructor.user(user_id=user.id),
            pickle.dumps(user_from_cache)
        )

    elif not user_from_cache.courses.get(utils.COURSE.id).payment_links.get(price_type):
        payment_info = create_payment(user.id, utils.COURSE, price_type)
        payment_link = payment_info.confirmation.confirmation_url
        user_from_cache.courses.get(utils.COURSE.id).payment_links[price_type] = payment_link
        await cache.create(
            CacheKeyConstructor.user(user_id=user.id),
            pickle.dumps(user_from_cache)
        )
    else:
        payment_link = user_from_cache.courses.get(utils.COURSE.id).payment_links.get(price_type)

    await callback.message.edit_text(
        text=texts.chosen_course.format(
            course_name='\n\"Базовый пакет\"' if price_type == 'basic' else '\n\"Расширенный пакет с проверкой домашних заданий'
        ),
        reply_markup=kb.pay_course_keyboard(payment_link)
    )


@router.callback_query(cb.CoursePartCallback.filter())
async def selected_part_callback(
        callback: types.CallbackQuery,
        callback_data: cb.CoursePartCallback
):
    print(callback_data.data)
    course_id, part_id = utils.get_course_id_and_course_part_id(callback_data.data)
    course = utils.COURSE

    await callback.message.edit_text(
        text=texts.selected_part.format(
            course_name=course.name, part_id=part_id, description=course.parts[part_id]
        ),
        reply_markup=kb.selected_part_keyboard(course, part_id)
    )


@router.callback_query(cb.DownloadPartCallback.filter())
async def download_part_callback(
        callback: types.CallbackQuery,
        callback_data: cb.CoursePartCallback
):
    cache: RedisDB = get_redis_db()

    print(callback_data.data)
    course_id, part_id = utils.get_course_id_and_course_part_id(
        callback_data.data.replace('course_part_', '')
    )
    course = utils.COURSE
    link_key = cache_key_constructor.CacheKeyConstructor.link(callback.from_user.id, course.id, part_id)
    data_from_cache = await cache.get(link_key)
    data_from_cache = pickle.loads(data_from_cache) if data_from_cache else None

    if data_from_cache:
        seconds = 24 * 60 * 60 - (int(time.time() - data_from_cache['created']))
        seconds = seconds if seconds > 0 else 0
        remaining_time = utils.remaining_time(seconds)
    else:
        remaining_time = utils.remaining_time(24 * 60 * 60)
        data_to_cache = pickle.dumps({'created': int(time.time())})
        await cache.create(link_key, data_to_cache)

    text = texts.link_description.format(time=remaining_time)

    await callback.message.edit_text(
        text=text,
        reply_markup=kb.link_to_download_part_keyboard(link_key, course.id, part_id)
    )


async def about(message: types.Message):
    logging.info('About')
    await message.edit_text(
        text=texts.about,
        reply_markup=kb.back_button(
            callback_data="menu"
        )
    )


async def catalog(message: types.Message):
    logging.info('Catalog')
    await message.edit_text(f'Список курсов.', reply_markup=kb.catalog_keyboard())


@router.callback_query(cb.BackButtonCallback.filter())
async def back_button_callback(callback: types.CallbackQuery, callback_data: cb.BackButtonCallback):
    print(f'Back button, callback data: {callback_data.data}')
    if callback_data.data == 'menu':
        await callback.message.edit_text(
            text=texts.menu, reply_markup=kb.user_main_menu_keyboard()
        )
    elif callback_data.data == 'course':
        await callback.message.edit_text(
            text=texts.course_description.format(description=utils.COURSE.description),
            reply_markup=kb.course_keyboard()
        )
    elif 'payed_course' in callback_data.data:
        course_id = utils.get_course_id_and_course_part_id(
            callback_data.data.replace('payed_course_', '')
        )[0]
        course = utils.COURSE
        await callback.message.edit_text(
            text=texts.course_part_list.format(course_name=course.name),
            reply_markup=kb.payed_course_keyboard(course)
        )
    elif 'course_part' in callback_data.data:
        course_id, part_id = utils.get_course_id_and_course_part_id(
            callback_data.data.replace('course_part_', '')
        )
        course = utils.COURSE
        await callback.message.edit_text(
            text=texts.selected_part.format(
                course_name=course.name, part_id=part_id, description=course.parts[part_id]
            ),
            reply_markup=kb.selected_part_keyboard(course, part_id)
        )
