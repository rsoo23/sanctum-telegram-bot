from datetime import datetime
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup,ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import CallbackContext, ConversationHandler
from config.config_env import SANCTUM_TG_BASE_URL, X_BASE_URL, SANCTUM_TG_KEY
from utils import headers, data, update_info, is_agent_chatting_with_user
from constants import AGE, ASKING, CHANGING, CONFIRMATION, DESCRIPTION, GENDER, GOALS, NAME


# CHATTING WITH AGENT COMMAND HANDLERS
async def chat(update: Update, context: CallbackContext) -> None:
    # # Error handling
    if update.edited_message != None:
        return
    
    if update.callback_query:
        chat_id = update.callback_query.message.chat.id
        name = update.callback_query.message.chat.full_name
    else:
        chat_id = update.message.chat_id
        name = update.message.chat.full_name

    # FIXME:
    # THIS CURRENTLY ASSUMES 1 AGENT PER USER
    if update_info(update, context, 1):
        await context.bot.send_message(chat_id=chat_id, text="Uh oh. Something went wrong.\nPlease try again later or use /start if you haven't registered")
        return
    if "user_info" in context.user_data and len(context.user_data["user_info"]["agents"]) == 0:
        reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("Yes", callback_data="yes"), InlineKeyboardButton("No", callback_data="no")]])
        await context.bot.send_message(chat_id=chat_id, text="It seems like you do not have a agent yet\nWould you like to proceed with the agent creation process?\nPlease respond with \'yes\' or \'no\'.", reply_markup=reply_markup)
        return ASKING

    data['agent_id'] = context.user_data['user_info']["agents"][0]["agent_id"]
    data['current_time'] = datetime.now().strftime("%H:%M")
    data['events']['user_conversation']['initiator_id'] = "email:" + str(chat_id) + "@telegram.id"
    data['events']['user_conversation']['name'] = name
    data['events']['user_conversation']['message'] = "start"
    data['events']['user_conversation']['is_end'] = False

    try:
        response = requests.post(X_BASE_URL + "/agent/actions", json=data, headers=headers)
        if response.status_code >= 200 and response.status_code <= 226:
            tmp_header = {"API-key": SANCTUM_TG_KEY}
            jsonBody = {
                "agent_id": context.user_data['user_info']["agents"][0]["agent_id"],
                "is_chatting": True
            }
            django_response = requests.post(SANCTUM_TG_BASE_URL + "/api/agent/chatting_with_agent/", json=jsonBody, headers=tmp_header)
            if django_response.status_code == 200:
                context.user_data['user_info']["agents"][0]["is_chatting_with_user"] = True
                jsonData = response.json()
                reply_markup = ReplyKeyboardMarkup([["End conversation with agent"]])
                await context.bot.send_message(chat_id=chat_id, text=jsonData["conversation"]['messages'][-1]['content'], reply_markup=reply_markup)
                return ConversationHandler.END
        await context.bot.send_message(chat_id=chat_id, text="Uh oh. Something went wrong.")
    except (requests.exceptions.RequestException, ValueError, KeyError):
        await context.bot.send_message(chat_id=chat_id, text="Uh oh. Something went wrong.")
    return ConversationHandler.END

async def endchat(update: Update, context: CallbackContext) -> None:
    # Error handling
    if update.edited_message != None:
        return
    
    if update_info(update, context, 0):
        await update.message.reply_text("Uh oh. Something went wrong.\nPlease try again later or use /start if you haven't registered")
        return
    if not is_agent_chatting_with_user(context):
        await update.message.reply_text("You're not currently in a conversation with a Agent\nPlease use the /chat command to initiate a conversation")
        return

    data['agent_id'] = context.user_data['user_info']["agents"][0]["agent_id"]
    data['current_time'] = datetime.now().strftime("%H:%M")
    data['events']['user_conversation']['initiator_id'] = "email:" + str(update.message.chat_id) + "@telegram.id"
    data['events']['user_conversation']['name'] = update.message.from_user.full_name
    data['events']['user_conversation']['message'] = "End"
    data['events']['user_conversation']['is_end'] = True

    try:
        response = requests.post(X_BASE_URL + "/agent/actions", json=data, headers=headers)
        if response.status_code >= 200 and response.status_code <= 226:
            tmp_header = {"API-key": SANCTUM_TG_KEY}
            jsonBody = {
                "agent_id": context.user_data['user_info']["agents"][0]["agent_id"],
                "is_chatting": True
            }
            response = requests.post(SANCTUM_TG_BASE_URL + "/api/agent/chatting_with_agent/", json=jsonBody, headers=tmp_header)
            if response.status_code == 200:
                context.user_data['user_info']["agents"][0]["is_chatting_with_user"] = False
                await update.message.reply_text("You've ended the conversation with your Agent.\nYou may use \'/chat\' to talk with them again in the future.", reply_markup=ReplyKeyboardRemove())
                return
        await update.message.reply_text("Uh oh. Something went wrong.")
    except requests.exceptions.RequestException:
        await update.message.reply_text("Uh oh. Something went wrong.")

