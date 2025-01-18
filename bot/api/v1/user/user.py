import logging
import pickle
import time
from datetime import datetime, timedelta, timezone

from aiogram import types, Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import FSInputFile

from core import *
from db.redis import get_redis_db, RedisDB
from models import User, UserCourse

router = Router()
config = get_config()

logger = logging.getLogger(__name__)

# TODO добавить описание к каждой функции


@router.message(Command(commands=('menu', 'start',)))
async def main_menu(message: types.Message):
    logger.info(f'Main menu. '
                f'user_id: {message.from_user.id}, '
                f'user_name: {message.from_user.username}')
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


@router.message(Command(commands=('support',)))
async def support(message: types.Message):
    logger.info(f'Support menu. '
                f'user_id: {message.from_user.id}, '
                f'user_name: {message.from_user.username}')
    response = await message.bot.send_message(
        chat_id=message.chat.id,
        text=texts.support_message.format(user_id=message.from_user.id, username=config.bot.support_address),
    )
    await utils.clear_messages(message.bot, message.chat.id, response.message_id - 1)


@router.callback_query(cb.MainMenuCallback.filter())
async def main_menu_callback_handler(callback: types.CallbackQuery, callback_data: cb.MainMenuCallback):
    if callback_data.data == 'about':
        await about(callback.message)
    elif callback_data.data == 'introduction':
        cache = get_redis_db()
        data_from_cache = await cache.get('intro_video_data')
        intro_video_data = pickle.loads(data_from_cache) if data_from_cache else None
        response = await callback.bot.send_video(
            chat_id=callback.message.chat.id,
            caption=texts.introduction_text,
            width=1280,
            height=720,
            video=intro_video_data['file_id'] if intro_video_data else FSInputFile(
                config.path_to_files + config.intro_video_path,
                filename=f'introduction_video',
                chunk_size=4096
            ),
            reply_markup=kb.back_button('introduction'),
            request_timeout=30
        )
        if not intro_video_data:
            await cache.create(object_id='intro_video_data', data=pickle.dumps(response.video.dict()))

        await utils.clear_messages(callback.bot, callback.message.chat.id, response.message_id - 1)


@router.callback_query(cb.CourseCallback.filter())
async def selected_course_callback(
        callback: types.CallbackQuery,
        callback_data: cb.CourseCallback,
):
    cache: RedisDB = get_redis_db()
    user = callback.from_user

    data_from_cache = await cache.get(CacheKeyConstructor.user(user_id=user.id))
    user_from_cache = utils.bytes_to_user(data_from_cache) if data_from_cache else None
    captured_at = None
    download_opened = utils.is_download_open()
    text = ''

    if user_from_cache:
        user_course = user_from_cache.courses.get(callback_data.data)
        if user_course and (user_course.paid or user_course.promo_access):
            logger.info(f'Paid course. '
                        f'user_id: {user.id}, '
                        f'user_name: {callback.from_user.username}, '
                        f'course_id: {user_course.course.id}, '
                        f'course_type: {user_course.paid}'
                        f'promo_access: {user_course.promo_access}')

            if user_course.paid == 'extended':
                if not user_from_cache.invite_link:
                    invite_link = await callback.bot.create_chat_invite_link(
                        chat_id=config.bot.group_id,
                        member_limit=1,
                    )
                    user_from_cache.invite_link = invite_link.invite_link
                    await cache.create(CacheKeyConstructor.user(user_id=user.id), pickle.dumps(user_from_cache))
                text += texts.invite_link_text

            captured_at = user_course.captured_at
            keyboard = kb.paid_course_keyboard(user_course.course, user_from_cache.invite_link)

        elif course_type := utils.course_already_paid(user_from_cache):
            logger.info(
                f'Paid course, but somthing was wrong with callback. '
                f'user_id: {user.id}, '
                f'user_name: {callback.from_user.username}, '
                f'course_id: {user_course.course.id}, '
                f'course_type: {user_course.paid}'
            )
            captured_at = utils.get_payment_captured_at(user_from_cache, course_type)
            user_from_cache.courses.get(callback_data.data).paid = course_type
            user_from_cache.courses.get(callback_data.data).captured_at = captured_at
            text = texts.course_description.format(description=user_course.course.description)

            if course_type == 'extended':
                invite_link = await callback.bot.create_chat_invite_link(
                    chat_id=config.bot.group_id,
                    member_limit=1,
                )
                user_from_cache.invite_link = invite_link.invite_link
                text += texts.invite_link_text

            keyboard = kb.paid_course_keyboard(user_course.course, user_from_cache.invite_link)
            await cache.create(CacheKeyConstructor.user(user_id=user.id), pickle.dumps(user_from_cache))
        else:
            logger.info(f'Not paid. user_id: {user.id}, user_name: {callback.from_user.username}')
            text = texts.course_description.format(description=user_course.course.description)
            keyboard = kb.course_keyboard()
    else:
        logger.info(f'New user. user_id: {user.id}, user_name: {callback.from_user.username}')
        course = utils.COURSE
        data_to_cache = User(
            courses={course.id: UserCourse(course=course)},
            tg_user_data=user.dict()
        )
        await cache.create(
            CacheKeyConstructor.user(user_id=user.id),
            pickle.dumps(data_to_cache)
        )
        text = texts.course_description.format(description=course.description)
        keyboard = kb.course_keyboard()

    if not utils.is_sale_open():
        logger.info(f'Sale not open. user_id: {user.id}, user_name: {callback.from_user.username}')
        text += texts.sales_start_dt.format(
            sales_start_dt=config.sales_start_dt.strftime("%Y-%m-%d %H:%M")
        )

    if utils.is_sale_stopped() and not captured_at:
        text += texts.sales_stopped

    if not download_opened and captured_at:
        text += texts.download_start_time_msg.format(
            time=config.download_start_dt.strftime("%Y-%m-%d %H:%M")
        )
        keyboard = kb.back_button('menu')
    elif download_opened and captured_at:
        moscow_tz = timezone(timedelta(hours=config.time_zone))
        captured_at = datetime.fromisoformat(
            captured_at.replace("Z", "+00:00")
        )
        if captured_at < config.download_start_dt:
            captured_at = config.download_start_dt

        can_download_before = captured_at + timedelta(
            days=config.days_to_download_course_after_payment,
            hours=config.time_zone
        )
        if datetime.now(moscow_tz).date() <= can_download_before.replace(tzinfo=moscow_tz).date():
            text += texts.paid_course_expire_information_msg.format(time=can_download_before.strftime("%d %b %Y"))
        else:
            text = texts.paid_course_expired_msg
            keyboard = kb.back_button('menu')

    await callback.message.edit_caption(
        caption=text,
        reply_markup=keyboard
    )


