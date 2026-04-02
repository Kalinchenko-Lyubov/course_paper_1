from datetime import datetime

import pytest
from freezegun import freeze_time

from src.utils import read_transactions_from_excel
from src.views import (calculate_card_statistics, filter_transactions_by_date, generate_json_response, get_greeting,
                       get_top_transactions)


@pytest.mark.parametrize(
    "current_hour,expected_greeting",
    [(5, "Доброй ночи"), (10, "Доброе утро"), (15, "Добрый день"), (20, "Добрый вечер")],
)
def test_get_greeting(current_hour, expected_greeting):
    with freeze_time(f"2023-10-01 {current_hour:02}:00"):
        greeting = get_greeting()
        assert greeting == expected_greeting


def test_filter_transactions_by_date():
    transactions = read_transactions_from_excel("data/operations.xlsx")
    input_date = "2020-05-20 12:00:00"
    filtered_transactions = filter_transactions_by_date(transactions, input_date)

    assert len(filtered_transactions) > 0
    assert all(
        datetime.strptime(transaction["Дата операции"].split()[0], "%d.%m.%Y") >= datetime(2020, 5, 1)
        for transaction in filtered_transactions
    )


def test_calculate_card_statistics():
    transactions = read_transactions_from_excel("data/operations.xlsx")
    input_date = "2020-05-20 12:00:00"
    filtered_transactions = filter_transactions_by_date(transactions, input_date)
    statistics = calculate_card_statistics(filtered_transactions)

    assert len(statistics) > 0
    assert all("last_digits" in stat and "total_spent" in stat and "cashback" in stat for stat in statistics)


def test_calculate_card_statistics_empty_list():
    transactions = []
    input_date = "2020-05-20 12:00:00"
    filtered_transactions = filter_transactions_by_date(transactions, input_date)
    statistics = calculate_card_statistics(filtered_transactions)
    assert statistics == []


def test_get_top_transactions():
    transactions = read_transactions_from_excel("data/operations.xlsx")
    input_date = "2020-05-20 12:00:00"
    filtered_transactions = filter_transactions_by_date(transactions, input_date)
    top_transactions = get_top_transactions(filtered_transactions)

    assert len(top_transactions) == 5
    assert all("Сумма операции" in transaction for transaction in top_transactions)


def test_get_top_transactions_empty_list():
    transactions = []
    input_date = "2020-05-20 12:00:00"
    filtered_transactions = filter_transactions_by_date(transactions, input_date)
    top_transactions = get_top_transactions(filtered_transactions)
    assert top_transactions == [], "Должен вернуть пустой список"


def test_generate_json_response():
    transactions = read_transactions_from_excel("data/operations.xlsx")
    input_date = "2020-05-20 12:00:00"
    json_response = generate_json_response(transactions, input_date)

    assert "greeting" in json_response
    assert "cards" in json_response
    assert "top_transactions" in json_response
    assert "currency_rates" in json_response
    assert "stock_prices" in json_response
