import time

import vk_api
import sqlite3

from cfg import TOKEN, DEV, STAFF
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor

vk_session = vk_api.VkApi(token=TOKEN)
lp = VkLongPoll(vk_session)
vk = vk_session.get_api()


def sender(for_user_id, message_text):
    vk_session.method("messages.send", {
        "user_id": for_user_id,
        "message": message_text,
        "random_id": 0
    })


def get_level(for_user_id):
    try:
        db = sqlite3.connect('admins.db'); c = db.cursor()
        level = c.execute(f"SELECT lvl FROM admin WHERE id = '{for_user_id}'")
        db.commit(); db.close()
        return int(level.fetchone()[0])
    except: return 0


def send_default_keyboard(for_user_id):
    keyboard = VkKeyboard()
    keyboard.add_button("Создать форму", VkKeyboardColor.POSITIVE)
    keyboard.add_button("Последняя форма", VkKeyboardColor.PRIMARY)

    vk_session.method("messages.send", {
        "user_id": for_user_id,
        "message": "Выход на главную...",
        "random_id": 0,
        "keyboard": keyboard.get_empty_keyboard()
    }); time.sleep(0.25)
    vk_session.method("messages.send", {
        "user_id": for_user_id,
        "message": "Выберите действие:",
        "random_id": 0,
        "keyboard": keyboard.get_keyboard()
    })


def send_form_keyboard(for_user_id, form):
    keyboard = VkKeyboard()
    keyboard.add_button("Принял форму", VkKeyboardColor.POSITIVE)
    keyboard.add_button("Нет в БД", VkKeyboardColor.NEGATIVE)

    vk_session.method("messages.send", {
        "user_id": for_user_id,
        "message": "Загружается последняя форма...",
        "random_id": 0,
        "keyboard": keyboard.get_empty_keyboard()
    }); time.sleep(0.25)
    vk_session.method("messages.send", {
        "user_id": for_user_id,
        "message": form,
        "random_id": 0,
        "keyboard": keyboard.get_keyboard()
    })


def get_last_form(for_lvl):
    db = sqlite3.connect("database.db"); c = db.cursor()
    last_form = c.execute(f"SELECT form FROM forms WHERE lvl <= {for_lvl}").fetchone()[0]
    db.commit(); db.close()
    return last_form


while True:
    try:
        for event in lp.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                text = event.text
                user_id = event.user_id
                lvl = get_level(user_id)

                if text == "Начать":
                    send_default_keyboard(user_id)

                elif text == "Последняя форма" and lvl > 0:
                    # send_form_keyboard(user_id, get_last_form(user_id))

                    i_keyboard = VkKeyboard(inline=True, one_time=True)
                    i_keyboard.add_button(label="Принял", color=VkKeyboardColor.POSITIVE, payload={"type": "accept"})
                    i_keyboard.add_button(label="Нет в БД", color=VkKeyboardColor.NEGATIVE, payload={"type": "deny"})

                    vk_session.method("messages.send", {
                        "user_id": user_id,
                        "message": "Haha", # get_last_form(user_id),
                        "random_id": 0,
                        "keyboard": i_keyboard.get_keyboard()
                    })

                elif text == "Создать форму" and lvl > 0:
                    pass

    except Exception as error:
        print(error)
