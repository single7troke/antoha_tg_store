from aiogram import types
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

from .config import Config
from .callback import *
from models.models import Course

config = Config()

COURSES = [
    Course(id=1, name='first course', price=1000, description='Описание\nкурса\nномер\nраз'),
    Course(id=2, name='second course', price=99999, description='Описание\nкурса\nномер\nдва'),
    Course(id=3, name='Third course', price=23)
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


async def selected_course_keyboard():
    buttons = [
        # [types.InlineKeyboardButton(text='Купить')],
        [types.InlineKeyboardButton(text=config.buttons.back, callback_data=BackButtonCallback(data='catalog').pack())]
    ]
    return types.InlineKeyboardMarkup(inline_keyboard=buttons)
