from unittest.mock import MagicMock, patch

import pytest

from src.services import get_currency_rates, get_stock_prices, investment_bank


def test_get_currency_rates():
    rates = get_currency_rates()

    assert len(rates) == 2  # Проверка наличия двух валют
    assert "USD" in [rate["currency"] for rate in rates]  # Проверка наличия USD
    assert "EUR" in [rate["currency"] for rate in rates]  # Проверка наличия EUR


@patch("src.services.requests.get")
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


@patch("src.services.requests.get")
def test_get_currency_rates_bad_status(mock_requests_get):
    mock_response = MagicMock(status_code=404, text="Not Found")
    mock_requests_get.return_value = mock_response
    rates = get_currency_rates()
    assert rates == []


def test_investment_bank_limit_100():
    transactions = [
        {"Дата операции": "2023-05-01", "Сумма операции": "1712"},
        {"Дата операции": "2023-05-15", "Сумма операции": "2345"},
    ]
    saved_amount = investment_bank("2023-05", transactions, 100)
    assert saved_amount == pytest.approx(143.0)


def test_investment_bank_invalid_limit():
    transactions = [
        {"Дата операции": "2023-05-01", "Сумма операции": "1712"},
        {"Дата операции": "2023-05-15", "Сумма операции": "2345"},
    ]
    with pytest.raises(ValueError, match="Порог округления должен быть 10, 50 или 100 ₽"):
        investment_bank("2023-05", transactions, 25)


def test_investment_bank_no_transactions():
    saved_amount = investment_bank("2023-05", [], 50)
    assert saved_amount == 0.0


def test_investment_bank_outside_month():
    transactions = [
        {"Дата операции": "2023-04-01", "Сумма операции": "1712"},
        {"Дата операции": "2023-06-15", "Сумма операции": "2345"},
    ]
    saved_amount = investment_bank("2023-05", transactions, 50)
    assert saved_amount == 0.0
