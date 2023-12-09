7# Kanged From @TroJanZheX
import asyncio
import re
import ast
import math
import random
import logging
lock = asyncio.Lock()
from datetime import date, datetime

import pytz
from pyrogram.errors.exceptions.bad_request_400 import MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty, UserNotParticipant
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, InputMediaPhoto
from pyrogram import Client, filters, enums
from pyrogram.errors import FloodWait, UserIsBlocked, MessageNotModified, PeerIdInvalid

from info import (
    ADMINS, AUTH_CHANNEL, AUTH_USERS, SUPPORT_CHAT_ID, CUSTOM_FILE_CAPTION, MSG_ALRT, PICS, AUTH_GROUPS,
    P_TTI_SHOW_OFF, GRP_LNK, CHNL_LNK, NOR_IMG, LOG_CHANNEL_PM, SPELL_IMG, MAX_B_TN, IMDB, SINGLE_BUTTON,
    FILE_CHANNEL, FILE_FORWARD, SPELL_CHECK_REPLY, IMDB_TEMPLATE, NO_RESULTS_MSG, IS_VERIFY, HOW_TO_VERIFY, FORCE_SUB_1, FORCE_SUB_2
)
from database.connections_mdb import active_connection, all_connections, delete_connection, if_active, make_active, \
    make_inactive
from database.users_chats_db import db
from database.ia_filterdb import Media, get_file_details, get_search_results, get_bad_files
from database.filters_mdb import del_all, find_filter, get_filters
from database.gfilters_mdb import find_gfilter, get_gfilters, del_allg

from Script import script
from utils import get_size, is_subscribed, get_poster, search_gagala, temp, get_settings, save_group_settings, get_shortlink, send_all, check_verification, get_token

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)

BUTTONS = {}
SPELL_CHECK = {}


@Client.on_message(filters.group & filters.text & filters.incoming)
async def give_filter(client, message):
    if message.chat.id != SUPPORT_CHAT_ID:
        glob = await global_filters(client, message)
        if glob == False:
            manual = await manual_filters(client, message)
            if manual == False:
                settings = await get_settings(message.chat.id)
                try:
                    if settings['auto_ffilter']:
                        await auto_filter(client, message)
                except KeyError:
                    grpid = await active_connection(str(message.from_user.id))
                    await save_group_settings(grpid, 'auto_ffilter', True)
                    settings = await get_settings(message.chat.id)
                    if settings['auto_ffilter']:
                        await auto_filter(client, message)
    else: #a better logic to avoid repeated lines of code in auto_filter function
        search = message.text
        temp_files, temp_offset, total_results = await get_search_results(chat_id=message.chat.id, query=search.lower(), offset=0, filter=True)
        if total_results == 0:
            return
        else:
            return await message.reply_text(f"<b>Hᴇʏ {message.from_user.mention}, {str(total_results)} ʀᴇsᴜʟᴛs ᴀʀᴇ ғᴏᴜɴᴅ ɪɴ ᴍʏ ᴅᴀᴛᴀʙᴀsᴇ ғᴏʀ ʏᴏᴜʀ ᴏ̨ᴜᴇʀʏ {search}. Kɪɴᴅʟʏ ᴜsᴇ ɪɴʟɪɴᴇ sᴇᴀʀᴄʜ ᴏʀ ᴍᴀᴋᴇ ᴀ ɢʀᴏᴜᴘ ᴀɴᴅ ᴀᴅᴅ ᴍᴇ ᴀs ᴀᴅᴍɪɴ ᴛᴏ ɢᴇᴛ ᴍᴏᴠɪᴇ ғɪʟᴇs. Tʜɪs ɪs ᴀ sᴜᴘᴘᴏʀᴛ ɢʀᴏᴜᴘ sᴏ ᴛʜᴀᴛ ʏᴏᴜ ᴄᴀɴ'ᴛ ɢᴇᴛ ғɪʟᴇs ғʀᴏᴍ ʜᴇʀᴇ...\n\nFᴏʀ Mᴏᴠɪᴇs, Jᴏɪɴ @free_movies_all_languages</b>")

@Client.on_message(filters.private & filters.text & filters.incoming)
async def pm_text(bot, message):
    content = message.text
    user = message.from_user.first_name
    user_id = message.from_user.id
    if content.startswith("/") or content.startswith("#"):
        return  # ignore commands and hashtags
    if user_id in ADMINS:
        return  # ignore admins
    
    await message.reply_text("<b>Your message has been sent to my moderators!</b>")

    # Create buttons for the Telegram channel
    buttons = [
        [
        InlineKeyboardButton("Movies Search", url="https://t.me/+_FmlDFAh13FlNTVl")
        ],
        [
        InlineKeyboardButton("PremiumMH Update", url="https://t.me/PremiumMHUpdate")
        ]
    ]
    keyboard = InlineKeyboardMarkup(buttons)

    # Set quote to True
    quote = True

    await bot.send_message(
        chat_id=LOG_CHANNEL,
        text=f"<b>#PM_MSG\n\nName: {user}\n\nID: {user_id}\n\nMessage: {content}</b>",
        reply_markup=keyboard,
        quote=quote
    )

@Client.on_message(filters.photo & filters.private)
async def payment_screenshot_received(client, message):
    user = message.from_user.username  # Get the username of the user
    
    # Send message to user and admin about payment screenshot received
    if user:
        user_notification = "Payment screenshot received. ADMIN will check the payment."
        admin_notification = f"{user}'s payment screenshot has been received. Checking the payment..."
        await message.reply_text(user_notification)
        await client.send_message("ADMIN", admin_notification)
    else:
        # If user sends anything other than a photo
        await message.reply_text("Process cancelled!")
        await message.reply_text("Process cancelled!")
        await client.send_message("ADMIN", "Process cancelled for user who tried to buy premium plan.")
        
@Client.on_callback_query(filters.regex(r"^next"))
async def next_page(bot, query):
    ident, req, key, offset = query.data.split("_")
    if int(req) not in [query.from_user.id, 0]:
        return await query.answer(script.ALRT_TXT.format(query.from_user.first_name), show_alert=True)
    try:
        offset = int(offset)
    except:
        offset = 0
    search = BUTTONS.get(key)
    if not search:
        await query.answer(script.OLD_ALRT_TXT.format(query.from_user.first_name),show_alert=True)
        return

    files, n_offset, total = await get_search_results(query.message.chat.id, search, offset=offset, filter=True)
    try:
        n_offset = int(n_offset)
    except:
        n_offset = 0

    if not files:
        return
    settings = await get_settings(query.message.chat.id)
    temp.SEND_ALL_TEMP[query.from_user.id] = files
    if 'is_shortlink' in settings.keys():
        ENABLE_SHORTLINK = settings['is_shortlink']
    else:
        await save_group_settings(query.message.chat.id, 'is_shortlink', False)
        ENABLE_SHORTLINK = False
    if ENABLE_SHORTLINK and settings['button']:
        btn = [
            [
                InlineKeyboardButton(
                    text=f"[{get_size(file.file_size)}] {file.file_name}", url=await get_shortlink(query.message.chat.id, f"https://telegram.me/{temp.U_NAME}?start=files_{file.file_id}")
                ),
            ]
            for file in files
        ]
    elif ENABLE_SHORTLINK and not settings['button']:
        btn = [
            [
                InlineKeyboardButton(
                    text=f"{file.file_name}", url=await get_shortlink(query.message.chat.id, f"https://telegram.me/{temp.U_NAME}?start=files_{file.file_id}")
                ),
                InlineKeyboardButton(
                    text=f"{get_size(file.file_size)}",
                    url=await get_shortlink(query.message.chat.id, f"https://telegram.me/{temp.U_NAME}?start=files_{file.file_id}")
                ),
            ]
            for file in files
        ]
    elif settings['button'] and not ENABLE_SHORTLINK:
        btn = [
            [
                InlineKeyboardButton(
                    text=f"[{get_size(file.file_size)}] {file.file_name}", callback_data=f'files#{file.file_id}'
                ),
            ]
            for file in files
        ]
    else:
        btn = [
            [
                InlineKeyboardButton(
                    text=f"{file.file_name}", callback_data=f'files#{file.file_id}'
                ),
                InlineKeyboardButton(
                    text=f"{get_size(file.file_size)}",
                    callback_data=f'files_#{file.file_id}',
                ),
            ]
            for file in files
        ]
    try:
        if settings['auto_delete']:
            btn.insert(0, 
                [
                    InlineKeyboardButton(f'Info', 'reqinfo'),
                    InlineKeyboardButton(f'Movie', 'minfo'),
                    InlineKeyboardButton(f'Series', 'sinfo')
                ]
            )
        else:
            btn.insert(0, 
                [
                    InlineKeyboardButton(f'Movie', 'minfo'),
                    InlineKeyboardButton(f'Series', 'sinfo')
                ]
            )            
    except KeyError:
        await save_group_settings(query.message.chat.id, 'auto_delete', True)
        btn.insert(0, 
            [
                InlineKeyboardButton(f'Info', 'reqinfo'),
                InlineKeyboardButton(f'Movie', 'minfo'),
                InlineKeyboardButton(f'Series', 'sinfo')
            ]
        )
    try:
        if settings['max_btn']:
            if 0 < offset <= 10:
                off_set = 0
            elif offset == 0:
                off_set = None
            else:
                off_set = offset - 10
            if n_offset == 0:
                btn.append(
                    [InlineKeyboardButton("⌫ Back", callback_data=f"next_{req}_{key}_{off_set}"), InlineKeyboardButton(f"{math.ceil(int(offset)/10)+1} / {math.ceil(total/10)}", callback_data="pages")]
                )
            elif off_set is None:
                btn.append([InlineKeyboardButton("Page", callback_data="pages"), InlineKeyboardButton(f"{math.ceil(int(offset)/10)+1} / {math.ceil(total/10)}", callback_data="pages"), InlineKeyboardButton("𝐍𝐄𝐗𝐓 ➪", callback_data=f"next_{req}_{key}_{n_offset}")])
            else:
                btn.append(
                    [
                        InlineKeyboardButton("⌫ Back", callback_data=f"next_{req}_{key}_{off_set}"),
                        InlineKeyboardButton(f"{math.ceil(int(offset)/10)+1} / {math.ceil(total/10)}", callback_data="pages"),
                        InlineKeyboardButton("Next ➪", callback_data=f"next_{req}_{key}_{n_offset}")
                    ],
                )
        else:
            if 0 < offset <= int(MAX_B_TN):
                off_set = 0
            elif offset == 0:
                off_set = None
            else:
                off_set = offset - int(MAX_B_TN)
            if n_offset == 0:
                btn.append(
                    [InlineKeyboardButton("⌫ Back", callback_data=f"next_{req}_{key}_{off_set}"), InlineKeyboardButton(f"{math.ceil(int(offset)/int(MAX_B_TN))+1} / {math.ceil(total/int(MAX_B_TN))}", callback_data="pages")]
                )
            elif off_set is None:
                btn.append([InlineKeyboardButton("Page", callback_data="pages"), InlineKeyboardButton(f"{math.ceil(int(offset)/int(MAX_B_TN))+1} / {math.ceil(total/int(MAX_B_TN))}", callback_data="pages"), InlineKeyboardButton("𝐍𝐄𝐗𝐓 ➪", callback_data=f"next_{req}_{key}_{n_offset}")])
            else:
                btn.append(
                    [
                        InlineKeyboardButton("⌫ Back", callback_data=f"next_{req}_{key}_{off_set}"),
                        InlineKeyboardButton(f"{math.ceil(int(offset)/int(MAX_B_TN))+1} / {math.ceil(total/int(MAX_B_TN))}", callback_data="pages"),
                        InlineKeyboardButton("Next ➪", callback_data=f"next_{req}_{key}_{n_offset}")
                    ],
                )
    except KeyError:
        await save_group_settings(query.message.chat.id, 'max_btn', True)
        if 0 < offset <= 10:
            off_set = 0
        elif offset == 0:
            off_set = None
        else:
            off_set = offset - 10
        if n_offset == 0:
            btn.append(
                [InlineKeyboardButton("⌫ Back", callback_data=f"next_{req}_{key}_{off_set}"), InlineKeyboardButton(f"{math.ceil(int(offset)/10)+1} / {math.ceil(total/10)}", callback_data="pages")]
            )
        elif off_set is None:
            btn.append([InlineKeyboardButton("Page", callback_data="pages"), InlineKeyboardButton(f"{math.ceil(int(offset)/10)+1} / {math.ceil(total/10)}", callback_data="pages"), InlineKeyboardButton("𝐍𝐄𝐗𝐓 ➪", callback_data=f"next_{req}_{key}_{n_offset}")])
        else:
            btn.append(
                [
                    InlineKeyboardButton("⌫ Back", callback_data=f"next_{req}_{key}_{off_set}"),
                    InlineKeyboardButton(f"{math.ceil(int(offset)/10)+1} / {math.ceil(total/10)}", callback_data="pages"),
                    InlineKeyboardButton("Next ➪", callback_data=f"next_{req}_{key}_{n_offset}")
                ],
            )
    btn.insert(0, [
        InlineKeyboardButton("! Send All To PM !", callback_data=f"send_fall#files#{offset}#{req}"),
        InlineKeyboardButton("! Languages !", callback_data=f"select_lang#{req}")
    ])
    btn.insert(0, [
        InlineKeyboardButton("⚡ How to Download ⚡", url="https://t.me/How_To_Verify_PMH/2")
    ])
    try:
        await query.edit_message_reply_markup(
            reply_markup=InlineKeyboardMarkup(btn)
        )
    except MessageNotModified:
        pass
    await query.answer()

