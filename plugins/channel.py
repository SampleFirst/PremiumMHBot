from pyrogram import Client, filters
from info import CHANNELS, UPDATE_CHANNEL, IMDB_TEMPLATE
from database.ia_filterdb import save_file
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors.exceptions.bad_request_400 import MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty
from utils import get_poster
from Script import script
import re

media_filter = filters.document | filters.video | filters.audio

# Your settings dictionary (update this as per your needs)
admin_settings = {
    "update": True  # Default value, you can change it
}

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
    full_file_name = media.file_name.replace('_', ' ').replace('(', ' ').replace(')', ' ').replace('.', ' ')
    file_name = ""

    # Detecting the year in 4-digit number format
    year_match = re.search(r'\b\d{4}\b', full_file_name)
    
    # Updated: Detecting series season using a more comprehensive pattern
    series_season_match = re.search(r'\b[Ss]|Season\b\d+\b', full_file_name)

    if year_match or series_season_match:
        # Extracting the part before year or series season
        file_name = re.search(r'^.*?(?=\d{4}\b|\b[Ss]|Season\b\d+\b)', full_file_name).group().strip()

    if not file_name:
        # If no year or series season is found, use the entire file name
        file_name = full_file_name
        
    # Detecting Episodes match
    series_season_episode_match = re.search(r'\b[Ee]|Episode\b\d+\b', full_file_name)

    # Detecting video resolution
    video_resolution_match = re.search(r'\b\d{3,4}p\b', file_name)
    video_resolution = video_resolution_match.group() if video_resolution_match else None
    
    LANGUAGE_KEYWORDS = {
        'English': ['English', 'english', 'Eng', 'eng'],
        'Marathi': ['Marathi', 'marathi', 'Mar', 'mar'],
        'Hindi': ['Hindi', 'hindi', 'Hin', 'hin'],
        'Malayalam': ['Malayalam', 'malayalam', 'Mal', 'mal'],
        'Kannada': ['Kannada', 'kannada', 'Kan', 'kan'],
        'Bengali': ['Bengali', 'bengali', 'Ben', 'ben'],
        'Punjabi': ['Punjabi', 'punjabi', 'Pun', 'pun'],
        'Bhojpuri': ['Bhojpuri', 'bhojpuri', 'Bhoj', 'bhoj'],
        'Korean': ['Korean', 'korean', 'Kor', 'kor'],
        'Chinese': ['Chinese', 'chinese', 'Chi', 'chi']
    }
    
    language_match = LANGUAGE_KEYWORDS
    
    if year_match:
        # Remove the year from the file name
        file_name_without_year = file_name.replace(year_match.group(), '').strip()

        # Combine the file name and year for search query
        search_query = f"{file_name_without_year} {year_match.group()}"
    else:
        # If year is not found, use entire file name for search query
        search_query = file_name

    # Check if the "update" setting is enabled
    if admin_settings["update"]:
        # Get IMDb data and poster based on search query
        imdb = await get_poster(search_query)
    
        # Send log in UPDATE_CHANNEL with IMDB_TEMPLATE and IMDb poster
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
            await bot.send_message(chat_id=UPDATE_CHANNEL, text=f"New File Added In Bot\n{file_name}")

    else: 
        # Your code to send IMDb poster with FILE_INFO format
        file_info_caption = FILE_INFO.format(
            title=f"Title 🎬: {imdb['title']}\nQuality 💿 : {video_resolution}\nAudio 🔊: {language_match}",
            search_query=search_query
        )
        if imdb.get('poster'):
            try:
                await bot.send_photo(chat_id=UPDATE_CHANNEL, photo=imdb['poster'], caption=file_info_caption)
            except (MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty):
                poster = imdb['poster'].replace('.jpg', '._V1_UX360.jpg')
                await bot.send_photo(chat_id=UPDATE_CHANNEL, photo=poster, caption=file_info_caption)
            except Exception as e:
                logger.exception(e)
                await bot.send_message(chat_id=UPDATE_CHANNEL, text=file_info_caption)
        else:
            await bot.send_message(chat_id=UPDATE_CHANNEL, text=file_info_caption)


@Client.on_message(filters.command("admin_settings"))
async def admin_settings_command(bot, message):
    # Example: "/settings update on" or "/settings update off"
    args = message.text.split()[1:]
    if len(args) == 2 and args[0] == "update":
        if args[1] == "on":
            admin_settings["update"] = True
            await bot.send_message(message.chat.id, "Update setting has been enabled.")
        elif args[1] == "off":
            admin_settings["update"] = False
            await bot.send_message(message.chat.id, "Update setting has been disabled.")
        else:
            await bot.send_message(message.chat.id, "Invalid usage. Use /settings update on or /settings update off.")
    else:
        await bot.send_message(message.chat.id, "Invalid usage. Use /settings update on or /settings update off.")
        
