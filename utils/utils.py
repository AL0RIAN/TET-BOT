import re
import json
import requests
import database
from typing import List
from telebot import types
from debugging import logg
from config_data.constants import *


def get_days(message: types.Message) -> None:
    """
    This function gets number of days from user and transmits control to function get_name.

    :param message: Message instance with number of days
    :return: None
    """

    try:
        if not message.text.isdigit() and int(message.text) > 0:
            raise ValueError
    except ValueError:
        bot.send_message(chat_id=message.chat.id, text="❌ <b>Error</b>: Incorrect value", parse_mode="html",
                         disable_notification=False)
        print("\nError: User input incorrect value")
    else:
        print(f"\nInfo: User input {message.text}")
        response_properties["days"] = int(message.text)
        bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
        bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        bot.send_message(chat_id=message.chat.id, text=f"✅ <b>NUMBER OF DAYS</b> | Your choice: {message.text}",
                         parse_mode="html", disable_notification=False)

        msg = bot.send_message(chat_id=message.chat.id, text="🌆 Enter city name:", disable_notification=False)
        bot.register_next_step_handler(msg, get_name)


def get_name(message: types.Message) -> None:
    """
    This function gets city name from user

    If sortOrder is "PRICE" or "PRICE_HIGHEST_FIRST" it then transmits control to function get_number.
    Otherwise, it transmits control to function get_price_range.

    :param message: Message instance with city name
    :return: None
    """

    try:
        if not re.fullmatch(pattern=r"[ A-Za-z]+", string=f"{message.text}"):
            raise ValueError
    except ValueError:
        bot.send_message(chat_id=message.chat.id, text="❌ <b>Error</b>: Incorrect value", parse_mode="html",
                         disable_notification=False)
        print("\nError: User input incorrect value")
    else:
        print(f"\nInfo: User input {message.text}")
        response_properties["city"] = message.text
        bot.delete_message(chat_id=message.chat.id, message_id=message.message_id - 1)
        bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        bot.send_message(chat_id=message.chat.id, text=f"✅ <b>CITY NAME</b> | Your choice: {message.text}",
                         parse_mode="html", disable_notification=False)

        if response_properties["sortOrder"] == "DISTANCE_FROM_LANDMARK":
            get_price_range(message=message)
        else:
            get_number(message)


def get_price_range(message: types.Message) -> None:
    """
    This function creates a keyboard with 2 rows and 5 columns
    With number buttons and OK-button.
    Then function sends it to user's chat.

    Clicking button calls data and sends it to callback handler function.

    :param message: Message instance with city name
    :return: None
    """

    # start price
    response_properties["priceRange"] = 0

    keyboard = types.InlineKeyboardMarkup()

    # button callback_data in first row: +X, where X is a number
    # button callback_data in second row: -X, where X is a number
    for symbol in ("+", "-"):
        button1 = types.InlineKeyboardButton(text=f"{symbol}10", callback_data=f"{symbol}10")
        button2 = types.InlineKeyboardButton(text=f"{symbol}50", callback_data=f"{symbol}50")
        button3 = types.InlineKeyboardButton(text=f"{symbol}100", callback_data=f"{symbol}100")
        button4 = types.InlineKeyboardButton(text=f"{symbol}250", callback_data=f"{symbol}250")
        button5 = types.InlineKeyboardButton(text=f"{symbol}500", callback_data=f"{symbol}500")

        keyboard.row(button1, button2, button3, button4, button5)

    ok_button = types.InlineKeyboardButton(text="OK", callback_data="+OK")
    keyboard.row(ok_button)

    bot.send_message(chat_id=message.chat.id, text="💵 Enter price range:", reply_markup=keyboard)
    bot.send_message(chat_id=message.chat.id,
                     text=f"Your input: {response_properties['priceRange']} {response_properties['currency']}")


