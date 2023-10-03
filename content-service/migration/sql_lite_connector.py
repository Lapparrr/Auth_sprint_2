import sqlite3
import logging

from typing import List, Any


class SQLite:
    def __init__(self, cursor: sqlite3.Cursor, package_limit: int):
        self.cur = cursor
        self.package_limit = package_limit

    def extract_data_by_table_name(self, table_name: str) -> dict:
        data = self.cur.execute(f"""SELECT * FROM {table_name}""")
        return data

    # Получение таблиц из SQLite
    def extract_all_table_name(self):
        self.cur.execute("SELECT name FROM sqlite_master WHERE type = 'table'")
        self.tables = self.cur.fetchall()
        return self.tables

    def count_len(self, table_name: str, schema: str) -> List[Any]:
        self.cur.execute(
            f"""SELECT count(*) as exact_count from {schema}{table_name}"""
        )
        return self.cur.fetchall()

    def _prepare_data(self, cur, row: list) -> dict:
        data = {}
        for index, column in enumerate(cur.description):
            data[column[0]] = row[index]
        return data

    def load_sqlite(self, table: str) -> tuple:
        try:
            self.cur.row_factory = self._prepare_data
            try:
                self.cur.execute(f"SELECT * FROM {table}")
            except sqlite3.Error as e:
                raise e
            while True:
                rows = self.cur.fetchmany(size=self.package_limit)

                if not rows:
                    return
                yield from rows
        except Exception as exception:
            logging.error(exception)

    def reformat_sqlite_fields(self, elem: dict) -> dict:
        # Создаем функцию осуществления замены по различающимся полям данным.
        # Список необходим для расширения, в случае добавления новых данных.

        if "created_at" in elem.keys():
            elem["created"] = elem["created_at"]
            del elem["created_at"]
        if "updated_at" in elem.keys():
            elem["modified"] = elem["updated_at"]
            del elem["updated_at"]
        if "file_path" in elem.keys():
            del elem["file_path"]
        return elem

    def format_dataclass_data(self, table: str, dataclass) -> List[Any]:
        data = self.load_sqlite(table)
        return [dataclass(**self.reformat_sqlite_fields(elem)) for elem in data]
