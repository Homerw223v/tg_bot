from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def create_kb_for_send_story(story_id, user_id) -> InlineKeyboardMarkup:
    kb: InlineKeyboardBuilder = InlineKeyboardBuilder()
    kb.row(
        InlineKeyboardButton(text='Опубликовать позже', callback_data=f'story/{story_id}'),
        InlineKeyboardButton(text='Пропустить', callback_data=f"don't_send/{story_id}"),
        InlineKeyboardButton(text='Опубликовать сейчас', callback_data=f'send_now/{story_id}'),
        InlineKeyboardButton(text='Удалить историю', callback_data=f'delete/{story_id}'),
        InlineKeyboardButton(text='Удалить и забанить',
                             callback_data=f'ban/{story_id}-{user_id}'),
        width=2
    )
    return kb.as_markup()


def create_kb_for_anonim() -> InlineKeyboardMarkup:
    kb: InlineKeyboardBuilder = InlineKeyboardBuilder()
    kb.add(InlineKeyboardButton(text="Опубликовать имя", callback_data='name'),
           InlineKeyboardButton(text="Опубликовать анонимно", callback_data='anonim')).as_markup()
    return kb.as_markup()


def create_kb_for_yes_no() -> InlineKeyboardMarkup:
    kb: InlineKeyboardBuilder = InlineKeyboardBuilder()
    kb.add(InlineKeyboardButton(text="Да", callback_data='yes'),
           InlineKeyboardButton(text="Нет", callback_data='no'))
    return kb.as_markup()


def create_kb_for_wrong_time(story) -> InlineKeyboardMarkup:
    kb: InlineKeyboardBuilder = InlineKeyboardBuilder()
    kb.row(InlineKeyboardButton(text='Опубликовать позже', callback_data=f'story/{story}'),
           InlineKeyboardButton(text='Пропустить', callback_data=f"don't_send/{story}"),
           InlineKeyboardButton(text='Опубликовать сейчас', callback_data=f'send_now/{story}')
           )
    return kb.as_markup()
