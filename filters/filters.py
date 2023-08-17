from aiogram.types import Message, CallbackQuery
import names
from bot.create_bot import config


async def is_banned(message: Message = None, callback: CallbackQuery = None):
    if message is not None:
        if message.from_user.id in names.name.banned_users:
            return True
    elif callback is not None:
        if callback.from_user.id in names.name.banned_users:
            return True
    return False


async def is_admin(message: Message):
    return message.from_user.id == int(config.tg_bot.admin_id)


async def photo_filter(callback: CallbackQuery):
    return any([callback.data == 'yes', callback.data == 'no'])


async def number_of_story_filter(callback: CallbackQuery):
    return any([callback.data.startswith("don't_send"), callback.data.startswith('send_now/'),
                callback.data.startswith('story/'), callback.data.startswith('delete/'),
                callback.data.startswith('ban/')]) and len(callback.data.split('/')) == 2


async def date_filter_for_story(callback: CallbackQuery):
    return len(callback.data.split('/')) == 3 and callback.data.startswith('story/')


async def set_schedule_for_posting(callback: CallbackQuery):
    return len(callback.data.split('/')) == 4 and callback.data.startswith('story/')


async def commercial_correct_amount_times(message: Message):
    return message.text.isdigit()


async def commercial_text_or_media(message: Message):
    return (message.text == 'No') or (message.photo != []) or (message.video is not None)


async def process_forward_back_publish_press_filter(callback: CallbackQuery):
    return callback.data.startswith('previous_story/') or callback.data.startswith(
        'next_story/') or callback.data.startswith('not_published/') or callback.data.startswith('close_stories/')
