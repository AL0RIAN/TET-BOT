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
    If user entered bestdeal: function sets sortOrder properties to 'DISTANCE_FROM_LANDMARK'

    And waits for a message from user with city name. Then it transmits control to Function get_name.

    :param message: Message instance with text '/lowprice'
    :return: None

</ol>


#   Utils

<ol>

##  <li>*get_days function*</li>
				
    This function gets number of days from user and transmits control to function get_name.

    :param message: Message instance with number of days
    :return: None
##   <li>*get_name function*</li> 

    This function gets city name from user

    If sortOrder is "PRICE" or "PRICE_HIGHEST_FIRST" it then transmits control to function get_number.
    Otherwise, it transmits control to function get_price_range.

    :param message: Message instance with city name
    :return: None

##   <li>*get_price_range function*</li> 

				
    This function creates a keyboard with 2 rows and 5 columns
    With number buttons and OK-button.
    Then function sends it to user's chat.

    Clicking button calls data and sends it to callback handler function.

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

##   <li>*callback_worker*</li>

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

</ol>
