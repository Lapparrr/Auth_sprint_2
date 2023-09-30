import logging
import sys
import time
from contextlib import closing, contextmanager

from elasticsearch import Elasticsearch
from typing import Any
import psycopg2
from psycopg2.extras import DictCursor

from storage import BaseStorage
from settings import SettingsPostgres, SettingsElastic

logging.basicConfig(stream=sys.stdout, level=logging.INFO)


class State:
    """
    Класс для хранения состояния при работе с данными, чтобы постоянно не перечитывать данные с начала.
    Здесь представлена реализация с сохранением состояния в файл.
    В целом ничего не мешает поменять это поведение на работу с БД или распределённым хранилищем.
    """

    def __init__(self, storage: BaseStorage):
        self.storage = storage

    def set_state(self, key: str, value: Any) -> None:
        """Установить состояние для определённого ключа"""
        self.storage.save_state({key: value})

    def get_state(self, key: str) -> Any:
        return self.storage.retrieve_state(key)


def backoff(func, start_sleep_time=0.1, factor=2, border_sleep_time=10):
    """
    Функция для повторного выполнения функции через некоторое время, если возникла ошибка. Использует наивный экспоненциальный рост времени повтора (factor) до граничного времени ожидания (border_sleep_time)

    Формула:
        t = start_sleep_time * 2^(n) if t < border_sleep_time
        t = border_sleep_time if t >= border_sleep_time
    :param start_sleep_time: начальное время повтора
    :param factor: во сколько раз нужно увеличить время ожидания
    :param border_sleep_time: граничное время ожидания
    :return: результат выполнения функции
    """

    def func_wrapper(*args, **kwargs):
        cur_time = start_sleep_time
        while cur_time < border_sleep_time:
            try:
                with closing(
                    psycopg2.connect(
                        **SettingsPostgres().dict(), cursor_factory=DictCursor
                    )
                ) as pg_conn, closing(
                    Elasticsearch(
                        f"http://{SettingsElastic().es_host}:{SettingsElastic().es_port}"
                    )
                ) as es_con:
                    data = func(*args, **kwargs, pg_conn=pg_conn, es_con=es_con)
                    return data
            except Exception as e:
                logging.info(e)
                cur_time = start_sleep_time * 2 ** (factor)
                time.sleep(cur_time)

    return func_wrapper
