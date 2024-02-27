
import cloudscraper
from bs4 import BeautifulSoup
import re

from pyrogram import Client, filters



@Client.on_message(filters.command("get"))
def get(client, message):
    url = message.text.split(" ", maxsplit=1)[1]
    scraper = cloudscraper.create_scraper()
    response = scraper.get(url)
    soup = BeautifulSoup(response.content, "html.parser")
    links = [a["href"] for a in soup.find_all("a", href=True)]
    message.reply_text("\n".join(links))

