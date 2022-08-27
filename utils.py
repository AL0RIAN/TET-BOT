import re
import logg
import json
import requests
from constants import *
from telebot import types
from typing import List, Dict


@bot.message_handler(commands=["lowprice", "highprice", "bestdeal"])
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

    # TODO
    response_properties["priceRange"] = float("inf")
    response_properties["distance"] = float("inf")

    # Search will be done by price (from cheap to expensive)
    if message.text == "/lowprice":
        response_properties["sortOrder"] = "PRICE"
    elif message.text == "/highprice":
        # Search will be done by price (from expensive to cheap)
        response_properties["sortOrder"] = "PRICE_HIGHEST_FIRST"
    else:
        # TODO
        response_properties["sortOrder"] = "DISTANCE_FROM_LANDMARK"

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

        if response_properties["sortOrder"] == "DISTANCE_FROM_LANDMARK":
            get_price_range(message=message)
        else:
            get_number(message)


def get_price_range(message: types.Message) -> None:
    """
    # TODO

    :param message:
    :return:
    """

    response_properties["priceRange"] = 0
    keyboard = types.InlineKeyboardMarkup()

    for symbol in ("+", "-"):
        button1 = types.InlineKeyboardButton(text=f"{symbol}10", callback_data=f"{symbol}10")
        button2 = types.InlineKeyboardButton(text=f"{symbol}50", callback_data=f"{symbol}50")
        button3 = types.InlineKeyboardButton(text=f"{symbol}100", callback_data=f"{symbol}100")
        button4 = types.InlineKeyboardButton(text=f"{symbol}250", callback_data=f"{symbol}250")
        keyboard.row(button1, button2, button3, button4)

    ok_button = types.InlineKeyboardButton(text="OK", callback_data="+OK")
    keyboard.row(ok_button)

    bot.send_message(chat_id=message.chat.id, text="💵 Enter price range:", reply_markup=keyboard)
    bot.send_message(chat_id=message.chat.id,
                     text=f"Your input: {response_properties['priceRange']} {response_properties['currency']}")


def get_distance(message: types.Message) -> None:
    """

    :param message:
    :return:
    """

    keyboard = types.InlineKeyboardMarkup()

    button1 = types.InlineKeyboardButton(text="1 mill", callback_data="d1")
    button2 = types.InlineKeyboardButton(text="3 mill", callback_data="d2")
    button3 = types.InlineKeyboardButton(text="5 mill", callback_data="d5")
    button4 = types.InlineKeyboardButton(text="7 mill", callback_data="d7")
    button5 = types.InlineKeyboardButton(text="7+ mill", callback_data="dinf")

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

    print(f"\nInfo: City id is {city_id}")

    # Getting list of hotels by city id
    hotels_querystring = {"destinationId": f"{city_id}", "pageNumber": "1", "pageSize": "25", "checkIn": "2022-01-08",
                          "checkOut": "2022-01-15", "adults1": "1", "sortOrder": f"{response_properties['sortOrder']}",
                          "locale": "en_US", "currency": "USD"}
    hotels_response = json.loads(
        requests.request("GET", url_properties, headers=headers, params=hotels_querystring).text)

    # TODO
    hotels: List[dict] = list()

    # правая граница цены
    right = response_properties["priceRange"]

    print(f"\nInfo: {response_properties}")

    for hotel in hotels_response["data"]["body"]["searchResults"]["results"]:
        if len(hotels) == response_properties["hotelCount"]:
            break

        # дистанция от центра
        try:
            result = re.match(pattern=r"\d+.\d{0,}", string=hotel["landmarks"][0]["distance"])
            distance = float(result.group(0))
        except KeyError:
            distance = 0.0

        # ценна данного отеля и проверка на её наличие
        # Если у отеля известна цена ... TODO
        try:
            curr_hotel_price = float(hotel["ratePlan"]["price"]["exactCurrent"])
        except KeyError:
            curr_hotel_price = 0.0

        # дистанция, заданная пользователем
        user_distance = response_properties["distance"]

        print(f'HOTEL: {hotel["name"]}')
        print(f"DISTANCE: {distance}")
        print(f"Current hotel price: {curr_hotel_price}\n")

        if (0 < curr_hotel_price <= right) and (distance <= response_properties["distance"]):
            hotels.append(hotel)
            print("YES")
        print()

    # TODO ЕСЛИ hotels 0, то писать об этом юзеру
    print("Вышел из поиска отелей")

    photos: List[dict] = list()
    for hotel in hotels:
        # id текущего отеля
        hotel_id = hotel["id"]

        # информация для запроса
        querystring = {"id": hotel_id}
        photo_response = json.loads(requests.request("GET", url_photos, headers=headers, params=querystring).text)

        for photo in range(response_properties["photoCount"]):
            # обработчик нужен, поскольку не у всех отелей есть фото комнат
            try:
                photos.append(photo_response["roomImages"][photo]["images"][photo]["baseUrl"].format(size="w"))
            except IndexError:
                photos.append(photo_response["hotelImages"][photo]["baseUrl"].format(size="w"))

    print("Вышел из поиска фото")
    print(f"Размер отелей: {len(hotels)}")
    print(f"Размер фото: {len(photos)}")
    print(photos)
    result_out(chat_id=chat_id, hotels=hotels, photos=photos)


def result_out(chat_id: str, hotels: list, photos: list) -> None:
    # индекс текущего фото
    current_photo = 0

    for hotel in hotels:
        # если у отеля известна цена
        if hotel.get("ratePlan"):
            caption = f"<b>{hotel['name']}</b>: {hotel['ratePlan']['price']['current']}\n\n" \
                      f"<b>Address</b>: {hotel['address']['streetAddress']}"
        # иначе пишем, что цена неизвестна
        else:
            caption = f"<b>{hotel['name']}</b>: Price not available\n\n" \
                      f"Address - {hotel['address']['streetAddress']}"

        # список временных фото (для текущего отеля)
        temp_photos: List[types.InputMediaPhoto] = list()

        # если пользователю нужны фото
        if response_properties["photoCount"] > 0:
            # только первое фото должно иметь описание (caption)
            temp_photos.append(types.InputMediaPhoto(photos[current_photo], caption=caption, parse_mode="html"))
            for photo in range(response_properties["photoCount"] - 1):
                current_photo += 1
                temp_photos.append(types.InputMediaPhoto(photos[current_photo], parse_mode="html"))

        # отправляем текущие фотографии с описанием
        bot.send_media_group(chat_id=chat_id, media=temp_photos, disable_notification=True)
        current_photo += 1
    else:
        bot.send_message(chat_id=chat_id, text="❌ Nothing found for this require")


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
    elif call.data.startswith("+") or call.data.startswith("-"):
        if re.fullmatch(pattern=r"[+-]\d+", string=f"{call.data}"):
            response_properties["priceRange"] += int(call.data)
            if response_properties["priceRange"] < 0:
                response_properties["priceRange"] = 0
            bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id + 1,
                                  text=f"Your input: {response_properties['priceRange']} {response_properties['currency']}")
        else:
            # TODO сделать комментарии
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

# TODO обновлять constants
# TODO файл с командами бота и файл БД и с записью инфы пользователя
# TODO убрать проверку на отсутствие цены
# TODO вывод дистанции в инфе
