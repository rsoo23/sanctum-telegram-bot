# Telegram bot

This is the telegram bot for sanctum

## Setup

### Telegram bot

1. Seach on telegram for a bot called "@BotFather"
2. Click the start
3. Enter the command "/newbot"
4. Follow the steps to create the bot
5. Copy and paste the bot token into the ".env" file

### .env
KEY | Description
----|----
BOT_TOKEN | Token from [Telegram bot step](#Telegram-bot)
BOT_USERNAME | Bot username with the @ from above
X_API_KEY | Provided by the Sanctum virtual team
X_BASE_KEY |Base API link for for calling the Sanctum virtual backend
SOURCE | For our case its "SANCTUM_TG" (not really used currently)
SANCTUM_TG_BASE_URL | This is the Django api endpoint base url
ANNOUNCE_PASSWORD | This is the announcement command password (your choice)
MAP_ID | Have to request from Sanctum virtual team
LOCATION | From the get request of getting map details
FAQ_LINK | From client
REPORT_LINK | From client
SANCTUM_TG_URL | Roulette cocos url

## How to use

1. Run the docker ([follow this guide to setup the docker](https://github.com/uefn-ai/sanctum-telegram-bot/tree/dev/django_app/README.md))

Changes made in any files ending with ".py" in the ```repo_root/bot/app/``` directory will automactically refresh ```bot.py``` a.k.a the telegram bot


### Python libraries

```pip install -r requirements.txt```

- *This shouldn't be needed if you followed the instruction properly*