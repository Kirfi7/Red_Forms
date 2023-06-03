import vk_api
import sqlite3

from cfg import TOKEN, COMMANDS
from forms import add_form, get_form, form_accepted, form_denied, form_ranked_up
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
                    with open("help.txt", mode="r", encoding="utf-8") as file:
                        help_text = file.read()
                    sender(user_id, help_text)

                elif text == "Принять форму" and lvl > 0:
                    form_text, form_arg, form_sender = get_form(lvl)

                    i_keyboard = VkKeyboard(inline=True)
                    i_keyboard.add_callback_button(
                        label="Выполнено",
                        color=VkKeyboardColor.POSITIVE,
                        payload={"call_back": f"accept-{form_text}-{form_arg}-{form_sender}"})
                    i_keyboard.add_callback_button(
                        label="Нет в БД",
                        color=VkKeyboardColor.NEGATIVE,
                        payload={"call_back": f"deny-{form_text}-{form_arg}-{form_sender}"})

                    i_keyboard.add_line()
                    i_keyboard.add_callback_button(
                        label="Передать форму выше",
                        color=VkKeyboardColor.PRIMARY,
                        payload={"call_back": f"rank_up-{form_text}-{form_arg}-{form_sender}"})

                    # form_text = 0 возвращается в случае ошибки
                    if str(form_text) != "Error":
                        vk_session.method("messages.send", {
                            "user_id": user_id,
                            "message": form_text,
                            "random_id": 0,
                            "keyboard": i_keyboard.get_keyboard()
                        })
                    else:
                        sender(user_id, "В данный момент нет подходящих форм")

                elif text[0] == "/" and lvl > 0 and "_" in text:
                    cmd = text[1:].split()
                    if cmd[0] in COMMANDS:
                        if len(cmd) >= int(COMMANDS[cmd[0]]['parameters']):
                            add_form(text, user_id)

            elif event.type == VkBotEventType.MESSAGE_EVENT:
                call_back = event.object.payload.get('call_back')

                if "deny" in call_back:
                    form_text, form_row, form_sender = call_back.split("-")[1:]

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
                        "message": form_text,
                        "conversation_message_id": event.obj.conversation_message_id,
                        "keyboard": e_keyboard.get_keyboard()
                    })

                    form_denied(int(form_row))
                    sender(form_sender, f"⚠️ Внимание ⚠️\nНика по вашей форме нет в БД:\n{form_text}")

                elif "accept" in call_back:
                    form_text, form_row, form_sender = call_back.split("-")[1:]

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
                        "message": form_text,
                        "conversation_message_id": event.obj.conversation_message_id,
                        "keyboard": e_keyboard.get_keyboard()
                    })

                    form_accepted(int(form_row))

                elif "rank_up" in call_back:
                    form_text, form_row, form_sender = call_back.split("-")[1:]

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
                        "message": form_text,
                        "conversation_message_id": event.obj.conversation_message_id,
                        "keyboard": e_keyboard.get_keyboard()
                    })

                    form_ranked_up(int(form_row), get_level(event.obj.user_id))

    except Exception as error:
        print(error)
