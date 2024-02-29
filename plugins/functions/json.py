from pyrogram import Client, filters
import requests
import json


# Define the command handler
@Client.on_message(filters.command("json"))
async def get_json(client, message):
    try:
        # Get the URL from the user's message
        url = message.text.split(" ")[1]

        # Send a message to the user that we're processing the request
        await client.send_message(message.chat.id, "Processing request...")

        # Send a GET request to the URL and get the JSON data
        response = requests.get(url)
        
        # Check if the response status is OK
        if response.status_code == 200:
            # Try to load JSON data from the response
            try:
                data = response.json()
                # Send the JSON data to the user
                await client.send_message(message.chat.id, json.dumps(data, indent=4))
            except json.JSONDecodeError:
                await client.send_message(message.chat.id, "Error: Response is not in valid JSON format.")
        else:
            await client.send_message(message.chat.id, f"Error: Failed to fetch data from {url}. Status code: {response.status_code}")
    except IndexError:
        await client.send_message(message.chat.id, "Error: Please provide a valid URL.")
