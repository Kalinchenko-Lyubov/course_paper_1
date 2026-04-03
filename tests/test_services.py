import pytest

from src.services import investment_bank


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
