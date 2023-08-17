import asyncio

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from bot.create_bot import bot
from lexicon.LEXICON_RU import LEXICON
from filters.filters import is_banned
from bot.create_bot import config

router = Router()


@router.message(is_banned)
async def banned_user(message: Message):
    await message.delete()
    await message.answer('Вы внесены в чёрный список и больше не можете отправлять боту сообщения.')


@router.message(Command(commands=['start']))
async def start_command(message: Message):
    await message.answer(text=f"Добрый день {message.from_user.full_name}.\n\n{LEXICON['/start']}")


@router.message(Command(commands=['help']))
async def help_command(message: Message):
    await message.delete()
    await bot.send_message(message.from_user.id,
                           text=LEXICON['/help'])


@router.message(Command(commands=['sticker']))
async def sticker_handler(message: Message):
    if message.from_user.id == int(config.tg_bot.admin_id):
        await bot.send_sticker(config.tg_bot.channel_id,
                               sticker="CAACAgIAAxkBAAIFCGS0GEKfckLjvqM2kFg83L8b_e2xAAIoAwACtXHaBpB6SodelUpuLwQ")


@router.message(Command(commands=['story']))
async def how_to_send_story(message: Message):
    if message.from_user.id == int(config.tg_bot.admin_id):
        while True:
            await bot.send_message(config.tg_bot.channel_id, text='Это бот для отправки ваших историй')
            await asyncio.sleep(600)