async def chat_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    return await chat(update, context)


# CREATING AGENT
def creating_agent_cleanup(context: CallbackContext):
    if "agent_name" in context.user_data:
        context.user_data.pop("agent_name")
    if "agent_age" in context.user_data:
        context.user_data.pop("agent_age")
    if "agent_gender" in context.user_data:
        context.user_data.pop("agent_gender")
    if "agent_goals" in context.user_data:
        context.user_data.pop("agent_goals")
    if "agent_desc" in context.user_data:
        context.user_data.pop("agent_desc")

async def get_asking(update: Update, context: CallbackContext):
    await update.callback_query.answer()
    user_input = update.callback_query.data
    chat_id = update.callback_query.message.chat.id
    if user_input == 'no':
        await context.bot.send_message(chat_id=chat_id, text="No problem, please use the /chat command when you wish to create and chat with the agent")
        return ConversationHandler.END
    elif user_input == 'yes':
        await context.bot.send_message(chat_id=chat_id, text="Please use /cancel at any time to stop the process")
        await context.bot.send_message(chat_id=chat_id, text="Please state the agents name")
        return NAME
    return ASKING

async def get_name(update: Update, context: CallbackContext):
    context.user_data['agent_name'] = update.message.text.strip()
    if "changing" in context.user_data and context.user_data["changing"] == 1:
        await update.message.reply_text("Do you confirm the following details for your character?")
        await update.message.reply_text("Name: " + context.user_data['agent_name'] + "\nAge: " + context.user_data['agent_age'] + "\nGender: " + context.user_data["agent_gender"] + '\nGoals: ' + context.user_data['agent_goals'] + "\nDescription: " + context.user_data['agent_desc'])
        reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("Yes", callback_data="yes"), InlineKeyboardButton("No", callback_data="no")]])
        await update.message.reply_text("Please select \"yes\" to confirm, and \"no\" to change a detail.", reply_markup=reply_markup)
        context.user_data["changing"] = 0
        return CONFIRMATION
    await update.message.reply_text("Please enter the age of the agent")
    return AGE

async def get_age(update: Update, context: CallbackContext):
    user_input = update.message.text.strip().lower()
    keyboard = [["Male"], ["Female"], ["Nonbinary"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    if user_input.isnumeric():
        context.user_data['agent_age'] = user_input
        if "changing" in context.user_data and context.user_data["changing"] == 1:
            await update.message.reply_text("Do you confirm the following details for your agent?")
            await update.message.reply_text("Name: " + context.user_data['agent_name'] + "\nAge: " + context.user_data['agent_age'] + "\nGender: " + context.user_data["agent_gender"] + '\nGoals: ' + context.user_data['agent_goals'] + "\nDescription: " + context.user_data['agent_desc'])
            reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("Yes", callback_data="yes"), InlineKeyboardButton("No", callback_data="no")]])
            await update.message.reply_text("Please select \"yes\" to confirm, and \"no\" to change a detail.", reply_markup=reply_markup)
            context.user_data["changing"] = 0
            return CONFIRMATION
        await update.message.reply_text("Please specify the gender of your agent", reply_markup=reply_markup)
        return GENDER
    await update.message.reply_text("please enter numbers only\nplease try again")
    return AGE

async def get_gender(update: Update, context: CallbackContext):
    user_input = update.message.text.strip().lower()
    if user_input == "male" or user_input == "female" or user_input == "nonbinary":
        context.user_data['agent_gender'] = user_input
        if "changing" in context.user_data and context.user_data["changing"] == 1:
            await update.message.reply_text("Do you confirm the following details for your agent?", reply_markup=ReplyKeyboardRemove())
            await update.message.reply_text("Name: " + context.user_data['agent_name'] + "\nAge: " + context.user_data['agent_age'] + "\nGender: " + context.user_data["agent_gender"] + '\nGoals: ' + context.user_data['agent_goals'] + "\nDescription: " + context.user_data['agent_desc'])
            reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("Yes", callback_data="yes"), InlineKeyboardButton("No", callback_data="no")]])
            await update.message.reply_text("Please select \"yes\" to confirm, and \"no\" to change a detail.", reply_markup=reply_markup)
            context.user_data["changing"] = 0
            return CONFIRMATION
        await update.message.reply_text("What is your agent\'s goal?", reply_markup=ReplyKeyboardRemove())
        return GOALS
    await update.message.reply_text("You can only choose between \'male\', \'female\' or \'nonbinary\'")
    return GENDER

