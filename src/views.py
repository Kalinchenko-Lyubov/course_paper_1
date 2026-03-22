import json
from datetime import datetime
from collections import defaultdict
from typing import List, Dict, Tuple


# Вспомогательные функции для работы с датами и временем
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


# Вспомогательные функции для работы с транзакциями
def filter_transactions_by_date(transactions: List[Dict], input_date: str) -> List[Dict]:
    """
    Фильтрует транзакции по дате.
    Входная дата должна быть в формате YYYY-MM-DD.
    """
    # Парсим входную дату
    target_date = datetime.strptime(input_date, "%Y-%m-%d")
    start_date = target_date.replace(day=1)  # Начало месяца
    end_date = target_date  # Входящая дата включительно

    # Преобразуем строки дат в объекты datetime для сравнения
    def parse_transaction_date(date_str: str) -> datetime:
        return datetime.strptime(date_str.split()[0], "%d.%m.%Y")

    # Фильтруем транзакции по дате операции
    filtered_transactions = [
        transaction for transaction in transactions
        if start_date <= parse_transaction_date(transaction["Дата операции"]) <= end_date
    ]

    return filtered_transactions


def calculate_card_statistics(filtered_transactions: List[Dict]) -> List[Dict]:
    """
    Рассчитывает статистику по картам: сумма расходов и кэшбэк.
    """
    card_stats = defaultdict(lambda: {"total_spent": 0, "cashback": 0})

    for transaction in filtered_transactions:
        # Приводим номер карты к строке и извлекаем последние 4 цифры
        card_number = str(transaction["Номер карты"]).strip()
        card_last_digits = card_number.split("*")[-1] if "*" in card_number else card_number[-4:]

        # Используем абсолютное значение суммы для расчета
        amount = abs(float(transaction["Сумма операции"]))

        card_stats[card_last_digits]["total_spent"] += amount
        card_stats[card_last_digits]["cashback"] += amount / 100  # 1% кэшбэк

    return [
        {
            "last_digits": card,
            "total_spent": round(stats["total_spent"], 2),
            "cashback": round(stats["cashback"], 2)
        }
        for card, stats in card_stats.items()
    ]


def get_top_transactions(filtered_transactions: List[Dict], top_n: int = 5) -> List[Dict]:
    """
    Возвращает топ-N транзакций по сумме платежа.
    """
    return sorted(filtered_transactions, key=lambda t: abs(float(t["Сумма операции"])), reverse=True)[:top_n]


# Основная функция для формирования JSON-ответа
def generate_json_response(transactions: List[Dict], input_date: str) -> Dict:
    """
    Формирует JSON-ответ на основе входящей даты.
    """
    # Фильтруем транзакции по дате
    filtered_transactions = filter_transactions_by_date(transactions, input_date)

    # Формируем приветствие
    greeting = get_greeting()

    # Рассчитываем статистику по картам
    card_statistics = calculate_card_statistics(filtered_transactions)

    # Получаем топ-5 транзакций
    top_transactions = get_top_transactions(filtered_transactions)

    # Курсы валют и стоимость акций (реализуем позже)
    currency_rates = []
    stock_prices = []

    # Формируем итоговый JSON-ответ
    response = {
        "greeting": greeting,
        "cards": card_statistics,
        "top_transactions": top_transactions,
        "currency_rates": currency_rates,
        "stock_prices": stock_prices
    }

    return response


# Пример использования
if __name__ == "__main__":
    # Загружаем транзакции из Excel-файла
    from utils import read_transactions_from_excel

    transactions = read_transactions_from_excel("../data/operations.xlsx")

    # Генерируем JSON-ответ для конкретной даты
    input_date = "2020-05-20"
    json_response = generate_json_response(transactions, input_date)

    # Выводим результат
    print(json.dumps(json_response, indent=2, ensure_ascii=False))