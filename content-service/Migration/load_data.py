import os
import logging
import sqlite3

import psycopg2
from psycopg2.extensions import connection as _connection
from psycopg2.extras import DictCursor
from dotenv import load_dotenv

load_dotenv()

from sql_lite_connector import SQLite
from postgres_connector import Postgres
from connect_db import connect
from settings import datatables_list


@connect
def load_from_sqlite(sqlite_cur: sqlite3.Cursor, pg_con: _connection):
    """Основной метод загрузки данных из SQLite в Postgres"""

    sqlite_extractor = SQLite(sqlite_cur, 10)
    postgres_saver = Postgres(pg_con)
    for base, schema in datatables_list.items():
        try:
            extract_data = sqlite_extractor.format_dataclass_data(base, schema)
            postgres_saver.insert_data(base, extract_data, schema)
        except Exception as exception:
            logging.error(exception)


if __name__ == "__main__":
    load_from_sqlite()
