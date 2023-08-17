import datetime

import requests
from requests.exceptions import MissingSchema, InvalidURL, ConnectionError
from urllib3.exceptions import LocationParseError

from bot.create_bot import bot, config
from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardButton, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters import Command, StateFilter
from aiogram.filters.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from database import db_func
from filters.filters import commercial_correct_amount_times, commercial_text_or_media
from lexicon.LEXICON_RU import LEXICON
from service.posts import utc
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
    await message.answer('Заполнения рекламы прекращено.\n\nЕсли кто захочет еще рекламы, ты знаешь что делать😁')


@router.message(Command(commands=['commercial']), F.text)
async def commercial_command(message: Message, state: FSMContext):
    """Команда news и активация машины состояний"""
    if message.from_user.id == int(config.tg_bot.admin_id):
        await state.set_state(FSMCommercial.commercial)
        await message.answer(
            'Вы приступили к заполнению формы. Чтобы отменить её заполнение введите /cancel\n\n'
            'В случае если вы отправите не то, что от вас ожидает бот, он удалит ваше сообщение.\n\n'
            'Введите текст рекламы')
    else:
        await message.answer(text=LEXICON['other'])


@router.message(F.text, StateFilter(FSMCommercial.commercial))
async def commercial_photo_or_video(message: Message, state: FSMContext):
    """Спращиваем будет ли фотография или видео прикреплены"""
    await state.update_data(commercial=message.text, times=1)
    await state.set_state(FSMCommercial.media)
    await message.answer('Хорошо, текст получен.\n\nЕсли будет фотография или видео к посту, пожалуйста отправьте их.\n'
                         'В ином случае введите "No"')


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
        await message.answer(
            'Пост будет без медиа.\n\nТеперь отправьте ссылку, куда нужно будет переадрессовывать пользователя')
    elif message.video is not None:
        await state.update_data(content_type='video',
                                file_id=message.video.file_id,
                                file_unique_id=message.video.file_unique_id)
        await state.set_state(FSMCommercial.link)
        await message.answer(
            'Ваше видео получено.\n\nТеперь отправьте ссылку, куда нужно будет переадрессовывать пользователя')
    elif message.photo is not None:
        await state.update_data(content_type='photo',
                                file_id=message.photo[-1].file_id,
                                file_unique_id=message.photo[-1].file_unique_id)
        await state.set_state(FSMCommercial.link)
        await message.answer(
            'Ваше фото получено.\n\nТеперь отправьте ссылку, куда нужно будет переадрессовывать пользователя')
    else:
        await message.delete()


@router.message(StateFilter(FSMCommercial.media), ~F.photo | ~F.text | ~F.video, )
async def commercial_not_media_content(message: Message):
    await message.delete()


@router.message(StateFilter(FSMCommercial.link), F.text)
async def commercial_get_link(message: Message, state: FSMContext):
    try:
        response = requests.get(message.text)
    except (MissingSchema, InvalidURL, ConnectionError, LocationParseError):
        await message.answer("Ссылка не работает")
    else:
        if response.status_code == 200:
            await message.answer('Ссылка в порядке')
        else:
            await message.answer(f'Вроде грузится. Код ответа {response.status_code}')
        await message.answer(
            'Отлично.\nТеперь нужно выбрать текст для кнопки. Текст должен быть коротким. До 30 символов.\n\n'
            'Например: Ссылка на группу')
        await state.update_data(link=message.text)
        await state.set_state(FSMCommercial.button_text)
        print(await state.get_state())


@router.message(StateFilter(FSMCommercial.link))
async def commercial_not_get_link(message: Message):
    await message.delete()


