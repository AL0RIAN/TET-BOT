import telebot

bot = telebot.TeleBot("5374577409:AAEqaoAS1vPRc1mDhre5aM3Z1rIw1Ln_yug")

bot.polling(none_stop=True, interval=0)
