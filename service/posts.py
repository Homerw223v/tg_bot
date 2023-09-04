import json
import datetime
import os
import random
from pathlib import Path
import names


def _next_day(data: dict, start_time, day: int) -> dict:
    for i in range(names.name.count - 1):
        data[str(i)] = data[str(i + 1)]
    data[str(names.name.count - 1)] = [
        (start_time + datetime.timedelta(days=day, hours=i, minutes=random.randint(1, 40))).strftime('%Y-%m-%d %H:%M')
        for i in range(15)]
    data[str(names.name.count)] = datetime.date.today().strftime('%Y-%m-%d')
    return data


def delete_time(day, time):
    names.name.days[str(day)].remove(time)
    save_weeks(names.name.days)


def save_weeks(data: dict):
    with open('days.json', 'w+', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=True, indent=4)


def _create_weeks_dict(start_time):
    week = dict()
    for i in range(names.name.count):
        week[str(i)] = [
            (start_time + datetime.timedelta(days=i, hours=j, minutes=random.randint(1, 40))).strftime('%Y-%m-%d %H:%M')
            for j in range(15)]
    week[str(names.name.count)] = datetime.date.today().strftime('%Y-%m-%d')
    return week


def create_days() -> dict:
    start_time = datetime.datetime.strptime(
        datetime.datetime.utcnow().replace(hour=10, minute=00).strftime('%Y-%m-%d %H:%M'), '%Y-%m-%d %H:%M')
    week: dict = _create_weeks_dict(start_time)
    if Path(os.getcwd() + r'/days.json').exists():
        with open('days.json', 'r', encoding='utf-8') as file:
            semi_week = json.loads(file.read())
            days_minus = datetime.date.today().day - datetime.datetime.strptime(semi_week[str(names.name.count)],
                                                                                '%Y-%m-%d').date().day
            if days_minus == 0:
                week = semi_week
            elif names.name.count > days_minus >= 1:
                for i in range(names.name.count - days_minus, names.name.count):
                    semi_week = _next_day(semi_week, start_time, i)
                week = semi_week
                save_weeks(week)
    else:
        save_weeks(week)
    return week


names.name.days = create_days()
