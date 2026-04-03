import json
import logging
from typing import Dict, List

from src.utils import (
    calculate_card_statistics,
    filter_transactions_by_date,
    get_currency_rates,
    get_greeting,
    get_stock_prices,
    get_top_transactions,
    load_user_settings,
    read_transactions_from_excel,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def main_page(transactions: List[Dict], input_date: str) -> Dict:
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


if __name__ == "__main__":

    transactions = read_transactions_from_excel("data/operations.xlsx")

    input_date = "2020-05-20 12:00:00"
    json_response = main_page(transactions, input_date)

    print(json.dumps(json_response, indent=2, ensure_ascii=False))
