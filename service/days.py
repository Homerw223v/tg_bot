from datetime import datetime, timedelta

import names


def days_for_choosing() -> dict:
    day_of_weeks = dict()
    for i in range(names.name.count):
        day_of_weeks[str(i)] = (
                (datetime.now() + timedelta(hours=names.name.utc)).date() + timedelta(days=i)).strftime('%Y-%m-%d')
    return day_of_weeks


names.name.dates = days_for_choosing()
