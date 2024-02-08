# get_name.py
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)


async def get_bot_name(query.data):
    bot_name = None
    if query.data == "mbot":
        bot_name = "Movies Bot"
    elif query.data == "abot":
        bot_name = "Anime Bot"
    elif query.data == "rbot":
        bot_name = "Rename Bot"
    elif query.data == "dbot":
        bot_name = "YouTube Downloader Bot"
    return bot_name


async def get_db_name(query.data):
    db_name = None
    if query.data == "mdb":
        db_name = "Movies Database"
    elif query.data == "adb":
        db_name = "Anime Database"
    elif query.data == "sdb":
        db_name = "TV Series Database"
    elif query.data == "bdb":
        db_name = "Audio Book Database"
    return db_name
    
