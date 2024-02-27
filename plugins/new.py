from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton


# Define the command handler
@Client.on_message(filters.command("show_urls"))
def show_urls(client, message):
    # URLs and their corresponding titles
    urls = [
        {"title": "new.gdflix.cfd", "url": "https://new.gdflix.cfd/file/Ocx6YdzBIt"},
        {"title": "hubdrive.lat", "url": "https://hubdrive.lat/file/1706522970"},
        {"title": "new3.gdtot.zip", "url": "https://new3.gdtot.zip/file/661661345"},
        {"title": "hubcloud.lol", "url": "https://hubcloud.lol/drive/f0jlkfvftj18h4r"},
        {"title": "new8.filepress.store", "url": "https://new8.filepress.store/file/65b77933869e1f441c3b3e69"},
        {"title": "wwa.fastxyz.in", "url": "https://wwa.fastxyz.in/xfile.php?id=aDFyZWNkeG5wZHNwbnVt"}
    ]

    buttons = [
        [InlineKeyboardButton(url["title"], url=url["url"])] for url in urls
    ]

    reply_markup = InlineKeyboardMarkup(buttons)

    # Send the message with inline keyboard
    message.reply_text("Here are the URLs:", reply_markup=reply_markup)

