from psycopg2.extensions import connection as _connection
from typing import List, Any

from dataclasses import dataclass


class Postgres:
    def __init__(self, pg_conn: _connection):
        self.pg_conn = pg_conn
        self.cur = pg_conn.cursor()

    def insert_data(self, base: str, extract_data: list, schema: dataclass):
        for data in extract_data:
            fields, new_data = self.validation(data, schema)
            to_mogrify = ", ".join(["%s"] * len(fields))
            self.cur.execute(
                f"""INSERT INTO content.{base} ({', '.join(fields)}) VALUES ({to_mogrify}) 
                            ON CONFLICT (id) DO NOTHING""",
                new_data,
            )

    @staticmethod
    def validation(data: dataclass, schema: dataclass):
        fields = list()
        new_data = list()
        for i in list(schema.__dataclass_fields__):
            if getattr(data, i) == None:
                new_data.append(getattr(schema, i))
            else:
                new_data.append(getattr(data, i))
            fields.append(i)
        return fields, new_data

    def count_len(self, schema: str, table_name: str) -> List[Any]:
        self.cur.execute(
            f"""SELECT count(*) as exact_count from {schema}{table_name}"""
        )
        return self.cur.fetchall()

    def extract_data_by_table_name(self, schema: str, table_name: str) -> dict:
        data = self.cur.execute(f"""SELECT * FROM {schema}{table_name}""")
        return data
