"""Работа с категориями"""
from typing import Dict, List, NamedTuple, Optional

import exceptions
import db
import re

class Category(NamedTuple):
    """Структура категории"""
    id: int
    user_id: int
    name: str
    max_ammount: int

class Message(NamedTuple):
    """ Message structure """
    category_name: str
    max_ammount: int

class Categories:
    def __init__(self):
        self._categories = self._load_categories()

    def _load_categories(self) -> List[Category]:
        """Returns all existing categories stored in db"""
        categories = db.fetchall(
                "categories", ["id", "user_id","name", "max_ammount"]
        )
        return self._fill_fields(categories)

    def add_category(self, user_id: int, raw_message: str) -> Category:
        """Создает категорию по названию """
        message = self._parse_message(raw_message)
        category = self.get_category(user_id, message.category_name)
        if not category: 
            db.insert("categories", {
                "name" : message.category_name,
                "user_id": user_id,
                "max_ammount" : message.max_ammount }
                )
            return self.get_category(user_id, message.category_name)
        return None

    def del_category(self, category: Category):
        """ Удаляет существующую категорию """
        category_name = {"name" : category.name}
        db.delete("categories", category_name)

    def _fill_fields(self, categories: List[Dict]) -> List[Category]:
        """Преобразует List[Dict] в List[Category] """
        categories_result = []
        for index, category in enumerate(categories):
            categories_result.append(Category(
                id = category['id'],
                user_id = category['user_id'],
                name = category['name'],
                max_ammount = category['max_ammount']
                ))
        return categories_result

    def get_all_categories(self) -> List[Category]:
        """Возращает все существующие категории"""
        return self._categories

    def get_category_list(self) -> str:
        """ Returns a string containing all available categories """
        categories = self.get_all_categories()
        if not categories:
            return "There are not categories yet"
        text = ""
        for category in categories:
            text+="\n" + category.name
            if category.max_ammount:
                text+= " (Monthly Limit: " + str(category.max_ammount) + ")"
        return text


    def get_category(self, user_id: int, category_name: str) -> Category:
        """ Возращает категорию по имени """

        for cat in self._load_categories():
            if cat.name == category_name and cat.user_id == user_id:
                return cat
        return None

    def _parse_message(self, raw_message: str) -> Message:
        regexp_result=re.match(r"(\w*) (-?[\d]+)|^(\w*)$", raw_message)
        if (not regexp_result or not regexp_result.group(0) \
                or not regexp_result.group(1) or not regexp_result.group(2)) \
                and not regexp_result.group(3):
                    raise exceptions.NotCorrectMessageException(
                            f"Could not understand {raw_message}. Please answer in fromat:\n"
                            "Category Ammoount\n"
                            "For Example: Transport -1000\n"
                            )

        if regexp_result.group(3):
            category_name = regexp_result.group(3).strip().lower()
            return Message(category_name = category_name, max_ammount = None)
        
        category_name = regexp_result.group(1).strip().lower()
        max_ammount = regexp_result.group(2)
        return Message(category_name = category_name, max_ammount = max_ammount) 



