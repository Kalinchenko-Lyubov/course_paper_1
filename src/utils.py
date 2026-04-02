import json
import logging
from pathlib import Path
from typing import Dict, List

import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def read_transactions_from_excel(file_path: str) -> List[Dict]:
    """
    Читает данные из Excel-файла и возвращает список словарей с транзакциями.
    """
    # Определяем путь относительно корня проекта
    project_root = Path(__file__).resolve().parents[1]  # Поднимаемся на 2 уровня вверх
    full_path = project_root / file_path

    logger.info(f"Попытка прочитать файл: {full_path}")
    try:
        df = pd.read_excel(full_path)
        transactions = df.to_dict(orient="records")
        return transactions
    except FileNotFoundError:
        logger.error(f"Файл {full_path} не найден.")
        return []


def load_user_settings() -> Dict:
    """
    Загружает пользовательские настройки из файла user_settings.json.
    """
    settings_path = Path(__file__).parent.parent / "user_settings.json"

    with open(settings_path, "r") as file:
        settings = json.load(file)

    return settings
