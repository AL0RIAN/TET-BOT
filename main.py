import telebot

# DiplomaTestSkillbox token
bot = telebot.TeleBot("5374577409:AAEqaoAS1vPRc1mDhre5aM3Z1rIw1Ln_yug")

# Requests URLs
url_city = "https://hotels4.p.rapidapi.com/locations/v2/search"
url_properties = "https://hotels4.p.rapidapi.com/properties/list"
url_photos = "https://hotels4.p.rapidapi.com/properties/get-hotel-photos"

# Header Parameters
headers = {
    "X-RapidAPI-Key": "624162d6f6msh896925e99832f85p116bfbjsn1aa5f4b17c97",
    "X-RapidAPI-Host": "hotels4.p.rapidapi.com"
}

bot.polling(none_stop=True, interval=0)
