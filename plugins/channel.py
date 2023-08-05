from pyrogram import Client, filters
from info import CHANNELS, UPDATE_CHANNEL
from database.ia_filterdb import save_file

media_filter = filters.document | filters.video | filters.audio

@Client.on_message(filters.chat(CHANNELS) & media_filter)
async def media(bot, message):
    for file_type in ("document", "video", "audio"):
        media = getattr(message, file_type, None)
        if media is not None:
            break
    else:
        return

    media.file_type = file_type
    media.caption = message.caption
    await save_file(media)

    # Send a log to the UPDATE_CHANNEL about the new added file
    log_message = f"New file added: {media.file_type} - {media.file_name} in {CHANNELS}"
    await bot.send_message(UPDATE_CHANNEL, log_message)
