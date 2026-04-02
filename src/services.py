import logging
import os
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Any, Dict, List

import requests
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


load_dotenv()

ALPHA_VANTAGE_API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")
CBR_API_URL = os.getenv("CBR_API_URL")


def get_currency_rates() -> List[Dict]:
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


def get_stock_prices(stock_symbols: List[str]) -> List[Dict]:
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


def investment_bank(month: str, transactions: List[Dict[str, Any]], limit: int) -> float:
    """
    Функция «Инвесткопилка» возвращает сумму, которую удалось бы отложить
    """
    if limit not in [10, 50, 100]:
        raise ValueError("Порог округления должен быть 10, 50 или 100 ₽")
    filtered_transactions = [
        t for t in transactions if datetime.strptime(t["Дата операции"], "%Y-%m-%d").strftime("%Y-%m") == month
    ]
    saved_amount = 0.0
    for transaction in filtered_transactions:
        original_amount = float(transaction["Сумма операции"])
        rounded_amount = ((original_amount + limit - 1) // limit) * limit
        saved_amount += rounded_amount - original_amount
    logger.info(f"Для месяца {month} отложено в Инвесткопилку: {saved_amount:.2f} ₽")
    return saved_amount
