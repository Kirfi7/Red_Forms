import vk_api

TOKEN = "vk1.a.Z_w2nL1jQ93q9R1K8cqETf8zttPoJdzYJBC1_5QJQYBTOzfQSfLAmmCjkqeureXhaiQBFzimFLjMGOiumeMrbL8QpwZwZ0QHjBQZc0gfyT47bR5V1OQ1OBxWrCwZkyHl4iboEbBozT4NNym3J3Hh017aBw5dXRLoUNRIf2Zg-MYqf9JiXvJr6y2pvGr_IHQQO7d2O9M_-Hqsg9vfq8goZQ"
# group token

DEV = {"534422651": "Миша", "468509613": "Кирилл"}

STAFF = ["327113505", "16715256", "137480835"]
#           Влад         Гей         Серый

SCOPE = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/spreadsheets",
         "https://www.googleapis.com/auth/drive.file", "https://www.googleapis.com/auth/drive"]

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
    "ungwarn": {"lvl": 4, "parameters": 4},
    "sban": {"lvl": 4, "parameters": 4},
    "spermban": {"lvl": 4, "parameters": 3}
}

vk_session = vk_api.VkApi(token=TOKEN)


def chat_sender(for_chat_id, message_text):
    vk_session.method("messages.send", {
        "chat_id": for_chat_id,
        "message": message_text,
        "random_id": 0
    })
