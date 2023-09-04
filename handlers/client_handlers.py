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
    await message.answer(LEXICON['black_list'])


@router.message(Command(commands=['start']))
async def start_command(message: Message):
    await message.answer(text=f"Добрый день {message.from_user.first_name}.\n\n{LEXICON['/start']}")


@router.message(Command(commands=['help']))
async def help_command(message: Message):
    await message.delete()
    await bot.send_message(message.from_user.id, text=LEXICON['/help'])


@router.message(Command(commands=['everyday']))
async def how_to_send_story(message: Message):
    if message.from_user.id == int(config.tg_bot.admin_id):
        while True:
            await bot.send_message(config.tg_bot.channel_id, text=LEXICON['everyday'])
            await asyncio.sleep(600)
