from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command, StateFilter
from aiogram.filters.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from filters.filters import is_admin
import names
from random import shuffle

router = Router()


class FSMHiragana(StatesGroup):
    kana = State()


@router.message(Command(commands=['cancel']), StateFilter(FSMHiragana))
async def cancel_command(message: Message, state: FSMContext):
    await message.answer('Закончили обучение')
    await state.clear()


@router.message(Command(commands=['hiragana']), is_admin)
async def hiragana_command(message: Message, state: FSMContext):
    await state.set_state(FSMHiragana.kana)
    await message.answer(
        'Начинаем тренировку Хираганы.\n\nЯ отправляю иероглиф, а ты отправляешь как он произносится.\n\n'
        'Чтобы прекратить тренировку введите /cancel. \n\n Поехали!')
    hieroglyph = list(names.name.hiragana.keys())
    shuffle(hieroglyph)
    quest = hieroglyph[-1]
    await state.update_data(hieroglyph=quest)
    await message.answer(f'Иероглиф {quest}')


@router.message(StateFilter(FSMHiragana.kana), F.text)
async def is_correct_hieroglyph(message: Message, state: FSMContext):
    data = await state.get_data()
    quest = data.get('hieroglyph')
    answer = names.name.hiragana[quest]
    hieroglyph = list(names.name.hiragana.keys())
    shuffle(hieroglyph)
    next_quest = hieroglyph[-1]
    await state.update_data(hieroglyph=next_quest)
    if message.text.lower() == answer:
        await message.answer(f'Поздралвляю. Твой ответ верный. Продолжаем.\n\n'
                             f'Следующий иероглиф {next_quest}')
    else:
        await message.answer(f'К сожалению пока не правильно.\nПридется еще повторить!\n\n'
                             f'Это иероглиф {quest} и читается как "{answer}"\n\n'
                             f'Следующий иероглиф {next_quest}')


@router.message(StateFilter(FSMHiragana.kana))
async def getting_not_text(message: Message):
    await message.delete()
