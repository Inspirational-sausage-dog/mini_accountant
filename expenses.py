""" Работа с затратами """
import os

from typing import Dict, List, NamedTuple, Optional, Tuple
from enum import Enum
import datetime
import db
import exceptions

import re
import pytz

from categories import Category, Categories

class Date(Enum):
    LAST = 0
    TODAY = 1
    MONTH = 2

class Message(NamedTuple):
    """ Message structure """
    category_name: str
    ammount: float

class Expense(NamedTuple):
    """ Expense structure """
    id: Optional[int]
    ammount: float
    category_name: str

def add_expense(raw_message: str):
    """ Add expense associated with category """
    message = _parse_input(raw_message)
    category = Categories().get_category(message.category_name)
    if not category:
        category = Categories().add_category(message.category_name)
    db.insert("expenses", {
        "category_id" : category.id,
        "ammount" : message.ammount,
        "created" : _get_now_formatted()
        })

def delete_expenses(category: Category):
    """ Delete expenses by category id """
    db.delete("expenses", {"category_id" : category.id})

def delete_last() -> str:
    """ [DOESN'T WORK]Delete last added expense, returns status of whether it deleted or not """
    cursor = db.get_cursor()
    result = db.fetchall("expenses", ['created'])
    if not result:
        return "There are no expenses yet."
    cursor.execute(
            "DELETE FROM expenses "
            "WHERE created IN "
            "(SELECT created FROM expenses "
            "ORDER BY created DESC LIMIT 1)"
            )
    return "Last expense was successfully deleted\n"

def get_last_expenses() -> str:
    """ Return answer containing last 10 expenses """
    cursor = db.get_cursor()
    cursor.execute(
            "SELECT c.name, e.created, e.ammount "
            "FROM expenses e "
            "LEFT JOIN categories c "
            "ON e.category_id = c.id "
            "ORDER BY created DESC "
            "LIMIT 10"
            )
    rows = cursor.fetchall()

    if not rows:
        return "There are no expenses yet\n"

    message = "Last 10 expenses:\n\n"
    for row in rows:
        name = row[0]
        created = row[1]
        ammount = row[2]
        message+=f"{created} | {name} | {ammount}\n"
    return message

def get_expenses(date: Date) -> str:

    switcher = {
            Date.LAST: get_last_expenses(),
            Date.TODAY: "Today's expenses: " + _parse_output('%Y-%m-%d'),
            Date.MONTH: "This month's expenses: " + _parse_output('%Y-%m')
            }
    return switcher.get(date)

def _parse_output(date: str)-> str:
    """ Return a parsed answer containing expenses in selected date """
    cursor = db.get_cursor()
    cursor.execute(
            "SELECT c.name, e.created, e.ammount "
            "FROM expenses e "
            "LEFT JOIN categories c "
            "ON e.category_id = c.id "
            f"WHERE strftime('{date}', created) = strftime('{date}', 'now') "
            "ORDER BY c.name ASC"
            )
    rows = cursor.fetchall()
    if not rows:
        return "There are no expenses yet\n"

    message = ""
    name = ""
    total = 0
    category_total = 0
    for row in rows:
        if name != row[0]:
            if name != "":
                message+="Category total: " + str(category_total)
                category_total = 0
            name = row[0]
            message+= "\n\n" + (f"{name}:\n").capitalize()
        created = datetime.datetime.strptime(row[1], "%Y-%m-%d %H:%M:%S")
        ammount = row[2]
        total += int(ammount)
        category_total+= int(ammount)
        message+=f"{created} | {ammount} \n"

    return message + "Category total: " + str(category_total) + "\n\nCurrent balance: " + str(total)

def _parse_input(raw_message: str) -> Message:
    """ Parse text and return a message object containing category name and ammount """
    regexp_result = re.match(r"(.*) (-?[\d]+)", raw_message)
    if not regexp_result or not regexp_result.group(0) \
            or not regexp_result.group(1) or not regexp_result.group(2):
        raise exceptions.NotCorrectMessageException(
                "Could not understand message. Please answer in format:\n"
                "Category Ammount\n"
                "For example: Transport -1000\n"
                )

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
