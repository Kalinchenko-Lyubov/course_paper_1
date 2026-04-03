from src.utils import read_transactions_from_excel
from src.views import main_page


def test_main_page():
    transactions = read_transactions_from_excel("data/operations.xlsx")
    input_date = "2020-05-20 12:00:00"
    json_response = main_page(transactions, input_date)

    assert "greeting" in json_response
    assert "cards" in json_response
    assert "top_transactions" in json_response
    assert "currency_rates" in json_response
    assert "stock_prices" in json_response