@Client.on_callback_query(filters.regex(r"^lang"))
async def language_check(bot, query):
    _, userid, language = query.data.split("#")
    if int(userid) not in [query.from_user.id, 0]:
        return await query.answer(script.ALRT_TXT.format(query.from_user.first_name), show_alert=True)
    if language == "unknown":
        return await query.answer("Select any language from the buttons below!", show_alert=True)
    movie = temp.KEYWORD.get(query.from_user.id)
    if not movie:
        return await query.answer(script.OLD_ALRT_TXT.format(query.from_user.first_name), show_alert=True)
    if language != "home":
        movie = f"{movie} {language}"
    files, offset, total_results = await get_search_results(query.message.chat.id, movie, offset=0, filter=True)
    if files:
        settings = await get_settings(query.message.chat.id)
        temp.SEND_ALL_TEMP[query.from_user.id] = files
        if 'is_shortlink' in settings.keys():
            ENABLE_SHORTLINK = settings['is_shortlink']
        else:
            await save_group_settings(query.message.chat.id, 'is_shortlink', False)
            ENABLE_SHORTLINK = False
        pre = 'filep' if settings['file_secure'] else 'file'
        if ENABLE_SHORTLINK and settings['button']:
            btn = [
                [
                    InlineKeyboardButton(
                        text=f"[{get_size(file.file_size)}] {file.file_name}", url=await get_shortlink(query.message.chat.id, f"https://telegram.me/{temp.U_NAME}?start=files_{file.file_id}")
                    ),
                ]
                for file in files
            ]
        elif ENABLE_SHORTLINK and not settings['button']:
            btn = [
                [
                    InlineKeyboardButton(
                        text=f"{file.file_name}",
                        url=await get_shortlink(query.message.chat.id, f"https://telegram.me/{temp.U_NAME}?start=files_{file.file_id}")
                    ),
                    InlineKeyboardButton(
                        text=f"{get_size(file.file_size)}",
                        url=await get_shortlink(query.message.chat.id, f"https://telegram.me/{temp.U_NAME}?start=files_{file.file_id}")
                    ),
                ]
                for file in files
            ]
        elif settings['button'] and not ENABLE_SHORTLINK:
            btn = [
                [
                    InlineKeyboardButton(
                        text=f"[{get_size(file.file_size)}] {file.file_name}", callback_data=f'{pre}#{file.file_id}'
                    ),
                ]
                for file in files
            ]
        else:
            btn = [
                [
                    InlineKeyboardButton(
                        text=f"{file.file_name}",
                        callback_data=f'{pre}#{file.file_id}',
                    ),
                    InlineKeyboardButton(
                        text=f"{get_size(file.file_size)}",
                        callback_data=f'{pre}#{file.file_id}',
                    ),
                ]
                for file in files
            ]

        try:
            if settings['auto_delete']:
                btn.insert(0, 
                    [
                        InlineKeyboardButton(f'Info', 'reqinfo'),
                        InlineKeyboardButton(f'Movie', 'minfo'),
                        InlineKeyboardButton(f'Series', 'sinfo')
                    ]
                )

            else:
                btn.insert(0, 
                    [
                        InlineKeyboardButton(f'Movie', 'minfo'),
                        InlineKeyboardButton(f'Series', 'sinfo')
                    ]
                )
                    
        except KeyError:
            await save_group_settings(query.message.chat.id, 'auto_delete', True)
            btn.insert(0, 
                [
                    InlineKeyboardButton(f'Info', 'reqinfo'),
                    InlineKeyboardButton(f'Movie', 'minfo'),
                    InlineKeyboardButton(f'Series', 'sinfo')
                ]
            )
        
        btn.insert(0, [
            InlineKeyboardButton("! Send All to PM !", callback_data=f"send_fall#{pre}#{0}#{userid}"),
            InlineKeyboardButton("! Languages !", callback_data=f"select_lang#{userid}")
        ])

        btn.insert(0, [
        InlineKeyboardButton("⚡ Check Bot PM ⚡", url="https://t.me/How_To_Verify_PMH/2")
        ])

        if offset != "":
            key = f"{query.message.chat.id}-{query.message.id}"
            BUTTONS[key] = movie
            req = userid
            try:
                if settings['max_btn']:
                    btn.append(
                        [InlineKeyboardButton("PAGE", callback_data="pages"), InlineKeyboardButton(text=f"1/{math.ceil(int(total_results)/10)}",callback_data="pages"), InlineKeyboardButton(text="NEXT ➪",callback_data=f"next_{req}_{key}_{offset}")]
                    )

                else:
                    btn.append(
                        [InlineKeyboardButton("PAGE", callback_data="pages"), InlineKeyboardButton(text=f"1/{math.ceil(int(total_results)/int(MAX_B_TN))}",callback_data="pages"), InlineKeyboardButton(text="NEXT ➪",callback_data=f"next_{req}_{key}_{offset}")]
                    )
            except KeyError:
                await save_group_settings(query.message.chat.id, 'max_btn', True)
                btn.append(
                    [InlineKeyboardButton("PAGE", callback_data="pages"), InlineKeyboardButton(text=f"1/{math.ceil(int(total_results)/10)}",callback_data="pages"), InlineKeyboardButton(text="NEXT ➪",callback_data=f"next_{req}_{key}_{offset}")]
                )
        else:
            btn.append(
                [InlineKeyboardButton(text="NO MORE PAGES AVAILABLE",callback_data="pages")]
            )
        try:
            await query.edit_message_reply_markup(
                reply_markup=InlineKeyboardMarkup(btn)
            )
        except MessageNotModified:
            pass
        await query.answer()
    else:
        return await query.answer(f"Sorry, no files found for your query: {movie}.", show_alert=True)
    
@Client.on_callback_query(filters.regex(r"^select_lang"))
async def select_language(bot, query):
    _, userid = query.data.split("#")
    if int(userid) not in [query.from_user.id, 0]:
        return await query.answer(script.ALRT_TXT.format(query.from_user.first_name), show_alert=True)

    btn = [
        [
            InlineKeyboardButton("Select Your Desired Language ↓", callback_data=f"lang#{userid}#unknown")
        ],
        [
            InlineKeyboardButton("English", callback_data=f"lang#{userid}#eng"),
            InlineKeyboardButton("Hindi", callback_data=f"lang#{userid}#hin")
        ],
        [
            InlineKeyboardButton("Marathi", callback_data=f"lang#{userid}#mar"),
            InlineKeyboardButton("Tamil", callback_data=f"lang#{userid}#tam")
        ],
        [
            InlineKeyboardButton("Kannada", callback_data=f"lang#{userid}#kan"),
            InlineKeyboardButton("Telugu", callback_data=f"lang#{userid}#tel")
        ],
        [
            InlineKeyboardButton("Malayalam", callback_data=f"lang#{userid}#mal"),
            InlineKeyboardButton("Gujarati", callback_data=f"lang#{userid}#guj")
        ],
        [
            InlineKeyboardButton("Punjabi", callback_data=f"lang#{userid}#pun"),
            InlineKeyboardButton("Bengali", callback_data=f"lang#{userid}#ben")
        ],
        [
            InlineKeyboardButton("Multi Audio", callback_data=f"lang#{userid}#multi"),
            InlineKeyboardButton("Dual Audio", callback_data=f"lang#{userid}#dual")
        ],
        [
            InlineKeyboardButton("Go Back", callback_data=f"group#{userid}#home")
        ]
    ]

    try:
        await query.edit_message_reply_markup(
            reply_markup=InlineKeyboardMarkup(btn)
        )
    except MessageNotModified:
        pass

    await query.answer()


@Client.on_callback_query(filters.regex(r"^spol"))
async def advantage_spoll_choker(bot, query):
    _, user, movie_ = query.data.split('#')
    movies = SPELL_CHECK.get(query.message.reply_to_message.id)
    if not movies:
        return await query.answer(script.OLD_ALRT_TXT.format(query.from_user.first_name), show_alert=True)
    if int(user) != 0 and query.from_user.id != int(user):
        return await query.answer(script.ALRT_TXT.format(query.from_user.first_name), show_alert=True)
    if movie_ == "close_spellcheck":
        return await query.message.delete()
    movie = movies[(int(movie_))]
    await query.answer(script.TOP_ALRT_MSG)
    gl = await global_filters(bot, query.message, text=movie)
    if gl == False:
        k = await manual_filters(bot, query.message, text=movie)
        if k == False:
            files, offset, total_results = await get_search_results(query.message.chat.id, movie, offset=0, filter=True)
            if files:
                k = (movie, files, offset, total_results)
                await auto_filter(bot, query, k)
            else:
                reqstr1 = query.from_user.id if query.from_user else 0
                reqstr = await bot.get_users(reqstr1)
                if NO_RESULTS_MSG:
                    await bot.send_message(chat_id=LOG_CHANNEL_PM, text=(script.NORSLTS.format(reqstr.id, reqstr.mention, movie)))
                k = await query.message.edit(script.MVE_NT_FND)
                await asyncio.sleep(10)
                await k.delete()


