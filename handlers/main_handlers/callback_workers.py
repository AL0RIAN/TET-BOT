from utils.utils import *
from utils.InlineKeyboards import *
from config_data.constants import *


@bot.callback_query_handler(func=lambda call: call.data.startswith("H"))
def history_handler(call: types.CallbackQuery) -> None:
    """
    If ">" button was pressed the page changes to the next
    If "<" button was pressed the page changes to the previous

    :param call: CallbackQuery instance
    :return: None
    """
    user_id = history_data["currentId"]
    result = database.db_utils.from_db(user_id=user_id)
    hotels_count = len(result) - 1

    if call.data[1:] == ">" and hotels_count != 0:
        if history_data["currentPage"] + 1 > hotels_count:
            history_data["currentPage"] = 0
        else:
            history_data["currentPage"] += 1
        book = history_book(data=result, current_page=history_data["currentPage"])
        bot.edit_message_text(text=book[0], message_id=call.message.message_id, chat_id=call.message.chat.id,
                              parse_mode="html", reply_markup=book[1])
        bot.answer_callback_query(callback_query_id=call.id)
    elif call.data[1:] == "<" and hotels_count != 0:
        if history_data["currentPage"] - 1 < 0:
            history_data["currentPage"] = hotels_count
        else:
            history_data["currentPage"] -= 1
        book = history_book(data=result, current_page=history_data["currentPage"])
        bot.edit_message_text(text=book[0], message_id=call.message.message_id, chat_id=call.message.chat.id,
                              parse_mode="html", reply_markup=book[1])
        bot.answer_callback_query(callback_query_id=call.id)
    elif call.data[1:] == "ok":
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id - 1)
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
    else:
        bot.answer_callback_query(callback_query_id=call.id)


@bot.callback_query_handler(func=lambda call: call.data.startswith("c"))
def calendar_handler(call: types.CallbackQuery) -> None:
    """
    If ">" button was pressed the calendar scrolls to the next month (creating a new calendar page)
    If "<" button was pressed the calendar scrolls to the previous month (creating a new calendar page)
    If the date button was pressed the information enters to calendar_date


    :param call: CallbackQuery instance
    :return: None
    """

    logg.logger(text=f"User selected {call.data}", report_type="debug")
    logg.logger(text=f"Calendar data - {calendar_data}", report_type="debug")

    def days_between(date1, date2):
        date1 = datetime.datetime.strptime(date1, "%Y-%m-%d")
        date2 = datetime.datetime.strptime(date2, "%Y-%m-%d")
        return abs((date2 - date1).days)

    if call.data[1:] == ">":
        # If current month is the last one the counter is reset
        if calendar_data["month"] == 12:
            calendar_data["month"] = 1
            calendar_data["year"] = calendar_data["year"] + 1
        else:
            calendar_data["month"] = calendar_data["month"] + 1

        keyboard = InlineKeyboards.calendar_maker(month=calendar_data["month"], year=calendar_data["year"])
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      inline_message_id=call.inline_message_id, reply_markup=keyboard)

        bot.answer_callback_query(callback_query_id=call.id)

    elif call.data[1:] == "<":
        # If the current month is the first one the counter is reset.
        if calendar_data["month"] == 1:
            calendar_data["month"] = 12
            calendar_data["year"] = calendar_data["year"] - 1
        else:
            calendar_data["month"] = calendar_data["month"] - 1
        keyboard = InlineKeyboards.calendar_maker(month=calendar_data["month"], year=calendar_data["year"])
        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      inline_message_id=call.inline_message_id, reply_markup=keyboard)
        bot.answer_callback_query(callback_query_id=call.id)

    elif re.fullmatch(pattern=r"c\d+.\d+.\d+", string=f"{call.data}"):

        if not calendar_data["from"]:
            data = call.data[1:].split("-")
            calendar_data["from"] = "{:4d}-{:02d}-{:02d}".format(int(data[0]), int(data[1]), int(data[2]))

            logg.logger(text=f"Check in - {calendar_data['from']}", report_type="debug")

            bot.edit_message_text(text=f"🕓 <b>BOOKING</b> | Your choice: from <b>{calendar_data['from']}</b> to -",
                                  chat_id=call.message.chat.id, message_id=call.message.message_id - 1,
                                  parse_mode="html")
            bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)

            get_days(chat_id=call.message.chat.id)
        else:
            data = call.data[1:].split("-")
            calendar_data["to"] = "{:4d}-{:02d}-{:02d}".format(int(data[0]), int(data[1]), int(data[2]))

            logg.logger(text=f"Check out - {calendar_data['to']}", report_type="debug")

            bot.edit_message_text(
                text=f"✅ <b>BOOKING</b> | Your choice: from <b>{calendar_data['from']}</b> to <b>{calendar_data['to']}</b>",
                chat_id=call.message.chat.id, message_id=call.message.message_id - 2,
                parse_mode="html")
            bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)

            response_properties["days"] = days_between(date1=calendar_data["from"], date2=calendar_data["to"])

            msg = bot.send_message(chat_id=call.message.chat.id, text="🌆 Enter city name:", disable_notification=False)
            bot.register_next_step_handler(msg, get_name)


