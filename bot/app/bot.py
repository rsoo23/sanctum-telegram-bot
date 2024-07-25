from datetime import datetime
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo, ReplyKeyboardMarkup, InlineQueryResultArticle, InputTextMessageContent
from telegram.ext import Application, MessageHandler, CommandHandler, ContextTypes, filters, CallbackContext, CallbackQueryHandler, ConversationHandler, InlineQueryHandler
from config.config_env import BOT_TOKEN, BOT_USERNAME, FAQ_LINK, REPORT_LINK, SANCTUM_TG_URL, SANCTUM_URL, X_BASE_URL
from utils import headers, data, register, update_info, is_agent_chatting_with_user
from constants import AGE, ASKING, CHANGING, CONFIRMATION, DESCRIPTION, GENDER, GOALS, NAME
from chat import chat, chat_callback, endchat, get_age, get_asking, get_confirmation_agent, get_description, get_gender, get_goals, get_if_change, get_name
from announcements import CONFIRM, IMAGE, TEXT, announcements, cancel, get_confirmation_announce, get_image, get_text
import traceback


# references
# user_data = {
#     "user_info": user_info_pulled_from_backend,
#     "chatting_with_agent": 0 | 1,
#     "web_url": SANCTUM_TG_URL + "?user_id=" + str(chat_id),
#     "announce_text": temp storage,
#     "announce_image": temp storage,
#     "agent_name": temp storage,
#     "agent_age": temp storage,
#     "agent_gender": temp storage,
#     "agent_goals": temp storage,
#     "agent_desc": temp storage
# }

# arr = [1904464168, 1525505267, 512004133, 6235773818, 1345867356]


# COMMAND HANDLERS
async def start(update: Update, context: CallbackContext) -> None:
    welcome_msg = "Welcome to Sanctum!"
    intro_msg = "💰 Start earning GODL now, boost your rankings and win up to USD100,000 airdrop rewards!\n\nSteps\n1️⃣ Select \"2X Your GODL\"\n2️⃣ Start Player\n3️⃣ Refer friends to earn more GODL\n\n⭐ Launching Soon\nSanctum Open World"
    image_name = "../assets/start_cmd.png"

    if "web_url" not in context.user_data:
        context.user_data["web_url"] = SANCTUM_TG_URL + "/#/roulette?user_id=" + str(update.message.chat_id)
    if "sanctum_url" not in context.user_data:
        context.user_data["sanctum_url"] = SANCTUM_URL + "/?user_id=" + str(update.message.chat_id)

    # Error handling
    if update.edited_message != None:
        return

    earn = InlineKeyboardButton(text="Refer & Earn GODL", callback_data='earngodl')
    roulette = InlineKeyboardButton(text="2X Your GODL", web_app=WebAppInfo(url=context.user_data['web_url']))
    play = InlineKeyboardButton(text="Enter Sanctum", web_app=WebAppInfo(url=context.user_data["sanctum_url"]))
    # agent_chat = InlineKeyboardButton(text="Chat with Agent", callback_data="start_agent_chat")
    agent_chat = InlineKeyboardButton(text="Chat with Agent", callback_data="coming_soon")
    help = InlineKeyboardButton(text="📖 Help", callback_data="help")

    custom_keyboard = [
        ["Refer & Earn GODL"],
        [roulette],
        [play],
        ["Chat with Agent"],
        ["📖 Help"]
    ]

    inlineButtons = [[earn], [roulette], [play], [agent_chat], [help]]

    reply_markup = ReplyKeyboardMarkup(custom_keyboard, resize_keyboard=True)
    await update.message.reply_text(welcome_msg, reply_markup=reply_markup)

    reply_markup = InlineKeyboardMarkup(inlineButtons)
    await update.message.reply_photo(open(image_name, "rb"), caption=intro_msg, reply_markup=reply_markup)
    update_info(update, context, 0)
    if "user_info" not in context.user_data:
        await register(update, context)

async def help(update: Update, context: ContextTypes) -> None:
    help_msg = f"🆘 Welcome to the Sanctum support zone.\n\n📖 Read FAQ: {FAQ_LINK}\n\n📢 Sanctum Announcement: @SanctumAI_Ann\n\n📢 Sanctum Community: @SanctumAI\n\n🚨 Report Bugs & Give Feedback: {REPORT_LINK}"

    # Error handling
    if update.edited_message != None:
        return

    if update.callback_query:
        chat_id = update.callback_query.message.chat.id
    else:
        chat_id = update.message.chat_id

    await context.bot.send_message(chat_id=chat_id, text=help_msg)

async def invite(update: Update, context: ContextTypes) -> None:
    invite_msg = "Share with your friends now and earn GODL for every friend you successfully invite."
    share_msg = "🎁 I'm giving you 100 GODL.\n@sanctumai_bot is the 1st Web3 AI open world on telegram. Play and earn mega airdrop rewards now!\n\n👉 Redeem GODL with my code: "
    image_name = "../assets/invite.png"

    twitter_url = 'https://twitter.com/intent/tweet?text='

    # Error handling
    if update.edited_message != None:
        return

    if update.callback_query:
        chat_id = update.callback_query.message.chat.id
    else:
        chat_id = update.message.chat_id
    
    if update_info(update, context, 0):
        await context.bot.send_message(chat_id=chat_id, text="Uh oh. Something went wrong.\nPlease try again later or use /start if you haven't registered")
        return
    share_msg += "https://t.me/" + BOT_USERNAME[1:] + "?start=" + context.user_data['user_info']['referral_id']
    twitter_url += share_msg

    button = InlineKeyboardButton(text="Share via Telegram", switch_inline_query=share_msg)
    button1 = InlineKeyboardButton(text="Share via 𝕏 (twitter)", url=twitter_url)
    keyboard = [[button], [button1]]
        
    reply_markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_photo(chat_id=chat_id, photo=open(image_name, "rb"), caption=invite_msg, reply_markup=reply_markup)


