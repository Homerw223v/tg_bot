from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.filters.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, StateFilter

import names.name
from city.city import cities
from lexicon.LEXICON_RU import LEXICON_STORY
from names.name import publishing
from bot.create_bot import bot, config
from database import db_func
from filters.filters import number_of_story_filter, date_filter_for_story, \
    set_schedule_for_posting, is_admin, process_forward_back_publish_press_filter
from keyboards.keyboards import create_kb_for_days, create_kb_for_choosing_time, create_kb_for_not_published_stories
from keyboards.keyboards_story import create_kb_for_send_story, create_kb_for_anonim, create_kb_for_yes_no, \
    create_kb_for_wrong_time
import datetime

from service.strings import story_string
from worker.celery import send_story_task, send_story_to_chat
from service.posts import delete_time

router = Router()


class FSMStory(StatesGroup):
    city = State()
    is_photo = State()
    photo = State()
    story = State()
    author = State()


@router.message(Command(commands=['cancel']), StateFilter(FSMStory))
async def process_cancel_command(message: Message, state: FSMContext):
    """Отмена машины состояний"""
    await message.answer(text=LEXICON_STORY['cancel'])
    await state.clear()


"""Началь машины состояний. Спрашиваем город произошедшего события."""


@router.message(Command(commands=['mystory']))
async def my_story_command(message: Message, state: FSMContext):
    """Начало взаимодействия с формой машины состояний"""
    await message.answer(text=LEXICON_STORY['city'])
    await state.set_state(FSMStory.city)


@router.message(StateFilter(FSMStory.city), F.text)
async def correct_city_name(message: Message, state: FSMContext):
    """Если пользователь ввел текст"""
    if message.text.lower() in cities:
        await state.update_data(user_id=message.from_user.id, city=message.text.capitalize())
        await state.set_state(FSMStory.is_photo)
        await message.answer(text=LEXICON_STORY['photo'],
                             reply_markup=create_kb_for_yes_no())
    else:
        await message.answer(text=LEXICON_STORY['no_city'])


@router.message(StateFilter(FSMStory.city))
async def not_correct_city_type(message: Message):
    """Удаляет сообщения, которые не ожидает машина состояний в данный момент"""
    await message.delete()


"""Второй этап. Спрашиваем желает ли пользователь прикрепить фотографию к его истории."""


@router.callback_query(StateFilter(FSMStory.is_photo), F.data)
async def yes_no_for_photo(callback: CallbackQuery, state: FSMContext):
    """Хочет ли пользователь загрузить фотографию к его истории"""
    if callback.data == 'yes':
        await state.set_state(FSMStory.photo)
        await callback.message.edit_text(text=LEXICON_STORY['send_photo'])
        await callback.answer()
    elif callback.data == 'no':
        await callback.message.edit_text(LEXICON_STORY['no_photo'])
        await state.update_data(content_type=None, file_id=None, file_unique_id=None)
        await callback.answer()
        await state.set_state(state=FSMStory.story)
    else:
        await callback.message.edit_text(text=LEXICON_STORY['something_wrong'])
        await state.clear()


@router.message(StateFilter(FSMStory.is_photo))
async def not_correct_city_type(message: Message):
    await message.delete()


@router.message(StateFilter(FSMStory.photo), F.photo | F.video)
async def getting_photo_or_video(message: Message, state: FSMContext):
    """Получаем и сохраняем фотографию"""
    if message.photo:
        photo = message.photo[-1]
        await state.update_data(content_type='photo', file_id=photo.file_id, file_unique_id=photo.file_unique_id)
    elif message.video:
        video = message.video
        await state.update_data(content_type='video', file_id=video.file_id, file_unique_id=video.file_unique_id)
    await state.set_state(FSMStory.story)
    await message.answer(text=LEXICON_STORY['send_story'])


@router.message(StateFilter(FSMStory.photo))
async def getting_not_photo_or_video(message: Message):
    await message.delete()


"""Отправка самой истории"""


@router.message(StateFilter(FSMStory.story), F.text)
async def story_correct(message: Message, state: FSMContext):
    """Получаем историю и спрашиваем про анонимность"""
    if len(str(message.text)) > 200:
        await state.update_data(story=message.text)
        await state.set_state(FSMStory.author)
        await message.answer(text=LEXICON_STORY['anonim'],
                             reply_markup=create_kb_for_anonim())
    else:
        await message.answer(text=LEXICON_STORY['short_story'])


@router.message(StateFilter(FSMStory.story))
async def getting_not_text_in_story(message: Message):
    await message.delete()


"""Хочет ли пользователь, чтобы его имя присутствовало в истории"""


