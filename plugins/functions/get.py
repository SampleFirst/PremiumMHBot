from pyrogram import Client, filters
from cloudscraper import create_scraper
from bs4 import BeautifulSoup
import re

@Client.on_message(filters.command("get"))
def get(client, message):
    # Check if a URL is provided after the command
    if len(message.text.split()) < 2:
        message.reply_text("Please provide a URL after the command.")
        return

    url = message.text.split(" ", maxsplit=1)[1]
    scraper = create_scraper()
    response = scraper.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    links = [a["href"] for a in soup.find_all("a", href=True)]
    message.reply_text("\n".join(links))
