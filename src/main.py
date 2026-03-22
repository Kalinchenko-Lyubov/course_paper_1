from utils import read_transactions_from_excel


def main():
    # Путь к Excel-файлу с операциями
    excel_file_path = "../data/operations.xlsx"

    # Читаем данные из Excel
    transactions = read_transactions_from_excel(excel_file_path)

    # Выводим первые 5 транзакций для проверки
    if transactions:
        print(transactions[:5])
    else:
        print("Не удалось прочитать данные из Excel-файла.")


if __name__ == "__main__":
    main()