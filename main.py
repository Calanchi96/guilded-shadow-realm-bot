import asyncio
import datetime
import guilded
import requests
from bs4 import BeautifulSoup
import html_to_json

# Replace with your API token
BOT_API_TOKEN = "gapi_y0tLhumUQqOp/zi98RY3Sbx6BLwdsZc6rt0N59LwUC25lF/B86Fcox9XH9FRtvbvtGxizbZJZvhVlENjtaHU7A=="
CALNEDAR_CHANNEL_ID = "af4e94e0-7c01-44f8-9833-10aef8650e6c"
MAPLE_NEWS_CHANNEL_ID = "5c5ee2f9-ded6-4623-bd0a-c87d2228d3ea"
ANNOUNCEMENTS_CHANNEL_ID = "153f1e58-b35d-49de-9627-26788276f981"
SERVER_ID = "1ED3VKKl"

# Set up the client
client = guilded.Client()

# Set the command prefix
COMMAND_PREFIX = "!"

# Define the on_ready function
@client.event
async def on_ready():
    print(f"Logged in as {client.user}")

    # Schedule the first task to check for calendar events at 8 AM
    client.loop.create_task(asyncio.sleep((datetime.datetime.now().replace(hour=8, minute=0, second=0, microsecond=0) - datetime.datetime.now()).total_seconds()))
    client.loop.create_task(check_calendar())
    client.loop.create_task(check_maple_news())

# Define the check_calendar function
async def check_calendar():
    try:
        # Get the "calendar" channel
        server = await client.fetch_server(SERVER_ID)
        calendar_channel = await server.fetch_channel(CALNEDAR_CHANNEL_ID)
        announcements_channel = await server.fetch_channel(ANNOUNCEMENTS_CHANNEL_ID)

        # Get today's date
        today = datetime.date.today()

        # Get the calendar channel's events
        headers = {
            'Authorization': 'Bearer ' + BOT_API_TOKEN,
            'Accept': 'application/json',
            'Content-type': 'application/json',
        }

        response = requests.get('https://www.guilded.gg/api/v1/channels/' + CALNEDAR_CHANNEL_ID + '/events', headers=headers)

        message_title = 'Today you have ' + str(len(response.json().get("calendarEvents"))) + ' events'

        #send the first message
        headers = {
            'Authorization': f'Bearer {BOT_API_TOKEN}',
            'Accept': 'application/json',
            'Content-type': 'application/json',
        }

        await announcements_channel.send(message_title)

        # Iterate over the threads
        if len(response.json().get("calendarEvents")) > 0:
            for event in response.json().get("calendarEvents"):
                    #Get event title
                    event_title = event.get("name")
                    #Get event description
                    event_description = event.get("description")
                    #send the first message
                    await announcements_channel.send("name: " + event_title)
                    await announcements_channel.send("description: " + event_description)

        # Schedule the task to run again tomorrow morning
        client.loop.create_task(asyncio.sleep((datetime.datetime.now().replace(hour=8, minute=0, second=0, microsecond=0) + datetime.timedelta(days=1) - datetime.datetime.now()).total_seconds()))
    except Exception as e:
        print(f"Error in check_calendar function: {e}")

# Define the on_message function to handle commands
@client.event
async def check_maple_news():
    try:
        url = 'https://maplestory.nexon.net/news'

        response = requests.get(url)
        soup = BeautifulSoup(response.content, 'html.parser')

        # Find the div element with class name 'news-wrapper'
        news_div = soup.find('div', {'class': 'news-wrapper'})

        # Find all child div elements with class name 'news-item'
        if news_div:
            news_items = news_div.find_all('li', {'class': 'news-item'})

        # Loop through each news item and extract the title, date, and link
        if news_items and len(news_items) > 0:
            for news_item in news_items:
                headers = {
                    'Authorization': f'Bearer {BOT_API_TOKEN}',
                    'Accept': 'application/json',
                    'Content-type': 'application/json',
                }

                ann_url = f'https://www.guilded.gg/api/v1/channels/{MAPLE_NEWS_CHANNEL_ID}/announcements'

                title = news_item.find('h3').text.strip()
                text = news_item.find('p').text.strip()
                date = news_item.find('p', {'class': 'timestamp'}).text.strip()
                link = 'https://maplestory.nexon.net' + news_item.find('a')['href']
                myobj = {'title': 'Latest GMS News', 'content': title+ '\n' + text +'\n'+date+'\n'+link}

                post_announcement = requests.post(ann_url, headers = headers, json = myobj)

        client.loop.create_task(asyncio.sleep((datetime.datetime.now().replace(hour=8, minute=0, second=0, microsecond=0) + datetime.timedelta(days=1) - datetime.datetime.now()).total_seconds()))
    except Exception as e:
        print(f"Error in check_calendar function: {e}")

# Log in the client
client.run(BOT_API_TOKEN)