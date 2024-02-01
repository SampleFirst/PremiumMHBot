import pyrogram
from pyrogram import Client, filters

# Replace with your actual API key
api_key = "YOUR_WEATHER_API_KEY"

@Client.on_message(filters.command("weather"))
async def get_weather(client, message):
   try:
       city = message.text.split(" ")[1]  # Extract city name from message
       url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}"

       response = await client.get_session().get(url)  # Use Pyrogram's HTTP client
       data = await response.json()

       temperature = data["main"]["temp"]
       description = data["weather"][0]["description"]
       message_text = f"Weather in {city}:\nTemperature: {temperature} K\nDescription: {description}"

       await message.reply_text(message_text)

   except Exception as e:
       await message.reply_text(f"An error occurred: {e}")  # Handle potential errors
