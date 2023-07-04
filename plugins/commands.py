import asyncio
import base64
import json
import logging
import os
import random
import re
from datetime import date, datetime

import pytz
from pyrogram import Client, filters, enums
from pyrogram.errors import ChatAdminRequired, FloodWait
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from Script import script
from database.connections_mdb import active_connection
from database.ia_filterdb import Media, get_file_details, unpack_new_file_id, get_bad_files
from database.users_chats_db import db
from info import (
    CHANNELS,
    ADMINS,
    AUTH_CHANNEL,
    LOG_CHANNEL,
    PICS,
    BATCH_FILE_CAPTION,
    CUSTOM_FILE_CAPTION,
    PROTECT_CONTENT,
    CHNL_LNK,
    GRP_LNK,
    REQST_CHANNEL,
    SUPPORT_CHAT_ID,
    MAX_B_TN,
    IS_VERIFY,
    HOW_TO_VERIFY,
)
from utils import (
    get_settings,
    get_size,
    is_subscribed,
    save_group_settings,
    temp,
    verify_user,
    check_token,
    check_verification,
    get_token,
    send_all,
)

logger = logging.getLogger(__name__)

BATCH_FILES = {}

@Client.on_message(filters.command("start") & filters.incoming)
async def start(client, message):
    if message.chat.type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        buttons = [
            [
                InlineKeyboardButton('Support Group', url=GRP_LNK),
                InlineKeyboardButton('Updates Channel', url=CHNL_LNK)
            ],
            [
                InlineKeyboardButton("⚡ How to Download ⚡", url="https://t.me/How_To_Verify_PMH/2")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        await message.reply(script.START_TXT.format(message.from_user.mention if message.from_user else message.chat.title, temp.U_NAME, temp.B_NAME), reply_markup=reply_markup)
        await asyncio.sleep(2)
        if not await db.get_chat(message.chat.id):
            total = await client.get_chat_members_count(message.chat.id)
            total_chat = await db.total_chat_count()
            tz = pytz.timezone('Asia/Kolkata')
            today = date.today()
            now = datetime.now(tz)
            time = now.strftime('%I:%M:%S %p')
            daily_chats = await db.daily_chats_count(today)
            await client.send_message(LOG_CHANNEL, script.LOG_TEXT_G.format(
                a=message.chat.title,
                b=message.chat.id,
                c=message.chat.username,
                d=total,
                e=total_chat,
                f=str(today),
                g=time,
                h=daily_chats + 1,
                i=temp.B_NAME,
                j="Unknown"
            ))
            await db.add_chat(message.chat.id, message.chat.title, message.chat.username)
        return

    if not await db.is_user_exist(message.from_user.id):
        await db.add_user(message.from_user.id, message.from_user.first_name)
        total_users = await db.total_users_count()
        tz = pytz.timezone('Asia/Kolkata')
        today = date.today()
        now = datetime.now(tz)
        time = now.strftime('%I:%M:%S %p')
        daily_users = await db.daily_users_count(today)
        await client.send_message(LOG_CHANNEL, script.LOG_TEXT_P.format(
            a=message.from_user.id,
            b=message.from_user.mention,
            c=message.from_user.username,
            d=total_users,
            e=str(today),
            f=time,
            g=daily_users + 1,
            h=temp.U_NAME
        ))
        
    if len(message.command) != 2:
        buttons = [
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
            ]
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        await message.reply_photo(
            photo=random.choice(PICS),
            caption=script.START_TXT.format(message.from_user.mention, temp.U_NAME, temp.B_NAME),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML,
            quote=True
        )

        return

    if AUTH_CHANNEL and not await is_subscribed(client, message):
        try:
            invite_link = await client.create_chat_invite_link(int(AUTH_CHANNEL))
        except ChatAdminRequired:
            logger.error("Make sure Bot is admin in Forcesub channel")
            return
        
        btn = [
            [
                InlineKeyboardButton("Join Our Backup Channel", url=invite_link.invite_link)
            ]
        ]
    
        if message.command[1] != "subscribe":
            try:
                kk, file_id = message.command[1].split("_", 1)
                pre = 'checksubp' if kk == 'filep' else 'checksub'
                btn.append([InlineKeyboardButton("Try Again", callback_data=f"{pre}#{file_id}")])
            except (IndexError, ValueError):
                btn.append([InlineKeyboardButton("Try Again", url=f"https://t.me/{temp.U_NAME}?start={message.command[1]}")])
    
        await client.send_message(
            chat_id=message.from_user.id,
            text=f"**Hello {message.from_user.mention}, Due to overload only my channel subscribers can use me.\n\nPlease join my channel and then start me again!...**",
            reply_markup=InlineKeyboardMarkup(btn),
            parse_mode=enums.ParseMode.MARKDOWN,
            quote=True
        )
        return

    if len(message.command) == 2 and message.command[1] in ["subscribe", "error", "okay", "help"]:
        buttons = [
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
            ]
        ]
        reply_markup = InlineKeyboardMarkup(buttons)
        await message.reply_photo(
            photo=random.choice(PICS),
            caption=script.START_TXT.format(message.from_user.mention, temp.U_NAME, temp.B_NAME),
            reply_markup=reply_markup,
            parse_mode=enums.ParseMode.HTML,
            quote=True
        )
        return
    data = message.command[1]

    try:
        pre, file_id = data.split('_', 1)
    except:
        file_id = data
        pre = ""
    
    if data.split("-", 1)[0] == "BATCH":
        sts = await message.reply("<b>Please wait...</b>")
        file_id = data.split("-", 1)[1]
        msgs = BATCH_FILES.get(file_id)
    
        if not msgs:
            file = await client.download_media(file_id)
            try:
                with open(file) as file_data:
                    msgs = json.loads(file_data.read())
            except:
                await sts.edit("Failed")
                return await client.send_message(LOG_CHANNEL, "Unable to open file.")
    
            os.remove(file)
            BATCH_FILES[file_id] = msgs
    
        for msg in msgs:
            title = msg.get("title")
            size = get_size(int(msg.get("size", 0)))
            f_caption = msg.get("caption", "")
    
            if BATCH_FILE_CAPTION:
                try:
                    f_caption = BATCH_FILE_CAPTION.format(file_name='' if title is None else title,
                                                          file_size='' if size is None else size,
                                                          file_caption='' if f_caption is None else f_caption)
                except Exception as e:
                    logger.exception(e)
                    f_caption = f_caption
    
            if f_caption is None:
                f_caption = f"{title}"
    
            try:
                await client.send_cached_media(
                    chat_id=message.from_user.id,
                    file_id=msg.get("file_id"),
                    caption=f_caption,
                    protect_content=msg.get('protect', False),
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
            except FloodWait as e:
                await asyncio.sleep(e.x)
                logger.warning(f"Floodwait of {e.x} sec.")
                await client.send_cached_media(
                    chat_id=message.from_user.id,
                    file_id=msg.get("file_id"),
                    caption=f_caption,
                    protect_content=msg.get('protect', False),
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
            except Exception as e:
                logger.warning(e, exc_info=True)
                continue
    
            await asyncio.sleep(1)
    
        await sts.delete()
        return
    elif data.split("-", 1)[0] == "DSTORE":
        sts = await message.reply("<b>Please wait...</b>")
        b_string = data.split("-", 1)[1]
        decoded = (base64.urlsafe_b64decode(b_string + "=" * (-len(b_string) % 4))).decode("ascii")
    
        try:
            f_msg_id, l_msg_id, f_chat_id, protect = decoded.split("_", 3)
        except:
            f_msg_id, l_msg_id, f_chat_id = decoded.split("_", 2)
            protect = "/pbatch" if PROTECT_CONTENT else "batch"
    
        diff = int(l_msg_id) - int(f_msg_id)
    
        async for msg in client.iter_messages(int(f_chat_id), int(l_msg_id), int(f_msg_id)):
            if msg.media:
                media = getattr(msg, msg.media.value)
    
                if BATCH_FILE_CAPTION:
                    try:
                        f_caption = BATCH_FILE_CAPTION.format(file_name=getattr(media, 'file_name', ''), file_size=getattr(media, 'file_size', ''), file_caption=getattr(msg, 'caption', ''))
                    except Exception as e:
                        logger.exception(e)
                        f_caption = getattr(msg, 'caption', '')
                else:
                    media = getattr(msg, msg.media.value)
                    file_name = getattr(media, 'file_name', '')
                    f_caption = getattr(msg, 'caption', file_name)
    
                try:
                    await msg.copy(message.chat.id, caption=f_caption, protect_content=True if protect == "/pbatch" else False)
                except FloodWait as e:
                    await asyncio.sleep(e.x)
                    await msg.copy(message.chat.id, caption=f_caption, protect_content=True if protect == "/pbatch" else False)
                except Exception as e:
                    logger.exception(e)
                    continue
            elif msg.empty:
                continue
            else:
                try:
                    await msg.copy(message.chat.id, protect_content=True if protect == "/pbatch" else False)
                except FloodWait as e:
                    await asyncio.sleep(e.x)
                    await msg.copy(message.chat.id, protect_content=True if protect == "/pbatch" else False)
                except Exception as e:
                    logger.exception(e)
                    continue
    
            await asyncio.sleep(1)
        return await sts.delete()
    
    elif data.split("-", 1)[0] == "verify":
        userid = data.split("-", 2)[1]
        token = data.split("-", 3)[2]
        fileid = data.split("-", 3)[3]
        
        if str(message.from_user.id) != str(userid):
            return await message.reply_text(
                text="<b>🚫 Invalid link or expired link!</b>",
                protect_content=True if PROTECT_CONTENT else False
            )
        
        is_valid = await check_token(client, userid, token)
        
        if is_valid == True:
            if fileid == "send_all":
                btn = [[
                    InlineKeyboardButton("📥 Get File", callback_data=f"checksub#send_all")
                ]]
                
                await verify_user(client, userid, token)
                
                await message.reply_text(
                    text=f"<b>🎉 Hey {message.from_user.mention}, you are successfully verified!\nNow you have unlimited access for all movies until the next verification, which is after 12 hours from now.</b>",
                    protect_content=True if PROTECT_CONTENT else False,
                    reply_markup=InlineKeyboardMarkup(btn)
                )
                return
            
            btn = [[
                InlineKeyboardButton("📥 Get File", url=f"https://telegram.me/{temp.U_NAME}?start=files_{fileid}")
            ]]
            
            await message.reply_text(
                text=f"<b>🎉 Hey {message.from_user.mention}, you are successfully verified!\nNow you have unlimited access for all movies until the next verification, which is after 12 hours from now.</b>",
                protect_content=True if PROTECT_CONTENT else False,
                reply_markup=InlineKeyboardMarkup(btn)
            )
            
            await verify_user(client, userid, token)
            return
        else:
            return await message.reply_text(
                text="<b>🚫 Invalid link or expired link!</b>",
                protect_content=True if PROTECT_CONTENT else False
            )
    
    files_ = await get_file_details(file_id)
    if not files_:
        pre, file_id = ((base64.urlsafe_b64decode(data + "=" * (-len(data) % 4))).decode("ascii")).split("_", 1)
        try:
            if IS_VERIFY and not await check_verification(client, message.from_user.id):
                btn = [[
                    InlineKeyboardButton("🔒 Verify", url=await get_token(client, message.from_user.id, f"https://telegram.me/{temp.U_NAME}?start=", file_id)),
                    InlineKeyboardButton("🔍 How To Verify", url=HOW_TO_VERIFY)
                ]]
                await message.reply_text(
                    text="<b>❌ You are not verified!\nKindly verify to continue so that you can get access to unlimited movies until 12 hours from now!</b>",
                    protect_content=True if PROTECT_CONTENT else False,
                    reply_markup=InlineKeyboardMarkup(btn)
                )
                return
            msg = await client.send_cached_media(
                chat_id=message.from_user.id,
                file_id=file_id,
                protect_content=True if pre == 'filep' else False,
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
            filetype = msg.media
            file = getattr(msg, filetype.value)
            title = file.file_name
            size = get_size(file.file_size)
            f_caption = f"<code>{title}</code>"
            if CUSTOM_FILE_CAPTION:
                try:
                    f_caption = CUSTOM_FILE_CAPTION.format(file_name='' if title is None else title, file_size='' if size is None else size, file_caption='')
                except:
                    return
            await msg.edit_caption(f_caption)
            return
        except:
            pass
        return await message.reply('❌ No such file exists.')
    
    files = files_[0]
    title = files.file_name
    size = get_size(files.file_size)
    f_caption = files.caption
    if CUSTOM_FILE_CAPTION:
        try:
            f_caption = CUSTOM_FILE_CAPTION.format(file_name='' if title is None else title, file_size='' if size is None else size, file_caption='' if f_caption is None else f_caption)
        except Exception as e:
            logger.exception(e)
            f_caption = f_caption
    if f_caption is None:
        f_caption = f"{files.file_name}"
    if IS_VERIFY and not await check_verification(client, message.from_user.id):
        btn = [[
            InlineKeyboardButton("🔒 Verify", url=await get_token(client, message.from_user.id, f"https://telegram.me/{temp.U_NAME}?start=", file_id)),
            InlineKeyboardButton("🔍 How To Verify", url=HOW_TO_VERIFY)
        ]]
        await message.reply_text(
            text="<b>❌ You are not verified!\nKindly verify to continue so that you can get access to unlimited movies until 12 hours from now!</b>",
            protect_content=True if PROTECT_CONTENT else False,
            reply_markup=InlineKeyboardMarkup(btn)
        )
        return
    await client.send_cached_media(
        chat_id=message.from_user.id,
        file_id=file_id,
        caption=f_caption,
        protect_content=True if pre == 'filep' else False,
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
               

@Client.on_message(filters.command('channel') & filters.user(ADMINS))
async def channel_info(bot, message):
    if isinstance(CHANNELS, (int, str)):
        channels = [CHANNELS]
    elif isinstance(CHANNELS, list):
        channels = CHANNELS
    else:
        raise ValueError("Unexpected type of CHANNELS")

    text = '📑 **Indexed channels/groups**\n'
    for channel in channels:
        chat = await bot.get_chat(channel)
        if chat.username:
            text += '\n👉 @' + chat.username
        else:
            text += '\n👉 ' + chat.title or chat.first_name

    text += f'\n\n**Total:** {len(CHANNELS)}'

    if len(text) < 4096:
        await message.reply(text)
    else:
        file = 'Indexed channels.txt'
        with open(file, 'w') as f:
            f.write(text)
        await message.reply_document(file)
        os.remove(file)


@Client.on_message(filters.command('logs') & filters.user(ADMINS))
async def log_file(bot, message):
    try:
        await message.reply_document('Logs.txt')
    except Exception as e:
        await message.reply(str(e))


@Client.on_message(filters.command('total') & filters.user(ADMINS))
async def total(bot, message):
    msg = await message.reply("Processing...⏳", quote=True)
    try:
        total = await Media.count_documents()
        await msg.edit(f'📁 Saved files: {total}')
    except Exception as e:
        logger.exception('Failed to check total files')
        await msg.edit(f'Error: {e}')
        

@Client.on_message(filters.command('delete') & filters.user(ADMINS))
async def delete(bot, message):
    reply = message.reply_to_message
    if reply and reply.media:
        msg = await message.reply("Processing...⏳", quote=True)
    else:
        await message.reply('Reply to a file with /delete to delete it.', quote=True)
        return

    for file_type in ("document", "video", "audio"):
        media = getattr(reply, file_type, None)
        if media is not None:
            break
    else:
        await msg.edit('This is not a supported file format.')
        return

    file_id, file_ref = unpack_new_file_id(media.file_id)

    result = await Media.collection.delete_one({
        '_id': file_id,
    })
    if result.deleted_count:
        await msg.edit('File is successfully deleted from the database.')
    else:
        file_name = re.sub(r"(_|\-|\.|\+)", " ", str(media.file_name))
        result = await Media.collection.delete_many({
            'file_name': file_name,
            'file_size': media.file_size,
            'mime_type': media.mime_type
        })
        if result.deleted_count:
            await msg.edit('File is successfully deleted from the database.')
        else:
            result = await Media.collection.delete_many({
                'file_name': media.file_name,
                'file_size': media.file_size,
                'mime_type': media.mime_type
            })
            if result.deleted_count:
                await msg.edit('🗑 File is successfully deleted from the database.')
            else:
                await msg.edit('File not found in the database.')


@Client.on_message(filters.command('deleteall') & filters.user(ADMINS))
async def delete_all_index(bot, message):
    await message.reply_text(
        'This will delete all indexed files.\nDo you want to continue?',
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="Yes", callback_data="autofilter_delete"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="Cancel", callback_data="close_data"
                    )
                ],
            ]
        ),
        quote=True,
    )

@Client.on_message(filters.command("deletefiletype") & filters.user(ADMINS))
async def delete_file_type_command(client, message):
    """Command handler for deleting files of a specific type from the database"""
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("📥 Document", callback_data="delete_filetype_document"),
                InlineKeyboardButton("🎬 Video", callback_data="delete_filetype_video"),
            ],
            [
                InlineKeyboardButton("🎧 Audio", callback_data="delete_filetype_audio"),
                InlineKeyboardButton("📦 Zip", callback_data="delete_filetype_zip"),
            ],
            [
                InlineKeyboardButton("❎ Cancel", callback_data="dft_cancel"),
            ]
        ]
    )

    await message.reply_text("🗑 Select the type of files you want to delete!\n\n🗑 This will delete related files from the database:",
        reply_markup=keyboard,
        quote=True,
    )

