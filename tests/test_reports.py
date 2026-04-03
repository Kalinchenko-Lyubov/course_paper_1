from unittest.mock import mock_open, patch

import pandas as pd
import pytest
from freezegun import freeze_time

from src.reports import spending_by_category


def test_spending_by_category_products():
    transactions = pd.DataFrame(
        [
            {"Дата операции": "2023-05-01", "Категория": "Продукты", "Сумма операции": "1234.56"},
            {"Дата операции": "2023-05-15", "Категория": "Транспорт", "Сумма операции": "-500.00"},
            {"Дата операции": "2023-06-01", "Категория": "Продукты", "Сумма операции": "789.00"},
            {"Дата операции": "2023-06-15", "Категория": "Развлечения", "Сумма операции": "-200.00"},
        ]
    )

    with freeze_time("2023-06-15"):
        report = spending_by_category(transactions, "Продукты")
    report_df = pd.DataFrame(report)

    assert len(report_df) == 2
    assert report_df["Сумма операции"].sum() == pytest.approx(2023.56)


def test_spending_by_category_transport():
    transactions = pd.DataFrame(
        [
            {"Дата операции": "2023-05-01", "Категория": "Продукты", "Сумма операции": "1234.56"},
            {"Дата операции": "2023-05-15", "Категория": "Транспорт", "Сумма операции": "-500.00"},
            {"Дата операции": "2023-06-01", "Категория": "Продукты", "Сумма операции": "789.00"},
            {"Дата операции": "2023-06-15", "Категория": "Развлечения", "Сумма операции": "-200.00"},
        ]
    )
    with freeze_time("2023-06-15"):
        report = spending_by_category(transactions, "Транспорт")
    report_df = pd.DataFrame(report)
    assert len(report_df) == 1
    assert report_df["Сумма операции"].sum() == pytest.approx(-500.0)


@patch("builtins.open", new_callable=mock_open)
def test_spending_by_category_save_report(mock_file):
    transactions = pd.DataFrame(
        [
            {"Дата операции": "2023-05-01", "Категория": "Продукты", "Сумма операции": "1234.56"},
            {"Дата операции": "2023-05-15", "Категория": "Транспорт", "Сумма операции": "-500.00"},
            {"Дата операции": "2023-06-01", "Категория": "Продукты", "Сумма операции": "789.00"},
            {"Дата операции": "2023-06-15", "Категория": "Развлечения", "Сумма операции": "-200.00"},
        ]
    )
    with freeze_time("2023-06-15"):
        spending_by_category(transactions, "Продукты")
    mock_file.assert_called_once()
