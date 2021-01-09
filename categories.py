"""Работа с категориями"""
from typing import Dict, List, NamedTuple

import db

class Category(NamedTuple):
    """Структура категории"""
    id: int
    name: str

class Categories:
    def __init__(self):
        self._categories = self._load_categories()

    def _load_categories(self) -> List[Category]:
        """Returns all existing categories stored in db"""
        categories = db.fetchall(
                "categories", ["id","name"]
        )
        return self._fill_fields(categories)

    def add_category(self, category_name: str):
        """Создает категорию по названию """
        db.insert("categories", {"name" : f"{category_name}"})

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
                name = category['name']
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
