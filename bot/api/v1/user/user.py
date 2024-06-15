import logging

from aiogram import types, Router
from aiogram.filters import Command

from core import utils, keyboard

router = Router()


@router.message(Command(commands=('menu',)))
async def main_menu(message: types.Message):
    await message.answer(text='Menu',
                         reply_markup=keyboard.user_main_menu_keyboard())


@router.callback_query(keyboard.MainMenuCallback.filter())
async def main_menu_callback_handler(callback: types.CallbackQuery, callback_data: keyboard.MainMenuCallback):
    if callback_data.data == 'about':
        await about(callback.message)
    elif callback_data.data == 'catalog':
        await catalog(callback.message)


@router.callback_query(keyboard.CourseCallback.filter())
async def selected_course_callback(callback: types.CallbackQuery, callback_data: keyboard.CourseCallback):
    course = await utils.get(callback_data.data)
    await callback.message.edit_text(
        text=f'description: {course.description}\n\nPrice: {course.price}',
        reply_markup=await keyboard.selected_course_keyboard()
    )


async def about(message: types.Message):
    logging.info('About')
    await message.edit_text(
        f'Тут\nбудет\nнебольшой\nили\nбольшой\nрассказ\nо себе',
        reply_markup=keyboard.back_button(
            callback_data="menu"
        )
    )


async def catalog(message: types.Message):
    logging.info(catalog)
    await message.edit_text(f'Список курсов.', reply_markup=await keyboard.catalog_keyboard())


async def selected_course_handler(message: types.Message):
    pass


@router.callback_query(keyboard.BackButtonCallback.filter())
async def back_button_callback(callback: types.CallbackQuery, callback_data: keyboard.BackButtonCallback):
    logging.info('Back button')
    # if callback_data.data == "event_list":
    #     data = await utils.event_list()
    #     events = data["events"]
    #     keyboard = keyboard.google_events_keyboard(events)
    #     await callback.message.edit_text(text="Events:", reply_markup=keyboard)
    if callback_data.data == "menu":
        await callback.message.edit_text(text="Menu", reply_markup=keyboard.user_main_menu_keyboard())
    elif callback_data.data == 'catalog':
        await catalog(callback.message)
