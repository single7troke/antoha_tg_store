import logging
import pickle
import time

from aiogram import types, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile

from core import *
from db.redis import get_redis_db, RedisDB
from models import User, UserCourse

router = Router()
config = get_config()

# TODO убрать принты, добавить логи

@router.message(Command(commands=('menu',)))
async def main_menu(message: types.Message):
    response = await message.bot.send_photo(
        chat_id=message.chat.id,
        photo=FSInputFile(
            config.path_to_files + '/image/horizontal.jpg',
            filename=f'pic_{time.time()}',
            chunk_size=4096
        ),
        reply_markup=kb.user_main_menu_keyboard()
    )
    await utils.clear_messages(message.bot, message.chat.id, response.message_id - 1)


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
            if not user_from_cache.invite_link:
                invite_link = await callback.bot.create_chat_invite_link(
                    chat_id=config.bot.group_id,
                    member_limit=1,
                )
                user_from_cache.invite_link = invite_link.invite_link
                await cache.create(CacheKeyConstructor.user(user_id=user.id), pickle.dumps(user_from_cache))
            if user_course.payed == 'extended':
                text += texts.invite_link_text.format(link=user_from_cache.invite_link)
        elif course_type := utils.course_already_payed(user_from_cache):
            print('Оплачен, но колбек почему-то не сработал')
            user_from_cache.courses.get(callback_data.data).payed = course_type
            text = texts.course_part_list.format(course_name=user_course.course.name)
            keyboard = kb.payed_course_keyboard(user_course.course)
            if course_type == 'extended':
                invite_link = await callback.bot.create_chat_invite_link(
                    chat_id=config.bot.group_id,
                    member_limit=1,
                )
                user_from_cache.invite_link = invite_link.invite_link
                text += texts.invite_link_text.format(link=user_from_cache.invite_link)
            await cache.create(CacheKeyConstructor.user(user_id=user.id), pickle.dumps(user_from_cache))
        else:
            print('Еще не оплачен')
            text = texts.course_description.format(description=user_course.course.description)
            keyboard = kb.course_keyboard()
    else:
        course = utils.COURSE
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

    await callback.message.edit_caption(
        caption=text,
        reply_markup=keyboard
    )


@router.callback_query(cb.CoursePricesCallback.filter())
async def selected_course_prices_callback(
        callback: types.CallbackQuery,
        callback_data: cb.CoursePricesCallback,
):
    await callback.message.edit_caption(
        caption=texts.prices_description.format(
            basic_price=utils.COURSE.prices['basic'][:-3],
            extended_price=utils.COURSE.prices['extended'][:-3]  # TODO это тоже хардкод, расценок может быть больше
        ),
        reply_markup=kb.selected_course_prices_keyboard(utils.COURSE.prices)
    )


@router.callback_query(cb.EnterEmailCallback.filter())
async def enter_email_callback(
        callback: types.CallbackQuery,
        callback_data: cb.EnterEmailCallback,
        state: FSMContext
):
    await state.set_state(form.Email.email)
    await state.update_data(price_type=callback_data.data)
    await callback.message.edit_caption(
        caption=texts.email_instruction,
        reply_markup=kb.back_button('course')
    )


@router.message(form.Email.email)
async def email_form(message: types.Message, state: FSMContext):
    data = await state.get_data()
    email = message.text
    if utils.is_valid_email(email):
        cache: RedisDB = get_redis_db()
        user = message.from_user
        data_from_cache = await cache.get(CacheKeyConstructor.user(user_id=user.id))
        user_from_cache = utils.bytes_to_user(data_from_cache) if data_from_cache else None
        user_from_cache.email = email

        await cache.create(
            CacheKeyConstructor.user(user_id=user.id),
            pickle.dumps(user_from_cache)
        )

        response = await message.bot.send_photo(
            chat_id=message.chat.id,
            caption=texts.email_new.format(email=email),
            photo=FSInputFile(
                config.path_to_files + '/image/horizontal.jpg',
                filename=f'pic_{time.time()}',
                chunk_size=4096
            ),
            reply_markup=kb.enter_or_confirm_email_keyboard(data.get('price_type'), enter_email=False)
        )
    else:
        response = await message.bot.send_photo(
            chat_id=message.chat.id,
            caption=texts.email_error.format(email=email),
            photo=FSInputFile(
                config.path_to_files + '/image/horizontal.jpg',
                filename=f'pic_{time.time()}',
                chunk_size=4096
            ),
            reply_markup=kb.enter_or_confirm_email_keyboard(data.get('price_type'), enter_email=True)
        )

    await utils.clear_messages(message.bot, message.chat.id, response.message_id - 1)


