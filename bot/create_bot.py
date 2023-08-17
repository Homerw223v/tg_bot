from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand
from aiogram.fsm.storage.redis import RedisStorage, Redis
from .config import Config, load_config
from lexicon.LEXICON_RU import LEXICON_COMMANDS

config: Config = load_config()
redis = Redis(host='redis')
# redis = Redis(host='127.0.0.1')
storage = RedisStorage(redis=redis)
bot = Bot(token=config.tg_bot.token, parse_mode='HTML')

dp = Dispatcher(storage=storage)


async def set_main_menu(my_bot: Bot):
    main_menu_commands = [BotCommand(
        command=command,
        description=description
    ) for command, description in LEXICON_COMMANDS.items()
    ]
    await my_bot.set_my_commands(main_menu_commands)
