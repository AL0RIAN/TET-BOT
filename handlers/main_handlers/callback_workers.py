from utils.utils import *
from config_data.constants import *


@bot.callback_query_handler(func=lambda call: call.data.startswith("h"))
def hotel_number_handler(call: types.CallbackQuery) -> None:
    """
    Step 1. callback_worker saves data to response_properties['hotelCount']
    Step 2. callback_worker edits input prompt message from call
    Step 3. callback_worker transmits control to function 'get_answer'

    :param call: CallbackQuery instance
    :return: None
    """

    print(f"\nInfo: User input {call.data}")
    response_properties["hotelCount"] = int(call.data[1:])
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text=f"✅ <b>NUMBER OF HOTELS</b> | Your choice: {call.data[1:]}", parse_mode="html")
    get_answer(call.message)


@bot.callback_query_handler(func=lambda call: call.data.startswith("No") or call.data.startswith("Yes"))
def get_answer_handler(call: types.CallbackQuery) -> None:
    """
        Step 1. callback_worker saves data to response_properties['photos']
        Step 2. callback_worker edits input prompt message from call
        Step 3. if data == 'Yes' callback_worker transmits control to function get_photo_number else is transmits
                control to function 'hotels_parser'

    :param call: CallbackQuery instance
    :return: None
    """

    print(f"\nInfo: User input {call.data}")
    response_properties["photos"] = call.data
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text=f"✅ <b>DO YOU NEED PHOTOS?</b> | Your choice: {call.data}", parse_mode="html")
    if call.data == "Yes":
        get_photo_number(call.message)
    else:
        response_properties["photoCount"] = 0
        hotels_parser(chat_id=call.message.chat.id)


@bot.callback_query_handler(func=lambda call: call.data.startswith("p"))
def photo_count_handler(call: types.CallbackQuery) -> None:
    """
    Step 1. callback_worker saves data to response_properties['photoCount']
    Step 2. callback_worker edits input prompt message from call
    Step 3. callback_worker transmits control to function 'hotels_parser'

    :param call: CallbackQuery instance
    :return: None
    """

    print(f"\nInfo: User input {call.data}")
    response_properties["photoCount"] = int(call.data[1:])
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text=f"✅ <b>NUMBER OF PHOTOS</b> | Your choice: {call.data[1:]}", parse_mode="html")
    hotels_parser(chat_id=call.message.chat.id)


@bot.callback_query_handler(func=lambda call: call.data.startswith("+") or call.data.startswith("-"))
def price_range_handler(call: types.CallbackQuery) -> None:
    """
    If callback data include pattern [+-]\d+:
        Step 1. It adds to response_properties["priceRange"]
        Step 2. callback_worker edits input prompt message from call
    If callback data include 'OK':
        Step 1. callback_worker edits input prompt message from call
        Step 2. callback_worker transmits control to function 'get_distance'

    :param call: CallbackQuery instance
    :return: None
    """

    print(f"\nInfo: User input {call.data}")
    if re.fullmatch(pattern=r"[+-]\d+", string=f"{call.data}"):
        response_properties["priceRange"] += int(call.data)
        if response_properties["priceRange"] < 0:
            response_properties["priceRange"] = 0

        try:
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id + 1,
                                  text=f"Your input: {response_properties['priceRange']} {response_properties['currency']}")
        finally:
            bot.answer_callback_query(callback_query_id=call.id)
    else:
        bot.edit_message_text(
            text=f"✅ <b>MAX PRICE</b> | Your choice: {response_properties['priceRange']} {response_properties['currency']}",
            chat_id=call.message.chat.id, message_id=call.message.message_id, parse_mode="html")
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id + 1)
        get_distance(call.message)


@bot.callback_query_handler(func=lambda call: call.data.startswith("d"))
def get_distance_handler(call: types.CallbackQuery) -> None:
    """
    Step 1. callback_worker saves data to response_properties['distance']
    Step 2. callback_worker edits input prompt message from call
    Step 3. callback_worker transmits control to function 'hotels_parser'

    :param call: CallbackQuery instance
    :return: None
    """
    print(f"\nInfo: User input {call.data}")
    response_properties["distance"] = float(call.data[1:])

    if call.data[1:] == "inf":
        miles = "7+"
    else:
        miles = call.data[1:]

    bot.edit_message_text(
        text=f"✅ <b>DISTANCE FROM CENTER</b> | Your choice: {miles} miles",
        chat_id=call.message.chat.id, message_id=call.message.message_id, parse_mode="html")
    get_number(call.message)
