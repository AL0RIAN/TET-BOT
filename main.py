from utils import *
from handlers import *
from config_data.constants import bot

if __name__ == "__main__":
    bot.polling(none_stop=True, interval=0)
