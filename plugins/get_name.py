# get_name.py
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)


async def get_bot_name(query):
    bot_name = None
    if query == "mbot":
        bot_name = "Movies Bot"
    elif query == "abot":
        bot_name = "Anime Bot"
    elif query == "rbot":
        bot_name = "Rename Bot"
    elif query == "dbot":
        bot_name = "YouTube Downloader Bot"
    return bot_name


async def get_db_name(query):
    db_name = None
    if query == "mdb":
        db_name = "Movies Database"
    elif query == "adb":
        db_name = "Anime Database"
    elif query == "sdb":
        db_name = "TV Series Database"
    elif query == "bdb":
        db_name = "Audio Book Database"
    return db_name
    
