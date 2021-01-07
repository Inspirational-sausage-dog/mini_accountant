""" Работа с затратами """
from typing import Dict, List, NamedTuple, Optional
import datetime
import db

import pytz

from categories import Category

class Expense(NamedTuple):
    """ Структура затраты """
    id: Optional[int]
    ammount: float
    category_name: str

def add_expense(category_name: str, ammount: float) -> Expense:

    cursor = db.get_cursor()
    cursor.execute("SELECT id, name FROM categories WHERE name= ?", (category_name,))
    category_data = cursor.fetchone()

    db.insert("expenses", {
        "category_id" : category_data[0],
        "ammount" : ammount,
        "created" : _get_now_formatted()
        })

    return Expense(id = None,
                   ammount = ammount,
                   category_name = category_data[1])

def get_today_expenses() -> str:

    cursor = db.get_cursor()
    cursor.execute("SELECT c.name, e.created, e.ammount "
            "FROM expenses e "
            "LEFT JOIN categories c "
            "ON e.category_id = c.id "
            "WHERE date(created) = date('now', 'localtime')"
            )
    rows = cursor.fetchall()

    result = []
    for row in rows:
        dict_row = {}
        for index, column in enumerate(['name', 'created', 'ammount']):
            dict_row[column] = row[index]
        result.append(dict_row)

    message = ""
    name = ""
    for r in result:
        created = r['created']
        ammount = r['ammount']
        if name != r['name']:
            name = r['name']
            message+=f"\n{name}:\n"
        message+=f"{created} - {ammount} Рублей\n"
 
    return message

def _get_now_formatted()  -> str:
    """ Возращает сегодняшнюю дату строкой """
    return _get_now_datetime().strftime("%Y-%m-%d %H:%M:%S")

def _get_now_datetime() -> datetime.datetime:
    """ Возращает сегодняшний datetime с учетом временной зоны МСК. """
    tz = pytz.timezone("Europe/Moscow")
    now = datetime.datetime.now(tz)
    return now
