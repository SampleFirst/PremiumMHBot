import logging
import os
import re
from datetime import datetime, timedelta, date, time
from typing import List, Union

import aiohttp
import asyncio
import pytz
import requests
import random
import string
from bs4 import BeautifulSoup
from pyrogram import enums
from pyrogram.errors import UserNotParticipant
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from database.users_chats_db import db
from imdb import Cinemagoer
from info import (
    AUTH_CHANNEL,
    CHNL_LNK,
    CUSTOM_FILE_CAPTION,
    GRP_LNK,
    HOW_TO_VERIFY,
    IS_VERIFY,
    LOG_CHANNEL,
    LONG_IMDB_DESCRIPTION,
    MAX_LIST_ELM,
    PROTECT_CONTENT,
    SHORTLINK_API,
    SHORTLINK_URL,
    VERIFY2_API,
    VERIFY2_URL,
)
from Script import script

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

BTN_URL_REGEX = re.compile(
    r"(\[([^\[]+?)\]\((buttonurl|buttonalert):(?:/{0,2})(.+?)(:same)?\))"
)

imdb = Cinemagoer()
TOKENS = {}
VERIFIED = {}
BANNED = {}
SMART_OPEN = '“'
SMART_CLOSE = '”'
START_CHAR = ('\'', '"', SMART_OPEN)


# Temp DB for banned
class temp(object):
    BANNED_USERS = []
    BANNED_CHATS = []
    VERIFIED_CHATS = []
    ME = None
    CURRENT = int(os.environ.get("SKIP", 2))
    CANCEL = False
    MELCOW = {}
    U_NAME = None
    B_NAME = None
    B_LINK = None
    SETTINGS = {}
    VERIFY = {}
    SEND_ALL_TEMP = {}
    KEYWORD = {}

MONTHLY_ATTEMPTS_COUNT = False
TOTAL_ATTEMPTS_COUNT = True

# Define variables for attempt limits
MONTHLY_TOTAL_COUNT = 4
MONTHLY_SPECIFIC_COUNT = 4

DAILY_TOTAL_COUNT = 4
DAILY_SPECIFIC_COUNT = 4


async def check_limit(bot_name):
    try:
        if MONTHLY_ATTEMPTS_COUNT:
            await monthly_limit(bot_name)
        else:
            await daily_limit(bot_name)
    except Exception as e:
        logger.exception(e)


async def monthly_limit(bot_name):
    try:
        if TOTAL_ATTEMPTS_COUNT:
            total_count = await db.total_attempt()
            if total_count >= MONTHLY_TOTAL_COUNT:
                await client.send_message("hii {username} This Monthly Premium limit is exceeded, try next calendar month or contact Admin! send  /help...")
                await client.send_message(LOG_CHANNEL, text=f"He ADMINS Monthly limit is exceeded\n\nuserid = {userid}\n User name = {username} \n\n this user Trying to buy premium")
                await client.send_message(ADMINS, text=f"He ADMINS Monthly limit is exceeded\n\nuserid = {userid}\n User name = {username} \n\n this user Trying to buy premium")
        else:
            bot_count = await db.specific_attempt(bot_name)
            if bot_count >= MONTHLY_SPECIFIC_COUNT:
                await client.send_message(f"hii {username} This {bot_name} This Month Premium limit is exceeded, try next calendar month or contact Admin! send  /help...")
                await client.send_message(LOG_CHANNEL, text=f"He ADMINS Monthly limit is exceeded\n\nuserid = {userid}\n User name = {username} \n\n this user Trying to buy premium")
                await client.send_message(ADMINS, text=f"He ADMINS Monthly limit is exceeded\n\nuserid = {userid}\n User name = {username} \n\n this user Trying to buy premium")
    except Exception as e:
        logger.exception(e)