def get_distance(message: types.Message) -> None:
    """
    This function creates a keyboard with 1 row and 5 columns
    With mileage buttons. Then function sends it to user's chat.

    Clicking button calls data and sends it to callback handler function.

    :param message: last Message instance in the chat
    :return: None
    """

    keyboard = types.InlineKeyboardMarkup()

    button1 = types.InlineKeyboardButton(text="1 miles", callback_data="d1")
    button2 = types.InlineKeyboardButton(text="3 miles", callback_data="d2")
    button3 = types.InlineKeyboardButton(text="5 miles", callback_data="d5")
    button4 = types.InlineKeyboardButton(text="7 miles", callback_data="d7")
    button5 = types.InlineKeyboardButton(text="7+ miles", callback_data="dinf")

    keyboard.row(button1, button2, button3, button4, button5)

    bot.send_message(chat_id=message.chat.id, text="🚗 Enter distance from city center:", reply_markup=keyboard)


def get_number(message: types.Message) -> None:
    """
    This function creates a keyboard with 3 rows and 3 columns
    With number buttons from 1 to 9 (including) and sends it to user's chat.

    Clicking button calls data and sends it to callback handler function.

    :param message: Last message (Message instance) in chat
    :return: None
    """

    keyboard = types.InlineKeyboardMarkup()

    for row in range(0, 3):
        button1 = types.InlineKeyboardButton(text=f"{row * 3 + 1}", callback_data=f"h{row * 3 + 1}")
        button2 = types.InlineKeyboardButton(text=f"{row * 3 + 2}", callback_data=f"h{row * 3 + 2}")
        button3 = types.InlineKeyboardButton(text=f"{row * 3 + 3}", callback_data=f"h{row * 3 + 3}")
        keyboard.row(button1, button2, button3)

    bot.send_message(chat_id=message.chat.id, text="🧳 Enter number of hotels:", reply_markup=keyboard,
                     disable_notification=False)


def get_answer(message: types.Message) -> None:
    """
    This function creates a keyboard with 1 rows and 2 columns
    With Yes-button and No-button and sends it to user's chat.

    Clicking button calls data and sends it to callback handler function.


    :param message: Last message (Message instance) in chat
    :return: None
    """

    keyboard = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton(text="Yes", callback_data="Yes")
    button2 = types.InlineKeyboardButton(text="No", callback_data="No")
    keyboard.add(button1, button2)

    bot.send_message(chat_id=message.chat.id, text="📷 Do you need photos:", reply_markup=keyboard,
                     disable_notification=False)


def get_photo_number(message: types.Message) -> None:
    """
    This function creates a keyboard with 1 rows and 3 columns
    With number buttons from 1 to 3 (including) and sends it to user's chat.

    Clicking button calls data and sends it to callback handler function.

    :param message: Last message (Message instance) in chat
    :return: None
    """

    keyboard = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton(text="1", callback_data="p1")
    button2 = types.InlineKeyboardButton(text="2", callback_data="p2")
    button3 = types.InlineKeyboardButton(text="3", callback_data="p3")

    keyboard.add(button1, button2, button3)

    bot.send_message(chat_id=message.chat.id, text="📸 How much: ", reply_markup=keyboard, disable_notification=False)


