import vk_api
import sqlite3

from vk_api.bot_longpoll import VkBotLongPoll

TOKEN = "vk1.a.Z_w2nL1jQ93q9R1K8cqETf8zttPoJdzYJBC1_5QJQYBTOzfQSfLAmmCjkqeureXhaiQBFzimFLjMGOiumeMrbL8QpwZwZ0QHjBQZc0gfyT47bR5V1OQ1OBxWrCwZkyHl4iboEbBozT4NNym3J3Hh017aBw5dXRLoUNRIf2Zg-MYqf9JiXvJr6y2pvGr_IHQQO7d2O9M_-Hqsg9vfq8goZQ"
# group token

DEV = ['534422651', '468509613']
#         Миша        Кирилл

STAFF = ['327113505', '16715256', '137480835']
#           Влад         Гей         Серый

COMMANDS = {
    "mute": {"lvl": 1, "parameters": 4},
    "unmute": {"lvl": 1, "parameters": 3},
    "jail": {"lvl": 1, "parameters": 4},
    "unjail": {"lvl": 1, "parameters": 3},
    "warn": {"lvl": 2, "parameters": 3},
    "unwarn": {"lvl": 2, "parameters": 3},
    "ban": {"lvl": 3, "parameters": 4},
    "unban": {"lvl": 3, "parameters": 3},
    "permban": {"lvl": 4, "parameters": 3},
    "ungwarn": {"lvl": 3, "parameters": 4}
}

# db = sqlite3.connect('admins.db')
# c = db.cursor()
# c.execute(f"CREATE TABLE admins (nick TEXT, lvl INTEGER, vk_id INTEGER)")
# db.commit()
# db.close()
#
# db = sqlite3.connect('forms.db')
# c = db.cursor()
# c.execute(f"CREATE TABLE forms (form TEXT, lvl INTEGER, date INTEGER, vk_id INTEGER)")
# db.commit()
# db.close()

vk_session = vk_api.VkApi(token=TOKEN)


def chat_sender(for_chat_id, message_text):
    vk_session.method("messages.send", {
        "chat_id": for_chat_id,
        "message": message_text,
        "random_id": 0
    })
