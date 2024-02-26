# getlinks.py
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bs4 import BeautifulSoup
import requests
from urllib.parse import urlparse


def extract_links(url):
    usr_agent = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)'
        'Chrome/61.0.3163.100 Safari/537.36'
    }
    response = requests.get(url, headers=usr_agent)
    response.raise_for_status()
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
                button = InlineKeyboardButton(domain, url="link")
                buttons.append([button])
            except Exception as e:
                print(f"Error creating button with URL {link}: {e}")
        if buttons:
            reply_markup = InlineKeyboardMarkup(buttons)
            message.reply_text("Here are the links from the website:", reply_markup=reply_markup)
        else:
            message.reply_text("No valid links found on the website.")
    else:
        message.reply_text("Please provide a valid URL.")

