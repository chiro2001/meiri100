import datetime


def get_date_timestamp(date) -> int:
    return int(datetime.datetime.timestamp(datetime.datetime.fromisoformat(date)) * 1000)


def get_timestamp_date(timestamp) -> str:
    return datetime.datetime.fromtimestamp(int(timestamp / 1000)).isoformat()[:10]


# YYYY-MM-DD 格式
def get_date_today() -> str:
    # TODO: 有可能以4:00做刷新界限
    return get_timestamp_date(datetime.datetime.today().timestamp() * 1000)


def get_date_tomorrow(date_now=None) -> str:
    if date_now is None:
        return get_timestamp_date(1000 * (datetime.datetime.today().timestamp() + 60 * 60 * 24))
    else:
        return get_timestamp_date(1000 * (get_date_timestamp(date_now) + 60 * 60 * 24))


# weekday: Monday是0，Sunday是6
def get_next_week_date(day: int) -> str:
    day_now = (datetime.datetime.now().weekday() + 1) % 7
    # print(f'day: {day}, day_now: {day_now}, += {day - day_now + 7}')
    if day == day_now:
        return get_timestamp_date(1000 * datetime.datetime.today().timestamp())
    if day > day_now:
        return get_timestamp_date(1000 * (datetime.datetime.today().timestamp() + 60 * 60 * 24 * (day - day_now)))
    # day < day_now
    return get_timestamp_date(1000 * (datetime.datetime.today().timestamp() + 60 * 60 * 24 * (day - day_now + 7)))