async def get_goals(update: Update, context: CallbackContext):
    context.user_data['agent_goals'] = update.message.text.strip()
    if "changing" in context.user_data and context.user_data["changing"] == 1:
        await update.message.reply_text("Do you confirm the following details for your agent?")
        await update.message.reply_text("Name: " + context.user_data['agent_name'] + "\nAge: " + context.user_data['agent_age'] + "\nGender: " + context.user_data["agent_gender"] + '\nGoals: ' + context.user_data['agent_goals'] + "\nDescription: " + context.user_data['agent_desc'])
        reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("Yes", callback_data="yes"), InlineKeyboardButton("No", callback_data="no")]])
        await update.message.reply_text("Please select \"yes\" to confirm, and \"no\" to change a detail.", reply_markup=reply_markup)
        context.user_data["changing"] = 0
        return CONFIRMATION
    await update.message.reply_text("Please provide a description of your agent. Include details you think are important.")
    return DESCRIPTION

async def get_description(update: Update, context: CallbackContext):
    context.user_data['agent_desc'] = update.message.text.strip()
    await update.message.reply_text("Do you confirm the following details for your agent?")
    await update.message.reply_text("Name: " + context.user_data['agent_name'] + "\nAge: " + context.user_data['agent_age'] + "\nGender: " + context.user_data["agent_gender"] + '\nGoals: ' + context.user_data['agent_goals'] + "\nDescription: " + context.user_data['agent_desc'])
    reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("Yes", callback_data="yes"), InlineKeyboardButton("No", callback_data="no")]])
    await update.message.reply_text("Please select \"yes\" to confirm, and \"no\" to change a detail.", reply_markup=reply_markup)
    context.user_data["changing"] = 0
    return CONFIRMATION

async def get_confirmation_agent(update: Update, context: CallbackContext):
    await update.callback_query.answer()
    user_input = update.callback_query.data
    chat_id = update.callback_query.message.chat.id
    if user_input == 'yes':
        tmp_headers = {
            'Content-Type': 'application/json'
        }
        json_body = {
            "name": context.user_data['agent_name'],
            "age": context.user_data['agent_age'],
            "gender": context.user_data['agent_gender'],
            "goal": context.user_data['agent_goals'],
            "description": context.user_data['agent_desc'],
            "telegram_id": update.callback_query.message.chat.id
        }
        try:
            response = requests.post(SANCTUM_TG_BASE_URL + "/api/agent/", json=json_body, headers=tmp_headers)
            if response.status_code >= 200 and response.status_code <= 226:
                JSONdata = response.json()
                context.user_data['user_info']["agents"].append(
                {
                    "name": JSONdata['data']['name'],
                    "agent_id": JSONdata['data']['agent_id'],
                    "created_at": JSONdata['data']['created_at'],
                    "updated_at": JSONdata['data']['updated_at']
                })
                await context.bot.send_message(chat_id=chat_id, text="Your agent has successfully been created!\nUse the /chat command to start chatting with your agent.")
                return ConversationHandler.END
            await context.bot.send_message(chat_id=chat_id, text="Uh oh. Something went wrong.")
        except (requests.exceptions.RequestException, KeyError):
            await context.bot.send_message(chat_id=chat_id, text="Uh oh. Something went wrong.")
        creating_agent_cleanup(context)
        return ConversationHandler.END
    elif user_input == 'no':
        reply_markup = InlineKeyboardMarkup([[InlineKeyboardButton("Name", callback_data="name")], [InlineKeyboardButton("Age", callback_data="age"), InlineKeyboardButton("Gender", callback_data="gender")], [InlineKeyboardButton("Goal", callback_data="goal"), InlineKeyboardButton("Description", callback_data="description")]])
        await context.bot.send_message(chat_id=chat_id, text="Please select which would you like to change", reply_markup=reply_markup)
        return CHANGING
    return CONFIRMATION

async def get_if_change(update: Update, context: CallbackContext):
    await update.callback_query.answer()
    user_input = update.callback_query.data
    chat_id = update.callback_query.message.chat.id

    if "name" == user_input:
        context.user_data['changing'] = 1
        await context.bot.send_message(chat_id=chat_id, text="Please enter the new name")
        return NAME
    elif "age" == user_input:
        context.user_data['changing'] = 1
        await context.bot.send_message(chat_id=chat_id, text="Please enter the correct age")
        return AGE
    elif "gender" == user_input:
        context.user_data['changing'] = 1
        keyboard = [["Male"], ["Female"], ["Nonbinary"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await context.bot.send_message(chat_id=chat_id, text="Please enter the correct gender", reply_markup=reply_markup)
        return GENDER
    elif "goal" == user_input:
        context.user_data['changing'] = 1
        await context.bot.send_message(chat_id=chat_id, text="Please enter the correct goal")
        return GOALS
    elif "description" == user_input:
        context.user_data['changing'] = 1
        await context.bot.send_message(chat_id=chat_id, text="Please enter the correct description")
        return DESCRIPTION
    return CHANGING
