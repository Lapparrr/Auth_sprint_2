import time
from functools import wraps


def backoff(exceptions=Exception, start_sleep_time=1, factor=2, border_sleep_time=60):
    if start_sleep_time <= 0:
        raise ValueError("start_sleep_time must be greater than 0")

    if factor <= 1:
        raise ValueError("factor must be greater than 1")

    if border_sleep_time <= 1:
        raise ValueError("border_sleep_time must be greater than 1")

    def func_wrapper(target):
        @wraps(target)
        async def inner(*args, **kwargs):
            _tries = 0
            while True:
                try:
                    value = await target(*args, **kwargs)
                    if value:
                        return value
                    _tries += 1
                    time.sleep(1)

                except exceptions as ex:
                    _tries -= 1
                    if _tries == 0:
                        raise ex

        return inner

    return func_wrapper
