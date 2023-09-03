import random
from datetime import datetime
from random import shuffle
from .db import cur, base

from names.name import commercial_keys, publishing


async def add_user_to_banned_list(user_id: str):
    cur.execute(f'INSERT INTO banned_users('
                f'user_id, since) VALUES (?,?)',
                (user_id, datetime.utcnow(),))
    base.commit()


async def get_banned_users():
    user = cur.execute(f'SELECT user_id FROM banned_users').fetchall()
    users = [i[0] for i in user]
    print('-----List of banned users created')
    return users


async def save_story(story: dict, text: str):
    story_id = cur.execute(
        f'INSERT INTO stories('
        f' city, content_type, file_id, file_unique_id, story, author, date_added, published) VALUES (?,?,?,?,?,?,?,?)',
        (story.get('city'),
         story.get('content_type'),
         story.get('file_id'),
         story.get('file_unique_id'),
         story.get('story'),
         story.get('author'),
         datetime.utcnow(),
         text), ).lastrowid
    base.commit()
    return story_id


async def get_story(story_id):
    story = cur.execute(f'SELECT * FROM stories WHERE id = (?)', (story_id,)).fetchone()
    return story


async def publish_story_at(story_id: str, time: str, text: str):
    cur.execute(f'UPDATE stories SET published = ?, will_be_published_at = ? WHERE id=?', (text, time, story_id,))
    base.commit()


async def published_story(story_id: str, text: str):
    cur.execute(f'UPDATE stories SET published=? WHERE id=?', (text, story_id))
    base.commit()


def select_unpublished_stories():
    stories = cur.execute('SELECT id FROM stories WHERE published=?', (publishing[0],)).fetchall()
    stories = [i[0] for i in list(stories)]
    shuffle(stories)
    return stories


async def delete_story(story_id):
    cur.execute(f'DELETE FROM stories WHERE id=?', (story_id,))
    base.commit()


async def commercial_new(data: dict):
    commercial_id = cur.execute(
        'INSERT INTO commercial(commercial, times, content_type, file_id, file_unique_id, link, button_text)'
        ' VALUES (?,?,?,?,?,?,?)', (*data.values(),)).lastrowid
    base.commit()
    return commercial_id


async def get_commercial(commercial_id):
    answer = cur.execute('SELECT * FROM commercial WHERE id=?', (commercial_id,)).fetchone()
    commercial = dict()
    for key in commercial_keys:
        commercial[key] = answer[key]
    return commercial
