from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

import names

import datetime

from aiogram.utils.keyboard import InlineKeyboardBuilder

from service.days import days_for_choosing
from service.posts import create_days


def create_kb_for_days(data: str) -> InlineKeyboardMarkup:
    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    if datetime.datetime.now() + datetime.timedelta(hours=names.name.utc) > datetime.datetime.strptime(
            names.name.dates['0'] + ' 23:59:59.999999', names.name.time_format):
        names.name.dates = days_for_choosing()
    buttons = []
    for key, value in names.name.dates.items():
        buttons.append(InlineKeyboardButton(text=value, callback_data=f'{data}/{key}'))
    kb_builder.row(*buttons, width=2)
    kb_builder.row(InlineKeyboardButton(text='Не публиковать', callback_data=f"don't_send/{data.split('/')[1]}")).add(
        InlineKeyboardButton(text='Опубликовать сейчас', callback_data=f'send_now/{data.split("/")[1]}'))
    return kb_builder.as_markup()


def create_kb_for_choosing_time(data: str) -> InlineKeyboardMarkup:
    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    info = data.split('/')
    if datetime.datetime.now() + datetime.timedelta(hours=names.name.utc) > datetime.datetime.strptime(
            names.name.days[str(names.name.count)] + ' 23:59:59.999999', names.name.time_format):
        names.name.days = create_days()
    buttons = []
    for value in names.name.days.get(str(info[-1])):
        buttons.append(InlineKeyboardButton(text=value[5:], callback_data=f'{data}/{value}'))
    kb_builder.row(*buttons, width=3)
    kb_builder.row(InlineKeyboardButton(text='◀️Назад', callback_data=f'{info[0]}/{info[1]}')).add(
        InlineKeyboardButton(text='Не публиковать', callback_data=f"don't_send/{info[1]}")).add(
        InlineKeyboardButton(text='Опубликовать сейчас', callback_data=f'send_now/{info[1]}')
    )
    return kb_builder.as_markup()


def create_kb_for_not_published_stories(value):
    kb = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text='Предыдущая', callback_data=f'previous_story/{value}'),
           InlineKeyboardButton(text='Выбрать',
                                callback_data=f'not_published/{names.name.stories_id[value]}'),
           InlineKeyboardButton(text='Следующая', callback_data=f'next_story/{value}'), width=3)
    return kb.row(InlineKeyboardButton(text='Закончить просмотр', callback_data=f'close_stories/{value}')).as_markup()


def create_kb_button(data) -> InlineKeyboardMarkup:
    kb: InlineKeyboardBuilder = InlineKeyboardBuilder()
    kb.add(InlineKeyboardButton(text=data['button_text'], url=data['link']))
    return kb.as_markup()