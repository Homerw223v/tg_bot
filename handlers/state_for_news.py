import datetime

from bot.create_bot import config

from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardButton
from aiogram.fsm.context import FSMContext
from aiogram.filters.state import State, StatesGroup, StateFilter
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.filters import Command

from lexicon.LEXICON_RU import LEXICON_NEWS
from service.posts import utc
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
    await message.answer(text='Заполнения новостной формы отменено.\n\nЕсли хотите отправить новость,'
                              ' то введите команду /news')
    await state.clear()


@router.message(Command(commands=['news']))
async def news_command(message: Message, state: FSMContext):
    """Команда news и активация машины состояний"""
    if message.from_user.id == int(config.tg_bot.admin_id):
        await state.set_state(FSMNews.news)
        await message.answer(
            'Вы приступили к заполнению формы. Чтобы отменить её заполнение введите /cancel\n\n'
            'В случае если вы отправите не то, что от вас ожидает бот, он удалит ваше сообщение.\n\n'
            'Напишите то, что вы хотите опубликовать')


@router.message(F.text, StateFilter(FSMNews.news))
async def news_send_story(message: Message, state: FSMContext):
    """Получаем и сохраняем текст и меняем состояние"""
    await state.update_data(news=message.text)
    await state.set_state(FSMNews.title)
    await message.answer('Хорошо. Теперь выберите тему вашей новости.', reply_markup=InlineKeyboardBuilder().add(
        InlineKeyboardButton(text='Новости', callback_data='news'),
        InlineKeyboardButton(text='Интересный факт', callback_data='fact')
    ).as_markup())


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
    await callback.message.edit_text(text=f' \t\t{LEXICON_NEWS[data.get("title")]}\n\n'
                                          f'{data.get("news")}',
                                     reply_markup=InlineKeyboardBuilder().add(
                                         InlineKeyboardButton(text='Опубликовать', callback_data='publish'),
                                         InlineKeyboardButton(text='Заполнить заново', callback_data='reset')
                                     ).as_markup())


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
        await callback.message.edit_text('Напишите то, что вы хотите опубликовать')
    elif callback.data == 'publish':
        await state.set_state(FSMNews.send_news)
        await callback.message.delete_reply_markup()
        await callback.message.answer('Когда будем публиковаться?', reply_markup=InlineKeyboardBuilder().add(
            InlineKeyboardButton(text='Прямо сейчас', callback_data='now'),
            InlineKeyboardButton(text='Ввести время и дату', callback_data='other_time')
        ).as_markup())
        await callback.answer()
    else:
        await callback.message.edit_text('Ну вот, я сломался. Выключаю машину состояний')
        await state.clear()


@router.message(StateFilter(FSMNews.correct))
async def news_publish_or_refill_no_callback(message: Message):
    await message.delete()


@router.callback_query(StateFilter(FSMNews.send_news))
async def news_publish_story(callback: CallbackQuery, state: FSMContext):
    """Выбираем когда нужно опубликовать текст"""
    if callback.data == 'now':
        await send_news_to_channel(await state.get_data())
        await callback.message.edit_text('Текст опубликован в группе')
        await callback.answer()
        await state.clear()
    elif callback.data == 'other_time':
        await state.set_state(FSMNews.choose_time)
        await callback.message.edit_text(text='Введите дату и время в формате гггг-мм-дд чч:мм')
        await callback.answer()
    else:
        await callback.message.edit_text('Ну вот, я сломался. Выключаю машину состояний')
        await state.clear()


@router.message(StateFilter(FSMNews.send_news))
async def news_publish_story_no_callback(message: Message):
    await message.delete()


@router.message(F.text, StateFilter(FSMNews.choose_time))
async def news_choose_time(message: Message, state: FSMContext):
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
            send_news_to_channel_task.apply_async((data,), eta=time - datetime.timedelta(hours=utc))
            await message.answer(f'Текст будет опубликован в группе {str(time)[:19]}')
            await state.clear()


@router.message(~F.text, StateFilter(FSMNews.choose_time))
async def news_choose_time_wrong_type(message: Message):
    await message.delete()
