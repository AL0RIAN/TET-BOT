import re
import json
import requests
import database
from typing import List
from telebot import types
from debugging import logg
from . import InlineKeyboards
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

    keyboard = InlineKeyboards.calendar_maker(month=month, year=year)
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
        logg.logger(text="User input incorrect value", report_type="error")
    else:
        logg.logger(text=f"User input {message.text}", report_type="debug")
        response_properties["city"] = message.text
        bot.delete_message(chat_id=message.chat.id, message_id=message.message_id)
        bot.edit_message_text(chat_id=message.chat.id, message_id=message.message_id - 1,
                              text=f"✅ <b>CITY NAME</b> | Your choice: {message.text}", parse_mode="html")

        if response_properties["sortOrder"] == "BEST_DEAL":
            get_price_range(message=message)
        else:
            get_number(message)


def get_price_range(message: types.Message) -> None:
    """
    This function gets the price range from the user

    :param message: Message instance with city name
    :return: None
    """

    response_properties["priceMax"] = 0

    keyboard = InlineKeyboards.calculator(flag="min")
    bot.send_message(chat_id=message.chat.id, text=f"💵 Enter min price:", reply_markup=keyboard)
    bot.send_message(chat_id=message.chat.id, text=f"Your input: {response_properties['priceMin']} USD")


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

    logg.logger(text=f"{response_properties}", report_type="debug")
    logg.logger(text=f"{calendar_data}", report_type="debug")

    # Getting city id
    bot.send_message(chat_id=chat_id, text="✅ <b>REQUEST HAD ACCEPTED</b> | Please Wait", parse_mode="html",
                     disable_notification=False)
    city_querystring = {"query": f"{response_properties['city']}", "locale": "en_US", "currency": "USD"}

    city_response = json.loads(requests.request("GET", url_city, headers=headers, params=city_querystring).text)

    city_id = city_response["suggestions"][0]["entities"][0]["destinationId"]

    logg.logger(text=f"City id is {city_id}", report_type="debug")

    # Getting list of hotels by city id
    min_price = response_properties["priceMin"]
    max_price = response_properties["priceMax"]
    hotels: List[dict] = list()
    sort_order = response_properties["sortOrder"]

    for response in ("PRICE", "PRICE_HIGHEST_FIRST"):
        if sort_order == response or sort_order == "BEST_DEAL":
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

        logg.logger(text=f"To database - {to_data_base}", report_type="debug")

        try:
            database.db_utils.to_db(data=to_data_base)
        except Exception:
            pass

        to_data_base.clear()
    else:
        bot.send_message(chat_id=chat_id, text="❌ Nothing found for this require")
