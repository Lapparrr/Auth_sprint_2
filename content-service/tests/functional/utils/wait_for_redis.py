import time
from tests.functional.settings import settings
from redis import Redis



if __name__ == '__main__':
    r_client = Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, decode_responses=True)
    while True:
        if r_client.ping():
            break
        time.sleep(1)