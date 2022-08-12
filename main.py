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
response_properties = {"sortOrder": "", "city": "", "hotelCount": 0, "photos": False, "photoCount": 0}


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

    msg = bot.reply_to(message, "🌆 Enter city name:")
    bot.register_next_step_handler(msg, get_name)


def get_name(message: types.Message) -> None:
    """
    This function gets city name from user
    It then transmits control to function get_number.

    :param message: Message instance with city name
    :return: None
    """

    try:
        if not re.fullmatch(pattern=r"[ A-Za-z]+", string=f"{message.text}"):
            raise ValueError
    except ValueError:
        bot.reply_to(message=message, text="❌ <b>Error</b>: Incorrect value", parse_mode="html")
        print("\nError: User input incorrect value\n")
    else:
        print(f"\nInfo: User input {message.text}")
        get_number(message)


def get_number(message: types.Message) -> None:
    """
    This function creates a keyboard with 3 rows and 3 columns
    With number buttons from 1 to 9 (including) and sends it to user's chat.

    Clicking button calls data and sends it to callback handler function.

    :param message: Last message (Message instance) in chat
    :return: None
    """

    keyboard = types.InlineKeyboardMarkup()

    for row in range(0, 3):
        button1 = types.InlineKeyboardButton(text=f"{row * 3 + 1}", callback_data=f"h{row * 3 + 1}")
        button2 = types.InlineKeyboardButton(text=f"{row * 3 + 2}", callback_data=f"h{row * 3 + 2}")
        button3 = types.InlineKeyboardButton(text=f"{row * 3 + 3}", callback_data=f"h{row * 3 + 3}")
        keyboard.row(button1, button2, button3)

    bot.reply_to(message=message, text="🧳 Enter number of hotels:", reply_markup=keyboard)


def get_answer(message: types.Message) -> None:
    """
    This function creates a keyboard with 1 rows and 2 columns
    With Yes-button and No-button and sends it to user's chat.

    Clicking button calls data and sends it to callback handler function.


    :param message:
    :return: None
    """

    keyboard = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton(text="Yes", callback_data="Yes")
    button2 = types.InlineKeyboardButton(text="No", callback_data="No")
    keyboard.add(button1, button2)

    bot.send_message(chat_id=message.chat.id, text="Do you need photos?", reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call: types.CallbackQuery) -> None:
    """
    This function handles the callback query:

    # TODO documentation

    :param call: CallbackQuery instance
    :return: None
    """

    if call.data.startswith("h"):
        try:
            response_properties["hotelCount"] = int(call.data[1:])
            if response_properties["hotelCount"] <= 0:
                raise ValueError
        except ValueError:
            print("\nError: User input incorrect value")
            bot.reply_to(message=call.message, text="❌ <b>Error</b>: Incorrect value", parse_mode="html")
        else:
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                  text=f"✅ <b>NUMBER OF HOTELS</b> | Your choice: {call.data[1:]}", parse_mode="html")
            get_answer(call.message)
    elif call.data == "Yes" or call.data == "No":
        response_properties["photos"] = call.data
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=f"✅ <b>DO YOU NEED PHOTOS?</b> | Your choice: {call.data}", parse_mode="html")


bot.polling(none_stop=True, interval=0)