@logg.timer
def hotels_parser(chat_id: str) -> None:
    """
    This function finds hotels by user request (response_properties)

    1 Step. Function gets city id from Hotels API and saves in city_id
    2 Step. Function gets list of hotels from Hotels API and saves in hotels: List[dict]
    3 Step. Function gets list of photos for hotels from Hotels API and saves in photos: list[str]
    4 Step. Function transmits control to function "result_out"

    :param chat_id: chat id
    :return: None
    """

    print(f"\nInfo: {response_properties}")

    # Getting city id
    bot.send_message(chat_id=chat_id, text="✅ <b>REQUEST HAD ACCEPTED</b> | Please Wait", parse_mode="html",
                     disable_notification=False)
    city_querystring = {"query": f"{response_properties['city']}", "locale": "en_US", "currency": "USD"}
    city_response = json.loads(requests.request("GET", url_city, headers=headers, params=city_querystring).text)
    city_id = city_response["suggestions"][0]["entities"][0]["destinationId"]

    print(f"\nInfo: City id is {city_id}")

    # Getting list of hotels by city id
    hotels: List[dict] = list()
    price_range = response_properties["priceRange"]
    user_distance = response_properties["distance"]
    hotels_querystring = {"destinationId": f"{city_id}", "pageNumber": "1", "pageSize": "25", "checkIn": "2021-01-08",
                          "checkOut": "2021-01-15", "adults1": "1", "sortOrder": f"{response_properties['sortOrder']}",
                          "locale": "en_US", "currency": "USD"}
    hotels_response = json.loads(
        requests.request("GET", url=url_properties, headers=headers, params=hotels_querystring).text)

    for hotel in hotels_response["data"]["body"]["searchResults"]["results"]:
        if len(hotels) == response_properties["hotelCount"]:
            break

        try:
            result = re.match(pattern=r"\d+.\d{0,}", string=hotel["landmarks"][0]["distance"])
            distance = float(result.group(0))
        except KeyError:
            distance = 0.0

        try:
            curr_hotel_price = float(hotel["ratePlan"]["price"]["exactCurrent"])
        except KeyError:
            curr_hotel_price = 0.0

        if (0 < curr_hotel_price <= price_range) and (distance <= response_properties["distance"]):
            hotels.append(hotel)

    # Getting list of photos
    photos: List[str] = list()
    if response_properties["photoCount"] > 0:
        for hotel in hotels:
            hotel_id = hotel["id"]
            querystring = {"id": hotel_id}
            photo_response = json.loads(requests.request("GET", url_photos, headers=headers, params=querystring).text)

            for photo in range(response_properties["photoCount"]):
                try:
                    photos.append(photo_response["roomImages"][photo]["images"][photo]["baseUrl"].format(size="w"))
                except IndexError:
                    photos.append(photo_response["hotelImages"][photo]["baseUrl"].format(size="w"))

    result_out(chat_id=chat_id, hotels=hotels, photos=photos)


