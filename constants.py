import telebot

# DiplomaTestSkillbox token
bot = telebot.TeleBot("5374577409:AAEqaoAS1vPRc1mDhre5aM3Z1rIw1Ln_yug")

# Requests URLs
url_city = "https://hotels4.p.rapidapi.com/locations/v2/search"
url_properties = "https://hotels4.p.rapidapi.com/properties/list"
url_photos = "https://hotels4.p.rapidapi.com/properties/get-hotel-photos"

# Header Parameters
headers = {
    "X-RapidAPI-Key": "46548059a6msh7a58f92b4026f21p107b6cjsn7daca088a053",
    "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
}

# Response Properties
response_properties = {"sortOrder": "", "city": "", "hotelCount": 0, "photos": "No", "photoCount": 0,
                       "priceRange": float("inf"), "distance": float("inf"), "currency": "USD"}
