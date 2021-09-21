import os
import gspread
from loguru import logger

from data.config import google_table_url

gc = gspread.service_account(filename=os.path.abspath('utils/google_sheets/key.json'))

sh = gc.open_by_url(google_table_url)

def update(letter, text, num_list: int):
    sh.get_worksheet(num_list).update(letter, text)

def get_column(id_column: int):
    """Важно: Столбцы идут с 1, а не с нуля"""
    column = sh.get_worksheet(0).col_values(id_column)
    column.pop(0)  # Удаляем результат от первой ячейки (т.к. там условно название столбца)
    logger.info(column)
    return column

def insert_rows(text: list):
    sh.get_worksheet(0).insert_rows(values=text, row=2)

