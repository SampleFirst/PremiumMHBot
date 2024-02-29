from pyrogram import Client, filters
import requests
import json


# Define the command handler
@Client.on_message(filters.command("json"))
async def get_json(client, message):
    # Get the URL from the user's message
    url = message.text.split(" ")[1]

    # Send a message to the user that we're processing the request
    client.send_message(message.chat.id, "Processing request...")

    # Send a GET request to the URL and get the JSON data
    response = requests.get(url)
    data = json.loads(response.text)

    # Send the JSON data to the user
    client.send_message(message.chat.id, json.dumps(data, indent=4))

