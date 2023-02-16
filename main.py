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
        db = sqlite3.connect('admins.db')
        c = db.cursor()
        level = c.execute(f"SELECT lvl FROM admins WHERE vk_id = {for_user_id}").fetchone()[0]
        db.commit()
        db.close()
        return int(level)
    except:
        return 0


def send_start_keyboard(for_user_id):
    keyboard = VkKeyboard(
        one_time=False,
        inline=False
    )
    keyboard.add_button(
        label="Принять форму",
        color=VkKeyboardColor.POSITIVE
    )
    keyboard.add_button(
        label="Помощь по боту",
        color=VkKeyboardColor.PRIMARY
    )

    vk_session.method("messages.send", {
        "user_id": for_user_id,
        "message": "Ознакомьтесь с руководством по использованию:",
        "random_id": 0,
        "keyboard": keyboard.get_empty_keyboard()
    })

    vk_session.method("messages.send", {
        "user_id": for_user_id,
        "message": open("help.txt", "r", encoding="utf-8").readline(),
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

                elif text == "Принять форму" and lvl > 0:
                    form_array = get_form(lvl)
                    form_text = form_array[1]
                    form_user_id = form_array[2]

                    i_keyboard = VkKeyboard(inline=True)
                    i_keyboard.add_callback_button(
                        label="ㅤВыполненоㅤ",
                        color=VkKeyboardColor.POSITIVE,
                        payload={
                            # форматирую call-back строчку
                            "type": f"accept-{form_text}"
                        }
                    )
                    i_keyboard.add_callback_button(
                        label="ㅤㅤНет в БДㅤㅤ",
                        color=VkKeyboardColor.NEGATIVE,
                        payload={
                            # форматирую call-back строчку
                            "type": f"deny-{form_text}-{form_user_id}"
                        }
                    )

                    # 0 возвращается в случае ошибки (строка 94)
                    if str(form_text) != "0":
                        vk_session.method("messages.send", {
                            "user_id": user_id,
                            "message": form_text,
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

                    e_keyboard = VkKeyboard(inline=True)
                    e_keyboard.add_callback_button("ㅤㅤㅤㅤㅤㅤ❌ㅤㅤㅤㅤㅤㅤ", VkKeyboardColor.NEGATIVE, {
                        "type": "empty_callback"
                    })

                    vk_session.method("messages.edit", {
                        "peer_id": event.obj.peer_id,
                        "message": call_message_text,
                        "conversation_message_id": event.obj.conversation_message_id,
                        "keyboard": e_keyboard.get_keyboard()
                    })

                elif "accept" in event.object.payload.get('type'):

                    call_message_text = event.object.payload.get('type').split("-")[1]

                    e_keyboard = VkKeyboard(inline=True)
                    e_keyboard.add_callback_button("ㅤㅤㅤㅤㅤㅤ✅ㅤㅤㅤㅤㅤㅤ", VkKeyboardColor.POSITIVE, {
                        "type": "empty_callback"
                    })

                    vk_session.method("messages.edit", {
                        "peer_id": event.obj.peer_id,
                        "message": call_message_text,
                        "conversation_message_id": event.obj.conversation_message_id,
                        "keyboard": e_keyboard.get_keyboard()
                    })

    except Exception as error:
        print(error)
