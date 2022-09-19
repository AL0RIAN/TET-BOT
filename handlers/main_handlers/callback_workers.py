import calendar
from utils.utils import *
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

    def create_page():
        current_page = history_data["currentPage"]

        keyboard = types.InlineKeyboardMarkup()
        button1 = types.InlineKeyboardButton(text="<", callback_data="H<")
        button2 = types.InlineKeyboardButton(text=">", callback_data="H>")
        button3 = types.InlineKeyboardButton(text="OK", callback_data="Hok")
        keyboard.add(button1, button3, button2)

        head = f"📄 Record #{current_page} - {result[current_page][0]}: {result[current_page][1]}:"
        hotels_list = result[current_page][2].split("\n")[:-1]
        hotels = "".join(list(map(lambda x: f"\n{hotels_list.index(x) + 1}. {x}", hotels_list)))
        text = f"{head} \n{hotels}\n"

        bot.edit_message_text(text=text, message_id=call.message.message_id, chat_id=call.message.chat.id,
                              parse_mode="html", reply_markup=keyboard)

        bot.answer_callback_query(callback_query_id=call.id)

    if call.data[1:] == ">":
        if history_data["currentPage"] + 1 > hotels_count:
            history_data["currentPage"] = 0
        else:
            history_data["currentPage"] += 1
        create_page()
    elif call.data[1:] == "<":
        if history_data["currentPage"] - 1 < 0:
            history_data["currentPage"] = hotels_count
        else:
            history_data["currentPage"] -= 1
        create_page()
    else:
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id - 1)
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)


@bot.callback_query_handler(func=lambda call: call.data.startswith("c"))
def calendar_handler(call: types.CallbackQuery) -> None:
    """
    If ">" button was pressed the calendar scrolls to the next month (creating a new calendar page)
    If "<" button was pressed the calendar scrolls to the previous month (creating a new calendar page)
    If the date button was pressed the information enters to calendar_date


    :param call: CallbackQuery instance
    :return: None
    """

    print(f"\nInfo: user selected {call.data}")
    print(f"\nInfo: {calendar_data}")

    def days_between(date1, date2):
        date1 = datetime.datetime.strptime(date1, "%d.%m.%Y")
        date2 = datetime.datetime.strptime(date2, "%d.%m.%Y")
        return abs((date2 - date1).days)

    def calendar_maker():
        keyboard = types.InlineKeyboardMarkup(row_width=7)

        # Current year and current month
        page = types.InlineKeyboardButton(
            text=f"{calendar.month_name[calendar_data['month']]}, {str(calendar_data['year'])}", callback_data="0")
        keyboard.row(page)

        # Days of week
        day_names: List[types.InlineKeyboardButton] = list()
        for number in range(7):
            day = types.InlineKeyboardButton(text=f"{calendar.day_abbr[number]}", callback_data=f"0")
            day_names.append(day)

        keyboard.add(day_names[0], day_names[1], day_names[2], day_names[3], day_names[4], day_names[5], day_names[6])

        # Days of month
        for week in calendar.monthcalendar(calendar_data["year"], calendar_data["month"]):
            row: List[types.InlineKeyboardButton] = list()
            for day in week:
                if day == 0:
                    row.append(types.InlineKeyboardButton(text=" ", callback_data="0"))

                elif f"{now_day.day}.{now_day.month}.{now_day.year}" == f"{day}.{calendar_data['month']}.{calendar_data['year']}":
                    row.append(types.InlineKeyboardButton(text=f"{day}",
                                                          callback_data=f"c{day}.{calendar_data['month']}.{calendar_data['year']}"))

                else:
                    row.append(types.InlineKeyboardButton(text=str(day),
                                                          callback_data=f"c{day}.{calendar_data['month']}.{calendar_data['year']}"))

            keyboard.add(row[0], row[1], row[2], row[3], row[4], row[5], row[6])

        keyboard.add(types.InlineKeyboardButton(text="<", callback_data="c<"),
                     types.InlineKeyboardButton(text=">", callback_data="c>"))

        bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,
                                      inline_message_id=call.inline_message_id, reply_markup=keyboard)

        bot.answer_callback_query(callback_query_id=call.id)

    now_day = datetime.datetime.now()
    if call.data[1:] == ">":
        # If current month is the last one the counter is reset
        if calendar_data["month"] == 12:
            calendar_data["month"] = 1
            calendar_data["year"] = calendar_data["year"] + 1
        else:
            calendar_data["month"] = calendar_data["month"] + 1
        calendar_maker()

    elif call.data[1:] == "<":
        # If the current month is the first one the counter is reset.
        if calendar_data["month"] == 1:
            calendar_data["month"] = 12
            calendar_data["year"] = calendar_data["year"] - 1
        else:
            calendar_data["month"] = calendar_data["month"] - 1
        calendar_maker()

    elif re.fullmatch(pattern=r"c\d+.\d+.\d+", string=f"{call.data}"):

        if not calendar_data["from"]:
            calendar_data["from"] = call.data[1:]
            print(f"\nInfo: {calendar_data['from']}")

            bot.edit_message_text(text=f"🕓 <b>BOOKING</b> | Your choice: from <b>{calendar_data['from']}</b> to -",
                                  chat_id=call.message.chat.id, message_id=call.message.message_id - 1,
                                  parse_mode="html")
            bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)

            get_days(chat_id=call.message.chat.id)
        else:
            calendar_data["to"] = call.data[1:]
            print(f"\nInfo: {calendar_data['to']}")

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


