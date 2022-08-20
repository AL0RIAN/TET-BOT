import re
import logg
import json
import requests
from constants import *
from telebot import types
from typing import List, Dict


@bot.message_handler(commands=["lowprice", "highprice"])
def price(message: types.Message) -> None:
    """
    This function sets functions route to find hotels

    If user entered lowprice: function sets sortOrder properties to 'PRICE' (from cheap to expensive)
    If user entered highprice: function sets sortOrder properties to 'PRICE_HIGHEST_FIRST' (from expensive to cheap)
    And waits for a message from user with city name. Then it transmits control to
    Function get_name.

    :param message: Message instance with text '/lowprice'
    :return: None
    """

    # Search will be done by price (from cheap to expensive)
    if message.text == "/lowprice":
        response_properties["sortOrder"] = "PRICE"
    else:
        # Search will be done by price (from expensive to cheap)
        response_properties["sortOrder"] = "PRICE_HIGHEST_FIRST"

    msg = bot.send_message(chat_id=message.chat.id, text="🌆 Enter city name:", disable_notification=False)
    bot.register_next_step_handler(msg, get_name)


def get_name(message: types.Message) -> None:
    """
    This function gets city name from user
    It then transmits control to function get_number.

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
        bot.send_message(chat_id=message.chat.id, text=f"✅ <b>CITY NAME</b> | Your choice: {message.text}",
                         parse_mode="html", disable_notification=False)
        get_number(message)


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
    3 Step. Function makes dictionary where key is room id and value is picture object
    4 Step. Function sends to chat a message with all information user requested

    :param chat_id: chat id
    :return: None
    """

    # Getting city id
    bot.send_message(chat_id=chat_id, text="✅ <b>REQUEST HAD ACCEPTED</b> | Please Wait", parse_mode="html",
                     disable_notification=False)
    city_querystring = {"query": f"{response_properties['city']}", "locale": "en_US", "currency": "USD"}
    city_response = json.loads(requests.request("GET", url_city, headers=headers, params=city_querystring).text)
    city_id = city_response["suggestions"][0]["entities"][0]["destinationId"]

    # Getting list of hotels by city id
    hotels_querystring = {"destinationId": f"{city_id}", "pageNumber": "1", "pageSize": "25", "checkIn": "2022-01-08",
                          "checkOut": "2022-01-15", "adults1": "1", "sortOrder": f"{response_properties['sortOrder']}",
                          "locale": "en_US", "currency": "USD"}
    hotels_response = json.loads(
        requests.request("GET", url_properties, headers=headers, params=hotels_querystring).text)

    hotels: List[dict] = list()
    for hotel in range(response_properties["hotelCount"]):
        hotels.append(hotels_response["data"]["body"]["searchResults"]["results"][hotel])

    # Getting dictionary of hotels pictures
    photos: Dict = dict()
    for photo in range(response_properties["hotelCount"]):
        hotel_id = hotels[photo]["id"]
        querystring = {"id": hotel_id}
        photo_response = json.loads(requests.request("GET", url_photos, headers=headers, params=querystring).text)

        for number in range(response_properties["photoCount"]):
            if hotel_id not in photos:
                photos[hotel_id] = list()
            try:
                photos[hotel_id].append(
                    photo_response["roomImages"][number]["images"][number]["baseUrl"].format(size="w"))
            except IndexError:
                photos[hotel_id].append(photo_response["hotelImages"][number]["baseUrl"].format(size="w"))

    # Result output
    for hotel in range(len(hotels)):
        temp_photos = list()
        if hotel == response_properties["hotelCount"]:
            break
        elif hotels[hotel].get("ratePlan"):
            caption = f"<b>{hotels[hotel]['name']}</b>: {hotels[hotel]['ratePlan']['price']['current']}\n\n" \
                      f"<b>Address</b>: {hotels[hotel]['address']['streetAddress']}"
        else:
            caption = f"<b>{hotels[hotel]['name']}</b>: Price not available\n\n" \
                      f"Address - {hotels[hotel]['address']['streetAddress']}"

        if response_properties["photoCount"] > 0:
            for photo in photos[hotels[hotel]["id"]]:
                if len(temp_photos) == 0:
                    temp_photos.append(types.InputMediaPhoto(photo, caption=caption, parse_mode="html"))
                else:
                    temp_photos.append(types.InputMediaPhoto(photo, parse_mode="html"))

            bot.send_media_group(chat_id=chat_id, media=temp_photos, disable_notification=True)
        else:
            bot.send_message(chat_id=chat_id, text=caption, disable_notification=True, parse_mode="html")


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call: types.CallbackQuery) -> None:
    """
    This function handles the callback query:

    1. If query from function get_number (data from user starts with 'h'):
        Step 1. callback_worker saves data to response_properties['hotelCount']
        Step 2. callback_worker edits input prompt message from call
        Step 3. callback_worker transmits control to function get_answer
    2. If query from function get_answer (data is 'Yes' or 'No'):
        Step 1. callback_worker saves data to response_properties['photos']
        Step 2. callback_worker edits input prompt message from call
        Step 3. if data == 'Yes' callback_worker transmits control to function get_photo_number else is transmits
                control to function hotels_parser
    3. If query from function get_photo_number (data from user starts with 'p'):
        Step 1. callback_worker saves data to response_properties['photoCount']
        Step 2. callback_worker edits input prompt message from call
        Step 3. callback_worker transmits control to function hotels_parser

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
