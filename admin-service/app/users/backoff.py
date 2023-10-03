import logging
from functools import wraps
from time import sleep


logger = logging.getLogger(__name__)


def backoff(start_sleep_time=0.1, factor=2, border_sleep_time=10, logger=logger):
    """
    Функция для повторного выполнения функции через некоторое время.
    """

    def func_wrapper(func):
        @wraps(func)
        def inner(*args, **kwargs):
            time_for_sleep = start_sleep_time
            while True:
                try:
                    sleep(time_for_sleep)
                    result = func(*args, **kwargs)
                    break
                except Exception as error:
                    logger.error(error)
                    if time_for_sleep >= border_sleep_time:
                        time_for_sleep = border_sleep_time
                    else:
                        time_for_sleep = time_for_sleep * 2 ** factor
            return result
        return inner
    return func_wrapper