@bot.callback_query_handler(func=lambda call: call.data.startswith("min"))
def min_price_handler(call: types.CallbackQuery) -> None:
    """
    If callback data include pattern r"min[+-]\d+":
        Step 1. It adds to response_properties["priceRange"]
        Step 2. callback_worker edits input prompt message from call
    If callback data include 'OK':
        Step 1. callback_worker edits input prompt message from call
        Step 2. callback_worker transmits control to function 'get_max_price'

    :param call: CallbackQuery instance
    :return: None
    """

    print(f"\nInfo: User input {call.data}")
    if re.fullmatch(pattern=r"min[+-]\d+", string=f"{call.data}"):

        if response_properties["priceMin"] + int(call.data[3:]) <= 0:
            response_properties["priceMin"] = 0
        else:
            response_properties["priceMin"] += int(call.data[3:])
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id + 1,
                                  text=f"Your input: {response_properties['priceMin']} {response_properties['currency']}")

        bot.answer_callback_query(callback_query_id=call.id)
    else:
        bot.edit_message_text(
            text=f"✅ <b>MIN PRICE</b> | Your choice: {response_properties['priceMin']} {response_properties['currency']}",
            chat_id=call.message.chat.id, message_id=call.message.message_id, parse_mode="html")
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id + 1)
        get_max_price(message=call.message)


@bot.callback_query_handler(func=lambda call: call.data.startswith("max"))
def min_price_handler(call: types.CallbackQuery) -> None:
    """
    If callback data include pattern r"max[+-]\d+":
        Step 1. It adds to response_properties["priceRange"]
        Step 2. callback_worker edits input prompt message from call
    If callback data include 'OK':
        Step 1. callback_worker edits input prompt message from call
        Step 2. callback_worker transmits control to function 'get_distance'

    :param call: CallbackQuery instance
    :return: None
    """

    print(f"\nInfo: User input {call.data}")
    if re.fullmatch(pattern=r"max[+-]\d+", string=f"{call.data}"):

        if response_properties["priceMax"] + int(call.data[3:]) <= 0:
            response_properties["priceMax"] = 0

        else:
            response_properties["priceMax"] += int(call.data[3:])
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id + 1,
                                  text=f"Your input: {response_properties['priceMax']} {response_properties['currency']}")

        bot.answer_callback_query(callback_query_id=call.id)
    else:
        bot.edit_message_text(
            text=f"✅ <b>MAX PRICE</b> | Your choice: {response_properties['priceMax']} {response_properties['currency']}",
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
