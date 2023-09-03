def commercial_string(time, times, ) -> str:
    days = "дня" if 1 < int(times) < 5 else 'дней'
    message = f'Реклама будет опубликована в группе {time} каждый день на протяжении {times} {days}'
    return message


def news_string(time):
    message = f'Текст будет опубликован в группе {time}'
    return message


def story_string(time):
    message = f"История будет опубликована {time}"
    return message