@router.callback_query(cb.CheckEmailCallback.filter())
async def check_email_callback(
        callback: types.CallbackQuery,
        callback_data: cb.CheckEmailCallback,
        state: FSMContext
):
    cache: RedisDB = get_redis_db()
    price_type = callback_data.data
    user = callback.from_user

    data_from_cache = await cache.get(CacheKeyConstructor.user(user_id=user.id))
    user_from_cache = utils.bytes_to_user(data_from_cache) if data_from_cache else None

    if not user_from_cache.email:
        await callback.message.edit_caption(
            caption=texts.email_need,
            reply_markup=kb.enter_or_confirm_email_keyboard(price_type, enter_email=True)
        )
    else:
        await callback.message.edit_caption(
            caption=texts.email_got.format(email=user_from_cache.email),
            reply_markup=kb.enter_or_confirm_email_keyboard(price_type, enter_email=False)
        )


@router.callback_query(cb.PayButtonCallback.filter())  # TODO отслеживать время создания платежа и создавать новый если время вышло
async def pay_button_callback(
        callback: types.CallbackQuery,
        callback_data: cb.CoursePartCallback,
        state: FSMContext
):
    await state.clear()
    cache: RedisDB = get_redis_db()
    price_type = callback_data.data
    user = callback.from_user

    data_from_cache = await cache.get(CacheKeyConstructor.user(user_id=user.id))
    user_from_cache = utils.bytes_to_user(data_from_cache) if data_from_cache else None
    payment_id = user_from_cache.courses.get(utils.COURSE.id).payment_ids.get(price_type, None)
    payment_data = get_payment(payment_id) if payment_id else None

    payment_link = None

    if not payment_data or user_from_cache.email != payment_data.metadata.get('email'):
        order_number = await cache.increase('order_number')
        # TODO передавать в create_payment пользователя(user.dict()) и там уже в metadata сохранять данные(не только id)
        new_payment = create_payment(user.id, utils.COURSE, price_type, user_from_cache.email, order_number)
        payment_link = new_payment.confirmation.confirmation_url
        user_from_cache.courses.get(utils.COURSE.id).payment_ids[price_type] = new_payment.id
        await cache.create(CacheKeyConstructor.user(user_id=user.id), pickle.dumps(user_from_cache))
    elif payment_data.status == 'pending':
        payment_link = payment_data.confirmation.confirmation_url
    elif payment_data.status == 'canceled':
        user_payment_problems = await cache.get(CacheKeyConstructor.payment_issues(user_id=user.id))
        user_payment_problems = pickle.loads(user_from_cache) if user_payment_problems else list()
        user_payment_problems.append(payment_id)
        await cache.create(
            CacheKeyConstructor.payment_issues(user_id=user.id),
            pickle.dumps(user_payment_problems)
        )
        order_number = await cache.increase('order_number')
        new_payment = create_payment(user.id, utils.COURSE, price_type, user_from_cache.email, order_number)
        payment_link = new_payment.confirmation.confirmation_url

        user_from_cache.courses.get(utils.COURSE.id).payment_ids[price_type] = new_payment.id
        await cache.create(
            CacheKeyConstructor.user(user_id=user.id),
            pickle.dumps(user_from_cache)
        )

    if not payment_link:
        await callback.message.edit_caption(
            caption='Error',  # TODO сделать текст ошибки если платеж неудалось создать + картинку с ошибкой(но тогда придется не edit_caption а edit_media)
            reply_markup=kb.back_button('menu')
        )
        return

    await callback.message.edit_caption(
        caption=texts.chosen_course.format(
            course_name='\n\"Базовый пакет\"' if price_type == 'basic' else '\n\"Расширенный пакет с проверкой домашних заданий\"'
        ),
        reply_markup=kb.pay_course_keyboard(payment_link)
    )


