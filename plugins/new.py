from os import path
from re import findall
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from cloudscraper import create_scraper
import requests  
from aiohttp import ClientSession 
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InKeyboardMarkup


class DDLException(Exception):
    pass

@Client.on_message(filters.command("filepress"))
async def filepress_handler(client, message):
    url = message.text.split(maxsplit=1)[1]
    try:
        result = await filepress(url)
        await message.reply_text(result, parse_mode="HTML")
    except DDLException as e:
        await message.reply_text(f"Error: {e}")

async def filepress(url: str):
    cget = create_scraper().request
    try:
        url = cget('GET', url).url
        raw = urlparse(url)
        async with ClientSession() as sess:
            json_data = {
                'id': raw.path.split('/')[-1],
                'method': 'publicDownlaod',
            }
            async with await sess.post(f'{raw.scheme}://{raw.hostname}/api/file/telegram/downlaod/', headers={'Referer': f'{raw.scheme}://{raw.hostname}'}, json=json_data) as resp:
                tg_id = await resp.json()
            if tg_id.get('data', False):
                t_url = f"https://tghub.xyz/?start={tg_id['data']}"
                bot_name = findall("filepress_[a-zA-Z0-9]+_bot", cget('GET', t_url).text)[0]
                tg_link = f"https://t.me/{bot_name}/?start={tg_id['data']}"
            else:
                tg_link = 'Unavailable' if tg_id["statusText"] == "Ok" else tg_id["statusText"]
    except Exception as e:
        raise DDLException(f'{e.__class__.__name__}')
    if tg_link == 'Unavailable':
        tg_link_text = 'Unavailable'
    else:
        tg_link_text = f'<a href="{tg_link}">Click Here</a>'

    parse_txt = f'''┏<b>FilePress:</b> <a href="{url}">Click Here</a>
┗<b>Telegram:</b> {tg_link_text}'''
    return parse_txt
