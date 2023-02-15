import time
import json
import datetime

import vk_api
import sqlite3

from cfg import TOKEN, DEV, STAFF
from forms import add_form, get_form
from vk_api.bot_longpoll import VkBotLongPoll, VkBotEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor

vk_session = vk_api.VkApi(token=TOKEN)
lp = VkBotLongPoll(vk_session, 218860473)
vk = vk_session.get_api()


def sender(for_user_id, message_text):
    vk_session.method("messages.send", {
        "user_id": for_user_id,
        "message": message_text,
        "random_id": 0
    })


def chat_sender(for_user_id, message_text):
    vk_session.method("messages.send", {
        "user_id": for_user_id,
        "message": message_text,
        "random_id": 0
    })


def get_level(for_user_id):
    try:
        db = sqlite3.connect('admins.db'); c = db.cursor()
        level = c.execute(f"SELECT lvl FROM admins WHERE vk_id = {for_user_id}").fetchone()[0]
        db.commit(); db.close()
        return int(level)
    except:
        return 0


def send_start_keyboard(for_user_id):
    keyboard = VkKeyboard()
    keyboard.add_button("Принять форму", VkKeyboardColor.POSITIVE)
    keyboard.add_button("Помощь по боту", VkKeyboardColor.PRIMARY)
    keyboard.add_line()
    keyboard.add_button("Бот с информацией", VkKeyboardColor.SECONDARY)

    button = {
        "action": {
            "type": "open_link",
            "link": "https://vk.com/red.table",
            "label": "ПЕРЕЙТИ НАХУЙ"
        },
        "color": "secondary"
    }
    keyboard.add_button(json.dumps(button), VkKeyboardColor.SECONDARY)

    vk_session.method("messages.send", {
        "user_id": for_user_id,
        "message": "Ознакомьтесь с руководством по использованию:",
        "random_id": 0,
        "keyboard": keyboard.get_empty_keyboard()
    }); time.sleep(0.25)
    vk_session.method("messages.send", {
        "user_id": for_user_id,
        "message": str(open("help.txt", "r", encoding="utf-8").readline()),
        "random_id": 0,
        "keyboard": keyboard.get_keyboard()
    })


while True:
    try:
        for event in lp.listen():
            if event.type == VkBotEventType.MESSAGE_NEW and not event.from_chat:
                text = event.object.message['text']
                user_id = event.object.message['from_id']
                message_id = event.object.message['conversation_message_id']
                lvl = get_level(user_id)

                if text == "Начать" or text == "start" and lvl > 0:
                    send_start_keyboard(user_id)

                elif "Помощь" in text or "help" in text and lvl > 0:
                    sender(user_id, str(open("help.txt", "r", encoding="utf-8").readline()))

                elif "Бот с информацией" in text and lvl > 0:
                    sender(user_id, "ЛЕЖАТЬ + СОСАТЬ")

                elif text == "Принять форму" and lvl > 0:
                    form_array = get_form(lvl)
                    form = form_array[1]; fid = form_array[2]

                    i_keyboard = VkKeyboard(inline=True)
                    i_keyboard.add_callback_button("ㅤВыполненоㅤ", VkKeyboardColor.POSITIVE, {"type": f"accept-{form}"})
                    i_keyboard.add_callback_button("ㅤㅤНет в БДㅤㅤ", VkKeyboardColor.NEGATIVE, {"type": f"deny-{form}-{fid}"})

                    if str(form) != "0":
                        vk_session.method("messages.send", {
                            "user_id": user_id,
                            "message": form,
                            "random_id": 0,
                            "keyboard": i_keyboard.get_keyboard()
                        })
                    else:
                        sender(user_id, "Нет подходящих форм!")

                elif text[0] == "/" and lvl > 0:
                    date = int(str(datetime.datetime.now().timestamp()).split('.')[0])
                    if add_form(text, date, user_id) == 1:
                        query_json = json.dumps({
                            "peer_id": user_id,
                            "conversation_message_ids": [message_id],
                            "is_reply": True
                        })
                        vk_session.method("messages.send", {
                            "user_id": user_id,
                            "message": f"✅ Форма успешно добавлена",
                            "conversation_message_id": event.obj.conversation_message_id,
                            "forward": [query_json],
                            "random_id": 0
                        })
                    else:
                        sender(user_id, "Ошибка добавления формы!")

            elif event.type == VkBotEventType.MESSAGE_EVENT:
                if "deny" in event.object.payload.get('type'):

                    call_back_text = event.object.payload.get('type').split("-")
                    form_user_id = int(call_back_text[2])

                    msg = f"⚠️ Внимание ⚠️\nНика по вашей форме нет в БД:\n{call_back_text[1]}"
                    sender(form_user_id, msg)

                    call_message_text = call_back_text[1]
                    e_txt = "ㅤㅤㅤㅤㅤㅤ❌ㅤㅤㅤㅤㅤㅤ"

                    e_keyboard = VkKeyboard(inline=True)
                    e_keyboard.add_callback_button(e_txt, VkKeyboardColor.NEGATIVE, {"type": "empty_callback"})

                    vk_session.method("messages.edit", {
                        "peer_id": event.obj.peer_id,
                        "message": call_message_text,
                        "conversation_message_id": event.obj.conversation_message_id,
                        "keyboard": e_keyboard.get_keyboard()
                    })

                elif "accept" in event.object.payload.get('type'):

                    call_message_text = event.object.payload.get('type').split("-")[1]
                    e_txt = "ㅤㅤㅤㅤㅤㅤ✅ㅤㅤㅤㅤㅤㅤ"

                    e_keyboard = VkKeyboard(inline=True)
                    e_keyboard.add_callback_button(e_txt, VkKeyboardColor.POSITIVE, {"type": "empty_callback"})

                    vk_session.method("messages.edit", {
                        "peer_id": event.obj.peer_id,
                        "message": call_message_text,
                        "conversation_message_id": event.obj.conversation_message_id,
                        "keyboard": e_keyboard.get_keyboard()
                    })

    except Exception as error:
        print(error)
