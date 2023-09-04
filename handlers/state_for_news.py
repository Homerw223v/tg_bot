import datetime

import names.name
from bot.create_bot import config

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters.state import State, StatesGroup, StateFilter
from aiogram.filters import Command

from keyboards.keyboards_news import create_kb_news_fact, create_kb_correct, create_kb_when_publish
from lexicon.LEXICON_RU import LEXICON_NEWS
from service.strings import news_string
from worker.celery import send_news_to_channel, send_news_to_channel_task

router = Router()


class FSMNews(StatesGroup):
    news = State()
    title = State()
    correct = State()
    send_news = State()
    choose_time = State()


"""Машина состояний для публикации сообщения от админа или модератора в группу"""


@router.message(StateFilter(FSMNews), Command(commands=['cancel']))
async def process_cancel_command(message: Message, state: FSMContext):
    """Отмена машины состояний"""
    await message.answer(text=LEXICON_NEWS['cancel'])
    await state.clear()


@router.message(Command(commands=['news']))
async def news_command(message: Message, state: FSMContext):
    """Команда news и активация машины состояний"""
    if message.from_user.id == int(config.tg_bot.admin_id):
        await state.set_state(FSMNews.news)
        await message.answer(LEXICON_NEWS['start'])


@router.message(F.text, StateFilter(FSMNews.news))
async def news_send_story(message: Message, state: FSMContext):
    """Получаем и сохраняем текст и меняем состояние"""
    await state.update_data(news=message.text)
    await state.set_state(FSMNews.title)
    await message.answer(LEXICON_NEWS['theme'], reply_markup=create_kb_news_fact())


@router.message(~F.text, StateFilter(FSMNews.news))
async def news_send_no_story(message: Message):
    await message.delete()


@router.callback_query(StateFilter(FSMNews.title))
async def news_answer_title(callback: CallbackQuery, state: FSMContext):
    """Получаем коллбак с заголовком текста"""
    await state.update_data(title=callback.data)
    await state.set_state(FSMNews.correct)
    await callback.answer()
    data = await state.get_data()
    await callback.message.edit_text(text=f' \t\t{LEXICON_NEWS[data.get("title")]}\n\n{data.get("news")}',
                                     reply_markup=create_kb_correct())


@router.message(StateFilter(FSMNews.title))
async def news_answer_no_title(message: Message):
    await message.delete()


@router.callback_query(StateFilter(FSMNews.correct))
async def news_publish_or_refill(callback: CallbackQuery, state: FSMContext):
    """Получаем колбак о публикации или перезаполнении"""
    if callback.data == 'reset':
        await state.clear()
        await state.set_state(FSMNews.news)
        await callback.answer()
        await callback.message.edit_text(LEXICON_NEWS['text'])
    elif callback.data == 'publish':
        await state.set_state(FSMNews.send_news)
        await callback.message.delete_reply_markup()
        await callback.message.answer(LEXICON_NEWS['when'], reply_markup=create_kb_when_publish())
        await callback.answer()
    else:
        await callback.message.edit_text(LEXICON_NEWS['something_wrong'])
        await state.clear()


@router.message(StateFilter(FSMNews.correct))
async def news_publish_or_refill_no_callback(message: Message):
    await message.delete()


@router.callback_query(StateFilter(FSMNews.send_news))
async def news_publish_story(callback: CallbackQuery, state: FSMContext):
    """Выбираем когда нужно опубликовать текст"""
    if callback.data == 'now':
        await send_news_to_channel(await state.get_data())
        await callback.message.edit_text(LEXICON_NEWS['published'])
        await callback.answer()
        await state.clear()
    elif callback.data == 'other_time':
        await state.set_state(FSMNews.choose_time)
        await callback.message.edit_text(text=LEXICON_NEWS['time'])
        await callback.answer()
    else:
        await callback.message.edit_text(LEXICON_NEWS['something_wrong'])
        await state.clear()


@router.message(StateFilter(FSMNews.send_news))
async def news_publish_story_no_callback(message: Message):
    await message.delete()


@router.message(F.text, StateFilter(FSMNews.choose_time))
async def news_choose_time(message: Message, state: FSMContext):
    """Получаем точное время и дату и ставим задачу для celery"""
    try:
        text = message.text
        time = datetime.datetime.strptime(text + ':00.156478', names.name.time_format)
    except ValueError:
        await message.answer(LEXICON_NEWS['wrong_time'])
    else:
        if time < datetime.datetime.now() + datetime.timedelta(hours=names.name.utc):
            await message.answer(LEXICON_NEWS['too_late'])
        else:
            data = await state.get_data()
            send_news_to_channel_task.apply_async((data,), eta=time - datetime.timedelta(hours=names.name.utc))
            await message.answer(news_string(str(time)[:19]))
            await state.clear()


@router.message(~F.text, StateFilter(FSMNews.choose_time))
async def news_choose_time_wrong_type(message: Message):
    await message.delete()
