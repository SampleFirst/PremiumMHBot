import os
from pyrogram import Client, filters
from info import CHANNELS, CHNL_LNK
from database.ia_filterdb import save_file

media_filter = filters.document | filters.video | filters.audio

@Client.on_message(filters.chat(CHANNELS) & media_filter)
async def media(bot, message):
    if message.document:
        media = message.document
        file_type = "document"
    elif message.video:
        media = message.video
        file_type = "video"
    elif message.audio:
        media = message.audio
        file_type = "audio"
    else:
        return

    media.file_type = file_type
    media.caption = message.caption
    await save_file(media)

    # Create the 'new_files' directory if it doesn't exist
    if not os.path.exists("new_files"):
        os.makedirs("new_files")

    # Write the new file to the disk
    with open(os.path.join("new_files", media.file_name), "wb") as f:
        await media.download(file_name=f.name)

    # Send a log to the UPDATE_CHANNEL about the new added file
    log_text = f"New file added: {media.file_name}"
    await bot.send_message(CHNL_LNK, log_text)