@Client.on_callback_query(filters.user(ADMINS) & filters.regex(r"^delete_filetype_(document|video|audio)$"))
async def delete_file_type_callback(client, callback_query):
    """Callback handler for deleting files of a specific type"""
    file_type = callback_query.data.replace("delete_filetype_", "")

    total_files = await Media.count_documents({"file_type": file_type})

    if total_files > 0:
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("🗑 Delete", callback_data=f"confirm_delete_{file_type}"),
                    InlineKeyboardButton("🏠 Home", callback_data="deletefiletype"),
                ]
            ]
        )

        await callback_query.edit_message_text(f"✅ Found {total_files} {file_type}(s) in the database.\n\n""Please select an action:",
            reply_markup=keyboard,
        )
    else:
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("🏠 Home", callback_data="deletefiletype"),
                    InlineKeyboardButton("❎ Cancel", callback_data="dft_cancel"),
                ]
            ]
        )

        await callback_query.edit_message_text(f"No {file_type}s found in the database.",
            reply_markup=keyboard,
        )

@Client.on_callback_query(filters.regex("delete_filetype_zip"))
async def delete_file_type_zip_callback(bot, callback_query):
    files, total = await get_bad_files('zip')
    if total > 0:
        confirm_btns = [
            [
                InlineKeyboardButton(f"🗑 Delete ({total} files)", callback_data="confirm_delete_zip"),
                InlineKeyboardButton("🏠 Home", callback_data="deletefiletype"),
            ]
        ]
        await callback_query.edit_message_text(
            f"✅ Found {total} zip file(s) in the database.\n\nPlease select an action:",
            reply_markup=InlineKeyboardMarkup(confirm_btns),
        )
    else:
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("🏠 Home", callback_data="deletefiletype"),
                    InlineKeyboardButton("❎ Cancel", callback_data="dft_cancel"),
                ]
            ]
        )

        await callback_query.edit_message_text(
            "No zip files found in the database.",
            reply_markup=keyboard,
        )
        
