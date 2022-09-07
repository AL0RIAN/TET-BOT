from telebot import types
from config_data.constants import bot


@bot.message_handler(commands=["help"])
def helper(message: types.Message):
    """
    This function sends list of commands to user

    :param message: Message instance with text '/help'
    :return: None
    """

    text = "📌 Commands:\n\n" \
           "1. /help - list of command\n" \
           "2. /lowprice - hotel search sorted by low price\n" \
           "3. /highprice - hotel search sorted by high price\n" \
           "4. /bestdeal - hotel search sorted by distance from center and price\n" \
           "5. /history - search history list"

    bot.send_message(chat_id=message.chat.id, text=text)
