import sqlite3

base = sqlite3.connect('../WartimeRussia.db')
base.row_factory = sqlite3.Row
cur = base.cursor()


async def sql_start():
    if base:
        base.execute('CREATE TABLE IF NOT EXISTS banned_users('
                     'user_id INT PRIMARY KEY,'
                     'since TEXT);')
        base.execute('CREATE TABLE IF NOT EXISTS stories('
                     'id INTEGER PRIMARY KEY AUTOINCREMENT,'
                     'city STRING,'
                     'content_type,'
                     'file_id TEXT,'
                     'file_unique_id TEXT,'
                     'story TEXT,'
                     'author STRING,'
                     'date_added TEXT,'
                     'published STRING,'
                     'will_be_published_at TEXT)')
        base.execute('CREATE TABLE IF NOT EXISTS commercial('
                     'id INTEGER PRIMARY KEY AUTOINCREMENT,'
                     'commercial TEXT,'
                     'times INTEGER,'
                     'content_type STRING,'
                     'file_id STRING,'
                     'file_unique_id STRING,'
                     'link STRING,'
                     'button_text STRING)')
    base.commit()
