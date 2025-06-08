import typing
from datetime import datetime, timedelta

import pytz
from dateutil.parser import parse

__all__ = [
    'as_local', 'to_utc', 'as_utc', 'to_tz',
    'is_today', 'midnight',
    'any_to_datetime', 'convert_values_to_date',
    'US_Eastern', 'US_Central', 'US_Mountain', 'US_Pacific'
]

US_Eastern = pytz.timezone('US/Eastern')
US_Pacific = pytz.timezone('US/Pacific')
US_Central = pytz.timezone('US/Central')
US_Mountain = pytz.timezone('US/Mountain')


def now():
    return as_local(datetime.now())


def is_today(time_point: datetime):
    now = as_local(datetime.now())
    return abs((now - time_point)) < timedelta(days=1)


def as_local(d: datetime):
    if d.tzinfo is not None:
        return d
    return d.astimezone()


def as_utc(d: datetime):
    if d.tzinfo is not None:
        return d

    return pytz.UTC.localize(d)


def to_utc(d: datetime):
    return to_tz(d, pytz.UTC)


def to_tz(d: datetime, tzinfo: pytz.BaseTzInfo):
    d = as_local(d)
    return d.astimezone(tzinfo)


def midnight(d: datetime):
    return d.replace(hour=0, minute=0, second=0, microsecond=0)


def any_to_datetime(v, default=None):
    if isinstance(v, datetime):
        return as_local(v)
    if isinstance(v, int):
        if v > 10 ** 10:  # Check if the timestamp is in milliseconds
            v = v / 1000  # Convert milliseconds to seconds
        return as_local(datetime.fromtimestamp(v))
    if isinstance(v, str):
        try:
            d = parse(v)
            if d.tzinfo is None:
                d = pytz.UTC.localize(d)
            return d
        except ValueError:
            return default
    return default


def convert_values_to_date(data: typing.Dict) -> typing.Dict:
    return {
        k: _covert_value(v) for k, v in data.items()
    }


def _covert_value(v):
    if isinstance(v, dict):
        return convert_values_to_date(v)
    if isinstance(v, str):
        return any_to_datetime(v, v)
    if isinstance(v, list):
        return [convert_values_to_date(el) for el in v]
    return v
