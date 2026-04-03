from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest
from freezegun import freeze_time

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


@pytest.mark.parametrize(
    "current_hour,expected_greeting",
    [(5, "Доброй ночи"), (10, "Доброе утро"), (15, "Добрый день"), (20, "Добрый вечер")],
)
def test_get_greeting(current_hour, expected_greeting):
    with freeze_time(f"2023-10-01 {current_hour:02}:00"):
        greeting = get_greeting()
        assert greeting == expected_greeting


def test_get_currency_rates():
    rates = get_currency_rates()

    assert len(rates) == 2  # Проверка наличия двух валют
    assert "USD" in [rate["currency"] for rate in rates]  # Проверка наличия USD
    assert "EUR" in [rate["currency"] for rate in rates]  # Проверка наличия EUR


@patch("src.utils.requests.get")
def test_get_currency_rates_bad_status(mock_requests_get):
    mock_response = MagicMock(status_code=404, text="Not Found")
    mock_requests_get.return_value = mock_response
    rates = get_currency_rates()
    assert rates == []


def test_read_transactions_from_excel():
    excel_file_path = "data/operations.xlsx"
    transactions = read_transactions_from_excel(excel_file_path)
    assert len(transactions) > 0
    assert isinstance(transactions, list)


def test_load_user_settings():
    settings = load_user_settings()
    assert "user_currencies" in settings
    assert "user_stocks" in settings


@patch("src.utils.requests.get")
def test_get_stock_prices(mock_requests_get):
    mock_response_data = {
        "Global Quote": {
            "01. symbol": "AAPL",
            "05. price": "247.99",
        }
    }

    mock_responses = [
        mock_response_data.copy(),  # AAPL
        mock_response_data.copy(),  # AMZN
        mock_response_data.copy(),  # GOOGL
        mock_response_data.copy(),  # MSFT
        mock_response_data.copy(),  # TSLA
    ]

    def side_effect(url):
        symbol = url.split("symbol=")[1].split("&")[0]
        index = ["AAPL", "AMZN", "GOOGL", "MSFT", "TSLA"].index(symbol)
        response_mock = MagicMock()
        response_mock.status_code = 200
        response_mock.json.return_value = mock_responses[index]
        return response_mock

    mock_requests_get.side_effect = side_effect

    stock_symbols = ["AAPL", "AMZN", "GOOGL", "MSFT", "TSLA"]
    prices = get_stock_prices(stock_symbols)

    assert len(prices) == len(stock_symbols)
    assert prices == [
        {"stock": "AAPL", "price": 247.99},
        {"stock": "AMZN", "price": 247.99},
        {"stock": "GOOGL", "price": 247.99},
        {"stock": "MSFT", "price": 247.99},
        {"stock": "TSLA", "price": 247.99},
    ]


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