async def daily_limit(bot_name):
    try:
        if TOTAL_ATTEMPTS_COUNT:
            total_count = await db.total_attempt()
            if total_count >= DAILY_TOTAL_COUNT:
                await client.send_message(f"hii {username} This Today Premium limit is exceeded, try next Tomorrow or contact Admin! send message with /send {{text message}}...")
                await client.send_message(LOG_CHANNEL, text=f"He ADMINS daily limit is exceeded\n\nuserid = {userid}\n User name = {username} \n\n this user Trying to buy premium")
                await client.send_message(ADMINS, text=f"He ADMINS daily limit is exceeded\n\nuserid = {userid}\n User name = {username} \n\n this user Trying to buy premium")
        else:
            bot_count = await db.specific_attempt(bot_name)
            if bot_count >= DAILY_SPECIFIC_COUNT:
                await client.send_message(f"hii {username} This {bot_name} Today Premium limit is exceeded, try Tomorrow or contact Admin! send message with /send {{text message}}...")
                await client.send_message(LOG_CHANNEL, text=f"He ADMINS Today limit is exceeded\n\nuserid = {userid}\n User name = {username} \n\n this user Trying to buy premium")
                await client.send_message(ADMINS, text=f"He ADMINS Today  limit is exceeded\n\nuserid = {userid}\n User name = {username} \n\n this user Trying to buy premium")
    except Exception as e:
        logger.exception(e)

async def is_subscribed(bot, query=None, userid=None):
    try:
        if userid is None and query is not None:
            user = await bot.get_chat_member(AUTH_CHANNEL, query.from_user.id)
        else:
            user = await bot.get_chat_member(AUTH_CHANNEL, int(userid))
    except UserNotParticipant:
        pass
    except Exception as e:
        logger.exception(e)
    else:
        if user.status != enums.ChatMemberStatus.BANNED:
            return True
    return False


async def get_poster(query, bulk=False, id=False, file=None):
    if not id:
        query = query.strip().lower()
        title = query
        year = re.findall(r'[1-2]\d{3}$', query, re.IGNORECASE)
        if year:
            year = list_to_str(year[:1])
            title = query.replace(year, "").strip()
        elif file is not None:
            year = re.findall(r'[1-2]\d{3}', file, re.IGNORECASE)
            if year:
                year = list_to_str(year[:1])
        else:
            year = None
        movieid = imdb.search_movie(title.lower(), results=10)
        if not movieid:
            return None
        if year:
            filtered = list(filter(lambda k: str(k.get('year')) == str(year), movieid))
            if not filtered:
                filtered = movieid
        else:
            filtered = movieid
        movieid = list(filter(lambda k: k.get('kind') in ['movie', 'tv series'], filtered))
        if not movieid:
            movieid = filtered
        if bulk:
            return movieid[0].movieID if movieid else None
        movieid = movieid[0].movieID if movieid else None
    else:
        movieid = query
    movie = imdb.get_movie(movieid)
    if movie.get("original air date"):
        date = movie["original air date"]
    elif movie.get("year"):
        date = movie.get("year")
    else:
        date = "N/A"
    plot = ""
    if not LONG_IMDB_DESCRIPTION:
        plot = movie.get('plot')
        if plot and len(plot) > 0:
            plot = plot[0]
    else:
        plot = movie.get('plot outline')
    if plot and len(plot) > 800:
        plot = plot[0:800] + "..."
    return {
        'title': movie.get('title'),
        'votes': movie.get('votes'),
        "aka": list_to_str(movie.get("akas")),
        "seasons": movie.get("number of seasons"),
        "box_office": movie.get('box office'),
        'localized_title': movie.get('localized title'),
        'kind': movie.get("kind"),
        "imdb_id": f"tt{movie.get('imdbID')}",
        "cast": list_to_str(movie.get("cast")),
        "runtime": list_to_str(movie.get("runtimes")),
        "countries": list_to_str(movie.get("countries")),
        "certificates": list_to_str(movie.get("certificates")),
        "languages": list_to_str(movie.get("languages")),
        "director": list_to_str(movie.get("director")),
        "writer": list_to_str(movie.get("writer")),
        "producer": list_to_str(movie.get("producer")),
        "composer": list_to_str(movie.get("composer")),
        "cinematographer": list_to_str(movie.get("cinematographer")),
        "music_team": list_to_str(movie.get("music department")),
        "distributors": list_to_str(movie.get("distributors")),
        'release_date': date,
        'year': movie.get('year'),
        'genres': list_to_str(movie.get("genres")),
        'poster': movie.get('full-size cover url'),
        'plot': plot,
        'rating': str(movie.get("rating")),
        'url': f'https://www.imdb.com/title/tt{movieid}'
    }
    