@Client.on_callback_query(filters.user(ADMINS) & filters.regex(r"^confirm_delete_document$"))
async def confirm_delete_document_callback(bot, callback_query):
    """Callback handler for confirming the deletion of document files"""
    result = await Media.collection.delete_many({"file_type": "document"})

    if result.deleted_count:
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("🏠 Home", callback_data="deletefiletype"),
                    InlineKeyboardButton("❎ Cancel", callback_data="dft_cancel"),
                ]
            ]
        )

        await callback_query.message.edit_text("🗑 All document files have been successfully deleted from the database.",
            reply_markup=keyboard,
        )
    else:
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("🏠 Home", callback_data="deletefiletype"),
                    InlineKeyboardButton("❎ Cancel", callback_data="dft_cancel"),
                ]
            ]
        )

        await callback_query.message.edit_text("❎ No document files found in the database.",
            reply_markup=keyboard,
        )

@Client.on_callback_query(filters.user(ADMINS) & filters.regex(r"^confirm_delete_video$"))
async def confirm_delete_video_callback(bot, callback_query):
    """Callback handler for confirming the deletion of video files"""
    result = await Media.collection.delete_many({"file_type": "video"})

    if result.deleted_count:
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("🏠 Home", callback_data="deletefiletype"),
                    InlineKeyboardButton("❎ Cancel", callback_data="dft_cancel"),
                ]
            ]
        )

        await callback_query.message.edit_text("🗑 All video files have been successfully deleted from the database.",
            reply_markup=keyboard,
        )
    else:
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("🏠 Home", callback_data="deletefiletype"),
                    InlineKeyboardButton("❎ Cancel", callback_data="dft_cancel"),
                ]
            ]
        )

        await callback_query.message.edit_text("🗑 No video files found in the database.",
            reply_markup=keyboard,
        )

