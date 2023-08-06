from pyrogram import Client, filters
from info import CHANNELS, UPDATE_CHANNEL, IMDB_TEMPLATE
from database.ia_filterdb import save_file
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors.exceptions.bad_request_400 import MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty
from utils import get_poster
from database.ia_filterdb import save_file
from Script import script
import re
from imdb import IMDb

ia = IMDb()

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
    file_name_pattern = r"(.*?)\s\(\d{4}\)\s"
    match = re.search(file_name_pattern, media.file_name)
    if match:
        search_query = match.group(1)
    else:
        search_query = media.file_name.split(' (')[0]  # Using the part before the first ' (' as the search query

    # Get the IMDB data and poster based on the search query
    imdb_data = ia.search_movie(search_query)
    imdb = imdb_data[0] if imdb_data else None

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
            aka=", ".join(imdb.get("akas", [])),
            seasons=imdb.get("number of seasons", "N/A"),
            box_office=imdb.get('box office', "N/A"),
            localized_title=imdb.get('localized title', "N/A"),
            kind=imdb.get('kind', "N/A"),
            imdb_id=imdb.movieID,
            cast=", ".join([str(person) for person in imdb.get("cast", [])]),
            runtime=imdb.get("runtime", "N/A"),
            countries=", ".join(imdb.get("countries", [])),
            certificates=", ".join(imdb.get("certificates", [])),
            languages=", ".join(imdb.get("languages", [])),
            director=", ".join([str(person) for person in imdb.get("director", [])]),
            writer=", ".join([str(person) for person in imdb.get("writer", [])]),
            producer=", ".join([str(person) for person in imdb.get("producer", [])]),
            composer=", ".join([str(person) for person in imdb.get("composer", [])]),
            cinematographer=", ".join([str(person) for person in imdb.get("cinematographer", [])]),
            music_team=", ".join([str(person) for person in imdb.get("music department", [])]),
            distributors=", ".join(imdb.get("distributors", [])),
            release_date=imdb.get('original air date', "N/A"),
            year=imdb.get('year', "N/A"),
            genres=", ".join(imdb.get('genres', [])),
            poster=imdb.get('full-size cover url'),
            plot=imdb.get('plot outline', "N/A"),
            rating=imdb.get('rating', "N/A"),
            url=ia.get_imdbURL(imdb),
            **locals()
        )

        if imdb.get('full-size cover url'):
            try:
                await bot.send_photo(chat_id=UPDATE_CHANNEL, photo=imdb['full-size cover url'], caption=cap, reply_markup=InlineKeyboardMarkup(buttons))
            except (MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty):
                poster = imdb['full-size cover url'].replace('.jpg', '._V1_UX360.jpg')
                await bot.send_photo(chat_id=UPDATE_CHANNEL, photo=poster, caption=cap, reply_markup=InlineKeyboardMarkup(buttons))
            except Exception as e:
                logger.exception(e)
                await bot.send_message(chat_id=UPDATE_CHANNEL, text=cap, reply_markup=InlineKeyboardMarkup(buttons))
        else:
            await bot.send_message(chat_id=UPDATE_CHANNEL, text=cap, reply_markup=InlineKeyboardMarkup(buttons))
    else:
        await bot.send_message(chat_id=UPDATE_CHANNEL, text=f"New File Added In Bot\n{search_query}")
