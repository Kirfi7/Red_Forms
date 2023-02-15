import sqlite3

from cfg import COMMANDS
from cfg import chat_sender


def add_form(text, date, vk_id):
    array = text.split()
    cmd = array[0][1:]

    dtb = sqlite3.connect('admins.db'); ct = dtb.cursor()
    nick_name = ct.execute(f"SELECT nick FROM admins WHERE vk_id = '{vk_id}'").fetchone()[0]
    nick_by = f" | by {nick_name[0]}. {nick_name.split('_')[1]}"

    if len(array) < 3 or not("_" in array[1]) or not(cmd in COMMANDS):
        return 0

    if COMMANDS[cmd]['parameters'] == 4 and len(array) >= 4:

        time = array[2]
        try:
            t = int(time)

        except ValueError:
            t = -1

        if t > 0:
            db = sqlite3.connect('forms.db'); c = db.cursor()
            c.execute(f"INSERT INTO forms VALUES ('{text + nick_by}', '{COMMANDS[cmd]['lvl']}', '{date}', '{vk_id}')")
            forms_count = len(c.execute(f"SELECT rowid FROM forms").fetchall())
            db.commit(); db.close()

            if forms_count >= 10:
                chat_sender(1, f"@all Примите формы! Накопилось уже {forms_count}!")

            return 1

        return 0

    elif COMMANDS[cmd]['parameters'] == 3 and len(array) >= 3:
        db = sqlite3.connect('forms.db'); c = db.cursor()
        c.execute(f"INSERT INTO forms VALUES ('{text + nick_by}', '{COMMANDS[cmd]['lvl']}', '{date}', '{vk_id}')")
        forms_count = len(c.execute(f"SELECT rowid FROM forms").fetchall())
        db.commit(); db.close()

        if forms_count >= 10:
            chat_sender(2, f"@all Примите формы! Накопилось уже {forms_count}!")

        return 1

    return 0


def get_form(lvl):
    db = sqlite3.connect('forms.db'); c = db.cursor()
    result = c.execute(f"SELECT rowid, form, vk_id FROM forms WHERE lvl <= '{int(lvl)}'").fetchone()

    if result is None:
        db.commit(); db.close()
        return 0, 0, 0

    c.execute(f"DELETE FROM forms WHERE rowid = '{result[0]}'")
    db.commit(); db.close()
    return result