async def search_gagala(text):
    user_agent = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/61.0.3163.100 Safari/537.36'
    }
    text = text.replace(" ", '+')
    url = f'https://www.google.com/search?q={text}'
    response = requests.get(url, headers=user_agent)
    response.raise_for_status()
    soup = BeautifulSoup(response.text, 'html.parser')
    titles = soup.find_all('h3')
    return [title.getText() for title in titles]


async def get_settings(group_id):
    settings = temp.SETTINGS.get(group_id)
    if not settings:
        settings = await db.get_settings(group_id)
        temp.SETTINGS[group_id] = settings
    return settings


async def save_group_settings(group_id, key, value):
    current = await get_settings(group_id)
    current[key] = value
    temp.SETTINGS[group_id] = current
    await db.update_settings(group_id, current)

def get_size(size):
    units = ["Bytes", "KB", "MB", "GB", "TB", "PB", "EB"]
    size = float(size)
    i = 0
    while size >= 1024.0 and i < len(units):
        i += 1
        size /= 1024.0
    return "%.2f %s" % (size, units[i])


def split_list(l, n):
    for i in range(0, len(l), n):
        yield l[i:i + n]


def get_file_id(msg: Message):
    if msg.media:
        for message_type in (
            "photo",
            "animation",
            "audio",
            "document",
            "video",
            "video_note",
            "voice",
            "sticker"
        ):
            obj = getattr(msg, message_type)
            if obj:
                setattr(obj, "message_type", message_type)
                return obj


def extract_user(message: Message) -> Union[int, str]:
    user_id = None
    user_first_name = None
    if message.reply_to_message:
        user_id = message.reply_to_message.from_user.id
        user_first_name = message.reply_to_message.from_user.first_name
    elif len(message.command) > 1:
        if (
            len(message.entities) > 1 and
            message.entities[1].type == enums.MessageEntityType.TEXT_MENTION
        ):
            required_entity = message.entities[1]
            user_id = required_entity.user.id
            user_first_name = required_entity.user.first_name
        else:
            user_id = message.command[1]
            user_first_name = user_id
        try:
            user_id = int(user_id)
        except ValueError:
            pass
    else:
        user_id = message.from_user.id
        user_first_name = message.from_user.first_name
    return (user_id, user_first_name)


def list_to_str(k):
    if not k:
        return "N/A"
    elif len(k) == 1:
        return str(k[0])
    elif MAX_LIST_ELM:
        k = k[:int(MAX_LIST_ELM)]
        return ' '.join(f'{elem}, ' for elem in k)
    else:
        return ' '.join(f'{elem}, ' for elem in k)


def last_online(from_user):
    time = ""
    if from_user.is_bot:
        time += "🤖 Bot 😔"
    elif from_user.status == enums.UserStatus.RECENTLY:
        time += "Recently ⏱️"
    elif from_user.status == enums.UserStatus.LAST_WEEK:
        time += "Within the last week 📅"
    elif from_user.status == enums.UserStatus.LAST_MONTH:
        time += "Within the last month 📆"
    elif from_user.status == enums.UserStatus.LONG_AGO:
        time += "A long time ago 😢"
    elif from_user.status == enums.UserStatus.ONLINE:
        time += "Currently Online 🌐"
    elif from_user.status == enums.UserStatus.OFFLINE:
        time += from_user.last_online_date.strftime("%a, %d %b %Y, %H:%M:%S")
    return time


