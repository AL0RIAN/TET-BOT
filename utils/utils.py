import re
import json
import threading
import time
import requests
import database
from threading import Thread, Lock
from typing import List
from telebot import types
from debugging import logg
from . import InlineKeyboards
from config_data.constants import *

lock = Lock()
stop_animation = False
load_dotenv()


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

        if response_properties["sortOrder"] == "RECOMMENDED":
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


def loading_animation(chat_id: int, msg_id: int):
    global stop_animation
    symbols = ['|', '/', '-', '\\']
    while not stop_animation:
        for symbol in symbols:
            bot.edit_message_text(chat_id=chat_id, message_id=msg_id,
                                  text=f"⌛ <b>REQUEST HAS BEEN ACCEPTED</b> {symbol} Please Wait", parse_mode="html")
            time.sleep(0.5)

    bot.edit_message_text(chat_id=chat_id, message_id=msg_id,
                          text=f"✅ <b>REQUEST HAS BEEN PROCESSED</b>", parse_mode="html")


@logg.timer
def hotels_parser(chat_id: int) -> None:
    """
    This function finds hotels by user request (response_properties)

    1 Step. Function gets city id from Hotels API and saves in city_id
    2 Step. Function gets list of hotels from Hotels API and saves in hotels: List[dict]
    3 Step. Function gets list of photos for hotels from Hotels API and saves in photos: list[str]
    4 Step. Function transmits control to function "result_out"

    :param chat_id: chat id
    :return: None
    """
    global stop_animation
    stop_animation = False
    msg = bot.send_message(chat_id=chat_id, text="⌛ <b>THE REQUEST HAS BEEN ACCEPTED</b> | Please Wait",
                           parse_mode="html",
                           disable_notification=False)

    animation_thread = threading.Thread(target=loading_animation, args=(chat_id, msg.message_id))
    animation_thread.start()

    logg.logger(text=f"{response_properties}", report_type="debug")
    logg.logger(text=f"{calendar_data}", report_type="debug")

    city_querystring = {"q": f"{response_properties['city']}", "locale": "en_US", "langid": "1033",
                        "siteid": "300000001"}

    city_response = json.loads(requests.get(url_city, headers=headers, params=city_querystring).text)

    # Getting city id
    city_id = city_response["sr"][0]["gaiaId"]

    logg.logger(text=f"City id is {city_id}", report_type="debug")

    # Getting list of hotels by city id
    min_price = response_properties["priceMin"]
    max_price = response_properties["priceMax"]
    hotels: List[dict] = list()
    sort_order = response_properties["sortOrder"]

    payload = {
        "currency": "USD",
        "eapid": 1,
        "locale": "en_US",
        "siteId": 300000001,
        "destination": {"regionId": str(city_id)},
        "checkInDate": {
            "day": datetime.datetime.strptime(calendar_data["from"], "%Y-%m-%d").day,
            "month": datetime.datetime.strptime(calendar_data["from"], "%Y-%m-%d").month,
            "year": datetime.datetime.strptime(calendar_data["from"], "%Y-%m-%d").year
        },
        "checkOutDate": {
            "day": datetime.datetime.strptime(calendar_data["to"], "%Y-%m-%d").day,
            "month": datetime.datetime.strptime(calendar_data["to"], "%Y-%m-%d").month,
            "year": datetime.datetime.strptime(calendar_data["to"], "%Y-%m-%d").year
        },
        "rooms": [
            {
                "adults": 1,
            }
        ],
        "resultsStartingIndex": 0,
        "resultsSize": 200,
        "sort": sort_order if sort_order in ("RECOMMENDED", "PRICE_LOW_TO_HIGH") else "PRICE_LOW_TO_HIGH"
    }

    if sort_order == "RECOMMENDED":
        payload["criteria"] = {
            "price": {
                "max": max_price,
                "min": min_price
            }}

    headers["Content-Type"] = "application/json"
    response = requests.post(url=url_properties, headers=headers, json=payload)
    hotels_response = json.loads(response.text)

    for hotel in hotels_response["data"]["propertySearch"]["properties"]:
        if len(hotels) == response_properties["hotelCount"]:
            break

        try:
            distance = hotel["destinationInfo"]["distanceFromDestination"]["value"]
            price = hotel["price"]["lead"]["amount"]
        except KeyError:
            price = 0.0
            distance = 0.0

        if sort_order == "RECOMMENDED":
            if (distance <= response_properties["distance"]) and (min_price <= price <= max_price):
                hotels.append(hotel)
        else:
            hotels.append(hotel)

    if sort_order == "PRICE_HIGHEST_FIRST":
        hotels.reverse()

    result_out(chat_id=chat_id, hotels=hotels)
    stop_animation = True
    animation_thread.join()


