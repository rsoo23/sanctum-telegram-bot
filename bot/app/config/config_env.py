import os
from dotenv import load_dotenv

load_dotenv()

# SENSITIVE INFO
BOT_TOKEN = os.getenv('BOT_TOKEN')
BOT_USERNAME = os.getenv('BOT_USERNAME')
X_API_KEY = os.getenv('X_API_KEY')
X_BASE_URL = os.getenv("X_BASE_URL")
SOURCE = os.getenv("SOURCE")
SANCTUM_TG_BASE_URL = os.getenv("SANCTUM_TG_BASE_URL")
ANNOUNCE_PASS = os.getenv("ANNOUNCE_PASSWORD")
SANCTUM_TG_KEY = os.getenv("DJANGO_API_KEY")

# MAP INFO
MAP_ID = os.getenv("MAP_ID")
LOCATION = os.getenv("LOCATION")

#LINKS
FAQ_LINK = os.getenv('FAQ_LINK')
REPORT_LINK = os.getenv('REPORT_LINK')
SANCTUM_TG_URL = os.getenv('SANCTUM_TG_URL')
SANCTUM_URL = os.getenv('SANCTUM_URL')