# PLACEHOLDERS
async def coming_soon(update: Update, context: CallbackContext):
    # text = "🎉 You've just joined the exclusive waitlist 🎉\nSanctum open world is launching soon. Stay tuned for updates and early access benefits.\n\nStudy Sanctum: litepaper.uefn.ai"
    text = "🚧 This feature is launching soon. Stay tuned for updates!"

    if update.callback_query:
        chat_id = update.callback_query.message.chat.id
    else:
        chat_id = update.message.chat_id

    await context.bot.send_message(chat_id=chat_id, text=text)


# MESSAGE HANDLER
async def handle_message(update: Update, context: CallbackContext):
    # Error handling
    if update.edited_message != None:
        return

    update_info(update, context, 0)
    is_chatting = is_agent_chatting_with_user(context)

    if not is_chatting:
        if '📖 Help' == update.message.text:
            await help(update, context)
        # if 'Enter Sanctum' == update.message.text:
        #     await coming_soon(update, context)
        if 'Refer & Earn GODL' == update.message.text:
            await invite(update, context)
        if 'Chat with Agent' == update.message.text:
            await coming_soon(update, context)
            # await chat(update, context)
    elif is_chatting:
        if 'End conversation with agent' == update.message.text:
            await endchat(update, context)
            return
        data['agent_id'] = context.user_data['user_info']["agents"][0]["agent_id"]
        data['current_time'] = datetime.now().strftime("%H:%M")
        data['events']['user_conversation']['initiator_id'] = "email:" + str(update.message.chat_id) + "@telegram.id"
        data['events']['user_conversation']['name'] = update.message.from_user.full_name
        data['events']['user_conversation']['message'] = update.message.text
        data['events']['user_conversation']['is_end'] = False

        try:
            response = requests.post(X_BASE_URL + "/agent/actions", json=data, headers=headers)
            if response.status_code >= 200 and response.status_code <= 226:
                jsonData = response.json()
                await update.message.reply_text(jsonData["conversation"]['messages'][-1]['content'])
        except (requests.exceptions.RequestException, ValueError, KeyError):
            await update.message.reply_text("Uh oh. Something went wrong.\nPlease try again later or use /start if you haven't registered")
        

# INLINE BUTTON HANDLER
async def button_callback(update: Update, context: CallbackContext):
    query = update.callback_query
    await query.answer()
    if query.data == 'coming_soon':
        await coming_soon(update, context)
    elif query.data == 'help':
        await help(update, context)
    elif query.data == 'earngodl':
        await invite(update, context)


# INLINE QUERY HANDLER
async def sharing_message(update: Update, context: CallbackContext):
    share_msg = "🎁 I'm giving you 100 GODL.\n@sanctumai_bot is the 1st Web3 AI open world on telegram. Play and earn mega airdrop rewards now!\n\n👉 Redeem GODL with my code: "

    if update_info(update, context, 0):
        await update.message.reply_text("Uh oh. Something went wrong.\nPlease try again later or use /start if you haven't registered")
        return
    share_msg += "https://t.me/" + BOT_USERNAME[1:] + "?start=" + context.user_data['user_info']['referral_id']

    results = [
        InlineQueryResultArticle(id="1", title="Click this to paste and share!", input_message_content=InputTextMessageContent(share_msg))
    ]
    await update.inline_query.answer(results)


# ERROR HANDLER
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print(f'update {update} caused error {context.error}')
    print(traceback.format_exc())


# TEST
# async def test(update: Update, context: CallbackContext) :


if __name__ == "__main__":
    print("Starting bot")
    app = Application.builder().token(BOT_TOKEN).build()

    # Commands
    app.add_handler(CommandHandler('start', start))
    app.add_handler(CommandHandler('help', help))
    app.add_handler(CommandHandler('invite', invite))

    # DEV
    # app.add_handler(CommandHandler('test', test))

    # Announcement
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('announcements', announcements)],
        states={
            TEXT:[MessageHandler(filters.TEXT & ~filters.COMMAND, get_text)],
            IMAGE:[MessageHandler(filters.TEXT | filters.PHOTO, get_image)],
            CONFIRM: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_confirmation_announce)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    app.add_handler(conv_handler)

    # Create Agent / chatting with agent
    creating_agent = ConversationHandler(
        entry_points=[
            CallbackQueryHandler(chat_callback, pattern="^start_agent_chat$"),
            CommandHandler("chat", chat)
        ],
        states={
            ASKING: [CallbackQueryHandler(get_asking)],
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_age)],
            GENDER: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_gender)],
            GOALS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_goals)],
            DESCRIPTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_description)],
            CONFIRMATION: [CallbackQueryHandler(get_confirmation_agent)],
            CHANGING: [CallbackQueryHandler(get_if_change)]
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    app.add_handler(creating_agent)
    app.add_handler(CommandHandler('endchat', endchat))

    # Messages
    app.add_handler(MessageHandler(filters.TEXT, handle_message))

    # Button callback
    app.add_handler(CallbackQueryHandler(button_callback))

    # Inline query
    app.add_handler(InlineQueryHandler(sharing_message))
    
    # ERROR
    app.add_error_handler(error)

    # POLLS THE BOT
    print("Polling...")
    app.run_polling(poll_interval=3)
