from pyrogram import Client, filters
from bs4 import BeautifulSoup
from urllib.parse import urlparse
import aiohttp

class DDLException(Exception):
    pass

async def filepress(url: str):
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(url) as response:
                if response.status != 200:
                    raise DDLException(f'Failed to fetch URL: {url}')
                url = str(response.url)
                raw = urlparse(url)
                json_data = {'id': raw.path.split('/')[-1], 'method': 'publicDownlaod'}
                async with session.post(f'{raw.scheme}://{raw.hostname}/api/file/telegram/downlaod/', headers={'Referer': f'{raw.scheme}://{raw.hostname}'}, json=json_data) as resp:
                    tg_id = await resp.json()
                if tg_id.get('data', False):
                    t_url = f"https://tghub.xyz/?start={tg_id['data']}"
                    async with session.get(t_url) as t_resp:
                        text = await t_resp.text()
                        bot_name = BeautifulSoup(text, 'html.parser').find('a', href=True).text
                        tg_link = f"https://t.me/{bot_name}/?start={tg_id['data']}"
                else:
                    tg_link = 'Unavailable' if tg_id["statusText"] == "Ok" else tg_id["statusText"]
        except Exception as e:
            raise DDLException(f'{e.__class__.__name__}')
    
    if tg_link == 'Unavailable':
        tg_link_text = 'Unavailable'
    else:
        tg_link_text = f'<a href="{tg_link}">Click Here</a>'

    parse_txt = f'''<b>FilePress:</b> <a href="{url}">Click Here</a>\n\n<b>Telegram:</b> {tg_link_text}'''
    return parse_txt



@Client.on_message(filters.command(["filepress"]))
async def extract_command(client, message):
    if len(message.command) != 2:
        await message.reply("Please provide a single URL to filepress.")
        return
    url = message.command[1]
    if not url.startswith("https"):
        url = "https://" + url  # Assuming it's a HTTP URL, adjust if needed
    try:
        result = await filepress(url)
        await message.reply(result, parse_mode="html")
    except DDLException as e:
        await message.reply(f"Failed to filepress: {e}")