@Client.on_callback_query(filters.user(ADMINS) & filters.regex(r"^confirm_delete_audio$"))
async def confirm_delete_audio_callback(bot, callback_query):
    """Callback handler for confirming the deletion of audio files"""
    result = await Media.collection.delete_many({"file_type": "audio"})

    if result.deleted_count:
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("🏠 Home", callback_data="deletefiletype"),
                    InlineKeyboardButton("❎ Cancel", callback_data="dft_cancel"),
                ]
            ]
        )

        await callback_query.message.edit_text("🗑 All audio files have been successfully deleted from the database.",
            reply_markup=keyboard,
        )
    else:
        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton("🏠 Home", callback_data="deletefiletype"),
                    InlineKeyboardButton("❎ Cancel", callback_data="dft_cancel"),
                ]
            ]
        )

        await callback_query.message.edit_text("❎ No audio files found in the database.",
            reply_markup=keyboard,
        )

@Client.on_callback_query(filters.regex("confirm_delete_zip"))
async def confirm_delete_zip_callback(bot, callback_query):
    files, total = await get_bad_files('zip')
    deleted = 0
    for file in files:
        file_ids = file.file_id
        result = await Media.collection.delete_one({'_id': file_ids})
        if result.deleted_count:
            logger.info(f'Zip file Found! Successfully deleted from the database.')
        deleted += 1
    deleted = str(deleted)
    await callback_query.message.edit_text(
        f"<b>Successfully deleted {deleted} zip file(s).</b>",
    )

    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("🏠 Home", callback_data="deletefiletype"),
                InlineKeyboardButton("❎ Cancel", callback_data="dft_cancel"),
            ]
        ]
    )

    await callback_query.message.edit_text(
        "🗑 All zip files have been successfully deleted from the database.",
        reply_markup=keyboard,
    )
    
