import time
from tests.functional.settings import settings
from elasticsearch import Elasticsearch


if __name__ == '__main__':
    es_client = Elasticsearch(hosts=f'http://{settings.ELASTIC_HOST}:{settings.ELASTIC_PORT}')
    while True:
        if es_client.ping():
            break
        time.sleep(1)

