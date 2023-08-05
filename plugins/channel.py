from pyrogram import Client, filters
from info import CHANNELS, UPDATE_CHANNEL
from database.ia_filterdb import save_file
from utils import get_poster

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

    # Get IMDb poster for the media and add it to the log message
    poster_info = await get_poster(media.file_name)
    if poster_info:
        log_message += f"\nPoster: {poster_info['poster']}"

    await bot.send_message(UPDATE_CHANNEL, log_message)

