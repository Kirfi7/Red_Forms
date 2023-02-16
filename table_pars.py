import time

import gspread
import sqlite3

from oauth2client.service_account import ServiceAccountCredentials

SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets",
         "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]

creds = ServiceAccountCredentials.from_json_keyfile_name("creds.json", SCOPE)
client = gspread.authorize(creds)
sheet = client.open("ADMINS RED1").sheet1

while True:
    db = sqlite3.connect('admins.db')
    c = db.cursor()
    c.execute("DELETE FROM admins")
    db.commit()
    db.close()

    # столбец перебора строк (id администраторов)
    row = sheet.col_values(7)
    for i in range(len(row)):
        try:
            integer = int(row[i])
            values = sheet.row_values(i + 1)
            array = list(values)
            db = sqlite3.connect('admins.db')
            c = db.cursor()
            c.execute(f"INSERT INTO admins VALUES ('{array[1]}', '{int(array[12])}', '{integer}')")
            db.commit()
            db.close()

        except ValueError:
            pass

    # спокойной ночи, змейка
    time.sleep(10_000)
