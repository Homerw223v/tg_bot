import asyncio
from datetime import datetime

from bot.create_bot import dp, bot, set_main_menu
from handlers import state_for_commercial, client_handlers, state_for_news, other_handlers, state_for_story, \
    hiragana_state
from database.db import sql_start
from database.db_func import get_banned_users
from city.city import create_cities
import names


async def main():
    print('-----Starting bot...')
    await set_main_menu(bot)
    await sql_start()
    await create_cities()
    names.name.banned_users = await get_banned_users()
    dp.include_routers(client_handlers.router, state_for_commercial.router, state_for_news.router,
                       state_for_story.router, hiragana_state.router, other_handlers.router)
    await bot.delete_webhook(drop_pending_updates=True)
    print(f'-----Bot started at {datetime.now()}.')
    await dp.start_polling(bot)


async def on_shutdown(_):
    await dp.storage.close()


if __name__ == '__main__':
    asyncio.run(main())
