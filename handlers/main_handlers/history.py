import database
from telebot import types
from debugging import logg
from utils.InlineKeyboards import history_book
from config_data.constants import bot, history_data


@bot.message_handler(commands=["history"])
def history(message: types.Message) -> None:
    """
    This function sends history of chat to user

    :param message: Message instance with text '/history'
    :return: None
    """

    logg.logger(text=f"User id is {message.from_user.id}", report_type="debug")
    history_data["currentId"] = message.from_user.id

    result = database.db_utils.from_db(user_id=message.from_user.id)

    if len(result) == 0:
        bot.send_message(chat_id=message.chat.id, text="❌ History is empty")
    else:
        book = history_book(data=result)
        bot.send_message(chat_id=message.chat.id, text=book[0], parse_mode="html", reply_markup=book[1])
