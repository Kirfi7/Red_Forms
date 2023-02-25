import json
import datetime

import vk_api
import sqlite3

from cfg import TOKEN, DEV, STAFF
from forms import add_form, get_form, form_count
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


def chat_sender(for_chat_id, message_text):
    vk_session.method("messages.send", {
        "chat_id": for_chat_id,
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

                if text == "Начать" and lvl > 0:
                    send_start_keyboard(user_id)

                elif text == "Помощь по боту" and lvl > 0:
                    sender(user_id, str(open("help.txt", "r", encoding="utf-8").readline()))

                elif text == "Количество форм" and lvl > 0:
                    sender(user_id, f"Количество активных форм: {form_count()}")

                elif text == "Принять форму" and lvl > 0:
                    form_array = get_form(lvl)
                    form_text = form_array[1]
                    form_user_id = form_array[2]

                    i_keyboard = VkKeyboard(inline=True)
                    i_keyboard.add_callback_button(
                        label="Выполнено",
                        color=VkKeyboardColor.POSITIVE,
                        payload={"call_back": f"accept-{form_text}"})
                    i_keyboard.add_line()
                    i_keyboard.add_callback_button(
                        label="Нет в БД",
                        color=VkKeyboardColor.NEGATIVE,
                        payload={"call_back": f"deny-{form_text}-{form_user_id}"})
                    i_keyboard.add_callback_button(
                        label="Передать форму ГА",
                        color=VkKeyboardColor.PRIMARY,
                        payload={"call_back": f"for_kirill-{form_text}-{form_user_id}"})

                    # form_text = 0 возвращается в случае ошибки
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
                if "deny" in event.object.payload.get('call_back'):
                    call_back_text = event.object.payload.get('call_back').split("-")
                    form_user_id = int(call_back_text[2])
                    call_form_text = call_back_text[1]

                    e_keyboard = VkKeyboard(inline=True)
                    e_keyboard.add_callback_button(
                        label="ㅤㅤㅤㅤㅤ❌ㅤㅤㅤㅤㅤ",
                        color=VkKeyboardColor.NEGATIVE,
                        payload={
                            "type": "empty_callback"
                        }
                    )

                    vk_session.method("messages.edit", {
                        "peer_id": event.obj.peer_id,
                        "message": call_form_text,
                        "conversation_message_id": event.obj.conversation_message_id,
                        "keyboard": e_keyboard.get_keyboard()
                    })

                    sender(form_user_id, f"⚠️ Внимание ⚠️\nНика по вашей форме нет в БД:\n{call_form_text}")
                    chat_sender(3, f"Ника по следующей форме нет в БД:\n{call_form_text}\n#нетвбд")

                elif "accept" in event.object.payload.get('call_back'):
                    call_form_text = event.object.payload.get('call_back').split("-")[1]

                    e_keyboard = VkKeyboard(inline=True)
                    e_keyboard.add_callback_button(
                        label="ㅤㅤㅤㅤㅤ✅ㅤㅤㅤㅤㅤ",
                        color=VkKeyboardColor.POSITIVE,
                        payload={
                            "type": "empty_callback"
                        }
                    )

                    vk_session.method("messages.edit", {
                        "peer_id": event.obj.peer_id,
                        "message": call_form_text,
                        "conversation_message_id": event.obj.conversation_message_id,
                        "keyboard": e_keyboard.get_keyboard()
                    })

                elif "for_kirill" in event.object.payload.get('call_back'):
                    call_back_text = event.object.payload.get('call_back').split("-")
                    form_user_id = int(call_back_text[2])
                    call_form_text = call_back_text[1]

                    e_keyboard = VkKeyboard(inline=True)
                    e_keyboard.add_callback_button(
                        label="ㅤㅤㅤПереданоㅤㅤㅤ",
                        color=VkKeyboardColor.POSITIVE,
                        payload={
                            "type": "empty_callback"
                        }
                    )

                    vk_session.method("messages.edit", {
                        "peer_id": event.obj.peer_id,
                        "message": call_form_text,
                        "conversation_message_id": event.obj.conversation_message_id,
                        "keyboard": e_keyboard.get_keyboard()
                    })

                    sender(468509613, f"[id{form_user_id}|Администратор] передал вам форму:\n{call_form_text}")

    except Exception as error:
        print(error)
