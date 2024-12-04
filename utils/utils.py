"""
utils.py
Модуль вспомогательных функций для обработки данных в приложении.
"""

from decimal import Decimal


def convert_decimals(obj):
    """
    Рекурсивно преобразует все объекты типа Decimal в структуре данных (список, словарь, или одиночный объект) в float.

    :param obj: Структура данных, которая может содержать объекты типа Decimal.
    :return: Та же структура данных, но с объектами Decimal, преобразованными в float.
    """
    if isinstance(obj, list):
        # Если объект - список, применяем функцию к каждому элементу списка
        return [convert_decimals(i) for i in obj]
    elif isinstance(obj, dict):
        # Если объект - словарь, применяем функцию к каждому значению словаря
        return {k: convert_decimals(v) for k, v in obj.items()}
    elif isinstance(obj, Decimal):
        # Преобразуем объект Decimal в float
        return float(obj)
    else:
        # Если объект не Decimal, список или словарь, возвращаем его без изменений
        return obj
