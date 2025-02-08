import os
import telebot
import datetime
from dotenv import load_dotenv

load_dotenv()

# DiplomaTestSkillbox token
bot = telebot.TeleBot(os.getenv("BOT_KEY"))

# Requests URLs
url_city = "https://hotels4.p.rapidapi.com/locations/v3/search"
url_properties = "https://hotels4.p.rapidapi.com/properties/v2/list"
url_photos = "https://hotels4.p.rapidapi.com/properties/get-hotel-photos"

# Header Parameters
headers = {
    "X-RapidAPI-Key": os.getenv("RAPID_API_KEY"),
    "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
}

# DB information
to_data_base = list()

history_data = {"currentPage": 0,
                "currentId": 0
                }

# Calendar Data
calendar_data = {"day": datetime.datetime.now(),
                 "year": datetime.datetime.now().year,
                 "month": datetime.datetime.now().month,
                 "from": None,
                 "to": None
                 }

# Response Properties
response_properties = {"sortOrder": str(),
                       "city": str(),
                       "days": 0,
                       "hotelCount": 0,
                       "photos": "No",
                       "photoCount": 0,
                       "priceMin": 0,
                       "priceMax": 10000.0,
                       "distance": 0.0,
                       "currency": "USD"
                       }
