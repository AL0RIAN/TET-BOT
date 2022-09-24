#   Default Handlers
<ol>

##   <li>*start function (/start command)*</li>
				
    This function sends welcome message to user

    :param message: Message instance with text '/start'
    :return: None

##   <li>*helper function (/help command)*</li>

    This function sends list of commands to user

    :param message: Message instance with text '/help'
    :return: None
</ol>

#   Main Handlers

<ol>

##  <li>*history function (/history command)*</li>
	
    This function sends history of chat to user

    :param message: Message instance with text '/history'
    :return: None

##  <li>*price function (commands: /lowprice, /highprice, /bestdeal)*</li>

    This function sets functions route to find hotels

    If user entered lowprice: function sets sortOrder properties to 'PRICE' (from cheap to expensive)
    If user entered highprice: function sets sortOrder properties to 'PRICE_HIGHEST_FIRST' (from expensive to cheap)
    If user entered bestdeal: function sets sortOrder properties to 'BEST_DEAL' (PRICE + PRICE_HIGHEST_FIRST)

    And waits for a message from user with city name. Then it transmits control to Function get_name.

    :param message: Message instance with text '/lowprice' or '/highprice' or '/bestdeal'
    :return: None

</ol>


#   Callback Workers (for Utils)


<ol>

##  <li>*history_handler*</li>

    If ">" button was pressed the page changes to the next
    If "<" button was pressed the page changes to the previous

    :param call: CallbackQuery instance
    :return: None

##  <li>*calendar_handler*</li>
    
    If ">" button was pressed the calendar scrolls to the next month (creating a new calendar page)
    If "<" button was pressed the calendar scrolls to the previous month (creating a new calendar page)
    If the date button was pressed the information enters to calendar_date

    :param call: CallbackQuery instance
    :return: None

##  <li>*hotel_number_handler*</li>

    Step 1. callback_worker saves data to response_properties['hotelCount']
    Step 2. callback_worker edits input prompt message from call
    Step 3. callback_worker transmits control to function 'get_answer'

    :param call: CallbackQuery instance
    :return: None

##  <li>*get_answer_handler*</li>

    Step 1. callback_worker saves data to response_properties['photos']
    Step 2. callback_worker edits input prompt message from call
    Step 3. if data == 'Yes' callback_worker transmits control to function get_photo_number else is transmits
    control to function 'hotels_parser'

    :param call: CallbackQuery instance
    :return: None

##  <li>*photo_count_handler*</li>

    Step 1. callback_worker saves data to response_properties['photoCount']
    Step 2. callback_worker edits input prompt message from call
    Step 3. callback_worker transmits control to function 'hotels_parser'

    :param call: CallbackQuery instance
    :return: None

##  <li>*price_range_handler*</li>

    The handler accepts a call starting with min or max.

    If max, then the data is entered into response_properties["priceMax"].
    Else added to response_properties["priceMin"].

    If the handler receives "maxOK", then control is transferred to the get_distance function

    :param call: CallbackQuery instance
    :return: None

##  <li>*get_distance_handler*</li>

    Step 1. callback_worker saves data to response_properties['distance']
    Step 2. callback_worker edits input prompt message from call
    Step 3. callback_worker transmits control to function 'hotels_parser'

    :param call: CallbackQuery instance
    :return: None

</ol>

#   Utils

<ol>

##  <li>*get_days function*</li>
				
    This function gets number of days from user and transmits control to function get_name.

    This function generates a calendar page for the current month.

    :param message: Message instance with number of days
    :return: None
##   <li>*get_name function*</li> 

    This function gets city name from user

    If sortOrder is "PRICE" or "PRICE_HIGHEST_FIRST" it then transmits control to function get_number.
    Otherwise, it transmits control to function get_price_range.

    :param message: Message instance with city name
    :return: None

##   <li>*get_price_range function*</li> 

    This function gets the price range from the user

    :param message: Message instance with city name
    :return: None

##  <li>*get_distance function*</li> 

				
    This function creates a keyboard with 1 row and 5 columns
    With mileage buttons. Then function sends it to user's chat.

    Clicking button calls data and sends it to callback handler function.

    :param message: last Message instance in the chat
    :return: None

##  <li>*get_number function*</li>
	
    This function creates a keyboard with 3 rows and 3 columns
    With number buttons from 1 to 9 (including) and sends it to user's chat.

    Clicking button calls data and sends it to callback handler function.

    :param message: Last message (Message instance) in chat
    :return: None

##  <li>*get_answer function*</li>
				
    This function creates a keyboard with 1 rows and 2 columns
    With Yes-button and No-button and sends it to user's chat.

    Clicking button calls data and sends it to callback handler function.


    :param message: Last message (Message instance) in chat
    :return: None

##  <li>*get_photo_number function*</li>

    This function creates a keyboard with 1 rows and 3 columns
    With number buttons from 1 to 3 (including) and sends it to user's chat.

    Clicking button calls data and sends it to callback handler function.

    :param message: Last message (Message instance) in chat
    :return: None
    #hotels_parser

				
    This function finds hotels by user request (response_properties)

    1 Step. Function gets city id from Hotels API and saves in city_id
    2 Step. Function gets list of hotels from Hotels API and saves in hotels: List[dict]
    3 Step. Function gets list of photos for hotels from Hotels API and saves in photos: list[str]
    4 Step. Function transmits control to function "result_out"

    :param chat_id: chat id
    :return: None

##  <li>*result_out function*</li>

    Function sends to chat a message with all information user requested

    :param chat_id: chat id
    :param hotels: list of hotels
    :param photos: list of photos
    :return: None

</ol>