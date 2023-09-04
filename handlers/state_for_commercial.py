import datetime
import names.name
from bot.create_bot import bot, config
import requests
from requests.exceptions import MissingSchema, InvalidURL, ConnectionError
from urllib3.exceptions import LocationParseError
from database import db_func
from filters.filters import commercial_correct_amount_times, commercial_text_or_media
from keyboards.keyboard_commercial import create_kb_for_publishing
from lexicon.LEXICON_RU import LEXICON, LEXICON_COMMERCIAL

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, StateFilter
from aiogram.filters.state import State, StatesGroup
from aiogram.fsm.context import FSMContext

from service.strings import commercial_string
from worker.celery import send_commercial_to_chat, send_commercial_task

router = Router()


class FSMCommercial(StatesGroup):
    commercial = State()
    media = State()
    link = State()
    button_text = State()
    pre_publish = State()
    amount_times = State()
    time = State()


@router.message(Command(commands=['cancel']), F.text, StateFilter(FSMCommercial))
async def cancel_command(message: Message, state: FSMContext):
    """Отменяет машину состояний рекламы"""
    await state.clear()
    await message.answer(LEXICON_COMMERCIAL['cancel'])


@router.message(Command(commands=['commercial']), F.text)
async def commercial_command(message: Message, state: FSMContext):
    """Команда news и активация машины состояний"""
    if message.from_user.id == int(config.tg_bot.admin_id):
        await state.set_state(FSMCommercial.commercial)
        await message.answer(LEXICON_COMMERCIAL['start'])
    else:
        await message.answer(text=LEXICON['other'])


@router.message(F.text, StateFilter(FSMCommercial.commercial))
async def commercial_photo_or_video(message: Message, state: FSMContext):
    """Спращиваем будет ли фотография или видео прикреплены"""
    await state.update_data(commercial=message.text, times=1)
    await state.set_state(FSMCommercial.media)
    await message.answer(LEXICON_COMMERCIAL['is_photo'])


@router.message(StateFilter(FSMCommercial.commercial))
async def commercial_photo_or_video_not_text(message: Message):
    await message.delete()


@router.message(StateFilter(FSMCommercial.media), F.photo | F.text | F.video, commercial_text_or_media)
async def commercial_media_content(message: Message, state: FSMContext):
    if message.text == 'No':
        await state.set_state(FSMCommercial.link)
        await state.update_data(content_type=None,
                                file_id=None,
                                file_unique_id=None)
        await message.answer(LEXICON_COMMERCIAL['no_media'])
    elif message.video is not None:
        await state.update_data(content_type='video',
                                file_id=message.video.file_id,
                                file_unique_id=message.video.file_unique_id)
        await state.set_state(FSMCommercial.link)
        await message.answer(LEXICON_COMMERCIAL['video'])
    elif message.photo is not None:
        await state.update_data(content_type='photo',
                                file_id=message.photo[-1].file_id,
                                file_unique_id=message.photo[-1].file_unique_id)
        await state.set_state(FSMCommercial.link)
        await message.answer(LEXICON_COMMERCIAL['photo'])
    else:
        await message.delete()


@router.message(StateFilter(FSMCommercial.media), ~F.photo | ~F.text | ~F.video, )
async def commercial_not_media_content(message: Message):
    await message.delete()


@router.message(StateFilter(FSMCommercial.link), F.text)
async def commercial_get_link(message: Message, state: FSMContext):
    try:
        if message.text.startswith('www.'):
            url = message.text.replace('www.', 'https://')
        else:
            url = message.text
        response = requests.get(url)
    except (MissingSchema, InvalidURL, ConnectionError, LocationParseError):
        await message.answer(LEXICON_COMMERCIAL['invalid_link'])
    else:
        if response.status_code == 200:
            await message.answer(LEXICON_COMMERCIAL['link_ok'])
        else:
            await message.answer(f'Вроде грузится. Код ответа {response.status_code}')
        await message.answer(LEXICON_COMMERCIAL['button_text'])
        await state.update_data(link=message.text)
        await state.set_state(FSMCommercial.button_text)