@Client.on_callback_query(filters.user(ADMINS) & filters.regex(r"^dft_cancel$"))
async def delete_file_type_cancel_callback(bot, callback_query):
    """Callback handler for canceling the delete file type operation"""
    await callback_query.message.edit_text("Delete file type operation canceled.")
    await callback_query.answer()
    
    
@Client.on_callback_query(filters.regex(r'^autofilter_delete'))
async def delete_all_index_confirm(bot, message):
    await Media.collection.drop()
    await message.answer("Everything's Gone")
    await message.message.edit('🗑 Successfully deleted all the indexed files.')


@Client.on_message(filters.command('settings'))
async def settings(client, message):
    userid = message.from_user.id if message.from_user else None
    if not userid:
        return await message.reply("You are an anonymous admin. Use /connect [chat_id] in PM")

    chat_type = message.chat.type

    if chat_type == enums.ChatType.PRIVATE:
        grpid = await active_connection(str(userid))
        if grpid is not None:
            grp_id = grpid
            try:
                chat = await client.get_chat(grpid)
                title = chat.title
            except:
                await message.reply_text("Make sure I'm present in your group!", quote=True)
                return
        else:
            await message.reply_text("I'm not connected to any groups!", quote=True)
            return
    elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        grp_id = message.chat.id
        title = message.chat.title
    else:
        return

    st = await client.get_chat_member(grp_id, userid)
    if (
            st.status != enums.ChatMemberStatus.ADMINISTRATOR
            and st.status != enums.ChatMemberStatus.OWNER
            and str(userid) not in ADMINS
    ):
        return

    settings = await get_settings(grp_id)

    try:
        if settings['max_btn']:
            settings = await get_settings(grp_id)
    except KeyError:
        await save_group_settings(grp_id, 'max_btn', False)
        settings = await get_settings(grp_id)

    if 'is_shortlink' not in settings.keys():
        await save_group_settings(grp_id, 'is_shortlink', False)
    else:
        pass

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

        btn = [
            [
                InlineKeyboardButton("Open Here", callback_data=f"opnsetgrp#{grp_id}"),
                InlineKeyboardButton("Open in PM", callback_data=f"opnsetpm#{grp_id}")
            ]
        ]

        reply_markup = InlineKeyboardMarkup(buttons)
        if chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
            await message.reply_text(
                text="<b>Do you want to open settings here?</b>",
                reply_markup=InlineKeyboardMarkup(btn),
                disable_web_page_preview=True,
                parse_mode=enums.ParseMode.HTML,
                reply_to_message_id=message.message_id if hasattr(message, 'message_id') else None
            )
        else:
            await message.reply_text(
                text=f"<b>Change your settings for {title} as you wish</b>",
                reply_markup=reply_markup,
                disable_web_page_preview=True,
                parse_mode=enums.ParseMode.HTML,
                reply_to_message_id=message.message_id if hasattr(message, 'message_id') else None
            )


