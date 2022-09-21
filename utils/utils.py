import re
import json
import requests
import database
import calendar
from typing import List
from telebot import types
from debugging import logg
from config_data.constants import *


def get_days(chat_id: str) -> None:
    """
    This function gets number of days from user and transmits control to function get_name.

    This function generates a calendar page for the current month.

    :param chat_id: chat id
    :return: None
    """

    now_day = datetime.datetime.now()
    year = now_day.year
    month = now_day.month

    keyboard = types.InlineKeyboardMarkup(row_width=7)

    # Current year and current month
    page = types.InlineKeyboardButton(text=f"{calendar.month_name[month]}, {str(year)}", callback_data="0")
    keyboard.row(page)

    # Days of week
    day_names: List[types.InlineKeyboardButton] = list()
    for number in range(7):
        day = types.InlineKeyboardButton(text=f"{calendar.day_abbr[number]}", callback_data=f"0")
        day_names.append(day)

    keyboard.add(day_names[0], day_names[1], day_names[2], day_names[3], day_names[4], day_names[5], day_names[6])

    # Days of month
    for week in calendar.monthcalendar(year, month):
        row: List[types.InlineKeyboardButton] = list()
        for day in week:
            if day == 0:
                row.append(types.InlineKeyboardButton(text=" ", callback_data="0"))

            elif f"{now_day.day}.{now_day.month}.{now_day.year}" == f"{day}.{month}.{year}":
                row.append(types.InlineKeyboardButton(text=f"{day}", callback_data=f"c{year}-{month}-{day}"))

            else:
                row.append(types.InlineKeyboardButton(text=str(day), callback_data=f"c{year}-{month}-{day}"))

        keyboard.add(row[0], row[1], row[2], row[3], row[4], row[5], row[6])

    keyboard.add(types.InlineKeyboardButton(text="<", callback_data="c<"),
                 types.InlineKeyboardButton(text=">", callback_data="c>"))

    bot.send_message(chat_id=chat_id, text="🗓 Enter your booking date:", reply_markup=keyboard)


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
        bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id - 1,
                              text=f"✅ <b>CITY NAME</b> | Your choice: {message.text}", parse_mode="html")

        if response_properties["sortOrder"] == "BEST_SELLER":
            get_min_price(message=message)
        else:
            get_number(message)


def get_min_price(message: types.Message) -> None:
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

    keyboard = types.InlineKeyboardMarkup(row_width=2)

    # button callback_data in first row: +X, where X is a number
    # button callback_data in second row: -X, where X is a number
    for symbol in ("+", "-"):
        row: List[types.InlineKeyboardButton] = list()
        for number in (10, 50, 100, 250, 500):
            button = types.InlineKeyboardButton(text=f"{symbol}{number}", callback_data=f"min{symbol}{number}")
            row.append(button)
        keyboard.row(row[0], row[1], row[2], row[3], row[4])

    ok_button = types.InlineKeyboardButton(text="OK", callback_data="minOK")
    keyboard.row(ok_button)

    bot.send_message(chat_id=message.chat.id, text="💵 Enter min price:", reply_markup=keyboard)
    bot.send_message(chat_id=message.chat.id,
                     text=f"Your input: {response_properties['priceRange']} {response_properties['currency']}")


def get_max_price(message: types.Message) -> None:
    """
    This function creates a keyboard with 2 rows and 5 columns
    With number buttons and OK-button.
    Then function sends it to user's chat.

    Clicking button calls data and sends it to callback handler function.

    :param message: Message instance with city name
    :return: None
    """

    # start price
    response_properties["priceMax"] = 0

    keyboard = types.InlineKeyboardMarkup(row_width=2)

    # button callback_data in first row: +X, where X is a number
    # button callback_data in second row: -X, where X is a number
    for symbol in ("+", "-"):
        row: List[types.InlineKeyboardButton] = list()
        for number in (10, 50, 100, 250, 500):
            button = types.InlineKeyboardButton(text=f"{symbol}{number}", callback_data=f"max{symbol}{number}")
            row.append(button)
        keyboard.row(row[0], row[1], row[2], row[3], row[4])

    ok_button = types.InlineKeyboardButton(text="OK", callback_data="maxOK")
    keyboard.row(ok_button)

    bot.send_message(chat_id=message.chat.id, text="💵 Enter max price:", reply_markup=keyboard)
    bot.send_message(chat_id=message.chat.id,
                     text=f"Your input: {response_properties['priceMax']} {response_properties['currency']}")


def get_distance(message: types.Message) -> None:
    """
    This function creates a keyboard with 1 row and 5 columns
    With mileage buttons. Then function sends it to user's chat.

    Clicking button calls data and sends it to callback handler function.

    :param message: last Message instance in the chat
    :return: None
    """

    keyboard = types.InlineKeyboardMarkup()

    row: List[types.InlineKeyboardButton] = list()

    for number in range(1, 8, 2):
        button = types.InlineKeyboardButton(text=f"{number} miles", callback_data=f"d{number}")
        row.append(button)

    last_button = types.InlineKeyboardButton(text="7+ miles", callback_data="dinf")

    keyboard.row(row[0], row[1], row[2], row[3], last_button)

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

    for number in range(3):
        row: List[types.InlineKeyboardButton] = list()
        for col in range(1, 4):
            button = types.InlineKeyboardButton(text=f"{number * 3 + col}", callback_data=f"h{number * 3 + col}")
            row.append(button)
        keyboard.row(row[0], row[1], row[2])

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

    button: List[types.InlineKeyboardButton] = list()
    for number in range(1, 4):
        button.append(types.InlineKeyboardButton(text=f"{number}", callback_data=f"p{number}"))
    keyboard.row(button[0], button[1], button[2])

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
    print(f"\nInfo: {calendar_data}")

    # Getting city id
    bot.send_message(chat_id=chat_id, text="✅ <b>REQUEST HAD ACCEPTED</b> | Please Wait", parse_mode="html",
                     disable_notification=False)
    city_querystring = {"query": f"{response_properties['city']}", "locale": "en_US", "currency": "USD"}
    city_response = json.loads(requests.request("GET", url_city, headers=headers, params=city_querystring).text)
    city_id = city_response["suggestions"][0]["entities"][0]["destinationId"]

    print(f"\nInfo: City id is {city_id}")

    # Getting list of hotels by city id
    hotels: List[dict] = list()
    min_price = response_properties["priceMin"]
    max_price = response_properties["priceMax"]
    hotels_querystring = {"destinationId": f"{city_id}", "pageNumber": "1", "pageSize": "25",
                          "checkIn": f"{calendar_data['from']}",
                          "checkOut": f"{calendar_data['to']}", "adults1": "1",
                          "sortOrder": f"{response_properties['sortOrder']}",
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

        if (min_price < curr_hotel_price <= max_price) and (distance <= response_properties["distance"]):
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

        print(f"Info: to database: {to_data_base}")

        try:
            database.db_utils.to_db(data=to_data_base)
        except Exception:
            pass

        to_data_base.clear()
    else:
        bot.send_message(chat_id=chat_id, text="❌ Nothing found for this require")