@router.message(StateFilter(FSMCommercial.link))
async def commercial_not_get_link(message: Message):
    await message.delete()


@router.message(StateFilter(FSMCommercial.button_text), F.text)
async def commercial_button_text(message: Message, state: FSMContext):
    if len(message.text) < 30:
        await state.update_data(button_text=message.text)
        data = await state.get_data()
        await send_commercial_to_chat(data, config.tg_bot.admin_id)
        await message.answer(LEXICON_COMMERCIAL['preview'],
                             reply_markup=create_kb_for_publishing())
        await state.set_state(FSMCommercial.pre_publish)
    elif not message.text:
        await message.delete()
    else:
        await message.answer(LEXICON_COMMERCIAL['long_text'])


@router.message(StateFilter(FSMCommercial.button_text))
async def commercial_not_button_text(message: Message):
    await message.delete()


@router.callback_query(StateFilter(FSMCommercial.pre_publish))
async def commercial_publishing(callback: CallbackQuery, state: FSMContext):
    if callback.data == 'refill':
        await state.clear()
        await state.set_state(FSMCommercial.commercial)
        await callback.message.edit_text(LEXICON_COMMERCIAL['refill'])
    elif callback.data == 'send':
        await state.set_state(FSMCommercial.amount_times)
        await callback.message.edit_text(LEXICON_COMMERCIAL['how_much'])
    else:
        await callback.message.edit_text(LEXICON_COMMERCIAL['something_wrong'])
        await state.clear()


@router.message(StateFilter(FSMCommercial.pre_publish))
async def commercial_not_publishing(message: Message):
    await message.delete()


@router.message(StateFilter(FSMCommercial.amount_times), F.text, commercial_correct_amount_times)
async def commercial_amount_times(message: Message, state: FSMContext):
    times = int(message.text)
    if times > 30:
        await message.answer(LEXICON_COMMERCIAL['much_days'])
    elif times <= 0:
        await bot.send_sticker(message.from_user.id,
                               sticker='CAACAgIAAxkBAAI5vmTM8Wnxa37WLECFEh9ON2dvFYHpAAI3AwACtXHaBqSAkerG-Gh2LwQ')
        await message.answer(LEXICON_COMMERCIAL['minus_days'])
    else:
        await state.update_data(times=message.text)
        await state.set_state(FSMCommercial.time)
        await message.answer(LEXICON_COMMERCIAL['date_time'])


@router.message(StateFilter(FSMCommercial.amount_times))
async def commercial_not_amount_times(message: Message):
    await message.delete()


@router.message(StateFilter(FSMCommercial.time), F.text)
async def commercial_publish_time(message: Message, state: FSMContext):
    """Получаем точное время и дату и ставим задачу для celery"""
    try:
        mess = message.text
        time = datetime.datetime.strptime(mess + ':00.156478', names.name.time_format)
    except ValueError:
        await message.answer(LEXICON_COMMERCIAL['wrong_format'])
    else:
        if time < datetime.datetime.utcnow() + datetime.timedelta(hours=names.name.utc):
            await message.answer(LEXICON_COMMERCIAL['too_late'])
        else:
            data = await state.get_data()
            commercial_id = await db_func.commercial_new(data)
            commercial = await db_func.get_commercial(commercial_id)
            for i in range(int(data['times'])):
                send_commercial_task.apply_async((commercial, config.tg_bot.channel_id),
                                                 eta=time - datetime.timedelta(
                                                     hours=names.name.utc) + datetime.timedelta(days=i))
            await message.answer(commercial_string(str(time)[:16], data["times"]))
            await state.clear()


@router.message(StateFilter(FSMCommercial.time))
async def commercial_not_publish_time(message: Message):
    await message.delete()
