from pyrogram import Client, filters, enums
from pyrogram.types import Message
import aiohttp
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from cloudscraper import create_scraper


async def filepress(url: str):
    async with aiohttp.ClientSession() as sess:
        scraper = create_scraper()
        try:
            url = scraper.get(url).url
            raw = urlparse(url)
            json_data = {
                'id': raw.path.split('/')[-1],
                'method': 'publicDownlaod',
            }
            async with sess.post(f'{raw.scheme}://{raw.hostname}/api/file/telegram/downlaod/', headers={'Referer': f'{raw.scheme}://{raw.hostname}'}, json=json_data) as resp:
                tg_id = await resp.json()
            if 'data' in tg_id:
                tg_id_data = tg_id['data']
                tg_url = f"https://tghub.xyz/?start={tg_id_data}"
                bot_name = [bot for bot in BeautifulSoup(await sess.get(tg_url)).text if "filepress_[a-zA-Z0-9]+_bot" in bot][0]
                tg_link = f"https://t.me/{bot_name}/?start={tg_id_data}"
            else:
                tg_link = 'Unavailable' if tg_id["statusText"] == "Ok" else tg_id["statusText"]
        except Exception as e:
            tg_link = f'ERROR: {e.__class__.__name__}'
    if tg_link == 'Unavailable':
        tg_link_text = 'Unavailable'
    else:
        tg_link_text = f'"{tg_link}">Click Here'

    parse_txt = f'''FilePress: "{url}">Click Here\nTelegram: {tg_link_text}'''
    return parse_txt


@Client.on_message(filters.command("filepress") & filters.private)
async def filepress_command(client: Client, message: Message):
    if len(message.command) != 2:
        await message.reply_text("Usage: /filepress url")
        return
    url = message.command[1]
    try:
        result = await filepress(url)
        await message.reply_text(result)
    except Exception as e:
        await message.reply_text(f"Error: {e}")
 
               