@router.message(StateFilter(FSMCommercial.button_text), F.text)
async def commercial_button_text(message: Message, state: FSMContext):
    if len(message.text) < 30:
        await state.update_data(button_text=message.text)
        data = await state.get_data()
        await send_commercial_to_chat(data, config.tg_bot.admin_id)
        await message.answer(
            'Вот как будет выглядеть реклама. Публикуем или что то исправим(придется все заполнять заново)',
            reply_markup=InlineKeyboardBuilder().row(
                InlineKeyboardButton(text='Публикуем', callback_data='send'),
                InlineKeyboardButton(text='Заполнить заново', callback_data='refill')
            ).as_markup())
        await state.set_state(FSMCommercial.pre_publish)
    elif not message.text:
        await message.delete()
    else:
        await message.answer('Какой у тебя длииинный текст. Нужно по короче.')


@router.message(StateFilter(FSMCommercial.button_text))
async def commercial_not_button_text(message: Message):
    await message.delete()


@router.callback_query(StateFilter(FSMCommercial.pre_publish))
async def commercial_publishing(callback: CallbackQuery, state: FSMContext):
    if callback.data == 'refill':
        await state.clear()
        await state.set_state(FSMCommercial.commercial)
        await callback.message.edit_text(
            'Хорошо. Давай исправим эту рекламу.\nЧтобы отменить её заполнение введите /cancel\n\n'
            'Введите текст рекламы')
    elif callback.data == 'send':
        await state.set_state(FSMCommercial.amount_times)
        await callback.message.edit_text('Введите количество раз, сколько нужно будет публиковать рекламу.'
                                         '(Реклама будем публиковаться каждый день в одно и то же время)')
    else:
        await callback.message.edit_text('Ну вот, я сломался. Выключаю машину состояний')
        await state.clear()


@router.message(StateFilter(FSMCommercial.pre_publish))
async def commercial_not_publishing(message: Message):
    await message.delete()


@router.message(StateFilter(FSMCommercial.amount_times), F.text, commercial_correct_amount_times)
async def commercial_amount_times(message: Message, state: FSMContext):
    times = int(message.text)
    if times > 30:
        await message.answer('Слишком большое количество дней.\nМаксимальное значение 30')
    elif times <= 0:
        await bot.send_sticker(message.from_user.id,
                               sticker='CAACAgIAAxkBAAI5vmTM8Wnxa37WLECFEh9ON2dvFYHpAAI3AwACtXHaBqSAkerG-Gh2LwQ')
        await message.answer('Длина не должна быть меньше 1. Baka')
    else:
        await state.update_data(times=message.text)
        await state.set_state(FSMCommercial.time)
        await message.answer(
            'Ну и теперь самое главное.\n\nВ какое время будем публиковать рекламу?\n'
            '(Реклама будет публиковаться каждый день в одно и то же время)\n\n'
            'Введите дату и время в формате гггг-мм-дд чч:мм')


@router.message(StateFilter(FSMCommercial.amount_times))
async def commercial_not_amount_times(message: Message):
    await message.delete()


@router.message(StateFilter(FSMCommercial.time), F.text)
async def commercial_publish_time(message: Message, state: FSMContext):
    """Получаем точное время и дату и ставим задачу для celery"""
    try:
        mess = message.text
        time = datetime.datetime.strptime(mess + ':00.156478', "%Y-%m-%d %H:%M:%S.%f")
    except ValueError:
        await message.answer('Неверный формат.\nФормат: гггг-мм-дд чч:мм.\nПример: 2023-02-04 14:25')
    else:
        if time < datetime.datetime.now() + datetime.timedelta(hours=utc):
            await message.answer('К сожалению, указанное вами время уже прошло')
        else:
            data = await state.get_data()
            days = "дня" if 1 < int(data.get('times')) < 5 else 'дней'
            commercial_id = await db_func.commercial_new(data)
            commercial = await db_func.get_commercial(commercial_id)
            for i in range(int(data['times'])):
                send_commercial_task.apply_async((commercial, config.tg_bot.channel_id),
                                                 eta=time - datetime.timedelta(hours=utc) + datetime.timedelta(days=i))
            await message.answer(f'Реклама будет опубликован в группе {str(time)[:16]} каждый день '
                                 f'на протяжении {data["times"]} {days}')
            await state.clear()


@router.message(StateFilter(FSMCommercial.time))
async def commercial_not_publish_time(message: Message):
    await message.delete()
