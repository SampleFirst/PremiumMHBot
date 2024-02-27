from urllib.parse import urlparse
from cfscrape import create_scraper
from pyrogram import Client, filters

@Client.on_message(filters.command("bypass"))
async def bypass_command(client, message):
    if len(message.command) == 2:
        url = message.command[1]
        gd_result, tg_result = await filepress(url)
        await message.reply(f"Google Drive: {gd_link}\nTelegram: {tg_link}")
    else:
        await message.reply("Invalid command. Please provide a valid URL after /bypass.")


async def filepress(url):
	cget = create_scraper().request
	try:
		url = cget('GET', url).url
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
		
	except Exception as e:
		return f'Google Drive: ERROR: {e.__class__.__name__} \nTelegram: ERROR: {e.__class__.__name__}'
	
	gd_result = f'https://drive.google.com/uc?id={gd_res["data"]}' if 'data' in gd_res else f'ERROR: {gd_res["statusText"]}'
	tg_result = f'https://tghub.xyz/?start={tg_res["data"]}' if 'data' in tg_res else "No Telegram file available "
	
	return gd_result, tg_result
