""" Functions to create, delete expenses and return related statistics """
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
    PREVIOUS_MONTH = 1
    THIS_MONTH  = 2

class Message(NamedTuple):
    """ Message structure """
    category_name: str
    ammount: float
    created: str

def set_budget(user_id: int, ammount: int):
    """ Set user budget  """
    db.replace("budget", {"user_id" : user_id, "ammount" : ammount})

def add_expense(user_id: int, raw_message: str):
    """ Add expense associated with category """
    messages = _parse_input(raw_message)
    for message in messages:
        category = Categories().get_category(user_id, message.category_name)
        if not category:
            category = Categories().add_category(user_id, message.category_name)
        db.insert("expenses", {
            "user_id" : user_id,
            "category_id" : category.id,
            "ammount" : message.ammount,
            "created" : message.created
            })

def delete_category(category: Category):
    """ Delete expenses by category id """
    db.delete("expenses", {"category_id" : category.id})

def delete_last(user_id: int) -> str:
    """ Delete last added expense, returns status of whether it deleted or not """
    cursor = db.get_cursor()
    cursor.execute(
            "SELECT id FROM expenses "
            f"WHERE user_id = {user_id} "
            "ORDER BY created DESC LIMIT 1"
            )
    result = cursor.fetchone()
    if not result:
        return "There are no expenses yet."
    db.delete("expenses", {"id" : result[0]})
    return "Last expense was successfully deleted\n"

def get_last_expenses(user_id: int) -> str:
    """ Return answer containing last 10 expenses """
    cursor = db.get_cursor()
    cursor.execute(
            "SELECT c.name, e.created, e.ammount "
            "FROM expenses e "
            "LEFT JOIN categories c "
            "ON e.category_id = c.id "
            f"WHERE c.user_id = {user_id} "
            "ORDER BY created ASC "
            "LIMIT 10"
            )
    rows = cursor.fetchall()

    if not rows:
        return "There are no expenses yet\n"

    message = "Last 10 added expenses:\n"
    for row in rows:
        name = row[0]
        created = row[1]
        ammount = row[2]
        message+=f"\n{row[1]} | {row[0].capitalize()} | {row[2]}"
    return message

def get_expenses(user_id: int, date: Date) -> str:


    if date == Date.LAST:
        message = get_last_expenses(user_id)
    elif date == Date.PREVIOUS_MONTH:
        message = "Last month's expenses: " + _parse_output(user_id, "DATE('now', '-1 month')")
    elif date == Date.THIS_MONTH:
        message = "This month's expenses: " + _parse_output(user_id, "'now'")

    return message

def _parse_output(user_id: int, date: str)-> str:
    """ Return a parsed answer containing expenses in selected date """

    cursor = db.get_cursor()
    cursor.execute(f"SELECT ammount FROM budget WHERE user_id={user_id}")
    budget = cursor.fetchone()
    if not budget:
        set_budget(user_id, 5000)
        budget = (5000,)
    budget = budget[0]
    cursor.execute(
            f"SELECT c.name, strftime('%d-%m %H:%M', e.created), e.ammount, c.max_ammount "
            "FROM expenses e "
            "LEFT JOIN categories c "
            "ON e.category_id = c.id "
            f"WHERE (strftime('%Y-%m', created) = strftime('%Y-%m', {date}) "
            "OR created = 'Monthly') "
            f"AND c.user_id = {user_id} "
            "ORDER BY c.name ASC"
            )
    rows = cursor.fetchall()
    if not rows:
        return "There are no expenses yet\n"
    
    message = ""
    category_message = ""
    name = ""
    total = 0
    category_total = 0
    
    for row in rows:
        created = row[1]
        if not row[1] : created = "Monthly"
        total += row[2]
        category_total += row[2]
        category_message += f"\n> {created} : {row[2]}"
        if row[0] != name:
            message += f"\n\n{row[0].capitalize()}"  
            category_max = row[3]
            message += f"{category_message}\nCategory Total: {category_total}"
            if category_max:
                message += f" (Monthly limit: {category_max})"
            category_total = 0
            category_message = ""
            name = row[0]
    return message + f"\n\nMonth Total/Budget: {total}/{budget} ({total-budget})"

def _parse_input(raw_message: str) -> List[Message]:
    """ Parse text and return a message object containing category name and ammount """
    messages = []
    created = _get_now_formatted()

    for raw in raw_message.split('\n'):
        regexp_result = re.match(r"(.*) (-?[\d]+)( M)?", raw, re.IGNORECASE)
        if not regexp_result or not regexp_result.group(0) \
                or not regexp_result.group(1) or not regexp_result.group(2):
            raise exceptions.NotCorrectMessageException(
                    f"Could not understand {raw}. Please answer in format:\n"
                    "Category Ammount\n"
                    "For example: Transport -1000\n"
                    )
        category_name = regexp_result.group(1).strip().lower()
        ammount = regexp_result.group(2)
        if regexp_result.group(3):
            created = "Monthly"
        messages.append(Message(
            category_name = category_name,
            ammount = ammount,
            created = created))
    return messages

def _get_now_formatted()  -> str:
    """ Return today's date and time as a string """
    return _get_now_datetime().strftime("%Y-%m-%d %H:%M:%S")

def _get_now_datetime() -> datetime.datetime:
    """ return current datetime in enviroment's timezone """
    tz = pytz.timezone(os.getenv("TZ"))
    now = datetime.datetime.now(tz)
    return now
