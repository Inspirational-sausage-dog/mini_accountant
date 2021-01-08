import os
from typing import Dict, List, Tuple

import sqlite3

conn = sqlite3.connect(os.path.join("db", "finance.db"), check_same_thread=False)
cursor = conn.cursor()

def insert(table: str, column_values: Dict):
    columns = ', '.join(column_values.keys())
    values = [tuple(column_values.values())]
    placeholders = ', '.join('?' * len(column_values.keys()))
    cursor.executemany(
        f"INSERT INTO {table}"
        f"({columns})"
        f"VALUES ({placeholders})",
        values)
    conn.commit()

def fetchall(table: str, columns: List[str]) -> List[Tuple]:
    columns_joined = ', '.join(columns)
    cursor.execute(f"SELECT {columns_joined} FROM {table}")
    rows = cursor.fetchall()
    result = []
    for row in rows:
        dict_row = {}
        for index, column in enumerate(columns):
            dict_row[column] = row[index]
        result.append(dict_row)
    return result

def delete(table: str, condition: Dict):
    """ Delete rows with passed condition """
    column = ', '.join(condition.keys())
    value = ', '.join(str(v) for v in condition.values())
    placeholder = "?"
    print(column, value)
    query = f"DELETE FROM {table} WHERE {column} = {placeholder}"
    cursor.execute(query, (value,))
    conn.commit()

def get_cursor():
    return cursor

def _init_db():
    """Инициализирует дб"""
    with open("createdb.sql", "r") as f:
        sql = f.read()
    cursor.executescript(sql)
    conn.commit()

def check_db_exists():
    """Проверяет инициализацию дб"""
    cursor.execute("SELECT name FROM sqlite_master "
                   "WHERE type='table' AND name='expenses'")
    table_exists = cursor.fetchall()
    if table_exists:
        return
    _init_db()

check_db_exists()
