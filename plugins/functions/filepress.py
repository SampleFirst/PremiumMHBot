from pyrogram import Client, filters
from urllib.parse import urlparse
import aiohttp
from info import ADMINS, LOG_CHANNEL 

async def filepress(url: str):
    try:
        async with aiohttp.ClientSession() as sess:
            json_data = {'id': urlparse(url).path.split('/')[-1]}
            async with sess.post(f'{url}/api/file/telegram/downlaod/', json=json_data) as resp:
                tg_id = await resp.json()
            if tg_id.get('data'):
                bot_name = findall("filepress_[a-zA-Z0-9]+_bot", await (await sess.get(f"https://tghub.xyz/?start={tg_id['data']}")).text)[0]
                tg_link = f"https://t.me/{bot_name}/?start={tg_id['data']}"
            else:
                tg_link = 'Unavailable' if tg_id["statusText"] == "Ok" else tg_id["statusText"]
    except Exception as e:
        raise e
    return f'''┏<b>FilePress:</b> <a href="{url}">Click Here</a>
┗<b>Telegram:</b> {'Unavailable' if tg_link == 'Unavailable' else f'<a href="{tg_link}">Click Here</a>'}'''

@Client.on_message(filters.command("filepress") & filters.private)
async def filepress_command(client, message):
    if len(message.command) != 2:
        await message.reply_text("Usage: /filepress [url]")
        return
    url = message.command[1]
    try:
        result = await filepress(url)
        await message.reply_text(result, parse_mode='html')
        await client.send_message(LOG_CHANNEL, result, parse_mode='html')
    except Exception as e:
        await message.reply_text(f"Error: {e}")

