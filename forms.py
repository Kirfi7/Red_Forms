import time
import gspread

from oauth2client.service_account import ServiceAccountCredentials
from cfg import SCOPE, COMMANDS

creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", SCOPE)
client = gspread.authorize(creds)
sheet = client.open("ADMINS RED1").worksheet("Админ-формы")


def add_form(form_text, user_id):
    now_time = time.strftime("%H:%M:%S %d.%m.%Y", time.localtime())
    command = form_text.split()[0][1:]

    sheet.append_row([form_text, COMMANDS[command]['lvl'], user_id, "В ожидании", now_time])
    sheet.add_rows(1)


def get_form(level: float):
    for cell in sheet.findall("В ожидании", in_column=4):
        row = cell.row
        if int(sheet.cell(row, 2).value) <= level:
            return sheet.cell(row, 1).value, row, sheet.cell(row, 3).value

    return "Error", "Error", "Error"


def form_accepted(row_number):
    sheet.update_cell(row_number, 4, "Принята")


def form_ranked_up(row_number, level):
    sheet.update_cell(row_number, 2, level + 1)


def form_denied(row_number):
    sheet.update_cell(row_number, 4, "Нет в базе")