@bot.callback_query_handler(func=lambda call: call.data.startswith("h"))
def hotel_number_handler(call: types.CallbackQuery) -> None:
    """
    Step 1. callback_worker saves data to response_properties['hotelCount']
    Step 2. callback_worker edits input prompt message from call
    Step 3. callback_worker transmits control to function 'get_answer'

    :param call: CallbackQuery instance
    :return: None
    """

    logg.logger(text=f"User input {call.data}", report_type="debug")
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

    logg.logger(text=f"User input {call.data}", report_type="debug")

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

    logg.logger(text=f"User input {call.data}", report_type="debug")

    response_properties["photoCount"] = int(call.data[1:])
    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text=f"✅ <b>NUMBER OF PHOTOS</b> | Your choice: {call.data[1:]}", parse_mode="html")
    hotels_parser(chat_id=call.message.chat.id)


@bot.callback_query_handler(func=lambda call: call.data.startswith("min") or call.data.startswith("max"))
def price_range_handler(call: types.CallbackQuery) -> None:
    """
    The handler accepts a call starting with min or max.

    If max, then the data is entered into response_properties["priceMax"].
    Else added to response_properties["priceMin"].

    If the handler receives "maxOK", then control is transferred to the get_distance function

    :param call: CallbackQuery instance
    :return: None
    """

    logg.logger(text=f"User input {call.data}", report_type="debug")
    flag = call.data[:3].capitalize()

    if re.fullmatch(pattern=r"[m]\w+[+-]\d+", string=f"{call.data}"):

        if response_properties[f"price{flag}"] + int(call.data[3:]) < 0:
            response_properties[f"price{flag}"] = 0
        else:
            response_properties[f"price{flag}"] += int(call.data[3:])
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id + 1,
                                  text=f"Your input: {response_properties[f'price{flag}']} USD")

        bot.answer_callback_query(callback_query_id=call.id)
    elif call.data == "minOK":
        bot.edit_message_text(
            text=f"✅ <b>{flag.upper()} PRICE</b> | Your choice: {response_properties['priceMin']} USD",
            chat_id=call.message.chat.id, message_id=call.message.message_id, parse_mode="html")
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id + 1)

        keyboard = InlineKeyboards.calculator("max")
        bot.send_message(chat_id=call.message.chat.id, text=f"💵 Enter max price:", reply_markup=keyboard)
        bot.send_message(chat_id=call.message.chat.id, text=f"Your input: {response_properties['priceMax']} USD")

    else:
        bot.edit_message_text(
            text=f"✅ <b>{flag.upper()} PRICE</b> | Your choice: {response_properties['priceMax']} USD",
            chat_id=call.message.chat.id, message_id=call.message.message_id, parse_mode="html")
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id + 1)

        get_distance(message=call.message)


@bot.callback_query_handler(func=lambda call: call.data.startswith("d"))
def get_distance_handler(call: types.CallbackQuery) -> None:
    """
    Step 1. callback_worker saves data to response_properties['distance']
    Step 2. callback_worker edits input prompt message from call
    Step 3. callback_worker transmits control to function 'hotels_parser'

    :param call: CallbackQuery instance
    :return: None
    """

    logg.logger(text=f"User input {call.data}", report_type="debug")
    response_properties["distance"] = float(call.data[1:])

    if call.data[1:] == "inf":
        miles = "7+"
    else:
        miles = call.data[1:]

    bot.edit_message_text(
        text=f"✅ <b>DISTANCE FROM CENTER</b> | Your choice: {miles} miles",
        chat_id=call.message.chat.id, message_id=call.message.message_id, parse_mode="html")
    get_number(call.message)
