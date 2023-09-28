from contextlib import contextmanager
import logging
import os

import sqlite3
import psycopg2
from psycopg2.extras import DictCursor
from dotenv import load_dotenv

load_dotenv()

from settings import Settings


def connect(func):
    def wrapper(*args, **kwargs):
        with open_db(os.environ.get("DB_SQLITE_PATH")) as sqlite_cur, closing(
            psycopg2.connect(**Settings().dict(), cursor_factory=DictCursor)
        ) as pg_con:
            return func(*args, **kwargs, sqlite_cur=sqlite_cur, pg_con=pg_con)

    return wrapper


@contextmanager
def open_db(file_name: str):
    conn = sqlite3.connect(file_name)
    try:
        logging.info("Creating connection")
        yield conn.cursor()
    finally:
        logging.info("Closing connection")
        conn.commit()
        conn.close()


@contextmanager
def closing(thing):
    try:
        yield thing
    finally:
        thing.commit()
        thing.close()
