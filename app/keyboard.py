from aiogram.types import (ReplyKeyboardMarkup, KeyboardButton, 
                           InlineKeyboardMarkup, InlineKeyboardButton)

main = ReplyKeyboardMarkup(keyboard=[[KeyboardButton(text='Каталог')],
                                     [KeyboardButton(text='Корзина')],
                                     [KeyboardButton(text='Контакты'),
                                      KeyboardButton(text='О нас')]],
                           resize_keyboard=True,
                           input_field_placeholder='Выберите пункт меню...')

catalog = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='Кроссовки', callback_data="sneakers")],
    [InlineKeyboardButton(text='туфли', callback_data="shoes")],
    [InlineKeyboardButton(text='кеды', callback_data="cud")]])

def get_game_keyboard():
    buttons = [
        [InlineKeyboardButton(text="🔫 Выстрелить", callback_data="shoot")],
        [InlineKeyboardButton(text="🔄 Крутануть", callback_data="spin")],
        [InlineKeyboardButton(text="🏁 Закончить", callback_data="stop")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)