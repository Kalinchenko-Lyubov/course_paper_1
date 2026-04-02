import logging
from collections import defaultdict
from datetime import datetime
from typing import Dict, List

from src.services import get_currency_rates, get_stock_prices
from src.utils import load_user_settings

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


def get_top_transactions(filtered_transactions: List[Dict], top_n: int = 5) -> List[Dict]:
    """
    Возвращает топ-N транзакций по сумме платежа.
    """
    return sorted(filtered_transactions, key=lambda t: abs(float(t["Сумма операции"])), reverse=True)[:top_n]


def generate_json_response(transactions: List[Dict], input_date: str) -> Dict:
    """
    Формирует JSON-ответ на основе входящей даты.
    """
    logger.info(f"Принята дата: {input_date}")

    filtered_transactions = filter_transactions_by_date(transactions, input_date)
    logger.info(f"Отфильтровано транзакций: {len(filtered_transactions)}")

    greeting = get_greeting()
    logger.info(f"Приветствие: {greeting}")

    card_statistics = calculate_card_statistics(filtered_transactions)
    logger.info(f"Рассчитана статистика по картам: {card_statistics}")

    top_transactions = get_top_transactions(filtered_transactions)
    logger.info(f"Топ-5 транзакций: {top_transactions}")

    currency_rates = get_currency_rates()
    logger.info(f"Курсы валют: {currency_rates}")

    user_settings = load_user_settings()
    stock_symbols = user_settings.get("user_stocks", [])
    stock_prices = get_stock_prices(stock_symbols)
    logger.info(f"Котировки акций: {stock_prices}")

    response = {
        "greeting": greeting,
        "cards": card_statistics,
        "top_transactions": top_transactions,
        "currency_rates": currency_rates,
        "stock_prices": stock_prices,
    }

    logger.info("JSON-ответ сформирован.")

    return response


# if __name__ == "__main__":
#     from utils import load_user_settings, read_transactions_from_excel
#
#     transactions = read_transactions_from_excel("../data/operations.xlsx")
#
#     input_date = "2020-05-20 12:00:00"
#     json_response = generate_json_response(transactions, input_date)
#
#     print(json.dumps(json_response, indent=2, ensure_ascii=False))
