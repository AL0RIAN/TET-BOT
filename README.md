## Tech Stack
- **pyTelegramBotAPI**
- **RapidAPI Hotels 4**

## Bot Commands:
- /help - list of available commands
- /lowprice - search for hotels sorted by lowest price
- /highprice - search for hotels sorted by highest price
- /bestdeal - search for hotels sorted by distance from the center and price
- /history - view search history

## Examples
<p align="center">
  <img src=https://github.com/user-attachments/assets/695e2693-2ba5-4dfe-9d5d-29eb775eb5ef width="800" alt="demo1" />
  <br>
  <i>Lowprice & Highprice search demo</i>
</p>
<p align="center">
  <img src=https://github.com/user-attachments/assets/cbe80130-4567-417f-ab87-1513482249f4 width="800" alt="demo1" />
  <br>
  <i>Bestdeal search demo</i>
</p>

## How to run

### Step 1: Configure Environment Variables

Create a `.env` file in the root directory of the project and add the necessary environment variables:
```
BASIC_URL=https://www.expedia.com/
BOT_KEY=YOUR_TELEGRAM_BOT_KEY
RAPID_API_KEY=YOUR_RAPID_API_KEY
```

### Step 2: Install Requirements:

```
pip install -r requirements.txt 
```

### Step 3: Running the Bot:

```
python3 main.py
```