@router.callback_query(cb.CoursePartCallback.filter())
async def selected_part_callback(
        callback: types.CallbackQuery,
        callback_data: cb.CoursePartCallback
):
    print(callback_data.data)
    cache: RedisDB = get_redis_db()
    course_id, part_id = utils.get_course_id_and_course_part_id(callback_data.data)
    course = utils.COURSE

    link_key = cache_key_constructor.CacheKeyConstructor.link(callback.from_user.id, course.id, part_id)
    data_from_cache = await cache.get(link_key)
    data_from_cache = pickle.loads(data_from_cache) if data_from_cache else None
    if data_from_cache:
        seconds = 24 * 60 * 60 - (int(time.time() - data_from_cache['created']))
        if seconds > 0:
            remaining_time = utils.remaining_time(seconds)
            text = texts.link_description.format(time=remaining_time)

            await callback.message.edit_caption(
                caption=text,
                reply_markup=kb.link_to_download_part_keyboard(link_key, course.id, part_id, back_to_menu=True)
            )
            return
        else:
            await callback.message.edit_caption(
                caption='Время вышло',  # TODO добавить текст
                reply_markup=kb.back_button('course')
            )
            return

    await callback.message.edit_caption(
        caption=texts.selected_part.format(
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

    await callback.message.edit_caption(
        caption=text,
        reply_markup=kb.link_to_download_part_keyboard(link_key, course.id, part_id)
    )


async def about(message: types.Message):
    logging.info('About') # TODO прикрепить фотку к сообщению, текст будет в описании фотки bot.edit_message_media(caption=text)
    await message.edit_caption(
        caption=texts.about,
        reply_markup=kb.back_button(
            callback_data="menu"
        )
    )


async def catalog(message: types.Message):
    logging.info('Catalog')
    await message.edit_caption(caption=f'Список курсов.', reply_markup=kb.catalog_keyboard())


@router.callback_query(cb.BackButtonCallback.filter())
async def back_button_callback(
        callback: types.CallbackQuery,
        callback_data: cb.BackButtonCallback,
        state: FSMContext
):
    print(f'Back button, callback data: {callback_data.data}')
    await state.clear()
    from_id = callback.message.message_id - 1

    if callback_data.data == 'menu':
        await callback.message.edit_caption(reply_markup=kb.user_main_menu_keyboard())
    elif callback_data.data == 'course':
        await callback.message.edit_caption(
            caption=texts.course_description.format(description=utils.COURSE.description),
            reply_markup=kb.course_keyboard()
        )
    elif 'payed_course' in callback_data.data:
        course_id = utils.get_course_id_and_course_part_id(
            callback_data.data.replace('payed_course_', '')
        )[0]
        course = utils.COURSE
        await callback.message.edit_caption(
            caption=texts.course_part_list.format(course_name=course.name),
            reply_markup=kb.payed_course_keyboard(course)
        )
    elif 'course_part' in callback_data.data:
        course_id, part_id = utils.get_course_id_and_course_part_id(
            callback_data.data.replace('course_part_', '')
        )
        course = utils.COURSE
        await callback.message.edit_caption(
            caption=texts.selected_part.format(
                course_name=course.name, part_id=part_id, description=course.parts[part_id]
            ),
            reply_markup=kb.selected_part_keyboard(course, part_id)
        )

    await utils.clear_messages(callback.bot, callback.message.chat.id, from_id)