def split_quotes(text: str) -> List:
    if not any(text.startswith(char) for char in START_CHAR):
        return text.split(None, 1)
    counter = 1
    while counter < len(text):
        if text[counter] == "\\":
            counter += 1
        elif text[counter] == text[0] or (text[0] == SMART_OPEN and text[counter] == SMART_CLOSE):
            break
        counter += 1
    else:
        return text.split(None, 1)

    key = remove_escapes(text[1:counter].strip())
    rest = text[counter + 1:].strip()
    if not key:
        key = text[0] + text[0]
    return list(filter(None, [key, rest]))


def gfilterparser(text, keyword):
    if "buttonalert" in text:
        text = (text.replace("\n", "\\n").replace("\t", "\\t"))
    buttons = []
    note_data = ""
    prev = 0
    i = 0
    alerts = []
    for match in BTN_URL_REGEX.finditer(text):
        n_escapes = 0
        to_check = match.start(1) - 1
        while to_check > 0 and text[to_check] == "\\":
            n_escapes += 1
            to_check -= 1

        if n_escapes % 2 == 0:
            note_data += text[prev:match.start(1)]
            prev = match.end(1)
            if match.group(3) == "buttonalert":
                if bool(match.group(5)) and buttons:
                    buttons[-1].append(InlineKeyboardButton(
                        text=match.group(2),
                        callback_data=f"gfilteralert:{i}:{keyword}"
                    ))
                else:
                    buttons.append([InlineKeyboardButton(
                        text=match.group(2),
                        callback_data=f"gfilteralert:{i}:{keyword}"
                    )])
                i += 1
                alerts.append(match.group(4))
            elif bool(match.group(5)) and buttons:
                buttons[-1].append(InlineKeyboardButton(
                    text=match.group(2),
                    url=match.group(4).replace(" ", "")
                ))
            else:
                buttons.append([InlineKeyboardButton(
                    text=match.group(2),
                    url=match.group(4).replace(" ", "")
                )])
        else:
            note_data += text[prev:to_check]
            prev = match.start(1) - 1
    else:
        note_data += text[prev:]

    try:
        return note_data, buttons, alerts
    except:
        return note_data, buttons, None


def parser(text, keyword):
    if "buttonalert" in text:
        text = (text.replace("\n", "\\n").replace("\t", "\\t"))
    buttons = []
    note_data = ""
    prev = 0
    i = 0
    alerts = []
    for match in BTN_URL_REGEX.finditer(text):
        n_escapes = 0
        to_check = match.start(1) - 1
        while to_check > 0 and text[to_check] == "\\":
            n_escapes += 1
            to_check -= 1

        if n_escapes % 2 == 0:
            note_data += text[prev:match.start(1)]
            prev = match.end(1)
            if match.group(3) == "buttonalert":
                if bool(match.group(5)) and buttons:
                    buttons[-1].append(InlineKeyboardButton(
                        text=match.group(2),
                        callback_data=f"alertmessage:{i}:{keyword}"
                    ))
                else:
                    buttons.append([InlineKeyboardButton(
                        text=match.group(2),
                        callback_data=f"alertmessage:{i}:{keyword}"
                    )])
                i += 1
                alerts.append(match.group(4))
            elif bool(match.group(5)) and buttons:
                buttons[-1].append(InlineKeyboardButton(
                    text=match.group(2),
                    url=match.group(4).replace(" ", "")
                ))
            else:
                buttons.append([InlineKeyboardButton(
                    text=match.group(2),
                    url=match.group(4).replace(" ", "")
                )])
        else:
            note_data += text[prev:to_check]
            prev = match.start(1) - 1
    else:
        note_data += text[prev:]

    try:
        return note_data, buttons, alerts
    except:
        return note_data, buttons, None