@Client.on_message(filters.command('set_template'))
async def save_template(client, message):
    sts = await message.reply("📝 Checking template...")
    userid = message.from_user.id if message.from_user else None
    if not userid:
        return await message.reply(f"🚫 You are an anonymous admin. Use /connect {message.chat.id} in PM")

    chat_type = message.chat.type

    if chat_type == enums.ChatType.PRIVATE:
        grpid = await active_connection(str(userid))
        if grpid is not None:
            grp_id = grpid
            try:
                chat = await client.get_chat(grpid)
                title = chat.title
            except:
                await message.reply_text("❗ Make sure I'm present in your group!", quote=True)
                return
        else:
            await message.reply_text("❗ I'm not connected to any groups!", quote=True)
            return
    elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        grp_id = message.chat.id
        title = message.chat.title
    else:
        return

    st = await client.get_chat_member(grp_id, userid)
    if (
            st.status != enums.ChatMemberStatus.ADMINISTRATOR
            and st.status != enums.ChatMemberStatus.OWNER
            and str(userid) not in ADMINS
    ):
        return

    if len(message.command) < 2:
        return await sts.edit("❌ No input!")

    template = message.text.split(" ", 1)[1]
    await save_group_settings(grp_id, 'template', template)
    await sts.edit(f"✅ Successfully changed template for {title} to:\n\n{template}")


