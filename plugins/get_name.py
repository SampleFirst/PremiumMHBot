# get_name.py
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)


def get_bot_name(query_data):
    bot_name = None
    if query_data == "mbot":
        bot_name = "Movies Bot"
    elif query_data == "abot":
        bot_name = "Anime Bot"
    elif query_data == "rbot":
        bot_name = "Rename Bot"
    elif query_data == "dbot":
        bot_name = "YouTube Downloader Bot"
    return bot_name


def get_db_name(query_data):
    db_name = None
    if query_data == "mdb":
        db_name = "Movies Database"
    elif query_data == "adb":
        db_name = "Anime Database"
    elif query_data == "sdb":
        db_name = "TV Series Database"
    elif query_data == "bdb":
        db_name = "Audio Book Database"
    return db_name
    