def send_hotel_with_photo(chat_id: int, hotel_id: int, caption: str, photo_count: int) -> None:
    headers["Content-Type"] = "application/json"
    payload = {
        "currency": "USD",
        "eapid": 1,
        "locale": "en_US",
        "siteId": 300000001,
        "propertyId": hotel_id
    }

    response_data = json.loads(
        requests.post(url="https://hotels4.p.rapidapi.com/properties/v2/get-summary",
                      json=payload,
                      headers=headers).text)

    current_photo = 0

    # list of temporary  photos
    hotel_photos: List[types.InputMediaPhoto] = list()

    images_grouped = response_data["data"]["propertyInfo"]["propertyGallery"]["imagesGrouped"][0]

    for photo in images_grouped["images"]:
        if current_photo == 0:
            hotel_photos.append(types.InputMediaPhoto(photo["image"]["url"], caption=caption, parse_mode="html"))
        else:
            hotel_photos.append(types.InputMediaPhoto(photo["image"]["url"], parse_mode="html"))

        current_photo += 1
        if current_photo >= photo_count:
            break

    bot.send_media_group(chat_id=chat_id, media=hotel_photos, disable_notification=True)


def result_out(chat_id: int, hotels: list) -> None:
    """
    Function sends to chat a message with all information user requested

    :param chat_id: chat id
    :param hotels: list of hotels
    :return: None
    """

    hotels_names = str()
    hotels_data = dict()

    if hotels:
        # current photo index in photos: List(str)
        for hotel in hotels:
            hotels_data[hotel["id"]] = dict()
            name = f"<b>{hotel['name']}</b>"
            url = f"<a href='{os.getenv('BASIC_URL')}.h{hotel['id']}.Hotel-Information/'>click it</a>"

            try:
                price_value = round(hotel["price"]["lead"]["amount"], 1)
            except KeyError:
                price_value = "Price not available"

            try:
                payload = {
                    "currency": "USD",
                    "eapid": 1,
                    "locale": "en_US",
                    "siteId": 300000001,
                    "propertyId": hotel["id"]
                }
                headers["Content-Type"] = "application/json"
                hotel_details = json.loads(
                    requests.post(url="https://hotels4.p.rapidapi.com/properties/v2/get-summary",
                                  json=payload,
                                  headers=headers).text)
                address = hotel_details["data"]["propertyInfo"]["summary"]["location"]["address"]["addressLine"]
            except KeyError:
                address = "address not available"

            try:
                distance = (f"<b>Distance from center</b>: "
                            f"{hotel['destinationInfo']['distanceFromDestination']['value']}")
            except KeyError:
                distance = "not available"

            caption = f"▫ {name}\n\n" \
                      f"▫ <b>Price</b>: {price_value} {response_properties['currency']}\n\n" \
                      f"▫ <b>Address</b>: {address}\n\n" \
                      f"▫ {distance} mi\n\n" \
                      f"▫ <b>Hotel page</b>: {url}"

            hotels_names += f"{name}\n"

            hotels_data[hotel["id"]]["caption"] = caption
    else:
        bot.send_message(chat_id=chat_id, text="❌ Nothing found for this require")

    if response_properties["photoCount"] > 0:
        threads = list()
        for hotel_id in hotels_data:
            thread = Thread(target=send_hotel_with_photo, args=(chat_id,
                                                                hotel_id,
                                                                hotels_data[hotel_id]["caption"],
                                                                response_properties["photoCount"]))
            thread.start()
            threads.append(thread)

        for thread in threads:
            thread.join()
    else:
        for hotel_id in hotels_data:
            bot.send_message(chat_id=chat_id, text=hotels_data[hotel_id]["caption"], parse_mode="html",
                             disable_notification=True,
                             disable_web_page_preview=True)

    # Insert to database
    to_data_base.append(hotels_names)

    logg.logger(text=f"To database - {to_data_base}", report_type="debug")

    try:
        database.db_utils.to_db(data=to_data_base)
    except Exception:
        pass
    to_data_base.clear()
