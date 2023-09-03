from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def create_kb_for_publishing() -> InlineKeyboardMarkup:
    kb: InlineKeyboardBuilder = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text='Публикуем', callback_data='send'),
           InlineKeyboardButton(text='Заполнить заново', callback_data='refill')
           )
    return kb.as_markup()
