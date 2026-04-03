import logging
from datetime import datetime
from typing import Any, Dict, List

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


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
