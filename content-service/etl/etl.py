import logging
import sys
import time
from datetime import datetime

import requests
from elasticsearch import Elasticsearch
from psycopg2.extensions import connection as _connection
from pydantic import parse_obj_as
from tqdm import tqdm
from elasticsearch.helpers import bulk

from helpers import State, backoff
from models import MoviesToES, GenreToES, PersonToES
from queries import (
    SQL_GENRES,
    SQL_MOVIES,
    SQL_PERSONS,
    SQL_GENRES_GENRES,
    SQL_PERSONS_PERSONS,
    SCHEMA_JSON_MOVIES,
    SCHEMA_JSON_GENRES,
    SCHEMA_JSON_PERSONS,
)
from storage import BaseStorage, JsonFileStorage
from settings import SettingsElastic, JsonPath

logging.basicConfig(stream=sys.stdout, level=logging.INFO)

KEYS = ["movies", "persons", "genres"]

QUERIES_MAPPING = {
    "movies_movies": SQL_MOVIES,
    "persons_movies": SQL_PERSONS,
    "genres_movies": SQL_GENRES,
    "genres_genres": SQL_GENRES_GENRES,
    "persons_persons": SQL_PERSONS_PERSONS,
}

MODELS_MAPPING = {"movies": MoviesToES, "persons": PersonToES, "genres": GenreToES}


class PostgresExtractor:
    """Извлекает данные из postgres"""

    def __init__(self, conn, batch_size=30):
        self.conn = conn
        self.batch_size = batch_size

    def _get_data(self, sql: str):
        with self.conn.cursor() as curs:
            curs.execute(sql)
            while result := curs.fetchmany(self.batch_size):
                yield result

    def get_data(self, key: str, p_date: datetime):
        """Получает данные по ключу и дате изменения

        Arguments:
            key {str} -- [description]
            p_date {datetime} -- [description]

        Returns:
            [type] -- [description]
        """
        if key not in QUERIES_MAPPING:
            return ValueError()
        sql = QUERIES_MAPPING[key]
        with self.conn.cursor() as curs:
            query = curs.mogrify(sql, [(p_date)])
        return self._get_data(query)


class ESTransformerLoader:
    """Трансформирует данные и загружает в Elastic"""

    def __init__(self, es_con):
        self.url_es = f"http://{SettingsElastic().es_host}:{SettingsElastic().es_port}"
        self.client = es_con
        self._init_schema()

    def _load(self, index, row_: dict):
        documents = [
            {"_index": index, "_id": row["uuid"], "_source": row} for row in row_
        ]
        bulk(self.client, documents)

    def _init_schema(self):
        requests.put(self.url_es + "/movies", json=SCHEMA_JSON_MOVIES)
        requests.put(self.url_es + "/genres", json=SCHEMA_JSON_GENRES)
        requests.put(self.url_es + "/persons", json=SCHEMA_JSON_PERSONS)

    def _transform_data(self, data: list, index) -> list[dict]:
        models = parse_obj_as(list[MODELS_MAPPING[index]], data)
        dicts = [mod.dict(exclude={"persons": True, "id": True}) for mod in models]
        return dicts

    def load_batch(self, data: list, index: str) -> None:
        rows = self._transform_data(data, index)
        self._load(index, rows)


class ETLPipeline:
    def __init__(
        self,
        pg_extractor: PostgresExtractor,
        es_transloader: ESTransformerLoader,
        storage: BaseStorage,
        timeout: int = 60,
    ):
        """Пайплайн, которые объединяет шаги Extract, Transform Load,
        а также позволяет запускать их в отказоустойчивом цикле

        Arguments:
            pg_extractor {PostgresExtractor} -- [description]
            es_transloader {ESTransformerLoader} -- [description]
            storage {BaseStorage} -- [description]
            keys {list[str]} -- Ключи, по которым будет происходить извлечение данных

        Keyword Arguments:
            timeout {int} -- [description] (default: {60})
        """
        self.pg_extractor = pg_extractor
        self.es_transloader = es_transloader
        self.storage = storage
        self.state = State(self.storage)
        self.timeout = timeout

    def etl_pipeline_movies(self, index, keys):
        """Один цикл пайплайна"""
        for key in keys:
            next_state = datetime.now()
            curr_state = self.state.get_state(index + "_" + key)
            logging.info(f"Key: {index}, state: {curr_state}")
            for data in tqdm(self.pg_extractor.get_data(key, curr_state)):
                logging.info("loading chunk")
                self.es_transloader.load_batch(data, index)
            self.state.set_state(index + "_" + key, next_state)

    def etl_loop(self):
        """Отказоустойчивый бесконечный цикл"""
        while True:
            self.etl_pipeline_movies(
                index="movies",
                keys=["movies_movies", "persons_movies", "genres_movies"],
            )
            self.etl_pipeline_movies(index="persons", keys=["persons_persons"])
            self.etl_pipeline_movies(index="genres", keys=["genres_genres"])

            time.sleep(self.timeout)


@backoff
def launch_loop(pg_conn: _connection, es_con: Elasticsearch):
    """Функция для запуска цикла в main

    Arguments:
        pg_conn {[type]} -- [description]
        es_con {[type]} -- [description]
    """
    pg_ext = PostgresExtractor(pg_conn)
    es_loader = ESTransformerLoader(es_con)
    etl_pipeline = ETLPipeline(pg_ext, es_loader, storage, timeout=60)
    etl_pipeline.etl_loop()


if __name__ == "__main__":
    storage = JsonFileStorage(JsonPath().json_storage_path)
    keys = ["movies", "persons", "genres"]
    launch_loop()