def result_out(chat_id: str, hotels: list, photos: list) -> None:
    """
     Function sends to chat a message with all information user requested

    :param chat_id: chat id
    :param hotels: list of hotels
    :param photos: list of photos
    :return: None
    """

    hotels_names = str()

    if hotels:
        # current photo index in photos: List(str)
        current_photo = 0

        for hotel in hotels:
            name = f"<b>{hotel['name']}</b>"
            url = f"<a href='https://ua.hotels.com/ho{hotel['id']}/'>click it</a>"

            try:
                price_value = hotel['ratePlan']['price']['current']
                total = round(response_properties["days"] * hotel['ratePlan']['price']['exactCurrent'], 1)
            except KeyError:
                price_value = "Price not available"
                total = "-"

            try:
                address = hotel['address']['streetAddress']
            except KeyError:
                address = "address not available"

            try:
                distance = f"<b>Distance from center</b>: {hotel['landmarks'][0]['distance']}"
            except KeyError:
                distance = "not available"

            caption = f"▫ {name}: {price_value} (total cost: {total} {response_properties['currency']})\n\n" \
                      f"▫ <b>Address</b>: {address}\n\n" \
                      f"▫ {distance}\n\n" \
                      f"▫ <b>Hotel page</b>: {url}"

            hotels_names += f"{name}\n"

            # list of temporary  photos
            temp_photos: List[types.InputMediaPhoto] = list()

            if response_properties["photoCount"] > 0:
                # only first photo might have caption
                temp_photos.append(types.InputMediaPhoto(photos[current_photo], caption=caption, parse_mode="html"))
                for photo in range(response_properties["photoCount"] - 1):
                    current_photo += 1
                    temp_photos.append(types.InputMediaPhoto(photos[current_photo], parse_mode="html"))

                bot.send_media_group(chat_id=chat_id, media=temp_photos, disable_notification=True)
                current_photo += 1
            else:
                bot.send_message(chat_id=chat_id, text=caption, parse_mode="html", disable_notification=True,
                                 disable_web_page_preview=True)

        # Insert to database
        to_data_base.append(hotels_names)

        try:
            database.db_utils.to_db(data=to_data_base)
        except Exception:
            pass

        to_data_base.clear()
    else:
        bot.send_message(chat_id=chat_id, text="❌ Nothing found for this require")


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call: types.CallbackQuery) -> None:
    """
    This function handles the callback query:

    1. If query from function get_number (data from user starts with 'h'):
        Step 1. callback_worker saves data to response_properties['hotelCount']
        Step 2. callback_worker edits input prompt message from call
        Step 3. callback_worker transmits control to function 'get_answer'

    2. If query from function get_answer (data is 'Yes' or 'No'):
        Step 1. callback_worker saves data to response_properties['photos']
        Step 2. callback_worker edits input prompt message from call
        Step 3. if data == 'Yes' callback_worker transmits control to function get_photo_number else is transmits
                control to function 'hotels_parser'

    3. If query from function get_photo_number (data from user starts with 'p'):
        Step 1. callback_worker saves data to response_properties['photoCount']
        Step 2. callback_worker edits input prompt message from call
        Step 3. callback_worker transmits control to function 'hotels_parser'

    4. If query from function get_price_range (data from user starts with '+' or '-'):
        If callback data include pattern [+-]\d+:
            Step 1. It adds to response_properties["priceRange"]
            Step 2. callback_worker edits input prompt message from call
        If callback data include 'OK':
            Step 1. callback_worker edits input prompt message from call
            Step 2. callback_worker transmits control to function 'get_distance'

    5. If query from function get_distance (data from user starts with 'd'):
        Step 1. callback_worker saves data to response_properties['distance']
        Step 2. callback_worker edits input prompt message from call
        Step 3. callback_worker transmits control to function 'hotels_parser'

    :param call: CallbackQuery instance
    :return: None
    """

    print(f"\nInfo: User input {call.data}")

    if call.data.startswith("h"):
        response_properties["hotelCount"] = int(call.data[1:])
        response_properties["hotelCount"] = int(call.data[1:])
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=f"✅ <b>NUMBER OF HOTELS</b> | Your choice: {call.data[1:]}", parse_mode="html")
        get_answer(call.message)
    elif call.data == "Yes" or call.data == "No":
        response_properties["photos"] = call.data
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=f"✅ <b>DO YOU NEED PHOTOS?</b> | Your choice: {call.data}", parse_mode="html")
        if call.data == "Yes":
            get_photo_number(call.message)
        else:
            response_properties["photoCount"] = 0
            hotels_parser(chat_id=call.message.chat.id)
    elif call.data.startswith("p"):
        response_properties["photoCount"] = int(call.data[1:])
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                              text=f"✅ <b>NUMBER OF PHOTOS</b> | Your choice: {call.data[1:]}", parse_mode="html")
        hotels_parser(chat_id=call.message.chat.id)
    elif call.data.startswith("+") or call.data.startswith("-"):
        if re.fullmatch(pattern=r"[+-]\d+", string=f"{call.data}"):
            response_properties["priceRange"] += int(call.data)
            if response_properties["priceRange"] < 0:
                response_properties["priceRange"] = 0
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id + 1,
                                  text=f"Your input: {response_properties['priceRange']} {response_properties['currency']}")
            bot.answer_callback_query(callback_query_id=call.id)
        else:
            bot.edit_message_text(
                text=f"✅ <b>MAX PRICE</b> | Your choice: {response_properties['priceRange']} {response_properties['currency']}",
                chat_id=call.message.chat.id, message_id=call.message.message_id, parse_mode="html")
            bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id + 1)
            get_distance(call.message)

    elif call.data.startswith("d"):
        response_properties["distance"] = float(call.data[1:])

        if call.data[1:] == "inf":
            miles = "7+"
        else:
            miles = call.data[1:]

        bot.edit_message_text(
            text=f"✅ <b>DISTANCE FROM CENTER</b> | Your choice: {miles} miles",
            chat_id=call.message.chat.id, message_id=call.message.message_id, parse_mode="html")
        get_number(call.message)
    else:
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.message_id)
