from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def create_kb_news_fact() -> InlineKeyboardMarkup:
    kb: InlineKeyboardBuilder = InlineKeyboardBuilder()
    kb.add(InlineKeyboardButton(text='Новости', callback_data='news'),
           InlineKeyboardButton(text='Интересный факт', callback_data='fact'))
    return kb.as_markup()


def create_kb_correct() -> InlineKeyboardMarkup:
    kb: InlineKeyboardBuilder = InlineKeyboardBuilder()
    kb.add(InlineKeyboardButton(text='Опубликовать', callback_data='publish'),
           InlineKeyboardButton(text='Заполнить заново', callback_data='reset'))
    return kb.as_markup()


def create_kb_when_publish() -> InlineKeyboardMarkup:
    kb: InlineKeyboardBuilder = InlineKeyboardBuilder()
    kb.add(InlineKeyboardButton(text='Прямо сейчас', callback_data='now'),
           InlineKeyboardButton(text='Ввести время и дату', callback_data='other_time'))
    return kb.as_markup()
