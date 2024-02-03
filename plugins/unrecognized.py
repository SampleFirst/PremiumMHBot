from pyrogram import Client, filters
from pyrogram.types import Message
import asyncio
from info import LOG_CHANNEL

@Client.on_message(filters.text & filters.command("", prefixes="/"))
async def unrecognized_command(client, message):
    await client.send_message(message.chat.id, "Unrecognized command. What are you trying to say?")
    await client.send_message(LOG_CHANNEL, f"{message.from_user.username} tried to execute the {message.text} command.")
    await asyncio.sleep(2)
    await message.delete()
