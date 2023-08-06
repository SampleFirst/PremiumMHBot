from pyrogram import Client, filters
from info import CHANNELS, UPDATE_CHANNEL, IMDB_TEMPLATE
from database.ia_filterdb import save_file
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors.exceptions.bad_request_400 import MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty
from utils import get_poster
import re

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

    # Extracting the search query from the file name
    full_file_name = re.sub(r'[^\w\d]+', ' ', media.file_name) # Update: Remove spaces from full_file_name
    file_name = ""

    # Detecting the year in 4-digit number format
    year_match = re.search(r'\b\d{4}\b', full_file_name)
    series_season_match = re.search(r'\bS\d+\b', full_file_name)

    if year_match or series_season_match:
        # Extracting the part before year or series season
        file_name = re.search(r'^.*?(?=\d{4}\b|\bS\d+\b)', full_file_name).group().strip()

    if not file_name:
        # If no year or series season is found, use the entire file name
        file_name = full_file_name

    # Detecting video resolution
    video_resolution_match = re.search(r'\b\d{3,4}p\b', file_name)
    video_resolution = video_resolution_match.group() if video_resolution_match else None

    # Detecting languages in the file name using regular expressions
    languages_match = re.search(r'{(.*?)}', file_name)
    languages = languages_match.group(1) if languages_match else None

    if not languages:
        # If no languages found in curly brackets, try to detect languages without curly brackets
        languages_match = re.search(r'\b(?:English|Hindi|Bengali|Telugu|Marathi|Tamil|Urdu|Gujarati|Kannada|Odia|Punjabi|Malayalam|Spanish|French|German|Italian|Russian|Chinese)\b', file_name, re.IGNORECASE)
        languages = languages_match.group() if languages_match else None

    if languages:
        # Remove the language portion from the file name
        file_name_without_languages = file_name.replace(languages_match.group(), '').strip()

        # Combine the file name without languages and year for IMDB search
        search_query = f"{file_name_without_languages} {year_match.group()}" if year_match else file_name_without_languages
    else:
        # If no languages found, use the entire file name for the search query
        search_query = file_name

    # Get the IMDB data and poster based on the search query
    imdb = await get_poster(search_query)

    # Check for same name or same name and same year in IMDB
    if imdb and (imdb['title'] == file_name or (year_match and imdb['title'] == file_name_without_languages and imdb['year'] == year_match.group())):
        await bot.send_message(chat_id=UPDATE_CHANNEL, text=f"Duplicate entry found in IMDB:\n{search_query}")
    else:
        # Send log in UPDATE_CHANNEL with IMDB_TEMPLATE and IMDB poster
        if imdb:
            buttons = [
                [
                    InlineKeyboardButton('Join', url='https://t.me/PremiumMHBot'),
                    InlineKeyboardButton('Join', url='https://t.me/PremiumMHBot')
                ],
            ]
            TEMPLATE = IMDB_TEMPLATE
            cap = TEMPLATE.format(
                query=search_query,
                title=imdb['title'],
                votes=imdb['votes'],
                aka=imdb["aka"],
                seasons=imdb["seasons"],
                box_office=imdb['box_office'],
                localized_title=imdb['localized_title'],
                kind=imdb['kind'],
                imdb_id=imdb["imdb_id"],
                cast=imdb["cast"],
                runtime=imdb["runtime"],
                countries=imdb["countries"],
                certificates=imdb["certificates"],
                languages=imdb["languages"],
                director=imdb["director"],
                writer=imdb["writer"],
                producer=imdb["producer"],
                composer=imdb["composer"],
                cinematographer=imdb["cinematographer"],
                music_team=imdb["music_team"],
                distributors=imdb["distributors"],
                release_date=imdb['release_date'],
                year=imdb['year'],
                genres=imdb['genres'],
                poster=imdb['poster'],
                plot=imdb['plot'],
                rating=imdb['rating'],
                url=imdb['url'],
                **locals()
            )

            if imdb.get('poster'):
                try:
                    await bot.send_photo(chat_id=UPDATE_CHANNEL, photo=imdb['poster'], caption=cap, reply_markup=InlineKeyboardMarkup(buttons))
                except (MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty):
                    poster = imdb['poster'].replace('.jpg', '._V1_UX360.jpg')
                    await bot.send_photo(chat_id=UPDATE_CHANNEL, photo=poster, caption=cap, reply_markup=InlineKeyboardMarkup(buttons))
                except Exception as e:
                    logger.exception(e)
                    await bot.send_message(chat_id=UPDATE_CHANNEL, text=cap, reply_markup=InlineKeyboardMarkup(buttons))
            else:
                await bot.send_message(chat_id=UPDATE_CHANNEL, text=cap, reply_markup=InlineKeyboardMarkup(buttons))
        else:
            # If IMDB data and poster not found, send the specific message format
            language = languages if languages else "Unknown"
            year = year_match.group() if year_match else "Unknown"
            video_resolution = video_resolution if video_resolution else "Unknown"
            text = f"New File Added In Bot\n\n🏷 Title: {file_name}\n🎭 Genres: {language}\n📆 Year: {year}\n🌟 Video resolution: {video_resolution}"
            await bot.send_message(chat_id=UPDATE_CHANNEL, text=text, parse_mode="HTML")
