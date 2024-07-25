import requests
from telegram import Update
from telegram.ext import CallbackContext, ConversationHandler
from config.config_env import ANNOUNCE_PASS, SANCTUM_TG_BASE_URL, SANCTUM_TG_KEY
from constants import   IMAGE, TEXT, CONFIRM


# ANNOUNCEMENTS
async def announcements(update: Update, context: CallbackContext):
    # Error handling
    if update.edited_message != None:
        return
    
    text = update.message.text.replace('/announcements', '').strip()

    if text == ANNOUNCE_PASS:
        await update.message.reply_text("You've started a session to broadcast a announcement\nYou may use \"/cancel\" at any time to end the process.")
        await update.message.reply_text("To utilize text formatting, Telegram supports Markdown V2. For example, to format your text as bold, you can send it like this: ```text here *bold text here*```")
        await update.message.reply_text("Please enter the text you want to be in the announcement.")
        return TEXT
    return ConversationHandler.END

async def get_text(update: Update, context: CallbackContext):
    context.user_data['announce_text'] = update.message.text
    await update.message.reply_text('Please send a photo to include with your announcement\ntype "/empty" if you don\'t want to include an image.')
    return IMAGE

async def get_image(update: Update, context: CallbackContext):
    user_input = update.message.text
    if user_input == '/cancel':
        await update.message.reply_text("Conversation cancelled")
        return ConversationHandler.END
    if len(update.message.photo) <= 1 and user_input != "/empty":
        await update.message.reply_text("Please send a photo or type \"/empty\" if you don't want to include a image.")
        return IMAGE
    if user_input == "/empty":
        context.user_data['announce_type'] = 'text'
        await update.message.reply_text("Here's a preview of the announcement")
        await update.message.reply_text(context.user_data["announce_text"], parse_mode='markdownv2')
        await update.message.reply_text("Do you confirm this announcement?\nPlease reply with \"yes\" to confirm or \"no\" to go back and create the text part of the announcement.")
        return CONFIRM
    context.user_data['announce_photo'] = update.message.photo[0].file_id
    context.user_data['announce_type'] = 'photo'
    await update.message.reply_text("Here's a preview of the announcement")
    await update.message.reply_photo(context.user_data['announce_photo'], caption=context.user_data['announce_text'], parse_mode='markdownv2')
    await update.message.reply_text("Do you confirm this announcement?\nPlease reply with \"yes\" to confirm or \"no\" to go back and create the text part of the announcement.")
    return CONFIRM

async def get_confirmation_announce(update: Update, context: CallbackContext):
    if update.message.text.lower() == 'no':
        await update.message.reply_text("Please enter the text you want to be in the announcement.")
        return TEXT
    elif update.message.text.lower() == 'yes':
        try:
            temp_header = {"API-key": SANCTUM_TG_KEY}
            response = requests.get(SANCTUM_TG_BASE_URL + "/api/user/",  headers=temp_header)
            if response.status_code >= 200 and response.status_code <= 226:
                JSONdata = response.json()
                arr = [i['telegram_id'] for i in JSONdata]
                print("sending announcement to: ", arr)
                for i in arr:
                    if context.user_data['announce_type'] == "photo":
                        await context.bot.send_photo(chat_id=i, photo=context.user_data['announce_photo'], caption=context.user_data['announce_text'], parse_mode='markdownv2')
                    else:
                        await context.bot.send_message(chat_id=i, text=context.user_data['announce_text'], parse_mode='markdownv2')
            else:
                await update.message.reply_text("Uh oh. Something went wrong.")
        except requests.exceptions.RequestException:
            await update.message.reply_text("Uh oh. Something went wrong.")
        return ConversationHandler.END
    await update.message.reply_text("Please reply with \"yes\" or \"no\".")
    return ConversationHandler.END

async def cancel(update: Update, context: CallbackContext):
    await update.message.reply_text("Conversation cancelled")
    return ConversationHandler.END
