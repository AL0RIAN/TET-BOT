import database
from telebot import types
from config_data.constants import bot


@bot.message_handler(commands=["history"])
def history(message: types.Message) -> None:
    """
    This function sends history of chat to user

    :param message: Message instance with text '/history'
    :return: None
    """

    text = str()
    text_size = 0
    result = database.db_utils.from_db(user_id=message.from_user.id)

    for command, date, hotels in result:
        hotels_list = hotels.split("\n")[:-1]
        hotels_text = "".join(list(map(lambda x: f"\n{hotels_list.index(x) + 1}. {x}", hotels_list)))
        text += f"\n📄 {date} - {command}: \n{hotels_text}\n"
        text_size += len(text)
        print(f"\nInfo: {len(text)} symbols")
        if len(text) >= 3096:
            bot.send_message(chat_id=message.chat.id, text=text, parse_mode="html")
            text_size = 0

    if text:
        bot.send_message(chat_id=message.chat.id, text=text, parse_mode="html")
    else:
        bot.send_message(chat_id=message.chat.id, text="❌ History is empty")