@Client.on_message((filters.command(["request", "Request"]) | filters.regex("#request") | filters.regex("#Request")) & filters.group)
async def requests(bot, message):
    if REQST_CHANNEL is None or SUPPORT_CHAT_ID is None:
        return  # Must add REQST_CHANNEL and SUPPORT_CHAT_ID to use this feature

    if message.reply_to_message and SUPPORT_CHAT_ID == message.chat.id:
        chat_id = message.chat.id
        reporter = str(message.from_user.id)
        mention = message.from_user.mention
        success = True
        content = message.reply_to_message.text
        try:
            if REQST_CHANNEL is not None:
                btn = [[
                    InlineKeyboardButton('🔍 View Request', url=f"{message.reply_to_message.link}"),
                    InlineKeyboardButton('🔧 Show Options', callback_data=f'show_option#{reporter}')
                ]]
                reported_post = await bot.send_message(chat_id=REQST_CHANNEL, text=f"<b>𝖱𝖾𝗉𝗈𝗋𝗍𝖾𝗋: {mention} ({reporter})\n\n𝖬𝖾𝗌𝗌𝖺𝗀𝖾: {content}</b>", reply_markup=InlineKeyboardMarkup(btn))
                success = True
            elif len(content) >= 3:
                for admin in ADMINS:
                    btn = [[
                        InlineKeyboardButton('🔍 View Request', url=f"{message.reply_to_message.link}"),
                        InlineKeyboardButton('🔧 Show Options', callback_data=f'show_option#{reporter}')
                    ]]
                    reported_post = await bot.send_message(chat_id=admin, text=f"<b>𝖱𝖾𝗉𝗈𝗋𝗍𝖾𝗋: {mention} ({reporter})\n\n𝖬𝖾𝗌𝗌𝖺𝗀𝖾: {content}</b>", reply_markup=InlineKeyboardMarkup(btn))
                    success = True
            else:
                if len(content) < 3:
                    await message.reply_text("<b>⚠️ You must type about your request [Minimum 3 characters]. Requests can't be empty.</b>")
                success = False
        except Exception as e:
            await message.reply_text(f"Error: {e}")
            pass

    elif SUPPORT_CHAT_ID == message.chat.id:
        chat_id = message.chat.id
        reporter = str(message.from_user.id)
        mention = message.from_user.mention
        success = True
        content = message.text
        keywords = ["#request", "/request", "#Request", "/Request"]
        for keyword in keywords:
            if keyword in content:
                content = content.replace(keyword, "")
        try:
            if REQST_CHANNEL is not None and len(content) >= 3:
                btn = [[
                    InlineKeyboardButton('🔍 View Request', url=f"{message.link}"),
                    InlineKeyboardButton('🔧 Show Options', callback_data=f'show_option#{reporter}')
                ]]
                reported_post = await bot.send_message(chat_id=REQST_CHANNEL, text=f"<b>𝖱𝖾𝗉𝗈𝗋𝗍𝖾𝗋: {mention} ({reporter})\n\n𝖬𝖾𝗌𝗌𝖺𝗀𝖾: {content}</b>", reply_markup=InlineKeyboardMarkup(btn))
                success = True
            elif len(content) >= 3:
                for admin in ADMINS:
                    btn = [[
                        InlineKeyboardButton('🔍 View Request', url=f"{message.link}"),
                        InlineKeyboardButton('🔧 Show Options', callback_data=f'show_option#{reporter}')
                    ]]
                    reported_post = await bot.send_message(chat_id=admin, text=f"<b>𝖱𝖾𝗉𝗈𝗋𝗍𝖾𝗋: {mention} ({reporter})\n\n𝖬𝖾𝗌𝗌𝖺𝗀𝖾: {content}</b>", reply_markup=InlineKeyboardMarkup(btn))
                    success = True
            else:
                if len(content) < 3:
                    await message.reply_text("<b>⚠️ You must type about your request [Minimum 3 characters]. Requests can't be empty.</b>")
                success = False
        except Exception as e:
            await message.reply_text(f"Eʀʀᴏʀ: {e}")
            pass

    else:
        success = False

    if success:
        btn = [[
            InlineKeyboardButton('🔍 View Request', url=f"{reported_post.link}")
        ]]
        await message.reply_text("<b>Your request has been added! Please wait for some time.</b>", reply_markup=InlineKeyboardMarkup(btn))

        
