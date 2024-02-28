# bypass.py
from urllib.parse import urlparse
from cfscrape import create_scraper
from pyrogram import Client, filters

# Command handler
@Client.on_message(filters.command("bypass"))
async def bypass_command(client, message):
    if len(message.command) == 2:
        url = message.command[1]
        gd_result, tg_result = await filepress(url)
        await message.reply(f"Google Drive: {gd_result}\nTelegram: {tg_result}")
    else:
        await message.reply("Invalid command. Please provide a valid URL after /bypass.")

# Filepress function
async def filepress(url):
    cget = create_scraper().get
    try:
        res = cget(url)
        url = res.url
        raw = urlparse(url)

        gd_data = {
            'id': raw.path.split('/')[-1],
            'method': 'publicDownload',
        }
        tg_data = {
            'id': raw.path.split('/')[-1],
            'method': 'telegramDownload',
        }
        
        api = f'{raw.scheme}://{raw.hostname}/api/file/download/'
        
        headers = {'Referer': f'{raw.scheme}://{raw.hostname}'}

        gd_res = cget(api, headers=headers, json=gd_data).json()
        tg_res = cget(api, headers=headers, json=tg_data).json()
        
    except Exception as e:
        gd_result = f'ERROR: {e.__class__.__name__}' 
        tg_result = f'ERROR: {e.__class__.__name__}'
    else:
        gd_result = f'https://drive.google.com/uc?id={gd_res["data"]}' if 'data' in gd_res else f'ERROR: {gd_res["statusText"]}'
        tg_result = f'https://tghub.xyz/?start={tg_res["data"]}' if 'data' in tg_res else "No Telegram file available"
    
    return gd_result, tg_result
