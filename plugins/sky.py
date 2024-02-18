import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin
from pyrogram import Client, filters, enums
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton


@Client.on_message(filters.command("sky"))
async def search_filesmkv(client, message):
    query = message.text.split(" ", 1)[1]
    link = f"https://skymovieshd.ngo/search.php?search={query}&cat=All"
    
    response = requests.get(link)
    soup = BeautifulSoup(response.text, "html.parser")
    
    results = soup.find_all("div", class_="movie-box")
    
    if not results:
        await message.reply("No results found.")
        return
    
    buttons = []
    for result in results:
        title = result.find("div", class_="name").text
        url = result.find("a")["href"]
        buttons.append([f"{title}", f"https://skymovieshd.ngo{url}"])
    
    await message.reply_text("Select a file:", reply_markup=InlineKeyboardMarkup(buttons))
    
    
    

@Client.on_callback_query()
async def download_file(client, callback_query):
    url = callback_query.data
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    
    links = soup.find_all("a", text=re.compile("Google Drive Direct Links", re.IGNORECASE))
    
    if not links:
        await callback_query.answer("No download links found.")
        return
    
    link = urljoin(url, links[0]["href"])
    response = requests.get(link)
    soup = BeautifulSoup(response.text, "html.parser")
    
    buttons = []
    for script in soup.find_all("script"):
        if "gdtot" in script.text:
            for link in re.findall(r"(https:\/\/[^\s]+)", script.text):
                buttons.append([f"{link}", link])
    
    await callback_query.answer("Select a download link:", reply_markup=InlineKeyboardMarkup(buttons))
    
    
@Client.on_callback_query()
async def send_download_link(client, callback_query):
    link = callback_query.data
    await callback_query.message.answer(link)
