import datetime


import sqlite3
from psycopg2.extensions import connection as _connection
from typing import List, Any
from dotenv import load_dotenv

load_dotenv()


from connect_db import connect
from settings import datatables_list
from sql_lite_connector import SQLite
from postgres_connector import Postgres


@connect
def get_len(table: str, sqlite_cur: sqlite3.Cursor, pg_con: _connection) -> List[int]:
    sql = SQLite(sqlite_cur, 10)
    count_lite = sql.count_len(table, "")
    sql = Postgres(pg_con)
    count_postgre = sql.count_len("content.", table)
    print(count_lite[0][0], count_postgre[0][0])
    return [count_lite[0][0], count_postgre[0][0]]


# Данный метод для сравнения данных с двух баз
@connect
def comapare_data(table: str, sqlite_cur: sqlite3.Cursor, pg_con: _connection) -> str:
    # Создаем объект класса Postgres, где описаны методы взаимодейсвия с Postgres
    sql_postgres = Postgres(pg_con)
    # Забираем данные из таблицы table
    sql_postgres.extract_data_by_table_name("content.", table)
    sql_data_postgres = sql_postgres.cur.fetchall()
    # Получаем расположение индексов(типов) таблицы, чтобы потом сопоставить с sqlite
    field_names_postgres = sql_data_postgres[0]._index
    id_posgres = field_names_postgres["id"]
    new_postgre_data = dict()
    for postgres_data in sql_data_postgres:
        new_postgre_data[postgres_data[id_posgres]] = postgres_data
    sql_lite = SQLite(sqlite_cur, 10)

    status = "Good"
    schema = datatables_list[table]

    # Забираем данные с SQLite, при этом приобразуем поля, чтобы были одинаковые
    extract_data = sql_lite.format_dataclass_data(table, schema)
    for data_sql in extract_data:
        if status == "Bad":
            break
        # Валидируем данные
        fields, new_data = sql_postgres.validation(data_sql, schema)
        id_sql_lite = new_data[fields.index("id")]
        if new_postgre_data.__contains__(id_sql_lite):
            for (
                item,
                field,
            ) in zip(new_postgre_data[id_sql_lite], field_names_postgres):
                sql_lite_index = fields.index(field)

                # Если формат дата, то преобразуем две даты в единый формат, чтобы сравнить
                if type(item) is datetime.datetime:
                    new_postgres_value = item.replace(tzinfo=None)
                    new_sql_lite_value = datetime.datetime.strptime(
                        new_data[sql_lite_index], "%Y-%m-%d %H:%M:%S.%f+00"
                    )
                else:
                    new_postgres_value = item
                    new_sql_lite_value = new_data[sql_lite_index]
                if new_postgres_value != new_sql_lite_value:
                    status = "Bad"
                    break
        else:
            status = "Bad"
            break
        return status
