from pyrogram import Client, filters
from info import CHANNELS, UPDATE_CHANNEL, IMDB_TEMPLATE
from database.ia_filterdb import save_file
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
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

    full_file_name = media.file_name.replace('_', ' ').replace('(', ' ').replace(')', ' ').replace('.', ' ')
    file_name = ""
    
    year_match = re.search(r'\b\d{4}\b', full_file_name)
    series_season_match = re.search(r'\b[Ss]|Season\b\d+\b', full_file_name)

    if year_match or series_season_match:
        file_name = re.search(r'^.*?(?=\d{4}\b|\b[Ss]|Season\b\d+\b)', full_file_name).group().strip()

    if not file_name:
        file_name = full_file_name
        
    series_season_episode_match = re.search(r'\b[Ee]|Episode\b\d+\b', full_file_name)
    video_resolution_match = re.search(r'\b\d{3,4}p\b', file_name)
    video_resolution = video_resolution_match.group() if video_resolution_match else None

    if year_match:
        file_name_without_year = file_name.replace(year_match.group(), '').strip()
        search_query = f"{file_name_without_year} {year_match.group()}"
    else:
        search_query = file_name

    await imdb_search(bot, message, search_query)

async def imdb_search(bot, message, search_query):
    k = await message.reply('Searching IMDb')
    movies = await get_poster(search_query, bulk=True)
    if not movies:
        return await message.reply("No results found")
    
    btn = [
        [
            InlineKeyboardButton(
                text=f"{movie['title']} - {movie['year']}",
                callback_data=f"imdb#{movie['movieID']}",
            )
        ]
        for movie in movies
    ]
    await k.edit('Here is what I found on IMDb', reply_markup=InlineKeyboardMarkup(btn))

@Client.on_callback_query(filters.regex('^imdb'))
async def imdb_callback(bot: Client, query: CallbackQuery):
    i, movie = query.data.split('#')
    imdb = await get_poster(query=movie, id=True)
    btn = [
        [
            InlineKeyboardButton(
                text=f"{imdb['title']}",
                url=imdb['url'],
            )
        ]
    ]
    message = query.message.reply_to_message or query.message
    if imdb:
        caption = IMDB_TEMPLATE.format(
            query=imdb['title'],
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
    else:
        caption = "No Results"
    
    if imdb.get('poster'):
        try:
            await bot.send_photo(
                chat_id=UPDATE_CHANNEL,
                photo=imdb['poster'],
                caption=caption,
                reply_markup=InlineKeyboardMarkup(btn)
            )
        except (MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty):
            pic = imdb.get('poster')
            poster = pic.replace('.jpg', "._V1_UX360.jpg")
            await bot.send_photo(
                chat_id=UPDATE_CHANNEL,
                photo=poster,
                caption=caption,
                reply_markup=InlineKeyboardMarkup(btn)
            )
        except Exception as e:
            logger.exception(e)
            await bot.send_message(
                chat_id=UPDATE_CHANNEL,
                text=caption,
                reply_markup=InlineKeyboardMarkup(btn),
                disable_web_page_preview=False
            )
    else:
        await bot.send_message(
            chat_id=UPDATE_CHANNEL,
            text=caption,
            reply_markup=InlineKeyboardMarkup(btn),
            disable_web_page_preview=False
        )
    
    
