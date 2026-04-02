from src.utils import load_user_settings, read_transactions_from_excel


def test_read_transactions_from_excel():
    excel_file_path = "data/operations.xlsx"
    transactions = read_transactions_from_excel(excel_file_path)
    assert len(transactions) > 0
    assert isinstance(transactions, list)


def test_load_user_settings():
    settings = load_user_settings()
    assert "user_currencies" in settings
    assert "user_stocks" in settings
