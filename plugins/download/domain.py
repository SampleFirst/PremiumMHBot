# domain.py
import asyncio
import requests
from bs4 import BeautifulSoup
from pyrogram import Client, filters
from info import ADMINS, LOG_CHANNEL


@Client.on_message(filters.command("domain") & filters.user(ADMINS))
async def show_domain(client, message):
    msg = await message.reply_text("Fetching the new current domain...", quote=True)

    website = "https://skybap.com/"
    response = requests.get(website)
    soup = BeautifulSoup(response.text, "html.parser")
    new_domain = soup.find("span", {"class": "badge"})

    if new_domain:
        new_domain = new_domain.text.strip()
        
        await msg.delete()
        main = await message.reply_text(f"Domain get from\n<code>{website}</code>\n\nThe **SkymoviesHD** latest domain is:\n<code>{new_domain}</code>", quote=True)
        await client.send_message(
            chat_id=LOG_CHANNEL,
            text=f"Domain get from\n<code>{website}</code>\n\nThe **SkymoviesHD** latest domain is:\n<code>{new_domain}</code>"
        )
        await asyncio.sleep(15)
        await main.delete()
    else:
        await message.reply_text("Failed to fetch the new current domain.")
