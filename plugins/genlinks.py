import requests
from bs4 import BeautifulSoup
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from urllib.parse import urlparse
import time

def extract_links(url):
    usr_agent = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'
    }
    try:
        response = requests.get(url, headers=usr_agent, timeout=5)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Error: {e}")
        return []
    soup = BeautifulSoup(response.content, 'html.parser')
    links = []
    for link in soup.find_all('a', href=True):
        links.append(link['href'])
    return links

def handle_cloudflare(url):
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        return False
    except requests.exceptions.RequestException as e:
        if response.status_code == 503:
            print("Website is protected by Cloudflare")
            return True
        else:
            print(f"Error: {e}")
            return False

def bypass_cf(url):
    if handle_cloudflare(url):
        print("Bypassing Cloudflare...")
        time.sleep(5)
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'
        }
        session = requests.Session()
        session.headers.update(headers)
        try:
            response = session.get(url, timeout=5)
            response.raise_for_status()
            print("Cloudflare bypassed successfully")
            return session
        except requests.exceptions.RequestException as e:
            print(f"Error: {e}")
            return None
    else:
        return None

@Client.on_message(filters.command(["getlinks"]))
def get_links(client, message):
    if len(message.command) > 1:
        url = message.command[1]
        session = bypass_cf(url)
        if session:
            links = extract_links(url)
            buttons = []
            for link in links:
                domain = urlparse(link).netloc
                print(f"Attempting to add button with URL: {link}")
                try:
                    button = InlineKeyboardButton(domain, url=link)
                    buttons.append(button)  # Append each button directly
                except Exception as e:
                    print(f"Error creating button with URL {link}: {e}")
            if buttons:
                reply_markup = InlineKeyboardMarkup([buttons])
                message.reply_text("Here are the links from the website:", reply_markup=reply_markup)
            else:
                message.reply_text("No valid links found on the website.")
        else:
            message.reply_text("Failed to bypass Cloudflare protection.")
    else:
        message.reply_text("Please provide a valid URL.")

