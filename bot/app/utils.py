import requests
from telegram import Update
from telegram.ext import  CallbackContext
from config.config_env import LOCATION, MAP_ID, SANCTUM_TG_BASE_URL, X_API_KEY


# for sanctum agent chatting
headers = {
    'X-API-KEY': X_API_KEY,
    'Content-Type': 'application/json'
}
data = {
        "agent_id": "",
        "current_day": "day 1", # not sure if this is used (no need to worry as of now)
        "location": LOCATION, # relates to map
        "map_id": MAP_ID,
        "current_time": "",
        "events": {
            "user_conversation": {
                "initiator_id": "", # intiator_id is formated like this (email:<telegram_id>@telegram.id)
                "name": "", # update.message.from_user.id
                "message": "",
                "is_end": True
            }
        }
    }


# UPDATING USER INFO
def update_info(update: Update, context: CallbackContext, must_update: int) -> int:

    if update.inline_query:
        chat_id = update.inline_query.from_user.id
    elif update.callback_query:
        chat_id = update.callback_query.message.chat.id
    elif update.message:
        chat_id = update.message.chat_id

    if 'user_info' not in context.user_data or must_update == 1:
        try:
            response = requests.get(SANCTUM_TG_BASE_URL + "/api/user/" + str(chat_id))
            if response.status_code >= 200 and response.status_code <= 226:
                JSONdata = response.json()
                context.user_data['user_info'] = JSONdata
                return 0
            return 1
        except (requests.exceptions.RequestException, ValueError, KeyError):
            return 1
    return 0


# REGISTER
async def register(update: Update, context: CallbackContext) -> None:
    chat_id = None
    name = None

    if update.callback_query:
        chat_id = update.callback_query.message.chat.id
    else:
        chat_id = update.message.chat_id

    if update.message.from_user.username:
        name = update.message.from_user.username
    else:
        name = update.message.from_user.full_name

    this_header = {
        'Content-Type': "application/json"
    }
    body_json = {
        "username": name,
        "telegram_id": update.message.chat.id
    }

    args = context.args
    if args:
        body_json['referred_by'] = args[0]

    try:
        response = requests.post(SANCTUM_TG_BASE_URL + "/api/user/", json=body_json, headers=this_header)
        if response.status_code >= 200 and response.status_code <= 226:
            JSONdata = response.json()
            context.user_data['user_info'] = JSONdata
            return
        await context.bot.send_message(chat_id=chat_id, text="Uh oh. Something went wrong.\nPlease try again later or use /start if you haven't registered")
    except requests.exceptions.RequestException:
        await context.bot.send_message(chat_id=chat_id, text="Uh oh. Something went wrong.\nPlease try again later or use /start if you haven't registered")


def is_agent_chatting_with_user(context) -> bool:
    # if context.user_data["user_info"]["agents"][0]["is_chatting_with_user"] == True:
    if "user_info" in context.user_data:
            if len(context.user_data["user_info"]["agents"]) >= 1:
                if context.user_data["user_info"]["agents"][0]["is_chatting_with_user"] == True:
                    return True
    return False
