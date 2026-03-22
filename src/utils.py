import pandas as pd
from typing import Any, Hashable, Optional, List, Dict


def read_transactions_from_excel(file_path: str) -> Optional[List[Dict[Hashable, Any]]]:
    """
    Читает данные из Excel-файла и возвращает список словарей с транзакциями.

    :param file_path: Путь к Excel-файлу
    :return: Список словарей с транзакциями или None в случае ошибки
    """
    try:
        # Читаем Excel-файл с помощью pandas
        df = pd.read_excel(file_path)

        # Преобразуем DataFrame в список словарей
        transactions = df.to_dict(orient='records')

        return transactions

    except FileNotFoundError:
        print(f"Файл {file_path} не найден.")
        return None

    except pd.errors.EmptyDataError:
        print(f"В файле {file_path} нет данных.")
        return None

    except pd.errors.ParserError:
        print(f"Ошибка при разборе файла {file_path}. Возможно, неверный формат.")
        return None

    except Exception as ex:
        print(f"Общая ошибка: {ex}")
        return None