@router.callback_query(StateFilter(FSMStory.author))
async def anonim_story(callback: CallbackQuery, state: FSMContext):
    """Сохраняем анонимность пользователя и отправляем историю модератору на рассмотрение"""
    if callback.data == 'name':
        await callback.answer()
        await state.update_data(author=callback.from_user.full_name)
    elif callback.data == 'anonim':
        await state.update_data(author='Анонимно')
        await callback.answer()
    await callback.message.edit_text(text=LEXICON_STORY['thanks'])
    story = await state.get_data()
    story_id = await db_func.save_story(story, publishing[0])
    await send_story_to_moderator(story_id, callback.from_user.id)
    await state.clear()


@router.message(StateFilter(FSMStory.author))
async def anonim_story_wrong_type_income(message: Message):
    await message.delete()


"""Отправляет модератору сообщение, как будет выглядеть пост и стоит ли его отправлять на канал"""


async def send_story_to_moderator(story_id: int, user_id: int = None):
    """Отправляем историю модератору"""
    await send_story_to_chat(story_id, config.tg_bot.admin_id)
    await bot.send_message(config.tg_bot.admin_id, text=LEXICON_STORY['publish'],
                           reply_markup=create_kb_for_send_story(story_id, user_id))


"""Отправляем сообщение на канал, пропускаем или удаляем историю."""


@router.callback_query(number_of_story_filter)
async def asking_for_sending_story(callback: CallbackQuery):
    """Inline KB Спрашиваем модератора, нужно ли отправлять исорию на канал"""
    story_id = callback.data.split('/')[1]
    if callback.data.startswith("don't_send/"):
        await callback.message.edit_text(text=LEXICON_STORY['no_publish'])
        await callback.answer()
    elif callback.data.startswith('send_now/'):
        await send_story_to_chat(story_id, config.tg_bot.channel_id)
        await callback.message.edit_text(LEXICON_STORY['published'])
        await callback.answer()
    elif callback.data.startswith('delete/'):
        await db_func.delete_story(story_id)
        await callback.message.edit_text(LEXICON_STORY['deleted'])
    elif callback.data.startswith('ban/'):
        data = callback.data.split('/')[1].split('-')
        await db_func.delete_story(data[0])
        await db_func.add_user_to_banned_list(data[1])
        names.name.banned_users.append(callback.from_user.id)
        await callback.message.edit_text(LEXICON_STORY['black_list'])
        await callback.answer()
    else:
        await callback.message.edit_text(text=LEXICON_STORY['date'],
                                         reply_markup=create_kb_for_days(callback.data))
        await callback.answer()


@router.callback_query(date_filter_for_story)
async def choose_date_for_posting(callback: CallbackQuery):
    await callback.message.edit_text(text=LEXICON_STORY['time'],
                                     reply_markup=create_kb_for_choosing_time(callback.data))
    await callback.answer()


@router.callback_query(set_schedule_for_posting)
async def choose_time_for_posting(callback: CallbackQuery):
    data = callback.data.split('/')
    delete_time(data[2], data[3])
    time = datetime.datetime.strptime(data[3] + ':00.000025', names.name.time_format)
    if time > datetime.datetime.now():
        await db_func.publish_story_at(data[1], time.strftime(names.name.time_format), publishing[1])
        send_story_task.apply_async((data[1], config.tg_bot.channel_id,),
                                    eta=time - datetime.timedelta(hours=names.name.utc))
        await callback.message.edit_text(story_string(data[3]))
    else:
        await callback.message.edit_text(
            text=LEXICON_STORY['late'],
            reply_markup=create_kb_for_wrong_time(data[1]))


"""Получаем неопубликованные истории в случае если нечего публиковать"""


@router.message(Command(commands=['stories']), is_admin)
async def get_unpublished_stories(_):
    names.name.stories_id = db_func.select_unpublished_stories()
    reply = create_kb_for_not_published_stories(0)
    await send_story_to_chat(names.name.stories_id[0], config.tg_bot.admin_id, reply)


@router.callback_query(process_forward_back_publish_press_filter)
async def process_forward_back_publish_press(callback: CallbackQuery):
    index = int(callback.data.split('/')[1])
    if callback.data.startswith('previous_story/'):
        if len(names.name.stories_id) > index != 0:
            reply = create_kb_for_not_published_stories(index - 1)
            await callback.message.delete()
            await send_story_to_chat(names.name.stories_id[index - 1], config.tg_bot.admin_id, reply)
            await callback.answer()
    elif callback.data.startswith('next_story/'):
        if len(names.name.stories_id) > index:
            reply = create_kb_for_not_published_stories(index + 1)
            await callback.message.delete()
            await send_story_to_chat(names.name.stories_id[index + 1], config.tg_bot.admin_id, reply)
            await callback.answer()
    elif callback.data.startswith('not_published/'):
        await callback.message.delete()
        await send_story_to_moderator(index)
    elif callback.data.startswith('close_stories/'):
        await callback.message.delete()
        await callback.answer()
