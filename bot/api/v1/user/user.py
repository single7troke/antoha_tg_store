import json
import logging
import pickle

from aiogram import types, Router
from aiogram.filters import Command
from aiogram.methods.send_invoice import SendInvoice
from yookassa import Payment

from core import *
from db.redis import get_redis_db, RedisDB
from models import User, UserCourse
from core import info_messages

router = Router()
config = get_config()


@router.message(Command(commands=('menu',)))
async def main_menu(message: types.Message):
    await message.answer(text='Menu',
                         reply_markup=kb.user_main_menu_keyboard())


@router.callback_query(cb.MainMenuCallback.filter())
async def main_menu_callback_handler(callback: types.CallbackQuery, callback_data: cb.MainMenuCallback):
    if callback_data.data == 'about':
        await about(callback.message)
    elif callback_data.data == 'catalog':
        await catalog(callback.message)


@router.callback_query(cb.CourseCallback.filter())
async def selected_course_callback(
        callback: types.CallbackQuery,
        callback_data: cb.CourseCallback,
):
    cache: RedisDB = get_redis_db()
    user = callback.from_user

    user_from_cache = await cache.get(CacheKeyConstructor.tg_id_key(user_id=user.id))
    user_from_cache = pickle.loads(user_from_cache) if user_from_cache else None
    if user_from_cache and (user_course := user_from_cache.courses.get(callback_data.data)):
        if user_course.payment_data['status'] == 'succeeded':
            print('Оплачен')
            text = info_messages.already_paid
            keyboard = kb.back_button('catalog')
        elif user_course.payment_data['status'] == 'canceled':
            print('Проблема')
            new_payment = create_payment(user_id=user.id, course=user_course)
            user_course.payment_link = new_payment.confirmation.confirmation_url
            user_course.payment_data = None
            await cache.create(
                CacheKeyConstructor.tg_id_key(user_id=user.id),
                pickle.dumps(user_from_cache)
            )

            user_payment_problems = await cache.get(CacheKeyConstructor.tg_id_payment_problems_key(user_id=user.id))
            user_payment_problems = pickle.loads(user_from_cache) if user_payment_problems else list()
            user_payment_problems.append(user_course.payment_data)
            await cache.create(
                CacheKeyConstructor.tg_id_payment_problems_key(user_id=user.id),
                pickle.dumps(user_payment_problems)
            )

            text = info_messages.canceled
            keyboard = await kb.selected_course_keyboard(user_course.payment_link)

        else:
            print('Еще не оплачен')
            text = f'Описание курса: {user_course.course.description}\n\nЦена: {user_course.course.price}'
            keyboard = await kb.selected_course_keyboard(user_course.payment_link)
    else:
        course = await utils.get(callback_data.data)
        payment = create_payment(user_id=user.id, course=course)
        if user_from_cache:
            print('Есть какие-то курсы в каком-то статусе, но этого нет')
            user_from_cache.courses[course.id] = UserCourse(course=course, payment_link=payment)
            data_to_cache = user_from_cache
        else:
            print('Вообще новый юзер')
            data_to_cache = User(
                courses={course.id: UserCourse(course=course, payment_link=payment.confirmation.confirmation_url)}
            )
        await cache.create(
            CacheKeyConstructor.tg_id_key(user_id=user.id),
            pickle.dumps(data_to_cache)
        )
        text = f'Описание курса: {course.description}\n\nЦена: {course.price}'
        keyboard = await kb.selected_course_keyboard(payment['confirmation']['confirmation_url'])

    await callback.message.edit_text(
        text=text,
        reply_markup=keyboard
    )
    # return await payment_callback(callback)


@router.callback_query(cb.PayButtonCallback.filter())
async def payment_callback(callback: types.CallbackQuery):
    return SendInvoice(
        # await callback.message.answer_invoice(
        chat_id=callback.message.chat.id,
        title='hello',
        description='description',
        provider_token=config.bot.pay_token,
        currency='RUB',
        prices=[types.LabeledPrice(amount=100000, label='price')],
        # start_parameter='time-machine-example',
        payload='some-invoice-payload-for-our-internal-use',
    )


async def about(message: types.Message):
    logging.info('About')
    await message.edit_text(
        f'Тут\nбудет\nнебольшой\nили\nбольшой\nрассказ\nо себе',
        reply_markup=kb.back_button(
            callback_data="menu"
        )
    )


async def catalog(message: types.Message):
    logging.info(catalog)
    await message.edit_text(f'Список курсов.', reply_markup=await kb.catalog_keyboard())


@router.callback_query(cb.BackButtonCallback.filter())
async def back_button_callback(callback: types.CallbackQuery, callback_data: cb.BackButtonCallback):
    logging.info('Back button')
    # if callback_data.data == "event_list":
    #     data = await utils.event_list()
    #     events = data["events"]
    #     keyboard = keyboard.google_events_keyboard(events)
    #     await callback.message.edit_text(text="Events:", reply_markup=keyboard)
    if callback_data.data == "menu":
        await callback.message.edit_text(text="Menu", reply_markup=kb.user_main_menu_keyboard())
    elif callback_data.data == 'catalog':
        await catalog(callback.message)
