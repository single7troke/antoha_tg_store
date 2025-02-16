from datetime import datetime

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import Union, Optional

from core import get_config, texts, utils
from .callback import *
from models.models import Course

config = get_config()


def user_main_menu_keyboard():
    course = utils.COURSE
    buttons = [
        [InlineKeyboardButton(text=config.buttons.about, callback_data=MainMenuCallback(data="about").pack())],
        [InlineKeyboardButton(text=config.buttons.introduction, callback_data=MainMenuCallback(data='introduction').pack())],
        [InlineKeyboardButton(text=config.buttons.course, callback_data=CourseCallback(data=course.id).pack())]
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def back_button(callback_data):
    buttons = [
        [InlineKeyboardButton(
            text=config.buttons.back,
            callback_data=BackButtonCallback(data=callback_data).pack()
        )]
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)

    return keyboard


def catalog_keyboard():
    courses = utils.COURSE

    buttons = [
        [InlineKeyboardButton(text=course.name, callback_data=CourseCallback(data=course.id).pack())]
        for course in courses.values()
    ]
    buttons.append(
        [InlineKeyboardButton(text=config.buttons.back, callback_data=BackButtonCallback(data='menu').pack())]
    )

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def course_keyboard() -> InlineKeyboardMarkup:
    buttons = []
    if utils.is_sale_open() and not utils.is_sale_stopped():
        buttons.append(
            [InlineKeyboardButton(
                text=config.buttons.prices, callback_data=CoursePricesCallback(data='prices').pack()
            )]
        )
        buttons.append(
            [InlineKeyboardButton(
                text=config.buttons.lessons_description, callback_data=LessonsDescriptionCallback(data='lessons_description').pack()
            )]
        )

    buttons.append([InlineKeyboardButton(text=config.buttons.back, callback_data=BackButtonCallback(data='menu').pack())])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def selected_course_prices_keyboard(prices: dict, extended_course_available: bool) -> InlineKeyboardMarkup:
    buttons = []
    for course_type, price in prices.items():
        if course_type != 'extended' or extended_course_available:
            buttons.append(
                [InlineKeyboardButton(
                    text=config.buttons.buy.format(price=price[:-3]),
                    callback_data=CheckEmailCallback(data=course_type).pack()
                )]
            )

    buttons.append(
        [InlineKeyboardButton(text=config.buttons.back, callback_data=BackButtonCallback(data='course').pack())]
    )
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def enter_or_confirm_email_keyboard(course_type, enter_email):
    if enter_email:
        buttons = [
            [InlineKeyboardButton(text=config.buttons.enter_email, callback_data=EnterEmailCallback(data=course_type).pack())],
            [InlineKeyboardButton(text=config.buttons.back, callback_data=BackButtonCallback(data='course').pack())]
        ]
        return InlineKeyboardMarkup(inline_keyboard=buttons)

    buttons = [
        [InlineKeyboardButton(text=config.buttons.change_email, callback_data=EnterEmailCallback(data=course_type).pack())],
        [InlineKeyboardButton(text=config.buttons.next, callback_data=PayButtonCallback(data=course_type).pack())],
        [InlineKeyboardButton(text=config.buttons.back, callback_data=BackButtonCallback(data='course').pack())]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def pay_course_keyboard(payment_link: str):
    buttons = [
        [InlineKeyboardButton(text=config.buttons.link_to_pay, url=payment_link)],
        [InlineKeyboardButton(text=config.buttons.back, callback_data=BackButtonCallback(data='menu').pack())]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def paid_course_keyboard(course: Course, invite_link: Optional[str] = None):
    buttons = [
        [
            InlineKeyboardButton(
                text=f'{texts.part} {part}',
                callback_data=CoursePartCallback(data=f'{course.id}---{part}').pack()
            )
        ] for part, text in course.parts.items()
    ]

    buttons.append(
        [InlineKeyboardButton(text=config.buttons.back, callback_data=BackButtonCallback(data='menu').pack())]
    )

    if invite_link:
        buttons.insert(
            0,
            [InlineKeyboardButton(text=config.buttons.home_work, url=invite_link)])
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def course_part_keyboard(course_id: int, part_id: int) -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(
            text=config.buttons.back,
            callback_data=CoursePartCallback(data=f'{course_id}---{part_id}').pack()
        )]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def create_download_link_keyboard(course: Course, part_id: int):
    buttons = [
        [InlineKeyboardButton(
            text=texts.get_download_link,
            callback_data=CreateDownloadLink(data=f'{course.id}---{part_id}').pack()
        )],
        [InlineKeyboardButton(
            text=config.buttons.back,
            callback_data=BackButtonCallback(data=f'paid_course_{course.id}---{part_id}').pack()
        )]
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def link_to_download_part_keyboard(link_key: str, course_id, part_id, back_to_menu=False):
    url = utils.get_download_link(link_key)
    buttons = [
        [InlineKeyboardButton(text=config.buttons.download, url=url)],
        [InlineKeyboardButton(
            text=config.buttons.back,
            callback_data=BackButtonCallback(
                data=f'course_part_{course_id}---{part_id}' if not back_to_menu else f'paid_course_{course_id}---{part_id}'
            ).pack()
        )]
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def admin_main_menu_keyboard():
    buttons = [
        [InlineKeyboardButton(
            text='Информация о пользователе',
            callback_data=AdminMainMenuCallback(data='user').pack()
        )],
        [InlineKeyboardButton(
            text='Купившие расширенный курс',
            callback_data=AdminMainMenuCallback(data='extended_buyers').pack()
        )],
        [InlineKeyboardButton(
            text='Купившие базовый курс',
            callback_data=AdminMainMenuCallback(data='basic_buyers').pack()
        )],
        [InlineKeyboardButton(
            text='Статистика покупок',
            callback_data=AdminMainMenuCallback(data='stats').pack()
        )],
        [InlineKeyboardButton(
            text='Информация о платеже',
            callback_data=AdminMainMenuCallback(data='payment').pack()
        )],
        [InlineKeyboardButton(
            text='Выдать доступ к курсу',
            callback_data=AdminMainMenuCallback(data='grant_access').pack()
        )],
        [InlineKeyboardButton(
            text='Продлить доступ к курсу',
            callback_data=AdminMainMenuCallback(data='extend_access').pack()
        )]
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)
