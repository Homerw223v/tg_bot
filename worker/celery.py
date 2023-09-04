import asyncio
from aiogram.exceptions import TelegramBadRequest
from celery import Celery
from bot.create_bot import bot, config
from database import db_func
from keyboards.keyboards import create_kb_button
from lexicon.LEXICON_RU import LEXICON_NEWS, LEXICON
from names.name import publishing
from service.strings import story_to_chat

celery_event_loop = asyncio.new_event_loop()

celery_app = Celery(main='celery', backend='redis://127.0.0.1:6379',
                    broker='redis://127.0.0.1:6379')
# celery_app = Celery(main='celery', backend='redis://redis:6379',
#                     broker='amqp://admin:password@rabbit:5672')
celery_app.autodiscover_tasks()


async def send_story_to_chat(story_id, chat_id, reply=None):
    """Вспомогательная функция для отправки истории модератору или на Канал"""
    story = await db_func.get_story(story_id=story_id)
    if story['content_type'] == 'photo':
        try:
            await bot.send_photo(chat_id, photo=story['file_id'],
                                 caption=story_to_chat(story), reply_markup=reply)
        except TelegramBadRequest:
            await bot.send_photo(chat_id, photo=story['file_id'])
            await bot.send_message(chat_id, text=story_to_chat(story), reply_markup=reply)
    elif story['content_type'] == 'video':
        try:
            await bot.send_video(chat_id, photo=story['file_id'], caption=story_to_chat(story), reply_markup=reply)
        except TelegramBadRequest:
            await bot.send_video(chat_id, video=story['file_id'])
            await bot.send_message(chat_id, text=story_to_chat(story), reply_markup=reply)
    else:
        await bot.send_message(chat_id, text=story_to_chat(story), reply_markup=reply)
    if chat_id == config.tg_bot.channel_id:
        await db_func.published_story(str(story_id), publishing[1])


async def send_news_to_channel(data):
    await bot.send_message(config.tg_bot.channel_id, text=f' \t\t{LEXICON_NEWS[data.get("title")]}\n\n'
                                                          f'{data.get("news")}')


async def send_commercial_to_chat(data: dict, chat):
    if data['content_type'] is None:
        text = f'{data["commercial"]}'
        await bot.send_message(chat, text=text, reply_markup=create_kb_button(data))
    elif len(data) == 7 and data['content_type'] == 'photo':
        await bot.send_photo(chat, photo=data['file_id'], caption=data['commercial'],
                             reply_markup=create_kb_button(data))
    elif len(data) == 7 and data['content_type'] == 'video':
        await bot.send_video(chat, video=data['file_id'], caption=data['commercial'],
                             reply_markup=create_kb_button(data))
    else:
        await bot.send_message(config.tg_bot.admin_id, text=f'{len(data), data}')
        await bot.send_message(config.tg_bot.admin_id,
                               text=LEXICON['wrong_data'])


@celery_app.task
def send_commercial_task(data: dict, chat):
    celery_event_loop.run_until_complete(send_commercial_to_chat(data, chat))


@celery_app.task
def send_story_task(story_id, chat_id):
    celery_event_loop.run_until_complete(send_story_to_chat(story_id, chat_id))


@celery_app.task
def send_news_to_channel_task(data):
    celery_event_loop.run_until_complete(send_news_to_channel(data))
