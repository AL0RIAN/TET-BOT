import database
from telebot import types
from config_data.constants import bot, history_data


@bot.message_handler(commands=["history"])
def history(message: types.Message) -> None:
    """
    This function sends history of chat to user

    :param message: Message instance with text '/history'
    :return: None
    """

    print(f"\nInfo: user id is {message.from_user.id}")
    history_data["currentId"] = message.from_user.id

    result = database.db_utils.from_db(user_id=message.from_user.id)
    if len(result) == 0:
        bot.send_message(chat_id=message.chat.id, text="❌ History is empty")
    else:
        current_page = 0

        keyboard = types.InlineKeyboardMarkup()
        button1 = types.InlineKeyboardButton(text="<", callback_data="H<")
        button2 = types.InlineKeyboardButton(text=">", callback_data="H>")
        button3 = types.InlineKeyboardButton(text="OK", callback_data="Hok")
        keyboard.add(button1, button3, button2)

        head = f"📄 Record #{current_page} - {result[current_page][0]}: {result[current_page][1]}:"
        hotels_list = result[current_page][2].split("\n")[:-1]
        hotels = "".join(list(map(lambda x: f"\n{hotels_list.index(x) + 1}. {x}", hotels_list)))
        text = f"{head} \n{hotels}\n"

        bot.send_message(chat_id=message.chat.id, text=text, parse_mode="html", reply_markup=keyboard)
