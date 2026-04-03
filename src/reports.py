import json
import logging
from datetime import datetime, timedelta
from functools import wraps
from typing import Any, Callable, Optional

import pandas as pd

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def save_report(filename: Optional[str] = None):
    """
    Декоратор для сохранения результата функции-отчета в файл.
    """

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            result = func(*args, **kwargs)
            if isinstance(result, pd.DataFrame):
                result = result.to_dict(orient="records")
            if filename:
                report_filename = filename
            else:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                report_filename = f"default_report_{timestamp}.json"
            with open(report_filename, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            logger.info(f"Сохранен отчет в файл: {report_filename}")
            return result

        return wrapper

    return decorator


@save_report()
def spending_by_category(transactions: pd.DataFrame, category: str, date: Optional[str] = None) -> pd.DataFrame:
    """
    Возвращает траты по заданной категории за последние три месяца
    """
    if date:
        end_date = datetime.strptime(date, "%Y-%m-%d")
    else:
        end_date = datetime.now()

    start_date = end_date - timedelta(days=90)  # 3 месяца назад

    filtered_transactions = transactions[
        (transactions["Дата операции"] >= start_date.strftime("%Y-%m-%d"))
        & (transactions["Дата операции"] <= end_date.strftime("%Y-%m-%d"))
        & (transactions["Категория"] == category)
    ].copy()

    filtered_transactions["Сумма операции"] = filtered_transactions["Сумма операции"].astype(float)

    result_df = filtered_transactions.groupby(["Дата операции", "Категория"])["Сумма операции"].sum().reset_index()
    result_df.sort_values(by=["Дата операции"], inplace=True)
    logger.info(f"Сформирован отчет по категории '{category}' за период {start_date.date()} - {end_date.date()}")
    return result_df