def remove_escapes(text: str) -> str:
    res = ""
    is_escaped = False
    for counter in range(len(text)):
        if is_escaped:
            res += text[counter]
            is_escaped = False
        elif text[counter] == "\\":
            is_escaped = True
        else:
            res += text[counter]
    return res


def humanbytes(size):
    if not size:
        return ""
    power = 2**10
    n = 0
    Dic_powerN = {0: ' ', 1: 'Ki', 2: 'Mi', 3: 'Gi', 4: 'Ti'}
    while size > power:
        size /= power
        n += 1
    return str(round(size, 2)) + " " + Dic_powerN[n] + 'B'
    
    
async def get_shortlink(chat_id, link):
    settings = await get_settings(chat_id) 
    if 'shortlink' in settings.keys():
        URL = settings['shortlink']
    else:
        URL = SHORTLINK_URL
    if 'shortlink_api' in settings.keys():
        API = settings['shortlink_api']
    else:
        API = SHORTLINK_API
    https = link.split(":")[0] 
    if "http" == https: 
        https = "https"
        link = link.replace("http", https)
    if URL == "api.shareus.in":
        url = f'https://{URL}/shortLink'
        params = {
            "token": API,
            "format": "json",
            "link": link,
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, raise_for_status=True, ssl=False) as response:
                    data = await response.json(content_type="text/html")
                    if data["status"] == "success":
                        return data["shortlink"]
                    else:
                        logger.error(f"Error: {data['message']}")
                        return f'https://{URL}/shortLink?token={API}&format=json&link={link}'
        except Exception as e:
            logger.error(e)
            return f'https://{URL}/shortLink?token={API}&format=json&link={link}'
    else:
        url = f'https://{URL}/api'
        params = {
            "api": API,
            "url": link,
        }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, raise_for_status=True, ssl=False) as response:
                    data = await response.json()
                    if data["status"] == "success":
                        return data["shortenedUrl"]
                    else:
                        logger.error(f"Error: {data['message']}")
                        if URL == 'clicksfly.com':
                            return f'https://{URL}/api?api={API}&url={link}'
                        else:
                            return f'https://{URL}/api?api={API}&link={link}'
        except Exception as e:
            logger.error(e)
            if URL == 'clicksfly.com':
                return f'https://{URL}/api?api={API}&url={link}'
            else:
                return f'https://{URL}/api?api={API}&link={link}'


async def get_verify_shorted_link(num, link):
    if int(num) == 1:
        API = SHORTLINK_API
        URL = SHORTLINK_URL
    else:
        API = VERIFY2_API
        URL = VERIFY2_URL
    https = link.split(":")[0]
    if "http" == https:
        https = "https"
        link = link.replace("http", https)

    if URL == "api.shareus.in":
        url = f"https://{URL}/shortLink"
        params = {"token": API,
                  "format": "json",
                  "link": link,
                  }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, raise_for_status=True, ssl=False) as response:
                    data = await response.json(content_type="text/html")
                    if data["status"] == "success":
                        return data["shortlink"]
                    else:
                        logger.error(f"Error: {data['message']}")
                        return f'https://{URL}/shortLink?token={API}&format=json&link={link}'

        except Exception as e:
            logger.error(e)
            return f'https://{URL}/shortLink?token={API}&format=json&link={link}'
    else:
        url = f'https://{URL}/api'
        params = {'api': API,
                  'url': link,
                  }
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, raise_for_status=True, ssl=False) as response:
                    data = await response.json()
                    if data["status"] == "success":
                        return data["shortenedUrl"]
                    else:
                        logger.error(f"Error: {data['message']}")
                        if URL == 'clicksfly.com':
                            return f'https://{URL}/api?api={API}&url={link}'
                        else:
                            return f'https://{URL}/api?api={API}&link={link}'
        except Exception as e:
            logger.error(e)
            if URL == 'clicksfly.com':
                return f'https://{URL}/api?api={API}&url={link}'
            else:
                return f'https://{URL}/api?api={API}&link={link}'


