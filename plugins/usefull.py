from pyrogram import Client, filters
import requests


# Define an echo command handler
@Client.on_message(filters.command("echo"))
def echo(client, message):
    # Get the text after the command
    text = message.text.split(maxsplit=1)[1]
    # Send the text back to the user
    message.reply(text)

# Define a weather command handler
@Client.on_message(filters.command("weather"))
def weather(client, message):
    # Get the location after the command
    location = message.text.split(maxsplit=1)[1]
    # Get the weather information from an API
    response = requests.get(f"https://api.openweathermap.org/data/2.5/weather?q={location}&appid=YOUR_API_KEY&units=metric")
    data = response.json()
    # Format the weather information
    text = f"Weather in {data['name']}:\n"
    text += f"Temperature: {data['main']['temp']}°C\n"
    text += f"Humidity: {data['main']['humidity']}%\n"
    text += f"Wind: {data['wind']['speed']} m/s\n"
    text += f"Condition: {data['weather'][0]['description']}"
    # Send the weather information to the user
    message.reply(text)

# Define a translate command handler
@Client.on_message(filters.command("translate"))
def translate(client, message):
    # Get the source and target languages and the text after the command
    args = message.text.split(maxsplit=3)
    source = args[1]
    target = args[2]
    text = args[3]
    # Get the translation from an API
    response = requests.get(f"https://libretranslate.com/translate?q={text}&source={source}&target={target}")
    data = response.json()
    # Format the translation
    text = f"Translation from {source} to {target}:\n"
    text += data['translatedText']
    # Send the translation to the user
    message.reply(text)

