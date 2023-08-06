from pyrogram import Client, filters
from info import CHANNELS, UPDATE_CHANNEL, IMDB_TEMPLATE
from database.ia_filterdb import save_file
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors.exceptions.bad_request_400 import MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty
from utils import get_poster
from database.ia_filterdb import save_file
from Script import script

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
    search_query = media.file_name.split(' (')[0]  # Using the part before the first ' (' as the search query

    # Get the IMDB data and poster based on the search query
    imdb_results = await get_poster(search_query)

    # Find the exact match using additional criteria
    imdb = None
    for result in imdb_results:
        # You can add more criteria to match the exact file, such as IMDb ID or release year
        if "series" in result.data["kind"].lower():  # Check if it's a series
            if "year" in result.data and str(result.data["year"]) in media.file_name:  # Check if release year matches
                imdb = result.data
                break
        else:
            if "year" in result.data and str(result.data["year"]) in media.file_name:  # Check if release year matches
                imdb = result.data
                break

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
        await bot.send_message(chat_id=UPDATE_CHANNEL, text=f"New File Added In Bot\n{search_query}")