@Client.on_callback_query()
async def cb_handler(client: Client, query: CallbackQuery):
    is_admin = query.from_user.id in ADMINS
    if query.data == "close_data":
        await query.message.delete()
    elif query.data == "gfiltersdeleteallconfirm":
        await del_allg(query.message, 'gfilters')
        await query.answer("✅ Done!")
        return
    elif query.data == "gfiltersdeleteallcancel":
        await query.message.reply_to_message.delete()
        await query.message.delete()
        await query.answer("❌ Process Cancelled!")
        return
    elif query.data == "delallconfirm":
        userid = query.from_user.id
        chat_type = query.message.chat.type

        if chat_type == enums.ChatType.PRIVATE:
            grpid = await active_connection(str(userid))
            if grpid is not None:
                grp_id = grpid
                try:
                    chat = await client.get_chat(grpid)
                    title = chat.title
                except:
                    await query.message.edit_text("Make sure I'm present in your group!", quote=True)
                    return await query.answer(MSG_ALRT)
            else:
                await query.message.edit_text(
                    "I'm not connected to any groups!\nCheck /connections or connect to any groups.",
                    quote=True
                )
                return await query.answer(MSG_ALRT)

        elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
            grp_id = query.message.chat.id
            title = query.message.chat.title

        else:
            return await query.answer(MSG_ALRT)

        st = await client.get_chat_member(grp_id, userid)
        if (st.status == enums.ChatMemberStatus.OWNER) or (str(userid) in ADMINS):
            await del_all(query.message, grp_id, title)
        else:
            await query.answer("You need to be a Group Owner or an Auth User to do that!", show_alert=True)

    elif query.data == "delallcancel":
        userid = query.from_user.id
        chat_type = query.message.chat.type
    
        if chat_type == enums.ChatType.PRIVATE:
            await query.message.reply_to_message.delete()
            await query.message.delete()
    
        elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
            grp_id = query.message.chat.id
            st = await client.get_chat_member(grp_id, userid)
            if (st.status == enums.ChatMemberStatus.OWNER) or (str(userid) in ADMINS):
                await query.message.delete()
                try:
                    await query.message.reply_to_message.delete()
                except:
                    pass
            else:
                await query.answer("🚫 That's not for you!", show_alert=True)
    elif "groupcb" in query.data:
        await query.answer()
    
        group_id = query.data.split(":")[1]
    
        act = query.data.split(":")[2]
        hr = await client.get_chat(int(group_id))
        title = hr.title
        user_id = query.from_user.id
    
        if act == "":
            stat = "CONNECT"
            cb = "connectcb"
        else:
            stat = "DISCONNECT"
            cb = "disconnect"
    
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(f"{stat}", callback_data=f"{cb}:{group_id}"),
             InlineKeyboardButton("DELETE", callback_data=f"deletecb:{group_id}")],
            [InlineKeyboardButton("BACK", callback_data="backcb")]
        ])
    
        await query.message.edit_text(
            f"🏢 Group Name: **{title}**\n🆔 Group ID: `{group_id}`",
            reply_markup=keyboard,
            parse_mode=enums.ParseMode.MARKDOWN
        )
        return await query.answer(MSG_ALRT)

    elif "connectcb" in query.data:
        await query.answer()
    
        group_id = query.data.split(":")[1]
    
        hr = await client.get_chat(int(group_id))
    
        title = hr.title
    
        user_id = query.from_user.id
    
        mkact = await make_active(str(user_id), str(group_id))
    
        if mkact:
            await query.message.edit_text(
                f"✅ Connected to **{title}**",
                parse_mode=enums.ParseMode.MARKDOWN
            )
        else:
            await query.message.edit_text('⚠️ Some error occurred!', parse_mode=enums.ParseMode.MARKDOWN)
        return await query.answer(MSG_ALRT)
    elif "disconnect" in query.data:
        await query.answer()
    
        group_id = query.data.split(":")[1]
    
        hr = await client.get_chat(int(group_id))
    
        title = hr.title
        user_id = query.from_user.id
    
        mkinact = await make_inactive(str(user_id))
    
        if mkinact:
            await query.message.edit_text(
                f"❌ Disconnected from **{title}**",
                parse_mode=enums.ParseMode.MARKDOWN
            )
        else:
            await query.message.edit_text(
                f"⚠️ Some error occurred!",
                parse_mode=enums.ParseMode.MARKDOWN
            )
        return await query.answer(MSG_ALRT)
    elif "deletecb" in query.data:
        await query.answer()
    
        user_id = query.from_user.id
        group_id = query.data.split(":")[1]
    
        delcon = await delete_connection(str(user_id), str(group_id))
    
        if delcon:
            await query.message.edit_text(
                "✅ Successfully deleted connection!"
            )
        else:
            await query.message.edit_text(
                f"⚠️ Some error occurred!",
                parse_mode=enums.ParseMode.MARKDOWN
            )
        return await query.answer(MSG_ALRT)

    elif query.data == "backcb":
        await query.answer()
    
        userid = query.from_user.id
    
        groupids = await all_connections(str(userid))
        if groupids is None:
            await query.message.edit_text(
                "⚠️ There are no active connections! Connect to some groups first."
            )
            return await query.answer(MSG_ALRT)
        buttons = []
        for groupid in groupids:
            try:
                ttl = await client.get_chat(int(groupid))
                title = ttl.title
                active = await if_active(str(userid), str(groupid))
                act = " - ACTIVE" if active else ""
                buttons.append(
                    [
                        InlineKeyboardButton(
                            text=f"{title}{act}", callback_data=f"groupcb:{groupid}:{act}"
                        )
                    ]
                )
            except:
                pass
        if buttons:
            await query.message.edit_text(
                "🔗 Your connected group details:\n\n",
                reply_markup=InlineKeyboardMarkup(buttons)
            )
    elif "gfilteralert" in query.data:
        grp_id = query.message.chat.id
        i = query.data.split(":")[1]
        keyword = query.data.split(":")[2]
        reply_text, btn, alerts, fileid = await find_gfilter('gfilters', keyword)
        if alerts is not None:
            alerts = ast.literal_eval(alerts)
            alert = alerts[int(i)]
            alert = alert.replace("\\n", "\n").replace("\\t", "\t")
            await query.answer(alert, show_alert=True)
    elif "alertmessage" in query.data:
        grp_id = query.message.chat.id
        i = query.data.split(":")[1]
        keyword = query.data.split(":")[2]
        reply_text, btn, alerts, fileid = await find_filter(grp_id, keyword)
        if alerts is not None:
            alerts = ast.literal_eval(alerts)
            alert = alerts[int(i)]
            alert = alert.replace("\\n", "\n").replace("\\t", "\t")
            await query.answer(alert, show_alert=True)
    if query.data.startswith("file"):
        clicked = query.from_user.id
        try:
            typed = query.message.reply_to_message.from_user.id
        except:
            typed = query.from_user.id
        ident, file_id = query.data.split("#")
        files_ = await get_file_details(file_id)
        if not files_:
            return await query.answer('❌ No such file exists.')
        files = files_[0]
        title = files.file_name
        size = get_size(files.file_size)
        f_caption = files.caption
        settings = await get_settings(query.message.chat.id)
        if CUSTOM_FILE_CAPTION:
            try:
                f_caption = CUSTOM_FILE_CAPTION.format(file_name='' if title is None else title,
                                                       file_size='' if size is None else size,
                                                       file_caption='' if f_caption is None else f_caption)
            except Exception as e:
                logger.exception(e)
            f_caption = f_caption
        if f_caption is None:
            f_caption = f"{files.file_name}"
        
        try:
            if AUTH_CHANNEL and not await is_subscribed(client, query):
                if clicked == typed:
                    await query.answer(url=f"https://t.me/{temp.U_NAME}?start={ident}_{file_id}")
                    return
                else:
                    await query.answer(f"Hey {query.from_user.first_name}, this is not your movie request. Request yours!", show_alert=True)
            elif settings['botpm']:
                if clicked == typed:
                    await query.answer(url=f"https://t.me/{temp.U_NAME}?start={ident}_{file_id}")
                    return
                else:
                    await query.answer(f"Hey {query.from_user.first_name}, this is not your movie request. Request yours!", show_alert=True)
            else:
                if clicked == typed:
                    if IS_VERIFY and not await check_verification(client, query.from_user.id):
                        btn = [[
                            InlineKeyboardButton("🔒 Verify", url=await get_token(client, query.from_user.id, f"https://telegram.me/{temp.U_NAME}?start=", file_id)),
                            InlineKeyboardButton("🔍 How To Verify", url=HOW_TO_VERIFY)
                        ]]
                        await client.send_message(
                            chat_id=query.from_user.id,
                            text="<b>❌ You are not verified!</b>\n\nKindly verify to continue so that you can get access to unlimited movies until 12 hours from now!",
                            protect_content=True if ident == 'checksubp' else False,
                            disable_web_page_preview=True,
                            parse_mode=enums.ParseMode.HTML,
                            reply_markup=InlineKeyboardMarkup(btn)
                        )
                        return await query.answer("Hey, you have not verified today. You have to verify to continue. Check my PM to verify and get files!", show_alert=True)
                    else:
                        file_send = await client.send_cached_media(
                            chat_id=FILE_CHANNEL,
                            file_id=file_id,
                            caption=script.CHANNEL_CAP.format(query.from_user.mention, title, query.message.chat.title),
                            protect_content=True if ident == "filep" else False,
                            reply_markup=InlineKeyboardMarkup(
                                [
                                    [
                                        InlineKeyboardButton("🔥 Channel 🔥", url=(CHNL_LNK))
                                    ]
                                ]
                            )
                        )
                        Joel_tgx = await query.message.reply_text(
                            script.FILE_MSG.format(query.from_user.mention, title, size),
                            parse_mode=enums.ParseMode.HTML,
                            reply_markup=InlineKeyboardMarkup(
                                [
                                    [
                                        InlineKeyboardButton('📥 Download Link 📥', url=file_send.link)
                                    ],
                                    [
                                        InlineKeyboardButton("⚠️ Can't Access ❓ Click Here ⚠️", url=(FILE_FORWARD))
                                    ]
                                ]
                            )
                        )
                        if settings['auto_delete']:
                            await asyncio.sleep(600)
                            await Joel_tgx.delete()
                            await file_send.delete()
                else:
                    return await query.answer(f"Hey {query.from_user.first_name}, this is not your movie request. Request yours!", show_alert=True)
        except UserIsBlocked:
            await query.answer('Unblock the bot!', show_alert=True)
        except PeerIdInvalid:
            await query.answer(url=f"https://t.me/{temp.U_NAME}?start={ident}_{file_id}")
        except Exception as e:
            await query.answer(url=f"https://t.me/{temp.U_NAME}?start={ident}_{file_id}")

    elif query.data.startswith("checksub"):
        if AUTH_CHANNEL and not await is_subscribed(client, query):
            await query.answer("Join our backup channel, mahnn! 😒", show_alert=True)
            return
        ident, file_id = query.data.split("#")
        if file_id == "send_all":
            send_files = temp.SEND_ALL_TEMP.get(query.from_user.id)
            is_over = await send_all(client, query.from_user.id, send_files, ident)
            if is_over == 'done':
                return await query.answer(f"Hey {query.from_user.first_name}, all files on this page have been sent successfully to your PM! 📥", show_alert=True)
            elif is_over == 'fsub':
                return await query.answer("Hey, you are not joined in my backup channel. Check my PM to join and get files! 📢", show_alert=True)
            elif is_over == 'verify':
                return await query.answer("Hey, you have not verified today. You have to verify to continue. Check my PM to verify and get files! ✅", show_alert=True)
            else:
                return await query.answer(f"Error: {is_over}", show_alert=True)
        files_ = await get_file_details(file_id)
        if not files_:
            return await query.answer('No such file exists.')
        files = files_[0]
        title = files.file_name
        size = get_size(files.file_size)
        f_caption = files.caption
        if CUSTOM_FILE_CAPTION:
            try:
                f_caption = CUSTOM_FILE_CAPTION.format(file_name='' if title is None else title,
                                                       file_size='' if size is None else size,
                                                       file_caption='' if f_caption is None else f_caption)
            except Exception as e:
                logger.exception(e)
                f_caption = f_caption
        if f_caption is None:
            f_caption = f"{title}"
        await query.answer()
        if IS_VERIFY and not await check_verification(client, query.from_user.id):
            btn = [[
                InlineKeyboardButton("🔒 Verify", url=await get_token(client, query.from_user.id, f"https://telegram.me/{temp.U_NAME}?start=", file_id)),
                InlineKeyboardButton("🔍 How To Verify", url=HOW_TO_VERIFY)
            ]]
            await client.send_message(
                chat_id=query.from_user.id,
                text="<b>❌ You are not verified!\nKindly verify to continue so that you can get access to unlimited movies until 12 hours from now! 🕐</b>",
                protect_content=True if ident == 'checksubp' else False,
                disable_web_page_preview=True,
                parse_mode=enums.ParseMode.HTML,
                reply_markup=InlineKeyboardMarkup(btn)
            )
            return
        file_send = await client.send_cached_media(
            chat_id=FILE_CHANNEL,
            file_id=file_id,
            caption=script.CHANNEL_CAP.format(query.from_user.mention, title, query.message.chat.title),
            protect_content=True if ident == 'checksubp' else False,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("🔥 Channel 🔥", url=(CHNL_LNK))
                    ]
                ]
            )
        )

    elif query.data == "pages":
        await query.answer()
    
    elif query.data.startswith("send_fall"):
        temp_var, ident, offset, userid = query.data.split("#")
        if int(userid) not in [query.from_user.id, 0]:
            return await query.answer(script.ALRT_TXT.format(query.from_user.first_name), show_alert=True)
        files = temp.SEND_ALL_TEMP.get(query.from_user.id)
        is_over = await send_all(client, query.from_user.id, files, ident)
        if is_over == 'done':
            return await query.answer(f"Hey {query.from_user.first_name}! All files on this page have been sent successfully to your PM! ✉️", show_alert=True)
        elif is_over == 'fsub':
            return await query.answer("Hey, you are not joined in my backup channel. Check my PM to join and get files! 📢", show_alert=True)
        elif is_over == 'verify':
            return await query.answer("Hey, you have not verified today. You have to verify to continue. Check my PM to verify and get files! ✅", show_alert=True)
        else:
            return await query.answer(f"Error: {is_over}", show_alert=True)
    
    elif query.data.startswith("killfilesdq"):
        ident, keyword = query.data.split("#")
        await query.message.edit_text(f"Fetching files for your query '{keyword}' on DB... Please wait... ⌛️")
        files, total = await get_bad_files(keyword)
        await query.message.edit_text(f"Found {total} files for your query '{keyword}'! File deletion process is starting. This may take some time. ⚠️")
        deleted = 0
        try:
            for file in files:
                file_ids = file.file_id
                file_name = file.file_name
                result = await Media.collection.delete_one({'_id': file_ids})
                if result.deleted_count:
                    logger.info(f"File found for your query '{keyword}'! Successfully deleted {file_name} from the database. ❌")
                deleted += 1
                if deleted % 20 == 0:
                    await query.message.edit_text(f"Process started for deleting files from DB. Successfully deleted {str(deleted)} files from DB for your query '{keyword}'! Please wait... ⌛️")
        except Exception as e:
            logger.exception(e)
            await query.message.edit_text(f"Error: {e}")
        else:
            await query.message.edit_text(f"Process completed for file deletion! Successfully deleted {str(deleted)} files from DB for your query '{keyword}'. ✅")
      
    elif query.data == "premium_plans":
        plans_message = """🏷 ᴄᴜʀʀᴇɴᴛ ᴘʟᴀɴ: free
            ☞ ᴅᴀɪʟʏ ᴜᴘʟᴏᴀᴅ: 0 / 5.0 GB
            ☞ ᴛɪᴍᴇ ɢᴀᴘ: 6 minutes
            ☞ 4ɢʙ sᴜᴘᴘᴏʀᴛ: False
            ☞ sᴄʀᴇᴇɴsʜᴏᴛs: False
            ☞ sᴀᴍᴘʟᴇ ᴠɪᴅᴇᴏ: False
            ☞ ᴘᴀʀᴀʟʟᴇʟ ᴘʀᴏᴄᴇss: 1 
            ☞ ᴠᴀʟɪᴅɪᴛʏ: Life Time"""
            await query.message.edit_text(caption=plans_message, reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("Silver Plan", callback_data="silver_plan"),
                        InlineKeyboardButton("Gold Plan", callback_data="gold_plan"),
                    ],
                    [
                        InlineKeyboardButton("Diamond Plan", callback_data="diamond_plan"),
                        InlineKeyboardButton("Platinum Plan", callback_data="platinum_plan"),
                    ]
                ]
            )
        )

    elif query.data == "silver_plan":
        plans_message = """🏷 ᴄᴜʀʀᴇɴᴛ ᴘʟᴀɴ: free
            ☞ ᴅᴀɪʟʏ ᴜᴘʟᴏᴀᴅ: 0 / 5.0 GB
            ☞ ᴛɪᴍᴇ ɢᴀᴘ: 6 minutes
            ☞ 4ɢʙ sᴜᴘᴘᴏʀᴛ: False
            ☞ sᴄʀᴇᴇɴsʜᴏᴛs: False
            ☞ sᴀᴍᴘʟᴇ ᴠɪᴅᴇᴏ: False
            ☞ ᴘᴀʀᴀʟʟᴇʟ ᴘʀᴏᴄᴇss: 1 
            ☞ ᴠᴀʟɪᴅɪᴛʏ: Life Time"""
            await query.answer("Set to Uploaded!")
            await query.message.edit_text(caption=plans_message, reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("Upgrade To Silver", callback_data="upgrade_silver"),
                    ],
                    [
                        InlineKeyboardButton("Cancel", callback_data="cancel_plan")
                    ]
                ]
            )
        )
    elif query.data == "gold_plan":
        plans_message = """🏷 ᴄᴜʀʀᴇɴᴛ ᴘʟᴀɴ: free
            ☞ ᴅᴀɪʟʏ ᴜᴘʟᴏᴀᴅ: 0 / 5.0 GB
            ☞ ᴛɪᴍᴇ ɢᴀᴘ: 6 minutes
            ☞ 4ɢʙ sᴜᴘᴘᴏʀᴛ: False
            ☞ sᴄʀᴇᴇɴsʜᴏᴛs: False
            ☞ sᴀᴍᴘʟᴇ ᴠɪᴅᴇᴏ: False
            ☞ ᴘᴀʀᴀʟʟᴇʟ ᴘʀᴏᴄᴇss: 1 
            ☞ ᴠᴀʟɪᴅɪᴛʏ: Life Time"""
            await query.answer("Set to Uploaded!")
            await query.message.edit_text(caption=plans_message, reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("Upgrade To Gold", callback_data="upgrade_gold"),
                    ],
                    [
                        InlineKeyboardButton("Cancel", callback_data="cancel_plan")
                    ]
                ]
            )
        )
    elif query.data == "diamond_plan":
        plans_message = """🏷 ᴄᴜʀʀᴇɴᴛ ᴘʟᴀɴ: free
            ☞ ᴅᴀɪʟʏ ᴜᴘʟᴏᴀᴅ: 0 / 5.0 GB
            ☞ ᴛɪᴍᴇ ɢᴀᴘ: 6 minutes
            ☞ 4ɢʙ sᴜᴘᴘᴏʀᴛ: False
            ☞ sᴄʀᴇᴇɴsʜᴏᴛs: False
            ☞ sᴀᴍᴘʟᴇ ᴠɪᴅᴇᴏ: False
            ☞ ᴘᴀʀᴀʟʟᴇʟ ᴘʀᴏᴄᴇss: 1 
            ☞ ᴠᴀʟɪᴅɪᴛʏ: Life Time"""
            await query.answer("Set to Uploaded!")
            await query.message.edit_text(caption=plans_message, reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("Upgrade To Diamond", callback_data="upgrade_diamond"),
                    ],
                    [
                        InlineKeyboardButton("Cancel", callback_data="cancel_plan")
                    ]
                ]
            )
        )
    elif query.data == "platinum_plan":
        plans_message = """🏷 ᴄᴜʀʀᴇɴᴛ ᴘʟᴀɴ: free
            ☞ ᴅᴀɪʟʏ ᴜᴘʟᴏᴀᴅ: 0 / 5.0 GB
            ☞ ᴛɪᴍᴇ ɢᴀᴘ: 6 minutes
            ☞ 4ɢʙ sᴜᴘᴘᴏʀᴛ: False
            ☞ sᴄʀᴇᴇɴsʜᴏᴛs: False
            ☞ sᴀᴍᴘʟᴇ ᴠɪᴅᴇᴏ: False
            ☞ ᴘᴀʀᴀʟʟᴇʟ ᴘʀᴏᴄᴇss: 1 
            ☞ ᴠᴀʟɪᴅɪᴛʏ: Life Time"""
            await query.answer("Set to Uploaded!")
            await query.message.edit_text(caption=plans_message, reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("Upgrade To Platinum", callback_data="upgrade_platinum"),
                    ],
                    [
                        InlineKeyboardButton("Cancel", callback_data="cancel_plan")
                    ]
                ]
            )
        )
    elif query.data == "upgrade_silver|upgrade_gold|upgrade_diamond|upgrade_platinum":
        upgrade_message = "Please choose your preferred duration"
        plan_type = callback_query.data.split('_')[1]  # Extract 'silver' or 'gold'
        
        prices = []
        if plan_type == "silver":
            prices.extend([
                InlineKeyboardButton("39 ₹ = 1 Month", callback_data="upgrade_1_month_silver"),
                InlineKeyboardButton("69 ₹ = 2 Months", callback_data="upgrade_2_months_silver")
            ])
        elif plan_type == "gold":
            prices.extend([
                InlineKeyboardButton("60 ₹ = 1 Month", callback_data="upgrade_1_month_gold"),
                InlineKeyboardButton("109 ₹ = 2 Months", callback_data="upgrade_2_months_gold")
            ])
        elif plan_type == "diamond":
            prices.extend([
                InlineKeyboardButton("99 ₹ = 1 Month", callback_data="upgrade_1_month_diamond"),
                InlineKeyboardButton("179 ₹ = 2 Months", callback_data="upgrade_2_months_diamond")
            ])
        elif plan_type == "platinum":
            prices.extend([
                InlineKeyboardButton("199 ₹ = 1 Month", callback_data="upgrade_1_month_platinum"),
                InlineKeyboardButton("369 ₹ = 2 Months", callback_data="upgrade_2_months_platinum")
            ])
        else:
            prices = []  # Handle invalid plan_type
            
        await query.answer("Set to Uploaded!")
        await query.message.edit_text(
            text=upgrade_message,
            reply_markup=InlineKeyboardMarkup([prices])
        )

    elif query.data == "upgrade_1_month|upgrade_2_months":
        user = callback_query.from_user.username  # Get the username of the user
        
        # Extract plan type and duration from callback_data
        callback_data_parts = callback_query.data.split('_')
        plan_type = callback_data_parts[2]  # Extract 'silver', 'gold', 'diamond', or 'platinum'
        duration = "1 Month" if "1_month" in callback_data_parts[1] else "2 Months"
        
        # Determine plan amount based on plan_type and duration
        if duration == "1 Month":
            if plan_type == "silver":
                plan_amount = "39 ₹"
            elif plan_type == "gold":
                plan_amount = "60 ₹"
            elif plan_type == "diamond":
                plan_amount = "99 ₹"
            elif plan_type == "platinum":
                plan_amount = "199 ₹"
        else:  # 2 Months
            if plan_type == "silver":
                plan_amount = "69 ₹"
            elif plan_type == "gold":
                plan_amount = "109 ₹"
            elif plan_type == "diamond":
                plan_amount = "179 ₹"
            elif plan_type == "platinum":
                plan_amount = "369 ₹"
        
        # Calculate the validity date (30 days from today for 1-month plan, 60 days for 2-month plan)
        days_validity = 30 if "1_month" in callback_query.data else 60
        validity_date = datetime.datetime.now() + datetime.timedelta(days=days_validity)
        validity_formatted = validity_date.strftime("%B %d, %Y")
        
        payment_message = f"Payment Process\n\n➢ Plan: {plan_type.capitalize()} Plan\n➢ Amount: {plan_amount}\n➢ Validity till: {validity_formatted}"
        await query.answer("Set to Uploaded!")
        await query.message.edit_text(
            text=payment_message,
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton("Confirmed", callback_data="confirmed_payment")
                    ],
                    [
                        InlineKeyboardButton("Back", callback_data="back_to_upgrade")
                    ]
                ]
            )
        )
        
        # Send ADMINS message about the user's intent to buy
        admin_message = f"{user} is trying to buy the {plan_type.capitalize()} plan."
        await client.send_message("ADMINS", admin_message)
    
    
    elif query.data == "confirmed_payment":
        user = callback_query.from_user.username  # Get the username of the user
        
        # Send confirmation message to the user
        confirmation_message = "Confirm Payment\n\nSend here your successful payment screenshot."
        await query.answer("Set to Uploaded!")
        await query.message.edit_text(text=confirmation_message)
    
        # Notify user to send payment screenshot
        user_notification = "Please send your payment screenshot now."
        await client.send_message(user, user_notification)
        
    elif query.data == "deletefiletype":
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("📥 Document", callback_data="delete_filetype_document"),
                    InlineKeyboardButton("🎬 Video", callback_data="delete_filetype_video"),
                ],
                [
                    InlineKeyboardButton("🎧 Audio", callback_data="delete_filetype_audio"),
                    InlineKeyboardButton("🗜️ Zip", callback_data="delete_filetype_zip"),
                ],
                [
                    InlineKeyboardButton("❎ Cancel", callback_data="dft_cancel"),
                ]
            ]
        )
    
        await query.message.edit_text(
            "🗑 Select the type of files you want to delete!\n\n🗑 This will delete related files from the database:",
            reply_markup=keyboard,
        )    
    
    elif query.data.startswith("opnsetgrp"):
        ident, grp_id = query.data.split("#")
        userid = query.from_user.id if query.from_user else None
        st = await client.get_chat_member(grp_id, userid)
        if (
            st.status != enums.ChatMemberStatus.ADMINISTRATOR
            and st.status != enums.ChatMemberStatus.OWNER
            and str(userid) not in ADMINS
        ):
            await query.answer("⚠️ You don't have the rights to do this!", show_alert=True)
            return
        title = query.message.chat.title
        settings = await get_settings(grp_id)
        if settings is not None:
            buttons = [
                [
                    InlineKeyboardButton('Filter Button', callback_data=f'setgs#button#{settings["button"]}#{str(grp_id)}'),
                    InlineKeyboardButton('🔘 Single' if settings["button"] else '🔳 Double',callback_data=f'setgs#button#{settings["button"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Redirect To', callback_data=f'setgs#botpm#{settings["botpm"]}#{str(grp_id)}'),
                    InlineKeyboardButton('🤖 Bot PM' if settings["botpm"] else '📣 Channel',callback_data=f'setgs#botpm#{settings["botpm"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Protect Content',callback_data=f'setgs#file_secure#{settings["file_secure"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✅ On' if settings["file_secure"] else '❌ Off',callback_data=f'setgs#file_secure#{settings["file_secure"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('IMDb', callback_data=f'setgs#imdb#{settings["imdb"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✅ On' if settings["imdb"] else '❌ Off',callback_data=f'setgs#imdb#{settings["imdb"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Send Update', callback_data=f'setgs#imdb#{settings["update"]}#{str(grp_id)}'),
                    InlineKeyboardButton('IMDB' if settings["update"] else 'Format+Photo',callback_data=f'setgs#imdb#{settings["update"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Spell Check',callback_data=f'setgs#spell_check#{settings["spell_check"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✅ On' if settings["spell_check"] else '❌ Off',callback_data=f'setgs#spell_check#{settings["spell_check"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Welcome Msg', callback_data=f'setgs#welcome#{settings["welcome"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✅ On' if settings["welcome"] else '❌ Off',callback_data=f'setgs#welcome#{settings["welcome"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Auto-Delete',callback_data=f'setgs#auto_delete#{settings["auto_delete"]}#{str(grp_id)}'),
                    InlineKeyboardButton('🕒 10 Mins' if settings["auto_delete"] else '❌ Off',callback_data=f'setgs#auto_delete#{settings["auto_delete"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Auto-Filter',callback_data=f'setgs#auto_ffilter#{settings["auto_ffilter"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✅ On' if settings["auto_ffilter"] else '❌ Off',callback_data=f'setgs#auto_ffilter#{settings["auto_ffilter"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Max Buttons',callback_data=f'setgs#max_btn#{settings["max_btn"]}#{str(grp_id)}'),
                    InlineKeyboardButton('🔟 10' if settings["max_btn"] else f'{MAX_B_TN}',callback_data=f'setgs#max_btn#{settings["max_btn"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('ShortLink',callback_data=f'setgs#is_shortlink#{settings["is_shortlink"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✅ On' if settings["is_shortlink"] else '❌ Off',callback_data=f'setgs#is_shortlink#{settings["is_shortlink"]}#{str(grp_id)}')
                ]
            ]
            reply_markup = InlineKeyboardMarkup(buttons)
            await query.message.edit_text(
                text=f"<b>Change your settings for {title} as you wish ⚙️</b>",
                disable_web_page_preview=True,
                parse_mode=enums.ParseMode.HTML
            )
            await query.message.edit_reply_markup(reply_markup)
        
    elif query.data.startswith("opnsetpm"):
        ident, grp_id = query.data.split("#")
        userid = query.from_user.id if query.from_user else None
        st = await client.get_chat_member(grp_id, userid)
        if (
            st.status != enums.ChatMemberStatus.ADMINISTRATOR
            and st.status != enums.ChatMemberStatus.OWNER
            and str(userid) not in ADMINS
        ):
            await query.answer("⚠️ You don't have the rights to do this!", show_alert=True)
            return
        title = query.message.chat.title
        settings = await get_settings(grp_id)
        btn2 = [[
            InlineKeyboardButton("Check PM", url=f"t.me/{temp.U_NAME}")
        ]]
        reply_markup = InlineKeyboardMarkup(btn2)
        await query.message.edit_text(f"<b>Your settings menu for {title} has been sent to your PM</b>")
        await query.message.edit_reply_markup(reply_markup)
        if settings is not None:
            buttons = [
                [
                    InlineKeyboardButton('Filter Button',callback_data=f'setgs#button#{settings["button"]}#{str(grp_id)}'),
                    InlineKeyboardButton('🔘 Single' if settings["button"] else '🔳 Double',callback_data=f'setgs#button#{settings["button"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Redirect To', callback_data=f'setgs#botpm#{settings["botpm"]}#{str(grp_id)}'),
                    InlineKeyboardButton('🤖 Bot PM' if settings["botpm"] else '📣 Channel',callback_data=f'setgs#botpm#{settings["botpm"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Protect Content',callback_data=f'setgs#file_secure#{settings["file_secure"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✅ On' if settings["file_secure"] else '❌ Off',callback_data=f'setgs#file_secure#{settings["file_secure"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('IMDb', callback_data=f'setgs#imdb#{settings["imdb"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✅ On' if settings["imdb"] else '❌ Off',callback_data=f'setgs#imdb#{settings["imdb"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Send Update', callback_data=f'setgs#imdb#{settings["update"]}#{str(grp_id)}'),
                    InlineKeyboardButton('IMDB' if settings["update"] else 'Format+Photo',callback_data=f'setgs#imdb#{settings["update"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Spell Check',callback_data=f'setgs#spell_check#{settings["spell_check"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✅ On' if settings["spell_check"] else '❌ Off',callback_data=f'setgs#spell_check#{settings["spell_check"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Welcome Msg',callback_data=f'setgs#welcome#{settings["welcome"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✅ On' if settings["welcome"] else '❌ Off',callback_data=f'setgs#welcome#{settings["welcome"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Auto-Delete',callback_data=f'setgs#auto_delete#{settings["auto_delete"]}#{str(grp_id)}'),
                    InlineKeyboardButton('🕒 10 Mins' if settings["auto_delete"] else '❌ Off',callback_data=f'setgs#auto_delete#{settings["auto_delete"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Auto-Filter',callback_data=f'setgs#auto_ffilter#{settings["auto_ffilter"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✅ On' if settings["auto_ffilter"] else '❌ Off',callback_data=f'setgs#auto_ffilter#{settings["auto_ffilter"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Max Buttons',callback_data=f'setgs#max_btn#{settings["max_btn"]}#{str(grp_id)}'),
                    InlineKeyboardButton('🔟 10' if settings["max_btn"] else f'{MAX_B_TN}',callback_data=f'setgs#max_btn#{settings["max_btn"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('ShortLink',callback_data=f'setgs#is_shortlink#{settings["is_shortlink"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✅ On' if settings["is_shortlink"] else '❌ Off',callback_data=f'setgs#is_shortlink#{settings["is_shortlink"]}#{str(grp_id)}')
                ]
            ]
            reply_markup = InlineKeyboardMarkup(buttons)
            await client.send_message(
                chat_id=userid,
                text=f"<b>Change your settings for {title} as you wish ⚙️</b>",
                reply_markup=reply_markup,
                disable_web_page_preview=True,
                parse_mode=enums.ParseMode.HTML,
                reply_to_message_id=query.message.id
            )

    elif query.data.startswith("show_option"):
        ident, from_user = query.data.split("#")
        btn = [
            [
                InlineKeyboardButton("🚫 Unavailable", callback_data=f"unavailable#{from_user}"),
                InlineKeyboardButton("✅ Uploaded", callback_data=f"uploaded#{from_user}")
            ],
            [
                InlineKeyboardButton("🔁 Already Available", callback_data=f"already_available#{from_user}")
            ]
        ]
        btn2 = [
            [
                InlineKeyboardButton("👀 View Status", url=f"{query.message.link}")
            ]
        ]
        if query.from_user.id in ADMINS:
            user = await client.get_users(from_user)
            reply_markup = InlineKeyboardMarkup(btn)
            await query.message.edit_reply_markup(reply_markup)
            await query.answer("Here are the options!")
        else:
            await query.answer("You don't have sufficient rights to do this!", show_alert=True)
    
    elif query.data.startswith("unavailable"):
        ident, from_user = query.data.split("#")
        btn = [
            [
                InlineKeyboardButton("⚠️ Unavailable ⚠️", callback_data=f"unalert#{from_user}")
            ]
        ]
        btn2 = [
            [
                InlineKeyboardButton("👀 View Status", url=f"{query.message.link}")
            ]
        ]
        if query.from_user.id in ADMINS:
            user = await client.get_users(from_user)
            reply_markup = InlineKeyboardMarkup(btn)
            content = query.message.text
            await query.message.edit_text(f"<b><strike>{content}</strike></b>")
            await query.message.edit_reply_markup(reply_markup)
            await query.answer("Set to Unavailable!")
            try:
                await client.send_message(chat_id=int(from_user), text=f"<b>Hey {user.mention}, Sorry, your request is unavailable. So our moderators can't upload it.</b>", reply_markup=InlineKeyboardMarkup(btn2))
            except UserIsBlocked:
                await client.send_message(chat_id=int(SUPPORT_CHAT_ID), text=f"<b>Hey {user.mention}, Sorry, your request is unavailable. So our moderators can't upload it.\n\nNote: This message is sent to this group because you've blocked the bot. To send this message to your PM, must unblock the bot.</b>", reply_markup=InlineKeyboardMarkup(btn2))
        else:
            await query.answer("You don't have sufficient rights to do this!", show_alert=True)
    
    elif query.data.startswith("uploaded"):
        ident, from_user = query.data.split("#")
        btn = [
            [
                InlineKeyboardButton("✅ Uploaded ✅", callback_data=f"upalert#{from_user}")
            ]
        ]
        btn2 = [
            [
                InlineKeyboardButton("👀 View Status", url=f"{query.message.link}")
            ]
        ]
        if query.from_user.id in ADMINS:
            user = await client.get_users(from_user)
            reply_markup = InlineKeyboardMarkup(btn)
            content = query.message.text
            await query.message.edit_text(f"<b><strike>{content}</strike></b>")
            await query.message.edit_reply_markup(reply_markup)
            await query.answer("Set to Uploaded!")
            try:
                await client.send_message(
                    chat_id=int(from_user),
                    text=f"<b>Hey {user.mention}, your request has been uploaded by our moderators. Please search again.</b>",
                    reply_markup=InlineKeyboardMarkup(btn2)
                )
            except UserIsBlocked:
                await client.send_message(
                    chat_id=int(SUPPORT_CHAT_ID),
                    text=f"<b>Hey {user.mention}, your request has been uploaded by our moderators. Please search again.</b>\n\nNote: This message is sent to this group because you've blocked the bot. To send this message to your PM, you must unblock the bot.",
                    reply_markup=InlineKeyboardMarkup(btn2)
                )
        else:
            await query.answer("You don't have sufficient rights to do this!", show_alert=True)
    
    elif query.data.startswith("already_available"):
        ident, from_user = query.data.split("#")
        btn = [
            [
                InlineKeyboardButton("🟢 Already Available 🟢", callback_data=f"alalert#{from_user}")
            ]
        ]
        btn2 = [
            [
                InlineKeyboardButton("👀View Status", url=f"{query.message.link}")
            ]
        ]
        if query.from_user.id in ADMINS:
            user = await client.get_users(from_user)
            reply_markup = InlineKeyboardMarkup(btn)
            content = query.message.text
            await query.message.edit_text(f"<b><strike>{content}</strike></b>")
            await query.message.edit_reply_markup(reply_markup)
            await query.answer("Set to Already Available!")
            try:
                await client.send_message(
                    chat_id=int(from_user),
                    text=f"<b>Hey {user.mention}, your request is already available on our bot's database. Please search again.</b>",
                    reply_markup=InlineKeyboardMarkup(btn2)
                )
            except UserIsBlocked:
                await client.send_message(
                    chat_id=int(SUPPORT_CHAT_ID),
                    text=f"<b>Hey {user.mention}, your request is already available on our bot's database. Please search again.</b>\n\nNote: This message is sent to this group because you've blocked the bot. To send this message to your PM, you must unblock the bot.",
                    reply_markup=InlineKeyboardMarkup(btn2)
                )
        else:
            await query.answer("You don't have sufficient rights to do this!", show_alert=True)
    
    elif query.data.startswith("alalert"):
        ident, from_user = query.data.split("#")
        if int(query.from_user.id) == int(from_user):
            user = await client.get_users(from_user)
            await query.answer(f"🔔 Hey {user.first_name}! Your request is already available!", show_alert=True)
        else:
            await query.answer("⛔️ You don't have sufficient rights to do this!", show_alert=True)
    
    elif query.data.startswith("upalert"):
        ident, from_user = query.data.split("#")
        if int(query.from_user.id) == int(from_user):
            user = await client.get_users(from_user)
            await query.answer(f"📤 Hey {user.first_name}! Your request is uploaded!", show_alert=True)
        else:
            await query.answer("⛔️ You don't have sufficient rights to do this!", show_alert=True)
            
    elif query.data.startswith("unalert"):
        ident, from_user = query.data.split("#")
        if int(query.from_user.id) == int(from_user):
            user = await client.get_users(from_user)
            await query.answer(f"❌ Hey {user.first_name}! Your request is unavailable!", show_alert=True)
        else:
            await query.answer("⛔️ You don't have sufficient rights to do this!", show_alert=True)
    
    elif query.data == "reqinfo":
        await query.answer(text="ℹ️ Here is the information about the request:", show_alert=True)
    
    elif query.data == "minfo":
        await query.answer(text="ℹ️ Here is the detailed information:", show_alert=True)
    
    elif query.data == "sinfo":
        await query.answer(text="ℹ️ Here is the summary information:", show_alert=True)
    

    elif query.data == "start":
        if is_admin:
            admin_buttons = [
                [
                    InlineKeyboardButton('➕ Add Me To Your Group ➕', url=f'http://t.me/{temp.U_NAME}?startgroup=true')
                ],
                [
                    InlineKeyboardButton('🤖 More Bots', callback_data="more_bots"),
                    InlineKeyboardButton('🌟 Support Group', url=GRP_LNK)
                ],
                [
                    InlineKeyboardButton('❓ Help', callback_data='help'),
                    InlineKeyboardButton('ℹ️ About', callback_data='about'),
                    InlineKeyboardButton('🔎 Inline Search', switch_inline_query_current_chat='')
                ],
                [
                    InlineKeyboardButton('📣 Join Updates Channel 📣', url=CHNL_LNK)
                ],
                [
                    InlineKeyboardButton('🔒 Admin Settings', callback_data='admin_settings')
                ]
            ]
            reply_markup = InlineKeyboardMarkup(admin_buttons)
            tz = pytz.timezone('Asia/Kolkata')
            now = datetime.now(tz)
            current_time = now.strftime('%Y-%m-%d %I:%M:%S %p')  # Update time to show date and time
            caption = script.ADMIN_START_TXT.format(
                admin=query.from_user.mention,
                bot=temp.B_LINK,
                total_users=await db.total_users_count(),
                total_chat=await db.total_chat_count(),
                daily_users=await db.daily_users_count(datetime.now().date()),
                daily_chats=await db.daily_chats_count(datetime.now().date()),
                current_time=current_time
            )
        else:
            regular_buttons = [
                [
                    InlineKeyboardButton('Premium List', callback_data="list"),
                    InlineKeyboardButton("Premium Plans", callback_data="premium_plans")
                ],
                [
                    InlineKeyboardButton('Bots Premium', callback_data="bots"),
                    InlineKeyboardButton('Database Premium', callback_data="database")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(regular_buttons)
            caption = script.START_TXT.format(user=query.from_user.mention, bot=temp.B_LINK)

        await client.edit_message_media(
            query.message.chat.id,
            query.message.id,
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text=caption,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
        await query.answer(MSG_ALRT)

    elif query.data == "filters":
        buttons = [
            [
                InlineKeyboardButton('Manual Filter', callback_data='manuelfilter'),
                InlineKeyboardButton('Auto Filter', callback_data='autofilter')
            ],
            [
                InlineKeyboardButton('Back', callback_data='help'),
                InlineKeyboardButton('Global Filters', callback_data='global_filters')
            ]
        ]
            
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text=script.ALL_FILTERS.format(query.from_user.mention),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    
    elif query.data == "global_filters":
        buttons = [
            [
                InlineKeyboardButton('Back', callback_data='filters')
            ]
        ]
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.GFILTER_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
        
    elif query.data == "help":
        buttons = [
            [
                InlineKeyboardButton('Filters', callback_data='filters'),
                InlineKeyboardButton('File Store', callback_data='store_file')
            ],
            [
                InlineKeyboardButton('Connection', callback_data='coct'),
                InlineKeyboardButton('Extra Mods', callback_data='extra')
            ],
            [
                InlineKeyboardButton('Home', callback_data='start'),
                InlineKeyboardButton('Status', callback_data='stats')
            ]
        ]
            
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text=script.HELP_TXT.format(query.from_user.mention),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
        
    elif query.data == "about":
        buttons = [
            [
                InlineKeyboardButton('Support Group', url=GRP_LNK),
                InlineKeyboardButton('Source Code', callback_data='source')
            ],
            [
                InlineKeyboardButton('Home', callback_data='start'),
                InlineKeyboardButton('Close', callback_data='close_data')
            ]
        ]
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.ABOUT_TXT.format(temp.B_NAME),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )

    elif query.data == "source":
        buttons = [
            [
                InlineKeyboardButton('Back', callback_data='about'),
                InlineKeyboardButton('More Bots', url='https://t.me/+9Z1w2KOebaliYzdl')
            ]
        ]
                     
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text=script.SOURCE_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
        
    elif query.data == "manuelfilter":
        buttons = [
            [
                InlineKeyboardButton('Back', callback_data='filters'),
                InlineKeyboardButton('Buttons', callback_data='button')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text=script.MANUELFILTER_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
        
    elif query.data == "button":
        buttons = [
            [
                InlineKeyboardButton('Back', callback_data='manuelfilter')
            ]
        ]
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.BUTTON_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )

    elif query.data == "autofilter":
        buttons = [
            [
                InlineKeyboardButton('Back', callback_data='filters')
            ]
        ]
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.AUTOFILTER_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    
    elif query.data == "coct":
        buttons = [
            [
                InlineKeyboardButton('Back', callback_data='help')
            ]
        ]
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.CONNECTION_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    
    elif query.data == "extra":
        buttons = [
            [
                InlineKeyboardButton('Back', callback_data='help'),
                InlineKeyboardButton('Admin', callback_data='admin')
            ]
        ]
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.EXTRAMOD_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
        
    elif query.data == "store_file":
        buttons = [
            [
                InlineKeyboardButton('Back', callback_data='help')
            ]
        ]
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.FILE_STORE_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    
    elif query.data == "admin":
        buttons = [
            [
                InlineKeyboardButton('Back', callback_data='extra')
            ]
        ]
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.ADMIN_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    
    elif query.data == "stats":
        buttons = [
            [
                InlineKeyboardButton('Back', callback_data='help'),
                InlineKeyboardButton('Refresh', callback_data='rfrsh')
            ]
        ]
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        total = await Media.count_documents()
        users = await db.total_users_count()
        chats = await db.total_chat_count()
        monsize = await db.get_db_size()
        free = 536870912 - monsize
        monsize = get_size(monsize)
        free = get_size(free)
        await query.message.edit_text(
            text=script.STATUS_TXT.format(total, users, chats, monsize, free),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    
    elif query.data == "rfrsh":
        await query.answer("Fetching MongoDB Database")
        buttons = [
            [
                InlineKeyboardButton('Back', callback_data='help'),
                InlineKeyboardButton('Refresh', callback_data='rfrsh')
            ]
        ]
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        total = await Media.count_documents()
        users = await db.total_users_count()
        chats = await db.total_chat_count()
        monsize = await db.get_db_size()
        free = 536870912 - monsize
        monsize = get_size(monsize)
        free = get_size(free)
        await query.message.edit_text(
            text=script.STATUS_TXT.format(total, users, chats, monsize, free),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )

    elif query.data == "more_bots":
        btn = [
            [
                InlineKeyboardButton("Back", callback_data="start"),
                InlineKeyboardButton("Bots Channel", url="https://t.me/+9Z1w2KOebaliYzdl")
            ]
        ]
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        reply_markup = InlineKeyboardMarkup(btn)
        await query.message.edit_text(
            text=script.MORE_BOTS,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "bots":
        buttons = [
            [
                InlineKeyboardButton('Movies Bot', callback_data='mbot'),
                InlineKeyboardButton('Anime Bot', callback_data='abot')
            ],
            [
                InlineKeyboardButton('Rename Bot', callback_data='rbot'),
                InlineKeyboardButton('Yt & Insta Bot', callback_data='yibot')
            ],
            [
                InlineKeyboardButton('Back', callback_data='start')
            ]
        ]           
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text=script.ALL_FILTERS.format(query.from_user.mention),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    
    elif query.data == "database":
        buttons = [
            [
                InlineKeyboardButton('Movies Database', callback_data='mdb'),
                InlineKeyboardButton('Anime Database', callback_data='adb')
            ],
            [
                InlineKeyboardButton('TV Show Database', callback_data='tvsdb'),
                InlineKeyboardButton('Back', callback_data='start')
            ]
        ]           
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text=script.ALL_FILTERS.format(query.from_user.mention),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
        
    elif query.data == "list":
        buttons = [
            [
                InlineKeyboardButton('Back', callback_data='filters')
            ]
        ]
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        reply_markup = InlineKeyboardMarkup(buttons)
        await query.message.edit_text(
            text=script.GFILTER_TXT,
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
        
    elif query.data == "mbot":
        buttons = [
            [
                InlineKeyboardButton('Buy it', callback_data='buym'),
                InlineKeyboardButton('Disclimer', callback_data='disclimer')
            ]
        ]
            
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text=script.HELP_TXT.format(query.from_user.mention),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "abot":
        buttons = [
            [
                InlineKeyboardButton('Buy it', callback_data='buya'),
                InlineKeyboardButton('Disclimer', callback_data='disclimer')
            ]
        ]
            
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text=script.HELP_TXT.format(query.from_user.mention),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "rbot":
        buttons = [
            [
                InlineKeyboardButton('Buy it', callback_data='buyr'),
                InlineKeyboardButton('Disclimer', callback_data='disclimer')
            ]
        ]
            
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text=script.HELP_TXT.format(query.from_user.mention),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "yibot":
        buttons = [
            [
                InlineKeyboardButton('Buy it', callback_data='buyyi'),
                InlineKeyboardButton('Disclimer', callback_data='disclimer')
            ]
        ]
            
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text=script.HELP_TXT.format(query.from_user.mention),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
        
    elif query.data == "mdb":
        buttons = [
            [
                InlineKeyboardButton('Buy it', callback_data='buymdb'),
                InlineKeyboardButton('Disclimer', callback_data='disclimer')
            ]
        ]
            
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text=script.HELP_TXT.format(query.from_user.mention),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "adb":
        buttons = [
            [
                InlineKeyboardButton('Buy it', callback_data='buyadb'),
                InlineKeyboardButton('Disclimer', callback_data='disclimer')
            ]
        ]
            
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text=script.HELP_TXT.format(query.from_user.mention),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
    elif query.data == "tvsdb":
        buttons = [
            [
                InlineKeyboardButton('Buy it', callback_data='buytvsdb'),
                InlineKeyboardButton('Disclimer', callback_data='disclimer')
            ]
        ]
            
        reply_markup = InlineKeyboardMarkup(buttons)
        await client.edit_message_media(
            query.message.chat.id, 
            query.message.id, 
            InputMediaPhoto(random.choice(PICS))
        )
        await query.message.edit_text(
            text=script.HELP_TXT.format(query.from_user.mention),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML
        )
        
    elif query.data.startswith("setgs"):
        ident, set_type, status, grp_id = query.data.split("#")
        grpid = await active_connection(str(query.from_user.id))
    
        if set_type == 'is_shortlink' and query.from_user.id not in ADMINS:
            return await query.answer(
                text=f"Hey {query.from_user.first_name}, you can't change shortlink settings for your group!\n\nIt's an admin-only setting!",
                show_alert=True
            )
    
        if str(grp_id) != str(grpid) and query.from_user.id not in ADMINS:
            await query.message.edit("Your active connection has been changed. Go to /connections and change your active connection.")
            return await query.answer(MSG_ALRT)
    
        if status == "True":
            await save_group_settings(grpid, set_type, False)
        else:
            await save_group_settings(grpid, set_type, True)
    
        settings = await get_settings(grpid)
    
        if settings is not None:
            buttons = [
                [
                    InlineKeyboardButton('Filter Button', callback_data=f'setgs#button#{settings["button"]}#{str(grp_id)}'),
                    InlineKeyboardButton('🔘 Single' if settings["button"] else '🔳 Double', callback_data=f'setgs#button#{settings["button"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Redirect To', callback_data=f'setgs#botpm#{settings["botpm"]}#{str(grp_id)}'),
                    InlineKeyboardButton('🤖 Bot PM' if settings["botpm"] else '📣 Channel', callback_data=f'setgs#botpm#{settings["botpm"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Protect Content', callback_data=f'setgs#file_secure#{settings["file_secure"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✅ On' if settings["file_secure"] else '❌ Off', callback_data=f'setgs#file_secure#{settings["file_secure"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('IMDb', callback_data=f'setgs#imdb#{settings["imdb"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✅ On' if settings["imdb"] else '❌ Off', callback_data=f'setgs#imdb#{settings["imdb"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Spell Check', callback_data=f'setgs#spell_check#{settings["spell_check"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✅ On' if settings["spell_check"] else '❌ Off', callback_data=f'setgs#spell_check#{settings["spell_check"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Welcome Msg', callback_data=f'setgs#welcome#{settings["welcome"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✅ On' if settings["welcome"] else '❌ Off', callback_data=f'setgs#welcome#{settings["welcome"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Auto-Delete', callback_data=f'setgs#auto_delete#{settings["auto_delete"]}#{str(grp_id)}'),
                    InlineKeyboardButton('🕒 10 Mins' if settings["auto_delete"] else '❌ Off', callback_data=f'setgs#auto_delete#{settings["auto_delete"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Auto-Filter', callback_data=f'setgs#auto_ffilter#{settings["auto_ffilter"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✅ On' if settings["auto_ffilter"] else '❌ Off', callback_data=f'setgs#auto_ffilter#{settings["auto_ffilter"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('Max Buttons', callback_data=f'setgs#max_btn#{settings["max_btn"]}#{str(grp_id)}'),
                    InlineKeyboardButton('🔟 10' if settings["max_btn"] else f'{MAX_B_TN}', callback_data=f'setgs#max_btn#{settings["max_btn"]}#{str(grp_id)}')
                ],
                [
                    InlineKeyboardButton('ShortLink', callback_data=f'setgs#is_shortlink#{settings["is_shortlink"]}#{str(grp_id)}'),
                    InlineKeyboardButton('✅ On' if settings["is_shortlink"] else '❌ Off', callback_data=f'setgs#is_shortlink#{settings["is_shortlink"]}#{str(grp_id)}')
                ]
            ]
            reply_markup = InlineKeyboardMarkup(buttons)
            await query.message.edit_reply_markup(reply_markup)
    await query.answer(MSG_ALRT)
    
    
async def auto_filter(client, msg, spoll=False):
    reqstr1 = msg.from_user.id if msg.from_user else 0
    reqstr = await client.get_users(reqstr1)
    if not spoll:
        message = msg
        settings = await get_settings(message.chat.id)
        if message.text.startswith("/"):
            return  # ignore commands
        if re.findall("((^\/|^,|^!|^\.|^[\U0001F600-\U000E007F]).*)", message.text):
            return
        if len(message.text) < 100:
            search = message.text
            files, offset, total_results = await get_search_results(message.chat.id, search.lower(), offset=0, filter=True)
            if not files:
                if settings["spell_check"]:
                    return await advantage_spell_check(client, msg)
                else:
                    if NO_RESULTS_MSG:
                        await client.send_message(chat_id=LOG_CHANNEL_PM, text=(script.NORSLTS.format(reqstr.id, reqstr.mention, search)))
                    return
        else:
            return
    else:
        message = msg.message.reply_to_message  # msg will be callback query
        search, files, offset, total_results = spoll
        settings = await get_settings(message.chat.id)
    temp.SEND_ALL_TEMP[message.from_user.id] = files
    temp.KEYWORD[message.from_user.id] = search
    if 'is_shortlink' in settings.keys():
        ENABLE_SHORTLINK = settings['is_shortlink']
    else:
        await save_group_settings(message.chat.id, 'is_shortlink', False)
        ENABLE_SHORTLINK = False
    pre = 'filep' if settings['file_secure'] else 'file'
    if ENABLE_SHORTLINK and settings["button"]:
        btn = [
            [
                InlineKeyboardButton(
                    text=f"[{get_size(file.file_size)}] {file.file_name}", url=await get_shortlink(message.chat.id, f"https://telegram.me/{temp.U_NAME}?start=files_{file.file_id}")
                ),
            ]
            for file in files
        ]

    elif ENABLE_SHORTLINK and not settings["button"]:
        btn = [
            [
                InlineKeyboardButton(
                    text=f"{file.file_name}",
                    url=await get_shortlink(message.chat.id, f"https://telegram.me/{temp.U_NAME}?start=files_{file.file_id}")
                ),
                InlineKeyboardButton(
                    text=f"{get_size(file.file_size)}",
                    url=await get_shortlink(message.chat.id, f"https://telegram.me/{temp.U_NAME}?start=files_{file.file_id}")
                ),
            ]
            for file in files
        ]
    elif settings["button"] and not ENABLE_SHORTLINK:
        btn = [
            [
                InlineKeyboardButton(
                    text=f"[{get_size(file.file_size)}] {file.file_name}",
                    callback_data=f'{pre}#{file.file_id}'
                ),
            ]
            for file in files
        ]
    else:
        btn = [
            [
                InlineKeyboardButton(
                    text=f"{file.file_name}",
                    callback_data=f'{pre}#{file.file_id}',
                ),
                InlineKeyboardButton(
                    text=f"{get_size(file.file_size)}",
                    callback_data=f'{pre}#{file.file_id}',
                ),
            ]
            for file in files
        ]
    
    try:
        if settings.get('auto_delete'):
            btn.insert(0,
                [
                    InlineKeyboardButton('Info', callback_data='reqinfo'),
                    InlineKeyboardButton('Movie', callback_data='minfo'),
                    InlineKeyboardButton('Series', callback_data='sinfo')
                ]
            )
        else:
            btn.insert(0,
                [
                    InlineKeyboardButton('Movie', callback_data='minfo'),
                    InlineKeyboardButton('Series', callback_data='sinfo')
                ]
            )       
    except KeyError:
        await save_group_settings(message.chat.id, 'auto_delete', True)
        btn.insert(0, 
            [
                InlineKeyboardButton(f'Info', 'reqinfo'),
                InlineKeyboardButton(f'Movie', 'minfo'),
                InlineKeyboardButton(f'Series', 'sinfo')
            ]
        )
    
    btn.insert(0, [
        InlineKeyboardButton("! Send All to PM !", callback_data=f"send_fall#{pre}#{0}#{message.from_user.id}"),
        InlineKeyboardButton("! Languages !", callback_data=f"select_lang#{message.from_user.id}")
    ])
    
    btn.insert(0, [
        InlineKeyboardButton("⚡ How to Download ⚡", url="https://t.me/How_To_Verify_PMH/2")
    ])
    
    if offset != "":
        key = f"{message.chat.id}-{message.id}"
        BUTTONS[key] = search
        req = message.from_user.id if message.from_user else 0
        try:
            if settings.get('max_btn'):
                btn.append(
                    [InlineKeyboardButton("Page", callback_data="pages"), InlineKeyboardButton(text=f"1/{math.ceil(int(total_results)/10)}", callback_data="pages"), InlineKeyboardButton(text="Next ➪", callback_data=f"next_{req}_{key}_{offset}")]
                )
            else:
                btn.append(
                    [InlineKeyboardButton("Page", callback_data="pages"), InlineKeyboardButton(text=f"1/{math.ceil(int(total_results)/int(MAX_B_TN))}", callback_data="pages"), InlineKeyboardButton(text="Next ➪", callback_data=f"next_{req}_{key}_{offset}")]
                )
        except KeyError:
            await save_group_settings(message.chat.id, 'max_btn', True)
            btn.append(
                [InlineKeyboardButton("Page", callback_data="pages"), InlineKeyboardButton(text=f"1/{math.ceil(int(total_results)/10)}", callback_data="pages"), InlineKeyboardButton(text="Next ➪", callback_data=f"next_{req}_{key}_{offset}")]
            )
    else:
        btn.append(
            [InlineKeyboardButton(text="No More Pages Available", callback_data="pages")]
        )
    imdb = await get_poster(search, file=(files[0]).file_name) if settings.get("imdb") else None
    TEMPLATE = settings['template']
    if imdb:
        cap = TEMPLATE.format(
            query=search,
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
        cap = f"<b>Hey {message.from_user.mention}, Here is what I found in my database for your query {search}.</b>"
    if imdb and imdb.get('poster'):
        try:
            hehe = await message.reply_photo(photo=imdb.get('poster'), caption=cap[:1024], reply_markup=InlineKeyboardMarkup(btn))
            try:
                if settings['auto_delete']:
                    await asyncio.sleep(600)
                    await hehe.delete()
                    await message.delete()
            except KeyError:
                await save_group_settings(message.chat.id, 'auto_delete', True)
                await asyncio.sleep(600)
                await hehe.delete()
                await message.delete()
        except (MediaEmpty, PhotoInvalidDimensions, WebpageMediaEmpty):
            pic = imdb.get('poster')
            poster = pic.replace('.jpg', "._V1_UX360.jpg")
            hmm = await message.reply_photo(photo=poster, caption=cap[:1024], reply_markup=InlineKeyboardMarkup(btn))
            try:
                if settings['auto_delete']:
                    await asyncio.sleep(600)
                    await hmm.delete()
                    await message.delete()
            except KeyError:
                await save_group_settings(message.chat.id, 'auto_delete', True)
                await asyncio.sleep(600)
                await hmm.delete()
                await message.delete()
        except Exception as e:
            logger.exception(e)
            fek = await message.reply_photo(photo=NOR_IMG, caption=cap, reply_markup=InlineKeyboardMarkup(btn))
            try:
                if settings['auto_delete']:
                    await asyncio.sleep(600)
                    await fek.delete()
                    await message.delete()
            except KeyError:
                await save_group_settings(message.chat.id, 'auto_delete', True)
                await asyncio.sleep(600)
                await fek.delete()
                await message.delete()
    else:
        fuk = await message.reply_photo(photo=NOR_IMG, caption=cap, reply_markup=InlineKeyboardMarkup(btn))
        try:
            if settings['auto_delete']:
                await asyncio.sleep(600)
                await fuk.delete()
                await message.delete()
        except KeyError:
            await save_group_settings(message.chat.id, 'auto_delete', True)
            await asyncio.sleep(600)
            await fuk.delete()
            await message.delete()
    if spoll:
        await msg.message.delete()


async def advantage_spell_chok(client, msg):
    mv_id = msg.id
    mv_rqst = msg.text
    reqstr1 = msg.from_user.id if msg.from_user else 0
    reqstr = await client.get_users(reqstr1)
    settings = await get_settings(msg.chat.id)
    query = re.sub(
        r"\b(pl(i|e)*?(s|z+|ease|se|ese|(e+)s(e)?)|((send|snd|giv(e)?|gib)(\sme)?)|movie(s)?|new|latest|br((o|u)h?)*|^h(e|a)?(l)*(o)*|mal(ayalam)?|t(h)?amil|file|that|find|und(o)*|kit(t(i|y)?)?o(w)?|thar(u)?(o)*w?|kittum(o)*|aya(k)*(um(o)*)?|full\smovie|any(one)|with\ssubtitle(s)?)",
        "", msg.text, flags=re.IGNORECASE)  # Please contribute some common words
    query = query.strip() + " movie"
    try:
        movies = await get_poster(mv_rqst, bulk=True)
    except Exception as e:
        logger.exception(e)
        reqst_gle = mv_rqst.replace(" ", "+")
        button = [[
                   InlineKeyboardButton("Google", url=f"https://www.google.com/search?q={reqst_gle}")
        ]]
        if NO_RESULTS_MSG:
            await client.send_message(chat_id=LOG_CHANNEL_PM, text=(script.NORSLTS.format(reqstr.id, reqstr.mention, mv_rqst)))
        k = await msg.reply_photo(
            photo=SPELL_IMG, 
            caption=script.I_CUDNT.format(mv_rqst),
            reply_markup=InlineKeyboardMarkup(button)
        )
        await asyncio.sleep(30)
        await k.delete()
        return
    movielist = []
    if not movies:
        reqst_gle = mv_rqst.replace(" ", "+")
        button = [[
                   InlineKeyboardButton("Google", url=f"https://www.google.com/search?q={reqst_gle}")
        ]]
        if NO_RESULTS_MSG:
            await client.send_message(chat_id=LOG_CHANNEL_PM, text=(script.NORSLTS.format(reqstr.id, reqstr.mention, mv_rqst)))
        k = await msg.reply_photo(
            photo=SPELL_IMG, 
            caption=script.I_CUDNT.format(mv_rqst),
            reply_markup=InlineKeyboardMarkup(button)
        )
        await asyncio.sleep(30)
        await k.delete()
        return
    movielist += [movie.get('title') for movie in movies]
    movielist += [f"{movie.get('title')} {movie.get('year')}" for movie in movies]
    SPELL_CHECK[mv_id] = movielist
    btn = [
        [
            InlineKeyboardButton(
                text=movie_name.strip(),
                callback_data=f"spol#{reqstr1}#{k}",
            )
        ]
        for k, movie_name in enumerate(movielist)
    ]
    btn.append([InlineKeyboardButton(text="Close", callback_data=f'spol#{reqstr1}#close_spellcheck')])
    spell_check_del = await msg.reply_photo(
        photo=SPELL_IMG,
        caption=script.CUDNT_FND.format(mv_rqst),
        reply_markup=InlineKeyboardMarkup(btn)
    )
    try:
        if settings['auto_delete']:
            await asyncio.sleep(600)
            await spell_check_del.delete()
    except KeyError:
        grpid = await active_connection(str(msg.from_user.id))
        await save_group_settings(grpid, 'auto_delete', True)
        settings = await get_settings(msg.chat.id)
        if settings['auto_delete']:
            await asyncio.sleep(600)
            await spell_check_del.delete()
            
            
async def manual_filters(client, message, text=False):
    settings = await get_settings(message.chat.id)
    group_id = message.chat.id
    name = text or message.text
    reply_id = message.reply_to_message.id if message.reply_to_message else message.id
    keywords = await get_filters(group_id)
    for keyword in reversed(sorted(keywords, key=len)):
        pattern = r"( |^|[^\w])" + re.escape(keyword) + r"( |$|[^\w])"
        if re.search(pattern, name, flags=re.IGNORECASE):
            reply_text, btn, alert, fileid = await find_filter(group_id, keyword)

            if reply_text:
                reply_text = reply_text.replace("\\n", "\n").replace("\\t", "\t")

            if btn is not None:
                try:
                    if fileid == "None":
                        if btn == "[]":
                            joelkb = await client.send_message(
                                group_id, 
                                reply_text, 
                                disable_web_page_preview=True,
                                protect_content=True if settings["file_secure"] else False,
                                reply_to_message_id=reply_id
                            )
                            try:
                                if settings['auto_ffilter']:
                                    await auto_filter(client, message)
                                    try:
                                        if settings['auto_delete']:
                                            await joelkb.delete()
                                    except KeyError:
                                        grpid = await active_connection(str(message.from_user.id))
                                        await save_group_settings(grpid, 'auto_delete', True)
                                        settings = await get_settings(message.chat.id)
                                        if settings['auto_delete']:
                                            await joelkb.delete()
                                else:
                                    try:
                                        if settings['auto_delete']:
                                            await asyncio.sleep(600)
                                            await joelkb.delete()
                                    except KeyError:
                                        grpid = await active_connection(str(message.from_user.id))
                                        await save_group_settings(grpid, 'auto_delete', True)
                                        settings = await get_settings(message.chat.id)
                                        if settings['auto_delete']:
                                            await asyncio.sleep(600)
                                            await joelkb.delete()
                            except KeyError:
                                grpid = await active_connection(str(message.from_user.id))
                                await save_group_settings(grpid, 'auto_ffilter', True)
                                settings = await get_settings(message.chat.id)
                                if settings['auto_ffilter']:
                                    await auto_filter(client, message)

                        else:
                            button = eval(btn)
                            joelkb = await client.send_message(
                                group_id,
                                reply_text,
                                disable_web_page_preview=True,
                                reply_markup=InlineKeyboardMarkup(button),
                                protect_content=True if settings["file_secure"] else False,
                                reply_to_message_id=reply_id
                            )
                            try:
                                if settings['auto_ffilter']:
                                    await auto_filter(client, message)
                                    try:
                                        if settings['auto_delete']:
                                            await joelkb.delete()
                                    except KeyError:
                                        grpid = await active_connection(str(message.from_user.id))
                                        await save_group_settings(grpid, 'auto_delete', True)
                                        settings = await get_settings(message.chat.id)
                                        if settings['auto_delete']:
                                            await joelkb.delete()
                                else:
                                    try:
                                        if settings['auto_delete']:
                                            await asyncio.sleep(600)
                                            await joelkb.delete()
                                    except KeyError:
                                        grpid = await active_connection(str(message.from_user.id))
                                        await save_group_settings(grpid, 'auto_delete', True)
                                        settings = await get_settings(message.chat.id)
                                        if settings['auto_delete']:
                                            await asyncio.sleep(600)
                                            await joelkb.delete()
                            except KeyError:
                                grpid = await active_connection(str(message.from_user.id))
                                await save_group_settings(grpid, 'auto_ffilter', True)
                                settings = await get_settings(message.chat.id)
                                if settings['auto_ffilter']:
                                    await auto_filter(client, message)

                    elif btn == "[]":
                        joelkb = await client.send_cached_media(
                            group_id,
                            fileid,
                            caption=reply_text or "",
                            protect_content=True if settings["file_secure"] else False,
                            reply_to_message_id=reply_id
                        )
                        try:
                            if settings['auto_ffilter']:
                                await auto_filter(client, message)
                                try:
                                    if settings['auto_delete']:
                                        await joelkb.delete()
                                except KeyError:
                                    grpid = await active_connection(str(message.from_user.id))
                                    await save_group_settings(grpid, 'auto_delete', True)
                                    settings = await get_settings(message.chat.id)
                                    if settings['auto_delete']:
                                        await joelkb.delete()
                            else:
                                try:
                                    if settings['auto_delete']:
                                        await asyncio.sleep(600)
                                        await joelkb.delete()
                                except KeyError:
                                    grpid = await active_connection(str(message.from_user.id))
                                    await save_group_settings(grpid, 'auto_delete', True)
                                    settings = await get_settings(message.chat.id)
                                    if settings['auto_delete']:
                                        await asyncio.sleep(600)
                                        await joelkb.delete()
                        except KeyError:
                            grpid = await active_connection(str(message.from_user.id))
                            await save_group_settings(grpid, 'auto_ffilter', True)
                            settings = await get_settings(message.chat.id)
                            if settings['auto_ffilter']:
                                await auto_filter(client, message)

                    else:
                        button = eval(btn)
                        joelkb = await message.reply_cached_media(
                            fileid,
                            caption=reply_text or "",
                            reply_markup=InlineKeyboardMarkup(button),
                            reply_to_message_id=reply_id
                        )
                        try:
                            if settings['auto_ffilter']:
                                await auto_filter(client, message)
                                try:
                                    if settings['auto_delete']:
                                        await joelkb.delete()
                                except KeyError:
                                    grpid = await active_connection(str(message.from_user.id))
                                    await save_group_settings(grpid, 'auto_delete', True)
                                    settings = await get_settings(message.chat.id)
                                    if settings['auto_delete']:
                                        await joelkb.delete()
                            else:
                                try:
                                    if settings['auto_delete']:
                                        await asyncio.sleep(600)
                                        await joelkb.delete()
                                except KeyError:
                                    grpid = await active_connection(str(message.from_user.id))
                                    await save_group_settings(grpid, 'auto_delete', True)
                                    settings = await get_settings(message.chat.id)
                                    if settings['auto_delete']:
                                        await asyncio.sleep(600)
                                        await joelkb.delete()
                        except KeyError:
                            grpid = await active_connection(str(message.from_user.id))
                            await save_group_settings(grpid, 'auto_ffilter', True)
                            settings = await get_settings(message.chat.id)
                            if settings['auto_ffilter']:
                                await auto_filter(client, message)

                except Exception as e:
                    logger.exception(e)
                break
    else:
        return False
        
async def global_filters(client, message, text=False):
    settings = await get_settings(message.chat.id)
    group_id = message.chat.id
    name = text or message.text
    reply_id = message.reply_to_message.id if message.reply_to_message else message.id
    keywords = await get_gfilters('gfilters')
    for keyword in reversed(sorted(keywords, key=len)):
        pattern = r"( |^|[^\w])" + re.escape(keyword) + r"( |$|[^\w])"
        if re.search(pattern, name, flags=re.IGNORECASE):
            reply_text, btn, alert, fileid = await find_gfilter('gfilters', keyword)

            if reply_text:
                reply_text = reply_text.replace("\\n", "\n").replace("\\t", "\t")

            if btn is not None:
                try:
                    if fileid == "None":
                        if btn == "[]":
                            joelkb = await client.send_message(
                                group_id, 
                                reply_text, 
                                disable_web_page_preview=True,
                                reply_to_message_id=reply_id
                            )
                            manual = await manual_filters(client, message, text=reply_text)
                            if manual == False:
                                settings = await get_settings(message.chat.id)
                                try:
                                    if settings['auto_ffilter']:
                                        await auto_filter(client, message)
                                        try:
                                            if settings['auto_delete']:
                                                await joelkb.delete()
                                        except KeyError:
                                            grpid = await active_connection(str(message.from_user.id))
                                            await save_group_settings(grpid, 'auto_delete', True)
                                            settings = await get_settings(message.chat.id)
                                            if settings['auto_delete']:
                                                await joelkb.delete()
                                    else:
                                        try:
                                            if settings['auto_delete']:
                                                await asyncio.sleep(600)
                                                await joelkb.delete()
                                        except KeyError:
                                            grpid = await active_connection(str(message.from_user.id))
                                            await save_group_settings(grpid, 'auto_delete', True)
                                            settings = await get_settings(message.chat.id)
                                            if settings['auto_delete']:
                                                await asyncio.sleep(600)
                                                await joelkb.delete()
                                except KeyError:
                                    grpid = await active_connection(str(message.from_user.id))
                                    await save_group_settings(grpid, 'auto_ffilter', True)
                                    settings = await get_settings(message.chat.id)
                                    if settings['auto_ffilter']:
                                        await auto_filter(client, message) 
                            else:
                                try:
                                    if settings['auto_delete']:
                                        await joelkb.delete()
                                except KeyError:
                                    grpid = await active_connection(str(message.from_user.id))
                                    await save_group_settings(grpid, 'auto_delete', True)
                                    settings = await get_settings(message.chat.id)
                                    if settings['auto_delete']:
                                        await joelkb.delete()
                            
                        else:
                            button = eval(btn)
                            joelkb = await client.send_message(
                                group_id,
                                reply_text,
                                disable_web_page_preview=True,
                                reply_markup=InlineKeyboardMarkup(button),
                                reply_to_message_id=reply_id
                            )
                            manual = await manual_filters(client, message, text=reply_text)
                            if manual == False:
                                settings = await get_settings(message.chat.id)
                                try:
                                    if settings['auto_ffilter']:
                                        await auto_filter(client, message)
                                        try:
                                            if settings['auto_delete']:
                                                await joelkb.delete()
                                        except KeyError:
                                            grpid = await active_connection(str(message.from_user.id))
                                            await save_group_settings(grpid, 'auto_delete', True)
                                            settings = await get_settings(message.chat.id)
                                            if settings['auto_delete']:
                                                await joelkb.delete()
                                    else:
                                        try:
                                            if settings['auto_delete']:
                                                await asyncio.sleep(600)
                                                await joelkb.delete()
                                        except KeyError:
                                            grpid = await active_connection(str(message.from_user.id))
                                            await save_group_settings(grpid, 'auto_delete', True)
                                            settings = await get_settings(message.chat.id)
                                            if settings['auto_delete']:
                                                await asyncio.sleep(600)
                                                await joelkb.delete()
                                except KeyError:
                                    grpid = await active_connection(str(message.from_user.id))
                                    await save_group_settings(grpid, 'auto_ffilter', True)
                                    settings = await get_settings(message.chat.id)
                                    if settings['auto_ffilter']:
                                        await auto_filter(client, message) 
                            else:
                                try:
                                    if settings['auto_delete']:
                                        await joelkb.delete()
                                except KeyError:
                                    grpid = await active_connection(str(message.from_user.id))
                                    await save_group_settings(grpid, 'auto_delete', True)
                                    settings = await get_settings(message.chat.id)
                                    if settings['auto_delete']:
                                        await joelkb.delete()

                    elif btn == "[]":
                        joelkb = await client.send_cached_media(
                            group_id,
                            fileid,
                            caption=reply_text or "",
                            reply_to_message_id=reply_id
                        )
                        manual = await manual_filters(client, message, text=reply_text)
                        if manual == False:
                            settings = await get_settings(message.chat.id)
                            try:
                                if settings['auto_ffilter']:
                                    await auto_filter(client, message)
                                    try:
                                        if settings['auto_delete']:
                                            await joelkb.delete()
                                    except KeyError:
                                        grpid = await active_connection(str(message.from_user.id))
                                        await save_group_settings(grpid, 'auto_delete', True)
                                        settings = await get_settings(message.chat.id)
                                        if settings['auto_delete']:
                                            await joelkb.delete()
                                else:
                                    try:
                                        if settings['auto_delete']:
                                            await asyncio.sleep(600)
                                            await joelkb.delete()
                                    except KeyError:
                                        grpid = await active_connection(str(message.from_user.id))
                                        await save_group_settings(grpid, 'auto_delete', True)
                                        settings = await get_settings(message.chat.id)
                                        if settings['auto_delete']:
                                            await asyncio.sleep(600)
                                            await joelkb.delete()
                            except KeyError:
                                grpid = await active_connection(str(message.from_user.id))
                                await save_group_settings(grpid, 'auto_ffilter', True)
                                settings = await get_settings(message.chat.id)
                                if settings['auto_ffilter']:
                                    await auto_filter(client, message) 
                        else:
                            try:
                                if settings['auto_delete']:
                                    await joelkb.delete()
                            except KeyError:
                                grpid = await active_connection(str(message.from_user.id))
                                await save_group_settings(grpid, 'auto_delete', True)
                                settings = await get_settings(message.chat.id)
                                if settings['auto_delete']:
                                    await joelkb.delete()

                    else:
                        button = eval(btn)
                        joelkb = await message.reply_cached_media(
                            fileid,
                            caption=reply_text or "",
                            reply_markup=InlineKeyboardMarkup(button),
                            reply_to_message_id=reply_id
                        )
                        manual = await manual_filters(client, message, text=reply_text)
                        if manual == False:
                            settings = await get_settings(message.chat.id)
                            try:
                                if settings['auto_ffilter']:
                                    await auto_filter(client, message)
                                    try:
                                        if settings['auto_delete']:
                                            await joelkb.delete()
                                    except KeyError:
                                        grpid = await active_connection(str(message.from_user.id))
                                        await save_group_settings(grpid, 'auto_delete', True)
                                        settings = await get_settings(message.chat.id)
                                        if settings['auto_delete']:
                                            await joelkb.delete()
                                else:
                                    try:
                                        if settings['auto_delete']:
                                            await asyncio.sleep(600)
                                            await joelkb.delete()
                                    except KeyError:
                                        grpid = await active_connection(str(message.from_user.id))
                                        await save_group_settings(grpid, 'auto_delete', True)
                                        settings = await get_settings(message.chat.id)
                                        if settings['auto_delete']:
                                            await asyncio.sleep(600)
                                            await joelkb.delete()
                            except KeyError:
                                grpid = await active_connection(str(message.from_user.id))
                                await save_group_settings(grpid, 'auto_ffilter', True)
                                settings = await get_settings(message.chat.id)
                                if settings['auto_ffilter']:
                                    await auto_filter(client, message) 
                        else:
                            try:
                                if settings['auto_delete']:
                                    await joelkb.delete()
                            except KeyError:
                                grpid = await active_connection(str(message.from_user.id))
                                await save_group_settings(grpid, 'auto_delete', True)
                                settings = await get_settings(message.chat.id)
                                if settings['auto_delete']:
                                    await joelkb.delete()

                except Exception as e:
                    logger.exception(e)
                break
    else:
        return False
        
