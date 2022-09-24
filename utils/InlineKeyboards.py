import calendar
from typing import List
from telebot import types
from config_data.constants import *


def calculator(flag: str) -> types.InlineKeyboardMarkup:
    # start price
    response_properties["priceRange"] = 0

    keyboard = types.InlineKeyboardMarkup(row_width=2)

    # button callback_data in first row: +X, where X is a number
    # button callback_data in second row: -X, where X is a number
    for symbol in ("+", "-"):
        row: List[types.InlineKeyboardButton] = list()
        for number in (10, 50, 100, 250, 500):
            button = types.InlineKeyboardButton(text=f"{symbol}{number}", callback_data=f"{flag}{symbol}{number}")
            row.append(button)
        keyboard.row(row[0], row[1], row[2], row[3], row[4])

    ok_button = types.InlineKeyboardButton(text="OK", callback_data=f"{flag}OK")
    keyboard.row(ok_button)

    return keyboard


def calendar_maker(month: int, year: int) -> types.InlineKeyboardMarkup:
    now_day = datetime.datetime.now()
    keyboard = types.InlineKeyboardMarkup(row_width=7)

    # Current year and current month
    page = types.InlineKeyboardButton(
        text=f"{calendar.month_name[month]}, {str(year)}", callback_data="0")
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
                                                      callback_data=f"c{calendar_data['year']}-{calendar_data['month']}-{day}"))
            else:
                row.append(types.InlineKeyboardButton(text=str(day),
                                                      callback_data=f"c{calendar_data['year']}-{calendar_data['month']}-{day}"))

        keyboard.add(row[0], row[1], row[2], row[3], row[4], row[5], row[6])

    keyboard.add(types.InlineKeyboardButton(text="<", callback_data="c<"),
                 types.InlineKeyboardButton(text=">", callback_data="c>"))

    return keyboard


def history_book(data: list, current_page: int = 0) -> tuple:
    keyboard = types.InlineKeyboardMarkup()
    button1 = types.InlineKeyboardButton(text="<", callback_data="H<")
    button2 = types.InlineKeyboardButton(text=">", callback_data="H>")
    button3 = types.InlineKeyboardButton(text="OK", callback_data="Hok")
    keyboard.add(button1, button3, button2)

    head = f"📄 Record #{current_page + 1} - {data[current_page][0]}: {data[current_page][1]}:"
    hotels_list = data[current_page][2].split("\n")[:-1]
    hotels = "".join(list(map(lambda x: f"\n{hotels_list.index(x) + 1}. {x}", hotels_list)))
    text = f"{head} \n{hotels}\n"

    return text, keyboard
