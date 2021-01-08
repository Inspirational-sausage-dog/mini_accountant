""" Работа с затратами """
from typing import Dict, List, NamedTuple, Optional
import datetime
import db

import pytz

from categories import Category, Categories

class Expense(NamedTuple):
    """ Expense structure """
    id: Optional[int]
    ammount: float
    category_id: Optional[int]

def add_expense(category_name: str, ammount: float):
    """ Add expense associated with category """
    category = Categories().get_category(category_name)
    db.insert("expenses", {
        "category_id" : category.id,
        "ammount" : ammount,
        "created" : _get_now_formatted()
        })

def delete_expenses(category: Category):
    """ Delete expenses by category id """
    db.delete("expenses", {"category_id" : category.id})

def get_today_expenses() -> str:

    cursor = db.get_cursor()
    cursor.execute("SELECT c.name, e.created, e.ammount "
            "FROM expenses e "
            "LEFT JOIN categories c "
            "ON e.category_id = c.id "
            "WHERE date(created) = date('now', 'localtime')"
            "ORDER BY c.name ASC"
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
