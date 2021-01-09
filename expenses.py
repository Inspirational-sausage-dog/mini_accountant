""" Работа с затратами """
import os

from typing import Dict, List, NamedTuple, Optional
import datetime
import db
import exceptions

import re
import pytz

from categories import Category, Categories

class Message(NamedTuple):
    """ Message structure """
    category_name: str
    ammount: float

class Expense(NamedTuple):
    """ Expense structure """
    id: Optional[int]
    ammount: float
    category_id: Optional[int]

def add_expense(raw_message: str):
    """ Add expense associated with category """
    message = _parse_message(raw_message)
    category = Categories().get_category(message.category_name)
    if not category:
        raise exceptions.CategoryDoesNotExistException(
                "Category does exist.\n"
                "Try again\n"
                )
    db.insert("expenses", {
        "category_id" : category.id,
        "ammount" : message.ammount,
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

def _parse_message(raw_message: str) -> Message:
    """ Parse text and return a message object containing category name and ammount """
    regexp_result = re.match(r"(.*) ([\d]+)", raw_message)
    if not regexp_result or not regexp_result.group(0) \
            or not regexp_result.group(1) or not regexp_result.group(2):
        raise exceptions.NotCorrectMessageException(
                "Cannot understand message. Try writing message in format:\n"
                "Transport 2000\n")

    category_name = regexp_result.group(1).strip().lower()
    ammount = regexp_result.group(2)
    return Message(category_name = category_name, ammount = ammount)

def _get_now_formatted()  -> str:
    """ Return today's date and time as a string """
    return _get_now_datetime().strftime("%Y-%m-%d %H:%M:%S")

def _get_now_datetime() -> datetime.datetime:
    """ return current datetime in enviroment's timezone """
    tz = pytz.timezone(os.getenv("TZ"))
    now = datetime.datetime.now(tz)
    return now
