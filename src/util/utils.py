import os
import re
import math
import datetime as dt
from typing import Callable, Any

DEFAULT_DATE_FORMAT: str = "%Y-%m-%d %H:%M:%S"
max_articles_per_category: Callable[[int, int], int] = lambda max_articles, categories: math.ceil(max_articles / categories)
clean_text: Callable[[Any], str] = lambda text: re.sub('\n+|\\s+|\\t+|\\r+|\\r\\n+|\\r\\n', ' ', ''.join(text)).strip()


def to_datetime_aware(dt_obj: dt.datetime | dt.date | str) -> dt.datetime:
    """ convert date or datetime to an aware utc datetime """
    if isinstance(dt_obj, str):
        dt_obj: dt.datetime = dt.datetime.strptime(dt_obj, DEFAULT_DATE_FORMAT)

    if isinstance(dt_obj, dt.date) and not isinstance(dt_obj, dt.datetime):
        dt_obj: dt.datetime = dt.datetime.combine(dt_obj, dt.datetime.min.time())

    if dt_obj.tzinfo is None or dt_obj.utcoffset() is None or dt_obj.tzname() != 'UTC':
        return dt_obj.replace(tzinfo=dt.timezone.utc)

    return dt_obj


def format_date(date: str, formate: str = DEFAULT_DATE_FORMAT) -> dt.datetime:
    """ formats a date string to a datetime specific formate to normalize it """
    return to_datetime_aware(dt.datetime.strptime(date, formate))


def path(file_path: str, secondary_path: str = None) -> str:
    """ converts a relative path to an absolute path """
    seperator: str = '\\' if 'nt' in os.name.lower() else '/'
    file: str = os.path.join(
        seperator.join(
            os.path.realpath(
                os.path.join(
                    os.getcwd(),
                    os.path.dirname(__file__)
                )
            ).split(seperator)[:-1]),  # remove the current folder from path
        file_path
    )

    return file if secondary_path is None else os.path.join(file, secondary_path)
