from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bs4 import BeautifulSoup
import requests
from urllib.parse import urlparse

# Function to extract links from a webpage
def extract_links(url):
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    links = []
    for link in soup.find_all('a', href=True):
        links.append(link['href'])
    return links


# Command handler
@Client.on_message(filters.command(["getlinks"]))
def get_links(client, message):
    if len(message.command) > 1:
        url = message.command[1]
        links = extract_links(url)
        buttons = []
        for link in links:
            domain = urlparse(link).netloc
            print(f"Attempting to add button with URL: {link}")
            try:
                button = InlineKeyboardButton(domain, url=link)
                buttons.append(button)
            except Exception as e:
                print(f"Error creating button with URL {link}: {e}")
        if buttons:
            reply_markup = InlineKeyboardMarkup([buttons])
            message.reply_text("Here are the links from the website:", reply_markup=reply_markup)
        else:
            message.reply_text("No valid links found on the website.")
    else:
        message.reply_text("Please provide a valid URL.")
