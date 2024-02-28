# getlinks_fixed.py
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from bs4 import BeautifulSoup
from requests_html import HTMLSession
from urllib.parse import urlparse

# Function to extract links from a website
def extract_links(url):
    try:
        session = HTMLSession()
        response = session.get(url)
        response.html.render()
        soup = BeautifulSoup(response.html.raw_html, 'html.parser')
        links = [a.get('href') for a in soup.find_all('a', href=True)]
        return links
    except Exception as e:
        return []

# Command handler
@Client.on_message(filters.command(["getlinks"]))
def get_links(client, message):
    if len(message.command) > 1:
        url = message.command[1]
        if not url.startswith(("http://", "https://")):
            url = "http://" + url
        try:
            links = extract_links(url)
            if links:
                links_list = []
                buttons = []
                for link in links:
                    domain = urlparse(link).netloc
                    buttons.append([InlineKeyboardButton(domain, url=link)])
                    links_list.append(link)
                message.reply_text("Here are the links from the website:\n" + "\n".join(links_list), reply_markup=InlineKeyboardMarkup(buttons))
            else:
                message.reply_text("No valid links found on the website.")
        except Exception as e:
            print(f"Error processing URL {url}: {e}")
            message.reply_text("Error processing the URL. Please try again later.")
    else:
        message.reply_text("Please provide a valid URL.")
