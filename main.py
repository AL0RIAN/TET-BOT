import re
import telebot
from telebot import types

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

# Response Properties
response_properties = {"sortOrder": "", "city": "", "hotelCount": 0, "picture": False, "pictureCount": 0}


@bot.message_handler(commands=["lowprice"])
def low_price(message: types.Message) -> None:
    """
    This function sets functions route to find cheapest hotels

    Function sets sortOrder properties to 'Price' (from cheap to expensive)
    And waits for a message from user with city name. Then it transmits control to
    Function get_name.

    :param message: Message instance with text '/lowprice'
    :return: None
    """

    # Search will be done by price (from cheap to expensive)
    response_properties["sortOrder"] = "PRICE"

    msg = bot.reply_to(message, "Enter city name:")
    bot.register_next_step_handler(msg, get_name)


def get_name(message: types.Message) -> None:
    """
    This function gets city name from user
    And waits for a message from user with number of hotels in this city.
    It then checks message text on correctness and transmits control to function get_number.

    :param message: Message instance with city name
    :return: None
    """

    try:
        if not re.fullmatch(pattern=r"[ A-Za-z]+", string=f"{message.text}"):
            raise ValueError
    except ValueError:
        bot.reply_to(message=message, text="<b>Error</b>: Incorrect value", parse_mode="html")
        print("\nError: User input incorrect value\n")
    else:
        print(f"\nInfo: User input {message.text}\n")
        msg = bot.reply_to(message, "Enter number of hotels:")
        # bot.register_next_step_handler(msg, get_number)


bot.polling(none_stop=True, interval=0)