@router.callback_query(cb.CoursePricesCallback.filter())
async def selected_course_prices_callback(
        callback: types.CallbackQuery,
        callback_data: cb.CoursePricesCallback,
):
    logger.info(f'Prices. user_id: {callback.from_user.id}, user_name: {callback.from_user.username}')
    text = texts.price_description['basic'].format(basic_price=utils.COURSE.prices['basic'][:-3])
    cache: RedisDB = get_redis_db()
    extended_course_sold_quantity = await cache.get('extended_course_sold_quantity')
    extended_course_available = utils.is_extended_course_available(int(extended_course_sold_quantity.decode()))

    if extended_course_available:
        text += texts.price_description['extended'].format(
            extended_price=utils.COURSE.prices['extended'][:-3],
            end_of_sale_time=config.stop_selling_extended_course_dt.replace(microsecond=0, tzinfo=None)
        )

    await callback.message.edit_caption(
        caption=text,
        reply_markup=kb.selected_course_prices_keyboard(utils.COURSE.prices, extended_course_available)
    )


@router.callback_query(cb.LessonsDescriptionCallback.filter())
async def selected_course_lessons_description_callback(
        callback: types.CallbackQuery,
        callback_data: cb.CoursePricesCallback,
):
    logger.info(f'Lessons description. user_id: {callback.from_user.id}, user_name: {callback.from_user.username}')
    text = ''
    for lesson_num, desc in utils.COURSE.parts.items():
        text += f'<b>Урок {lesson_num}</b>\n{desc}\n'

    response = await callback.bot.send_message(
        chat_id=callback.message.chat.id,
        text=text,
        reply_markup=kb.back_button('lessons_description')
    )

    await utils.clear_messages(callback.bot, callback.message.chat.id, response.message_id - 1)


