import json
import logging
import os
import xml.etree.ElementTree as ET
from collections import defaultdict
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd
import requests
from dotenv import load_dotenv

load_dotenv()

ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")
CBR_API_URL = os.getenv("CBR_API_URL")


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def get_greeting() -> str:
    """
    Возвращает приветствие в зависимости от текущего времени.
    """
    hour = datetime.now().hour
    if 6 <= hour < 12:
        return "Доброе утро"
    elif 12 <= hour < 18:
        return "Добрый день"
    elif 18 <= hour < 24:
        return "Добрый вечер"
    else:
        return "Доброй ночи"


def get_currency_rates() -> list[Any] | str:
    """
    Получает актуальные курсы валют (USD, EUR) от Центрального Банка России.
    """
    response = requests.get(CBR_API_URL)

    logger.info(f"Статус ответа от API Центробанка: {response.status_code}")

    if response.status_code != 200:
        logger.error(f"Ошибка при получении данных от API Центробанка: {response.text}")
        return []

    try:
        root = ET.fromstring(response.content)

        usd_rate = next(
            (float(val.text.replace(",", ".")) for val in root.findall(".//Valute[@ID='R01235']/Value")), None
        )

        eur_rate = next(
            (float(val.text.replace(",", ".")) for val in root.findall(".//Valute[@ID='R01239']/Value")), None
        )

        return [{"currency": "USD", "rate": usd_rate}, {"currency": "EUR", "rate": eur_rate}]

    except ET.ParseError as e:
        logger.error(f"Ошибка разбора XML: {e}")
        logger.debug(f"Полный ответ от API: {response.text}")
        return []

    except Exception as e:
        logger.error(f"Неожиданная ошибка: {e}")
        return []


def get_stock_prices(stock_symbols: List[str]) -> list[dict[str, str | float]]:
    """
    Получает текущие котировки акций через Alpha Vantage API.
    """
    stock_prices = []

    for symbol in stock_symbols:
        url = f"https://www.alphavantage.co/query?function=GLOBAL_QUOTE&symbol={symbol}&apikey={ALPHA_VANTAGE_API_KEY}"
        response = requests.get(url)
        data = response.json()

        if "Global Quote" in data:
            quote = data["Global Quote"]
            price = float(quote["05. price"])

            stock_prices.append({"stock": symbol, "price": price})
        else:
            logger.warning(f"Акция {symbol} не найдена или API вернуло ошибку.")

    return stock_prices


def calculate_card_statistics(filtered_transactions: List[Dict]) -> List[Dict]:
    """
    Рассчитывает статистику по картам: сумма расходов и кэшбэк.
    """
    card_stats = defaultdict(lambda: {"total_spent": 0, "cashback": 0})

    for transaction in filtered_transactions:
        card_number = str(transaction["Номер карты"]).strip()
        card_last_digits = card_number.split("*")[-1] if "*" in card_number else card_number[-4:]

        amount = abs(float(transaction["Сумма операции"]))

        card_stats[card_last_digits]["total_spent"] += amount
        card_stats[card_last_digits]["cashback"] += amount / 100  # 1% кэшбэк

    return [
        {"last_digits": card, "total_spent": round(stats["total_spent"], 2), "cashback": round(stats["cashback"], 2)}
        for card, stats in card_stats.items()
    ]


def filter_transactions_by_date(transactions: List[Dict], input_date: str) -> List[Dict]:
    """
    Фильтрует транзакции по дате
    """
    target_date = datetime.strptime(input_date, "%Y-%m-%d %H:%M:%S")
    start_date = target_date.replace(day=1, hour=0, minute=0, second=0)
    end_date = target_date

    def parse_transaction_date(date_str: str) -> datetime:
        return datetime.strptime(date_str.split()[0], "%d.%m.%Y")

    filtered_transactions = [
        transaction
        for transaction in transactions
        if start_date <= parse_transaction_date(transaction["Дата операции"]) <= end_date
    ]

    return filtered_transactions


def get_top_transactions(filtered_transactions: List[Dict], top_n: int = 5) -> List[Dict]:
    """
    Возвращает топ-N транзакций по сумме платежа.
    """
    return sorted(filtered_transactions, key=lambda t: abs(float(t["Сумма операции"])), reverse=True)[:top_n]


def read_transactions_from_excel(file_path: str) -> List[Dict]:
    """
    Читает данные из Excel-файла и возвращает список словарей с транзакциями.
    """
    project_root = Path(__file__).resolve().parents[1]
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