async def check_token(bot, userid, token):
    user = await bot.get_users(userid)
    if not await db.is_user_exist(user.id):
        await db.add_user(user.id, user.first_name)
        await bot.send_message(LOG_CHANNEL, script.LOG_TEXT_V.format(user.id, user.mention, date_var, time_var))
    if user.id in TOKENS.keys():
        TKN = TOKENS[user.id]
        if token in TKN.keys():
            is_used = TKN[token]
            if is_used == True:
                return False
            else:
                return True
    else:
        return False


async def get_token(bot, userid, link, fileid):
    user = await bot.get_users(userid)
    if not await db.is_user_exist(user.id):
        await db.add_user(user.id, user.first_name)
        await bot.send_message(LOG_CHANNEL, script.LOG_TEXT_V.format(user.id, user.mention, date_var, time_var))
    token = ''.join(random.choices(string.ascii_letters + string.digits, k=7))
    TOKENS[user.id] = {token: False}
    url = f"{link}verify-{user.id}-{token}-{fileid}"
    status = await get_verify_status(user.id)
    date_var = status["date"]
    time_var = status["time"]
    hour, minute, second = time_var.split(":")
    year, month, day = date_var.split("-")
    last_date, last_time = (datetime(year=int(year), month=int(month), day=int(day), hour=int(hour), minute=int(minute), second=int(second))-timedelta(hours=12)).strftime("%Y-%m-%d %H:%M:%S").split(" ")
    tz = pytz.timezone('Asia/Kolkata')
    curr_date, curr_time = datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S").split(" ")
    if last_date == curr_date:
        vr_num = 2
    else:
        vr_num = 1
    shortened_verify_url = await get_verify_shorted_link(vr_num, url)
    return str(shortened_verify_url)
    

async def send_all(bot, userid, files, ident):
    if AUTH_CHANNEL and not await is_subscribed(bot=bot, userid=userid):
        try:
            invite_link = await bot.create_chat_invite_link(int(AUTH_CHANNEL))
        except ChatAdminRequired:
            logger.error("Make sure Bot is admin in Backup Channel")
            return
        if ident == 'filep' or 'checksubp':
            pre = 'checksubp'
        else:
            pre = 'checksub'
        btn = [
            [
                InlineKeyboardButton("Join Our Backup Channel", url=invite_link.invite_link)
            ],
            [
                InlineKeyboardButton("Try Again", callback_data=f"{pre}#send_all")
            ]
        ]
        await bot.send_message(
            chat_id=userid,
            text="**You are not in our Backup Channel!**\n\nTo receive the movie files, click on the 'Join Our Backup Channel' button below and join our Backup Channel. Then click on the '↻ Try Again' button below.\n\nAfter that, you will get the movie files...",
            reply_markup=InlineKeyboardMarkup(btn),
            parse_mode=enums.ParseMode.MARKDOWN
        )
        return 'fsub'

    if IS_VERIFY and not await check_verification(bot, userid):
        btn = [
            [
                InlineKeyboardButton("🔒 Verify", url=await get_token(bot, userid, f"https://telegram.me/{temp.U_NAME}?start=", 'send_all')),
                InlineKeyboardButton("🔍 How To Verify", url=HOW_TO_VERIFY)
            ]
        ]
        await bot.send_message(
            chat_id=userid,
            text="<b>❌ You are not verified!\n\nKindly verify to continue so that you can get access to unlimited movies until 12 hours from now!</b>",
            protect_content=True if PROTECT_CONTENT else False,
            reply_markup=InlineKeyboardMarkup(btn)
        )
        return 'verify'

    for file in files:
        f_caption = file.caption
        title = file.file_name
        size = get_size(file.file_size)
        if CUSTOM_FILE_CAPTION:
            try:
                f_caption = CUSTOM_FILE_CAPTION.format(
                    file_name='' if title is None else title,
                    file_size='' if size is None else size,
                    file_caption='' if f_caption is None else f_caption
                )
            except Exception as e:
                print(e)
                f_caption = f_caption
        if f_caption is None:
            f_caption = f"{title}"
        try:
            await bot.send_cached_media(
                chat_id=userid,
                file_id=file.file_id,
                caption=f_caption,
                protect_content=True if ident == "filep" else False,
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton('Support Group', url=GRP_LNK),
                            InlineKeyboardButton('Updates Channel', url=CHNL_LNK)
                        ],
                        [
                            InlineKeyboardButton("Share And Support", url="http://t.me/share/url?url=Checkout%20%40PremiumMHBot%20for%20searching%20latest%20movies%20and%20series%20in%20multiple%20languages")
                        ]
                    ]
                )
            )
        except UserIsBlocked:
            logger.error(f"The user {userid} blocked the bot. Unblock the bot!")
            return "User has blocked the bot! Unblock to send files!"
        except PeerIdInvalid:
            logger.error("Error: Peer ID invalid!")
            return "Peer ID invalid!"
        except Exception as e:
            logger.error(f"Error: {e}")
            return f"Error: {e}"
    return 'done'


