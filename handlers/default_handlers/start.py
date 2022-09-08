from telebot import types
from config_data.constants import bot


@bot.message_handler(commands=["start"])
def start(message: types.Message):
    """
    This function sends welcome message to user

    :param message: Message instance with text '/start'
    :return: None
    """

    bot.send_message(chat_id=message.chat.id, text="👋 Hello! Enter /help")