@Client.on_message(filters.command("send") & filters.user(ADMINS))
async def send_msg(bot, message):
    if message.reply_to_message:
        target_id = message.text.split(" ", 1)[1]
        out = "📥 **Users Saved in DB:**\n\n"
        success = False
        try:
            user = await bot.get_users(target_id)
            users = await db.get_all_users()
            async for usr in users:
                out += f"{usr['id']}"
                out += '\n'
            if str(user.id) in str(out):
                await message.reply_to_message.copy(int(user.id))
                success = True
            else:
                success = False
            if success:
                await message.reply_text(f"✅ **Your message has been successfully sent to {user.mention}.**")
            else:
                await message.reply_text("⚠️ **This user has not started this bot yet!**")
        except Exception as e:
            await message.reply_text(f"⚠️ **Error: {e}**")
    else:
        await message.reply_text("⚠️ **Use this command as a reply to any message using the target chat ID. For example: /send user_id**")


@Client.on_message(filters.command("deletename") & filters.user(ADMINS))
async def delete_multiple_files(bot, message):
    chat_type = message.chat.type
    if chat_type != enums.ChatType.PRIVATE:
        return await message.reply_text(f"<b>Hey {message.from_user.mention}, this command won't work in groups. It only works on my PM!</b>")
    
    try:
        keyword = message.text.split(" ", 1)[1]
        files, total = await get_bad_files(keyword)
    except:
        return await message.reply_text(f"<b>Hey {message.from_user.mention}, please provide a keyword along with the command to delete files.</b>")
    
    btn = [
        [
            InlineKeyboardButton(f"Delete ({total} files) 🗑️", callback_data=f"killfilesdq#{keyword}"),
            InlineKeyboardButton("No, Abort Operation ❌", callback_data="close_data")
        ]
    ]
    
    await message.reply_text(
        text=f"Are you sure you want to delete {total} files matching the keyword '{keyword}'? 🗑️\n\nNote: This could be a destructive action!",
        reply_markup=InlineKeyboardMarkup(btn),
        parse_mode=enums.ParseMode.HTML,
        quote=True,
    )

@Client.on_message(filters.command("deletefiles") & filters.user(ADMINS))
async def deletemultiplefiles(bot, message):
    btn = [[
            InlineKeyboardButton("Delete PreDVDs", callback_data="predvd"),
            InlineKeyboardButton("Delete CamRips", callback_data="camrip")
          ],[
            InlineKeyboardButton("Delete HDCams", callback_data="hdcam"),
            InlineKeyboardButton("Delete S-Prints", callback_data="s-print")
          ],[
            InlineKeyboardButton("Delete HDTVRip", callback_data="hdtvrip"),
            InlineKeyboardButton("Delete Cancel", callback_data="cancel_delete")
          ]]
    await message.reply_text(
        text="<b>Select the type of files you want to delete !\n\nThis will delete 100 files from the database for the selected type.</b>",
        reply_markup=InlineKeyboardMarkup(btn), quote=True,
    )
    
    
@Client.on_message(filters.command("shortlink") & filters.user(ADMINS))
async def shortlink(bot, message):
    chat_type = message.chat.type
    if chat_type == enums.ChatType.PRIVATE:
        return await message.reply_text(f"⚠️ **Hey {message.from_user.mention}, this command only works on groups!**")
    elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        grpid = message.chat.id
        title = message.chat.title
    else:
        return
    data = message.text
    userid = message.from_user.id
    user = await bot.get_chat_member(grpid, userid)
    if user.status != enums.ChatMemberStatus.ADMINISTRATOR and user.status != enums.ChatMemberStatus.OWNER and str(userid) not in ADMINS:
        return await message.reply_text("<b>You don't have access to use this command!</b>")
    else:
        pass
    try:
        command, shortlink_url, api = data.split(" ")
    except:
        return await message.reply_text("<b>Command Incomplete! 😕\n\nGive me a shortlink and API along with the command.\n\nFormat: /shortlink shorturllink.in 95a8195c40d31e0c3b6baa68813fcecb1239f2e9</b>")
    reply = await message.reply_text("<b>Please wait...</b>")
    await save_group_settings(grpid, 'shortlink', shortlink_url)
    await save_group_settings(grpid, 'shortlink_api', api)
    await save_group_settings(grpid, 'is_shortlink', True)
    await reply.edit_text(f"<b>Successfully added shortlink API for {title}.\n\nCurrent Shortlink Website: <code>{shortlink_url}</code>\nCurrent API: <code>{api}</code></b>")
    
