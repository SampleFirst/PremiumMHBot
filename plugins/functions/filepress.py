from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import MessageIdInvalid
from pyrogram.errors.exceptions.bad_request_400 import MessageIdInvalid
from requests import Session
from requests.exceptions import RequestException
from urllib.parse import urlparse
from re import findall
from info import ADMINS, LOG_CHANNEL


async def filepress(url: str):
    try:
        async with ClientSession() as sess:
            async with sess.get(url) as resp:
                if resp.status != 200:
                    return 'Invalid URL'
                raw = urlparse(url)
                json_data = {
                    'id': raw.path.split('/')[-1],
                    'method': 'publicDownlaod',
                }
                del json_data['method']
                async with sess.post(f'{raw.scheme}://{raw.hostname}/api/file/telegram/downlaod/', headers={'Referer': f'{raw.scheme}://{raw.hostname}'}, json=json_data) as resp:
                    tg_id = await resp.json()
                if tg_id.get('data', False):
                    t_url = f"https://tghub.xyz/?start={tg_id['data']}"
                    bot_name = findall("filepress_[a-zA-Z0-9]+_bot", await sess.get(t_url)).text
                    tg_link = f"https://t.me/{bot_name}/?start={tg_id['data']}"
                else:
                    tg_link = 'Unavailable' if tg_id["statusText"] == "Ok" else tg_id["statusText"]
    except RequestException as e:
        raise (f'{e.__class__.__name__}')
    if tg_link == 'Unavailable':
        tg_link_text = 'Unavailable'
    else:
        tg_link_text = f'<a href="{tg_link}">{tg_link}</a>'

    parse_txt = f'''┏<b>FilePress:</b> <a href="{url}">{url}</a>
┗<b>Telegram:</b> {tg_link_text}'''
    return parse_txt


@Client.on_message(filters.command("filepress") & filters.private)
async def filepress_command(client: Client, message: Message):
    if len(message.command) != 2:
        await message.reply_text("Usage: /filepress [url]")
        return
    url = message.command[1]
    try:
        result = await filepress(url)
        await message.reply_text(result, parse_mode=enums.ParseMode.HTML)
        await client.send_message(LOG_CHANNEL, result, parse_mode=enums.ParseMode.HTML)
    except MessageIdInvalid as e:
        await message.reply_text(f"Error: {e}")
    except Exception as e:
        await message.reply_text(f"Error: {e}")
