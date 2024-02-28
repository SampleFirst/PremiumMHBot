# domain_dm.py
import asyncio
import requests
from bs4 import BeautifulSoup
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from info import ADMINS, LOG_CHANNEL
from database.domain_db import dm 
import random
import re

@Client.on_message(filters.command("domain") & filters.user(ADMINS))
async def get_domain(client, message):
    msg = await message.reply_text("Fetching the new current domain...", quote=True)

    website = "https://skybap.com/"
    response = requests.get(website)
    soup = BeautifulSoup(response.text, "html.parser")
    new_domain = soup.find("span", {"class": "badge"})

    if new_domain:
        new_domain = new_domain.text.strip()
        site = re.search(r'(?<=://)(.*?)(?=\.)', new_domain).group(0)
        latest_domain = await dm.get_latest_domain(site)

        if latest_domain == new_domain:
            await msg.delete()
            button = [
                [
                    InlineKeyboardButton(text="Show Domain", callback_data="show_domain")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(button)
            caption = f"Domain get from\n<code>{website}</code>\n\nThe **SkymoviesHD** latest domain is:\n<code>{new_domain}</code>\n\nAnd Latest Store Domain is:\n<code>{latest_domain}</code>\n\nNew Domain and Latest Store domain are Match ✅ Select 'Show Domain' Button to Show all Updated Domains..."
            main = await message.reply_text(
                text=caption,
                reply_markup=reply_markup,
                quote=True
            )
            await client.send_message(
                chat_id=LOG_CHANNEL,
                text=f"Domain get from\n<code>{website}</code>\n\nThe **SkymoviesHD** latest domain is:\n<code>{new_domain}</code>"
            )
            await asyncio.sleep(15)
            await main.delete()
        else:
            await msg.delete()
            button = [
                [
                    InlineKeyboardButton(text="Domain Update", callback_data="update_domain")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(button)
            caption = f"Domain get from\n<code>{website}</code>\n\nThe **SkymoviesHD** latest domain is:\n<code>{new_domain}</code>\n\nAnd Latest Store Domain is:\n<code>{latest_domain}</code>\n\nNew Domain and Latest Store domain are not Match ❎ Select 'Domain Update' Button to Update the new Domain..."
            main = await message.reply_text(
                text=caption,
                reply_markup=reply_markup,
                quote=True
            )
            await client.send_message(
                chat_id=LOG_CHANNEL,
                text=f"Domain get from\n<code>{website}</code>\n\nThe **SkymoviesHD** latest domain is:\n<code>{new_domain}</code>"
            )
            await asyncio.sleep(15)
            await main.delete()
    else:
        await message.reply_text("Failed to fetch the new current domain.")


@Client.on_callback_query(filters.regex("^update_domain$"))
async def update_domain(client, callback_query):
    try:
        msg = await callback_query.message.reply_text("Updating...")
    
        website = "https://skybap.com/"
        response = requests.get(website)
        soup = BeautifulSoup(response.text, "html.parser")
        new_domain = soup.find("span", {"class": "badge"})

        new_domain = new_domain.text.strip()
        site = re.search(r'(?<=://)(.*?)(?=\.)', new_domain).group(0)
        await dm.add_domain(site, new_domain)
        
        latest_domain = await dm.get_latest_domain()
        if latest_domain == new_domain: 
            await msg.delete()
            button = [
                [
                    InlineKeyboardButton(text="Show Domain", callback_data="show_domain")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(button)
            caption = f"Domain get from\n<code>{website}</code>\n\nThe **SkymoviesHD** latest domain is:\n<code>{new_domain}</code>\n\nAnd Latest Store Domain is:\n<code>{latest_domain}</code>\n\nNew Domain Update as a Latest domain ✅ Select 'Show Domain' Button to Show all Updated Domains..."
            main = await callback_query.message.edit_text(
                text=caption,
                reply_markup=reply_markup
            )
            await client.send_message(
                chat_id=LOG_CHANNEL,
                text=f"Domain get from\n<code>{website}</code>\n\nThe **SkymoviesHD** latest domain is:\n<code>{new_domain}</code>"
            )
            await asyncio.sleep(15)
            await main.delete()
    except Exception as e:
        await callback_query.message.edit_text(f"An error occurred: {str(e)}")
 
@Client.on_callback_query(filters.regex("^show_domain$"))
async def show_domain(client, callback_query):
    try:
        domains = await dm.get_all_domains()
        if domains:
            domain_list = "\n".join([f"{domain['domain']} - {domain['timestamp']}" for domain in domains])
            await callback_query.message.edit_text(f"All updated domains:\n{domain_list}")
        else:
            await callback_query.message.edit_text("No domains found in the database.")
    except Exception as e:
        await callback_query.message.edit_text(f"An error occurred: {str(e)}")


@Client.on_message(filters.command("delete_domains") & filters.user(ADMINS))
async def delete_confirmation(client, message):
    buttons = [
        [InlineKeyboardButton("Yes Delete", callback_data="yes_delete")],
        [InlineKeyboardButton("Nope Now", callback_data="nope_now")],
        [InlineKeyboardButton("Not Now", callback_data="not_now")]
    ]
    random.shuffle(buttons)
    reply_markup = InlineKeyboardMarkup(buttons)
    main = await message.reply_text("Do you want to delete?", reply_markup=reply_markup)
    await asyncio.sleep(30)
    await main.delete()

@Client.on_callback_query(filters.regex("^yes_delete$"))
async def yes_delete(client, callback_query):
    try:
        msg = await callback_query.message.edit_text("Deleting domains...")
        site = "SkymoviesHD"
        await dm.delete_all_domains(site)
        await msg.delete()
        main = await callback_query.message.edit_text("All data deleted successfully!")
        await client.send_message(LOG_CHANNEL, "All data deleted successfully!")
        await callback_query.answer("Not deleting now.")
        await asyncio.sleep(30)
        await main.delete()
    except Exception as e:
        main = await callback_query.message.edit_text(f"An error occurred: {str(e)}")
        await callback_query.answer("Not deleting now.")
        await asyncio.sleep(30)
        await main.delete()
        

@Client.on_callback_query(filters.regex("^nope_now$"))
async def nope_now(client, callback_query):
    note = await callback_query.message.edit_text("Not deleting now...")
    await callback_query.answer("Not deleting now.")
    await asyncio.sleep(30)
    await note.delete()


@Client.on_callback_query(filters.regex("^not_now$"))
async def not_now(client, callback_query):
    note = await callback_query.message.edit_text("Okay, not deleting...")
    await callback_query.answer("Okay, not deleting.")
    await asyncio.sleep(30)
    await note.delete()