@router.callback_query(cb.EnterEmailCallback.filter())
async def enter_email_callback(
        callback: types.CallbackQuery,
        callback_data: cb.EnterEmailCallback,
        state: FSMContext
):
    logger.info(f'user_id: {callback.from_user.id}, user_name: {callback.from_user.username}')
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
        logger.info(f'Valid email'
                    f'user_id: {message.from_user.id}, '
                    f'user_name: {message.from_user.username}, '
                    f'email: {email}')
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
        logger.info(f'invalid email'
                    f'user_id: {message.from_user.id}, '
                    f'user_name: {message.from_user.username},'
                    f'entered_email: {email}')
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
        logger.info(f'Need email'
                    f'user_id: {callback.from_user.id}, '
                    f'user_name: {callback.from_user.username},')
        await callback.message.edit_caption(
            caption=texts.email_need,
            reply_markup=kb.enter_or_confirm_email_keyboard(price_type, enter_email=True)
        )
    else:
        logger.info(f'Got email'
                    f'user_id: {callback.from_user.id}, '
                    f'user_name: {callback.from_user.username}, '
                    f'email: {user_from_cache.email}')
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
        order_number = await cache.increase('receipt_number')
        new_payment = create_payment(user.dict(), utils.COURSE, price_type, user_from_cache.email, order_number)
        payment_link = new_payment.confirmation.confirmation_url
        user_from_cache.courses.get(utils.COURSE.id).payment_ids[price_type] = new_payment.id
        await cache.create(CacheKeyConstructor.user(user_id=user.id), pickle.dumps(user_from_cache))
        logger.info(f'user_id: {callback.from_user.id}, new payment created: {new_payment.id}')
    elif payment_data.status == 'pending':
        logger.info(f'Payment pending'
                    f'user_id: {callback.from_user.id}, '
                    f'user_name: {callback.from_user.username}, '
                    f'payment_id: {payment_data.id}')
        payment_link = payment_data.confirmation.confirmation_url
    elif payment_data.status == 'canceled':
        logger.info(
            f'Payment canceled'
            f'user_id: {callback.from_user.id}, '
            f'user_name: {callback.from_user.username}, '
            f'payment_id: {payment_data.id}')
        user_payment_problems = await cache.get(CacheKeyConstructor.payment_issues(user_id=user.id))
        user_payment_problems = pickle.loads(user_from_cache) if user_payment_problems else list()
        user_payment_problems.append(payment_id)
        await cache.create(
            CacheKeyConstructor.payment_issues(user_id=user.id),
            pickle.dumps(user_payment_problems)
        )
        order_number = await cache.increase('receipt_number')
        new_payment = create_payment(user.dict(), utils.COURSE, price_type, user_from_cache.email, order_number)
        payment_link = new_payment.confirmation.confirmation_url

        user_from_cache.courses.get(utils.COURSE.id).payment_ids[price_type] = new_payment.id
        await cache.create(
            CacheKeyConstructor.user(user_id=user.id),
            pickle.dumps(user_from_cache)
        )
        logger.info(f'New payment created'
                    f'user_id: {callback.from_user.id}, '
                    f'user_name: {callback.from_user.username}, '
                    f'payment_id: {new_payment.id}')

    if not payment_link:
        await callback.message.edit_caption(
            caption='Извините, возникла проблема,\nпопробуйте позже.', # TODO сделать текст ошибки если платеж неудалось создать + картинку с ошибкой(но тогда придется не edit_caption а edit_media)
            reply_markup=kb.back_button('menu')
        )
        logger.error(f'Payment ERROR. user_id: {callback.from_user.id}, user_name: {callback.from_user.username}')
        return

    text = texts.chosen_course_type.format(
            course_type='\n\"Базовый пакет\"' if price_type == 'basic' else '\n\"Расширенный пакет с проверкой домашних заданий\"'
        )
    text += texts.offer_rules

    await callback.message.edit_caption(
        caption=text,
        reply_markup=kb.pay_course_keyboard(payment_link)
    )


@router.callback_query(cb.CoursePartCallback.filter())
async def course_part_callback(
        callback: types.CallbackQuery,
        callback_data: cb.CoursePartCallback
):
    cache: RedisDB = get_redis_db()
    course_id, part_id = utils.get_course_id_and_course_part_id(callback_data.data)
    course = utils.COURSE

    link_key = cache_key_constructor.CacheKeyConstructor.link(callback.from_user.id, course.id, part_id)
    data_from_cache = await cache.get(link_key)
    link_data = pickle.loads(data_from_cache) if data_from_cache else None
    if link_data:
        seconds = 24 * 60 * 60 - (int(time.time() - link_data['created']))
        if seconds > 0:
            remaining_time = utils.remaining_time(seconds)
            logger.info(
                f'Valid link. '
                f'user_id: {callback.from_user.id}, '
                f'user_name: {callback.from_user.username}, '
                f'course_id: {course_id},  part_id: {part_id}, '
                f'remaining_time: {remaining_time}'
            )
            text = texts.selected_part.format(
                course_name=course.name, part_id=part_id, description=course.parts[part_id]
            )
            text += texts.link_description.format(time=remaining_time)

            await callback.message.edit_caption(
                caption=text,
                reply_markup=kb.link_to_download_part_keyboard(link_key, course.id, part_id, back_to_menu=True)
            )
            return
        else:
            logger.info(
                f'Link exired. '
                f'user_id: {callback.from_user.id}, '
                f'user_name: {callback.from_user.username},'
                f'course_id: {course_id} part_id: {part_id} expired'
            )
            await callback.message.edit_caption(
                caption=texts.link_expired,
                reply_markup=kb.back_button(f'paid_course_{course_id}---{part_id}')
            )
            return

    logger.info(
        f'No link to download course part. '
        f'user_id: {callback.from_user.id}, '
        f'user_name: {callback.from_user.username}, '
        f'course_id: {course_id} part_id: {part_id}'
    )
    await callback.message.edit_caption(
        caption=texts.selected_part.format(
            course_name=course.name, part_id=part_id, description=course.parts[part_id]
        ) + texts.link_expire_info,
        reply_markup=kb.create_download_link_keyboard(course, part_id)
    )


