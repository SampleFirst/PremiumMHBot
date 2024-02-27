from urllib.parse import urlparse
from cfscrape import create_scraper
from pyrogram import Client, filters

@Client.on_message(filters.command("bypass"))
async def bypass_command(client, message):
    if len(message.command) == 2:
        url = message.command[1]
        gd_link, tg_link = await extract_filepress_links(url)
        await message.reply(f"Google Drive: {gd_link}\nTelegram: {tg_link}")
    else:
        await message.reply("Invalid command. Please provide a valid URL after /bypass.")


async def extract_filepress_links(url):
    gd_link = ""
    tg_link = ""
    cget = create_scraper().request
    for link in filepress_links:
        try:
            url = cget('GET', link).url
            raw = urlparse(url)

            gd_data = {
                'id': raw.path.split('/')[-1],
                'method': 'publicDownlaod',
            }
            tg_data = {
                'id': raw.path.split('/')[-1],
                'method': 'telegramDownload',
            }

            api = f'{raw.scheme}://{raw.hostname}/api/file/downlaod/'

            gd_res = cget('POST', api, headers={'Referer': f'{raw.scheme}://{raw.hostname}'}, json=gd_data).json()
            tg_res = cget('POST', api, headers={'Referer': f'{raw.scheme}://{raw.hostname}'}, json=tg_data).json()

            gd_result = f'https://drive.google.com/uc?id={gd_res["data"]}' if 'data' in gd_res else f'ERROR: {gd_res["statusText"]}'
            tg_result = f'https://tghub.xyz/?start={tg_res["data"]}' if 'data' in tg_res else "No Telegram file available "

            gd_link += gd_result + "\n"
            tg_link += tg_result + "\n"

        except Exception as e:
            gd_link += f'Google Drive: ERROR: {e.__class__.__name__}\n'
            tg_link += f'Telegram: ERROR: {e.__class__.__name__}\n'
    return gd_link, tg_link