async def get_verify_status(userid):
    status = temp.VERIFY.get(userid)
    if not status:
        status = await db.get_verified(userid)
        temp.VERIFY[userid] = status
    return status


async def update_verify_status(userid, date_temp, time_temp):
    status = await get_verify_status(userid)
    status["date"] = date_temp
    status["time"] = time_temp
    temp.VERIFY[userid] = status
    await db.update_verification(userid, date_temp, time_temp)


async def verify_user(bot, userid, token):
    user = await bot.get_users(int(userid))
    if not await db.is_user_exist(user.id):
        await db.add_user(user.id, user.first_name)
        await bot.send_message(LOG_CHANNEL, script.LOG_TEXT_V.format(user.id, user.first_name, date_var, temp_time))
    TOKENS[user.id] = {token: True}
    tz = pytz.timezone('Asia/Kolkata')
    date_var = datetime.now(tz) + timedelta(hours=12)
    temp_time = date_var.strftime("%H:%M:%S")
    date_var, time_var = date_var.strftime("%Y-%m-%d"), date_var.strftime("%I:%M:%S %p")
    await update_verify_status(user.id, date_var, temp_time)


async def check_verification(bot, userid):
    user = await bot.get_users(int(userid))
    if not await db.is_user_exist(user.id):
        await db.add_user(user.id, user.first_name)
        await bot.send_message(LOG_CHANNEL, script.LOG_TEXT_V.format(user.id, user.first_name, date_var, time_var))
    tz = pytz.timezone('Asia/Kolkata')
    today = date.today()
    now = datetime.now(tz)
    curr_time = now.strftime("%H:%M:%S")
    hour1, minute1, second1 = curr_time.split(":")
    curr_time = time(int(hour1), int(minute1), int(second1))
    status = await get_verify_status(user.id)
    date_var = status["date"]
    time_var = status["time"]
    years, month, day = date_var.split('-')
    comp_date = date(int(years), int(month), int(day))
    hour, minute, second = time_var.split(":")
    comp_time = time(int(hour), int(minute), int(second))
    if comp_date < today:
        return False
    else:
        if comp_date == today:
            if comp_time < curr_time:
                return False
            else:
                return True
        else:
            return True


async def send_verification_log(bot, userid, date_var, time_var):
    user = await bot.get_users(int(userid))
    await bot.send_message(LOG_CHANNEL, script.LOG_TEXT_V.format(user.id, user.first_name, date_var, time_var))
