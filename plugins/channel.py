from pyrogram import Client, filters
from info import CHANNELS, UPDATE_CHANNEL, IMDB_TEMPLATE
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

    # Extracting the search query from the file name
    full_file_name = media.file_name.replace('_', ' ').replace('(', ' ').replace(')', ' ').replace('.', ' ')
    file_name = re.search(r'^.*?(?=\d{4}\b|\b[Ss]|Season\b\d+\b)', full_file_name).group().strip()

    # Send the search query to IMDb and process the results
    await imdb_search(bot, message, file_name)

# New function to perform IMDb search and display results
async def imdb_search(bot, message, search_query):
    movies = await get_poster(search_query, bulk=True)
    if not movies:
        return await bot.send_message(
            chat_id=message.chat.id,
            text="No results found"
        )
    btn = [
        [
            InlineKeyboardButton(
                text=f"{movie.get('title')} - {movie.get('year')}",
                callback_data=f"imdb#{movie.movieID}",
            )
        ]
        for movie in movies
    ]
    await bot.send_message(
        chat_id=message.from_user.id,  # Send the message to the bot's private message (PM)
        text='Here is what I found on IMDb',
        reply_markup=InlineKeyboardMarkup(btn)
    )

@Client.on_callback_query(filters.regex('^imdb'))
async def imdb_callback(bot, query):
    i, movie = query.data.split('#')
    imdb = await get_poster(query=movie, id=True)
    btn = [
        [
            InlineKeyboardButton(
                text=f"{imdb.get('title')}",
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
        
