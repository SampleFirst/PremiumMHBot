# getlinks.py
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bs4 import BeautifulSoup
import requests
from urllib.parse import urlparse


def extract_links(url):
    response = requests.get(url)
    response.raise_for_status()
    soup = BeautifulSoup(response.content, 'html.parser')
    links = []
    for link in soup.find_all('a', href=True):
        href = link.get('href')
        if href.startswith("https://"):
            links.append(href)
    return links
    

# Command handler
@Client.on_message(filters.command(["getlinks"]))
def get_links(client, message):
    if len(message.command) > 1:
        url = message.command[1]
        try:
            links = extract_links(url)
            buttons = []
            links_list = []
            for link in links:
                domain = urlparse(link).netloc
                buttons.append([InlineKeyboardButton(domain, url=link)])
                links_list.append(link)
            if buttons:
                reply_markup = InlineKeyboardMarkup(buttons)
                message.reply_text("Here are the links from the website:", reply_markup=reply_markup)
            elif links_list:
                message.reply_text("Here are the links from the website:\n" + "\n".join(links_list))
            else:
                message.reply_text("No valid links found on the website.")
        except Exception as e:
            print(f"Error processing URL {url}: {e}")
            message.reply_text("Error processing the URL. Please try again later.")
    else:
        message.reply_text("Please provide a valid URL.")
