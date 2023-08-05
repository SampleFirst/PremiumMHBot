from pyrogram import Client, filters
from info import CHANNELS, CHNL_LNK
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

    # Write the new file to the disk (modify this part according to your needs)
    # Example:
    with open(f"new_files/{media.file_name}", "wb") as f:
        await media.download(file_name=f.name)

    # Send a log to the UPDATE_CHANNEL about the new added file
    log_text = f"New file added: {media.file_name}"
    await bot.send_message(CHNL_LNK, log_text)
