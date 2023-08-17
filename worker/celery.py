import asyncio
from aiogram.exceptions import TelegramBadRequest
from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from celery import Celery
from bot.create_bot import bot, config
from database import db_func
from lexicon.LEXICON_RU import LEXICON_NEWS
from names.name import publishing

celery_event_loop = asyncio.new_event_loop()

# celery_app = Celery(main='celery', backend='redis://127.0.0.1:6379',
#                     broker='redis://127.0.0.1:6379')
celery_app = Celery(main='celery', backend='redis://redis:6379',
                    broker='amqp://admin:password@rabbit:5672')
celery_app.autodiscover_tasks()


async def send_story_to_chat(story_id, chat_id, reply=None):
    """Вспомогательная функция для отправки истории модератору или на Канал"""
    story = await db_func.get_story(story_id=story_id)
    if story['content_type'] == 'photo':
        try:
            await bot.send_photo(chat_id, photo=story['file_id'],
                                 caption=f'История от: {story["author"]}\nГород: {story["city"]}\n\n{story["story"]}',
                                 reply_markup=reply)
        except TelegramBadRequest:
            await bot.send_photo(chat_id, photo=story['file_id'])
            await bot.send_message(chat_id,
                                   text=f'История от: {story["author"]}\nГород: {story["city"]}\n\n{story["story"]}',
                                   reply_markup=reply)
    elif story['content_type'] == 'video':
        try:
            await bot.send_photo(chat_id, photo=story['file_id'],
                                 caption=f'История от: {story["author"]}\nГород: {story["city"]}\n\n{story["story"]}',
                                 reply_markup=reply)
        except TelegramBadRequest:
            await bot.send_video(chat_id, video=story['file_id'])
            await bot.send_message(chat_id,
                                   text=f'История от: {story["author"]}\nГород: {story["city"]}\n\n{story["story"]}',
                                   reply_markup=reply)
    else:
        await bot.send_message(chat_id, text=f'История от: {story[5]}\nГород: {story[1]}\n\n{story[4]}',
                               reply_markup=reply)
    if chat_id == config.tg_bot.channel_id:
        await db_func.published_story(str(story_id), publishing[1])


async def send_news_to_channel(data):
    await bot.send_message(config.tg_bot.channel_id, text=f' \t\t{LEXICON_NEWS[data.get("title")]}\n\n'
                                                          f'{data.get("news")}')


async def send_commercial_to_chat(data: dict, chat):
    if data['content_type'] is None:
        text = f'{data["commercial"]}'
        await bot.send_message(chat, text=text, reply_markup=InlineKeyboardBuilder().add(
            InlineKeyboardButton(text=data['button_text'], url=data['link'])
        ).as_markup())
    elif len(data) == 7 and data['content_type'] == 'photo':
        await bot.send_photo(chat, photo=data['file_id'], caption=data['commercial'],
                             reply_markup=InlineKeyboardBuilder().add(
                                 InlineKeyboardButton(text=data['button_text'], url=data['link'])
                             ).as_markup())
    elif len(data) == 7 and data['content_type'] == 'video':
        await bot.send_video(chat, video=data['file_id'], caption=data['commercial'],
                             reply_markup=InlineKeyboardBuilder().add(
                                 InlineKeyboardButton(text=data['button_text'], url=data['link'])
                             ).as_markup())
    else:
        await bot.send_message(chat, text=f'{len(data), data}')
        await bot.send_message(chat, text='Если пришло это сообщение значит функция получила неправильные данные.')


@celery_app.task
def send_commercial_task(data: dict, chat):
    celery_event_loop.run_until_complete(send_commercial_to_chat(data, chat))


@celery_app.task
def send_story_task(story_id, chat_id):
    celery_event_loop.run_until_complete(send_story_to_chat(story_id, chat_id))


@celery_app.task
def send_news_to_channel_task(data):
    celery_event_loop.run_until_complete(send_news_to_channel(data))
