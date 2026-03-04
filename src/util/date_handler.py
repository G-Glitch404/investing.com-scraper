import re
from typing import Union
import datetime as dt

from src.core.logger import Logger
from src.settings import settings
from src.util.utils import to_datetime_aware, format_date
from src.util.decorators import catch_exceptions

logger = Logger('DatesHandlers')


@catch_exceptions
def convert_time_date(date: str) -> Union[dt.datetime, bool]:
    """
     convert a time to a date. e.g. ("1d", "2h", "3m", "4s")
     :param date: (str) time
     :return: (Union[str, bool]) date as str or False if failed
    """
    if isinstance(date, int):
        return to_datetime_aware(dt.datetime.fromtimestamp(date))

    if not isinstance(date, str) and not len(date) >= 2:
        logger.error(f"invalid date provided can't be converted {date}")
        return False

    date: str = date.strip().replace('hours ago', 'h').replace('minutes ago', 'm')
    if re.match(r'^\d{1,2} \w$|^\d{1,2}\w$', date):  # re pattern for date format: 23 h
        char: str = date[-1].lower()
        if 'h' == char: delta = dt.timedelta(hours=int(date[:-1]))
        elif 's' == char: delta = dt.timedelta(seconds=int(date[:-1]))
        elif 'M' == date[-1]: delta = dt.timedelta(weeks=int(date[:-1]) * 4)
        elif 'm' == char: delta = dt.timedelta(minutes=int(date[:-1]))
        elif 'd' == char: delta = dt.timedelta(days=int(date[:-1]))
        elif 'w' == char: delta = dt.timedelta(weeks=int(date[:-1]))
        elif 'y' == char: delta = dt.timedelta(weeks=int(date[:-1]) * 48)
        else:
            logger.warning(f"couldn't convert date format: {date} detected as 23 h pattern.")
            return False

        return to_datetime_aware(dt.datetime.now() - delta)

    date: str = date.lower()
    if re.match(r'^\d{2}/\d{2}/\d{4},\d{2}:\d{2} [AaPp][Mm]$', date):  # re pattern for date format: 08/30/2024,04:14 pm
        formatted_date = format_date(date, "%m/%d/%Y,%H:%M %p")
        if formatted_date: return formatted_date

    re_pattern: str = r"^\d{2} \w+ \d{4} \d{2}:\d{2}, utc$|^\d{2} \w+ \d{4} \d{2}:\d{2}$"
    if re.match(re_pattern, date):  # regex pattern for date format: 24 august 2024 20:38, utc
        if formatted_date := format_date(date, "%d %B %Y %H:%M, %Z"):
            return formatted_date

    logger.warning(f"none of the current date formats matched date format: {date}")
    return False


if __name__ == '__main__':
    settings['ALLOWED_DATE'] = dt.date(2026, 1, 7)
    for pattern in ['12 hours ago', 'Jan 31, 2026', '24 august 2024 20:38, utc', '1h', '23 H', '08/30/2024,04:14 pm', '25h', '05 September 2024 19:22, UTC']:
        date_ = convert_time_date(pattern)
        print(date_)
        print(f"{pattern} -> {date_} -> {to_datetime_aware(date_)}")
