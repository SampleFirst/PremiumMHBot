import aiohttp
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from cloudscraper import create_scraper
from pyrogram import Client, filters, enums
from pyrogram.types import Message


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
            if tg_id.get('data', False):
                t_url = f"https://tghub.xyz/?start={tg_id['data']}"
                bot_name = [bot for bot in BeautifulSoup(await sess.get(t_url)).text if "filepress_[a-zA-Z0-9]+_bot" in bot][0]
                tg_link = f"https://t.me/{bot_name}/?start={tg_id['data']}"
            else:
                tg_link = 'Unavailable' if tg_id["statusText"] == "Ok" else tg_id["statusText"]
        except Exception as e:
            tg_link = f'ERROR: {e.__class__.__name__}'
    if tg_link == 'Unavailable':
        tg_link_text = 'Unavailable'
    else:
        tg_link_text = tg_link
    sess.close()
    parse_txt = f'''<b>FilePress:</b> <a href="{url}">Click Here</a>
<b>Telegram:</b> <a href="{tg_link}">Click Tg</a>'''
    return parse_txt


@Client.on_message(filters.command("fileone") & filters.private)
async def filepress_command(client: Client, message: Message):
    if len(message.command) != 2:
        await message.reply_text("Usage: /filepress [url]")
        return
    url = message.command[1]
    try:
        result = await filepress(url)
        await message.reply_text(result, parse_mode=enums.ParseMode.HTML)
    except Exception as e:
        await message.reply_text(f"Error: {e}")

