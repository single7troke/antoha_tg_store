from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

from core import get_config
from .callback import *
from models.models import Course

config = get_config()

COURSES = [
    Course(id=1001, name='first course', price='1000.00', description='Описание\nкурса\nномер\nраз'),
    Course(id=1002, name='second course', price='123.00', description='Описание\nкурса\nномер\nдва'),
    Course(id=1003, name='Third course', price='500.00')
]


def user_main_menu_keyboard():
    buttons = [
        [types.InlineKeyboardButton(text=config.buttons.about, callback_data=MainMenuCallback(data="about").pack())],
        [types.InlineKeyboardButton(text=config.buttons.catalog, callback_data=MainMenuCallback(data="catalog").pack())]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def back_button(callback_data):
    buttons = [
        [types.InlineKeyboardButton(
            text=config.buttons.back,
            callback_data=BackButtonCallback(data=callback_data).pack()
        )]
    ]
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


async def catalog_keyboard():
    courses = COURSES

    buttons = [
        [types.InlineKeyboardButton(text=course.name, callback_data=CourseCallback(data=course.id).pack())]
        for course in courses
    ]
    buttons.append(
        [types.InlineKeyboardButton(text=config.buttons.back, callback_data=BackButtonCallback(data='menu').pack())]
    )

    return types.InlineKeyboardMarkup(inline_keyboard=buttons)


async def selected_course_keyboard(payment_link):
    buttons = [
        [types.InlineKeyboardButton(text=config.buttons.buy, url=payment_link)],
        # [types.InlineKeyboardButton(text=config.buttons.buy, pay=True)],
        [types.InlineKeyboardButton(text=config.buttons.back, callback_data=BackButtonCallback(data='catalog').pack())]
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=buttons)
