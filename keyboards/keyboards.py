from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

import names

import datetime

from aiogram.utils.keyboard import InlineKeyboardBuilder
from service.posts import create_days, utc


def days_for_choosing() -> dict:
    day_of_weeks = dict()
    for i in range(6):
        day_of_weeks[str(i)] = (
                    (datetime.datetime.now() + datetime.timedelta(hours=utc)).date() + datetime.timedelta(days=i)).strftime(
            '%Y-%m-%d')
    print(day_of_weeks)
    return day_of_weeks


names.name.five_days = days_for_choosing()


def create_kb_for_days(data: str) -> InlineKeyboardMarkup:
    print(data)
    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    # if datetime.datetime.now() > datetime.datetime.strptime(names.name.five_days['0'] + ' 23:59:59.999999',
    #                                                         '%Y-%m-%d %H:%M:%S.%f'):
    if datetime.datetime.now() + datetime.timedelta(hours=utc) > datetime.datetime.strptime(
            names.name.five_days['0'] + ' 23:59:59.999999',
            '%Y-%m-%d %H:%M:%S.%f'):
        names.name.five_days = days_for_choosing()
    buttons = []
    for key, value in names.name.five_days.items():
        buttons.append(InlineKeyboardButton(text=value, callback_data=f'{data}/{key}'))
    kb_builder.row(*buttons, width=2)
    kb_builder.row(InlineKeyboardButton(text='Не публиковать', callback_data=f"don't_send/{data.split('/')[1]}")).add(
        InlineKeyboardButton(text='Опубликовать сейчас', callback_data=f'send_now/{data.split("/")[1]}'))
    return kb_builder.as_markup()


def create_kb_for_choosing_time(data: str) -> InlineKeyboardMarkup:
    kb_builder: InlineKeyboardBuilder = InlineKeyboardBuilder()
    info = data.split('/')
    # if datetime.datetime.now() > datetime.datetime.strptime(names.name.days['6'] + ' 23:59:59.999999',
    #                                                         '%Y-%m-%d %H:%M:%S.%f'):
    if datetime.datetime.now() + datetime.timedelta(hours=utc) > datetime.datetime.strptime(
            names.name.days['6'] + ' 23:59:59.999999',
            '%Y-%m-%d %H:%M:%S.%f'):
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
