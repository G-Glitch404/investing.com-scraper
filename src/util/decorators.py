import json
import time

from src.core.logger import Logger
from functools import wraps
from typing import Any, Callable

retry_logger = Logger("Retry")
catch_logger = Logger('ExceptionsHandler')


def catch_exceptions(func, exceptions: tuple = (Exception, json.decoder.JSONDecodeError)) -> Callable:
    """ decorator for catching selenium exceptions """
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        try: return func(*args, **kwargs)
        except exceptions as e:
            catch_logger.exception(f'function "{func.__name__}" failed with exception "{e}" and parameters: "{args, kwargs}"')
            return False

    return wrapper


def retry(
        func,
        times: int = 3,
        interval: int = 5,
        exceptions: tuple = (Exception, json.decoder.JSONDecodeError)
) -> Callable:
    """ decorator for retrying a function after failure """
    @wraps(func)
    def wrapper(*args, **kwargs) -> Any:
        for _ in range(times):
            try:
                response = func(*args, **kwargs)
                if not response:
                    retry_logger.error(f'function "{func.__name__}" failed with bad response "{response}" \n with parameters: {args, kwargs} retying after {interval} seconds.')
                    continue
                return response
            except exceptions as e:
                retry_logger.exception(f'function "{func.__name__}" failed with exception "{e}" \n with parameters: {args, kwargs} retrying after {interval} seconds.')
                time.sleep(interval)
        return False

    return wrapper
