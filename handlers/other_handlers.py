import datetime

from aiogram import Router
from aiogram.types import Message

from lexicon.LEXICON_RU import LEXICON

router = Router()


@router.message()
async def other_commands(message: Message):
    await message.answer(text=LEXICON['other'])
    await message.answer(text=f'{datetime.datetime.now()}')
    await message.answer(text=f'{message.from_user.id}')
