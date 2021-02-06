"""Работа с категориями"""
from typing import Dict, List, NamedTuple, Optional

import exceptions
import db
import re

class Category(NamedTuple):
    """Структура категории"""
    id: int
    name: str
    max_ammount: Optional[int]

class Message(NamedTuple):
    """ Message structure """
    category_name: str
    max_ammount: Optional[int]

class Categories:
    def __init__(self):
        self._categories = self._load_categories()

    def _load_categories(self) -> List[Category]:
        """Returns all existing categories stored in db"""
        categories = db.fetchall(
                "categories", ["id","name", "max_ammount"]
        )
        return self._fill_fields(categories)

    def add_category(self, raw_message: str) -> Category:
        """Создает категорию по названию """
        message = self._parse_message(raw_message) 
        db.insert("categories", {
            "name" : message.category_name,
            "max_ammount" : message.max_ammount }
            )
        return self.get_category(message.category_name)

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
                name = category['name'],
                max_ammount = category['max_ammount']
                ))
        return categories_result

    def get_all_categories(self) -> List[Category]:
        """Возращает все существующие категории"""
        return self._categories

    def get_category(self, category_name: str) -> Category:
        """ Возращает категорию по имени """

        for cat in self._load_categories():
            if cat.name == category_name:
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