@router.callback_query(cb.CreateDownloadLink.filter())
async def create_download_link_callback(
        callback: types.CallbackQuery,
        callback_data: cb.CreateDownloadLink
):
    cache: RedisDB = get_redis_db()

    course_id, part_id = utils.get_course_id_and_course_part_id(
        callback_data.data.replace('course_part_', '')
    )
    course = utils.COURSE
    link_key = cache_key_constructor.CacheKeyConstructor.link(callback.from_user.id, course.id, part_id)
    data_to_cache = pickle.dumps({'created': int(time.time())})
    await cache.create(link_key, data_to_cache)
    logger.info(
        f'Link created. user_id: {callback.from_user.id}, user_name: {callback.from_user.username}, course_id: {course_id}, part_id: {part_id}, link_key: {link_key}'
    )

    await callback.message.edit_caption(
        caption=texts.link_created,
        reply_markup=kb.course_part_keyboard(course_id, part_id)
    )


async def about(message: types.Message):
    logger.info(f'About. user_id: {message.from_user.id}, user_name: {message.from_user.username}')
    await message.edit_caption(
        caption=texts.about,
        reply_markup=kb.back_button(
            callback_data="menu"
        )
    )


async def catalog(message: types.Message):  # Не используется
    logger.info('Catalog')
    await message.edit_caption(caption=f'Список курсов.', reply_markup=kb.catalog_keyboard())


@router.callback_query(cb.BackButtonCallback.filter(F.data != 'admin_main_menu'))  # TODO переделать? кнопка назад идет не с колбеком BackButtonCallback.
async def back_button_callback(
        callback: types.CallbackQuery,
        callback_data: cb.BackButtonCallback,
        state: FSMContext
):
    logger.info(f'Back button.'
                f'user_id: {callback.from_user.id}, '
                f'user_name: {callback.from_user.username}, '
                f'callback_data: {callback_data.data}')
    await state.clear()
    cache = get_redis_db()
    data_from_cache = await cache.get(CacheKeyConstructor.user(user_id=callback.from_user.id))
    user_from_cache = utils.bytes_to_user(data_from_cache) if data_from_cache else None
    from_id = callback.message.message_id - 1

    if callback_data.data == 'menu':
        await callback.message.edit_caption(reply_markup=kb.user_main_menu_keyboard())
    elif callback_data.data == 'course':
        await callback.message.edit_caption(
            caption=texts.course_description.format(description=utils.COURSE.description),
            reply_markup=kb.course_keyboard()
        )
    elif callback_data.data == 'lessons_description':
        response = await callback.bot.send_photo(
            chat_id=callback.message.chat.id,
            photo=FSInputFile(
                config.path_to_files + '/image/horizontal.jpg',
                filename=f'pic_{time.time()}',
                chunk_size=4096
            ),
            caption=texts.course_description.format(description=utils.COURSE.description),
            reply_markup=kb.course_keyboard()
        )
        from_id = response.message_id - 1
    elif 'paid_course' in callback_data.data:
        # course_id = utils.get_course_id_and_course_part_id(
        #     callback_data.data.replace('paid_course_', '')
        # )[0]
        course = utils.COURSE
        await callback.message.edit_caption(
            caption=texts.course_description.format(description=course.description),
            reply_markup=kb.paid_course_keyboard(course, user_from_cache.invite_link)
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
            reply_markup=kb.course_part_keyboard(course_id, part_id)
        )
    elif 'introduction' in callback_data.data:
        await main_menu(callback.message)
        from_id = callback.message.message_id

    await utils.clear_messages(callback.bot, callback.message.chat.id, from_id)
