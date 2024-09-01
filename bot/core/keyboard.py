from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from typing import Union

from core import get_config, texts, utils
from .callback import *
from models.models import Course

config = get_config()


def user_main_menu_keyboard():
    course = utils.COURSE
    buttons = [
        [InlineKeyboardButton(text=config.buttons.about, callback_data=MainMenuCallback(data="about").pack())],
        [InlineKeyboardButton(text=course.name, callback_data=CourseCallback(data=course.id).pack())]
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


def course_keyboard():
    buttons = [
        [InlineKeyboardButton(text=config.buttons.prices, callback_data=CoursePricesCallback(data='prices').pack())],
        [InlineKeyboardButton(text=config.buttons.back, callback_data=BackButtonCallback(data='menu').pack())]
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def selected_course_prices_keyboard(prices: dict):
    buttons = list()
    print(prices)

    for course_type, price in prices.items():
        buttons.append(
            [InlineKeyboardButton(
                text=config.buttons.buy.format(price=price[:-3]),
                callback_data=PayButtonCallback(data=course_type).pack())]
        )

    buttons.append(
        [InlineKeyboardButton(text=config.buttons.back, callback_data=BackButtonCallback(data='course').pack())]
    )
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def pay_course_keyboard(payment_link: str):
    buttons = [
        [InlineKeyboardButton(text=config.buttons.link_to_pay, url=payment_link)],
        [InlineKeyboardButton(text=config.buttons.back, callback_data=BackButtonCallback(data='course').pack())]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def payed_course_keyboard(course: Course):
    buttons = [
        [
            InlineKeyboardButton(
                text=f'{texts.part} {part}',
                callback_data=CoursePartCallback(data=f'{course.id}---{part}').pack()
            )
        ] for part, text in course.parts.items()
    ]

    buttons.append(
        [InlineKeyboardButton(text=config.buttons.back, callback_data=BackButtonCallback(data='catalog').pack())]
    )
    print(buttons)

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def selected_part_keyboard(course: Course, part_id: int):
    buttons = [
        [InlineKeyboardButton(
            text=texts.download_link_button_text,
            callback_data=DownloadPartCallback(data=f'{course.id}---{part_id}').pack()
        )],
        [InlineKeyboardButton(
            text=config.buttons.back,
            callback_data=BackButtonCallback(data=f'payed_course_{course.id}---{part_id}').pack()
        )]
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def link_to_download_part_keyboard(link_key: str, course_id, part_id):
    url = utils.get_download_link(link_key)
    buttons = [
        [InlineKeyboardButton(text=texts.link_button_text, url=url)],
        [InlineKeyboardButton(
            text=config.buttons.back,
            callback_data=BackButtonCallback(data=f'course_part_{course_id}---{part_id}').pack()
        )]
    ]

    return InlineKeyboardMarkup(inline_keyboard=buttons)
