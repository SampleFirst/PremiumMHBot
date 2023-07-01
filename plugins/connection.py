from pyrogram import filters, Client, enums
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from database.connections_mdb import add_connection, all_connections, if_active, delete_connection
from info import ADMINS
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)


@Client.on_message((filters.private | filters.group) & filters.command('connect'))
async def add_connection(client, message):
    userid = message.from_user.id if message.from_user else None
    if not userid:
        return await message.reply(f"🔒 You are an anonymous admin. Use /connect {message.chat.id} in PM")

    chat_type = message.chat.type

    if chat_type == enums.ChatType.PRIVATE:
        try:
            cmd, group_id = message.text.split(" ", 1)
        except:
            await message.reply_text(
                "❌ Enter in the correct format!\n\n"
                "<code>/connect groupid</code>\n\n"
                "<i>Get your Group ID by adding this bot to your group and use <code>/id</code></i>",
                quote=True
            )
            return

    elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        group_id = message.chat.id

    try:
        st = await client.get_chat_member(group_id, userid)
        if (
            st.status != enums.ChatMemberStatus.ADMINISTRATOR
            and st.status != enums.ChatMemberStatus.OWNER
            and userid not in ADMINS
        ):
            await message.reply_text("⚠️ You should be an admin in the given group!", quote=True)
            return
    except Exception as e:
        logger.exception(e)
        await message.reply_text(
            "❌ Invalid Group ID!\n\nIf correct, make sure I'm present in your group!!",
            quote=True,
        )
        return

    try:
        st = await client.get_chat_member(group_id, "me")
        if st.status == enums.ChatMemberStatus.ADMINISTRATOR:
            ttl = await client.get_chat(group_id)
            title = ttl.title

            add_con = await add_connection(str(group_id), str(userid))
            if add_con:
                await message.reply_text(
                    f"✅ Successfully connected to **{title}**\nNow manage your group from my PM!",
                    quote=True,
                    parse_mode=enums.ParseMode.MARKDOWN
                )
                if chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
                    await client.send_message(
                        userid,
                        f"✅ Connected to **{title}**!",
                        parse_mode=enums.ParseMode.MARKDOWN
                    )
            else:
                await message.reply_text(
                    "ℹ️ You're already connected to this chat!",
                    quote=True
                )
        else:
            await message.reply_text("❌ Add me as an admin in the group", quote=True)
    except Exception as e:
        logger.exception(e)
        await message.reply_text('❌ Some error occurred! Try again later.', quote=True)
        return


@Client.on_message((filters.private | filters.group) & filters.command('disconnect'))
async def delete_connection(client, message):
    userid = message.from_user.id if message.from_user else None
    if not userid:
        return await message.reply(f"🔒 You are an anonymous admin. Use /connect {message.chat.id} in PM")

    chat_type = message.chat.type

    if chat_type == enums.ChatType.PRIVATE:
        await message.reply_text("❓ Run /connections to view or disconnect from groups!", quote=True)

    elif chat_type in [enums.ChatType.GROUP, enums.ChatType.SUPERGROUP]:
        group_id = message.chat.id

        st = await client.get_chat_member(group_id, userid)
        if (
            st.status != enums.ChatMemberStatus.ADMINISTRATOR
            and st.status != enums.ChatMemberStatus.OWNER
            and str(userid) not in ADMINS
        ):
            return

        del_con = await delete_connection(str(userid), str(group_id))
        if del_con:
            await message.reply_text("✅ Successfully disconnected from this chat", quote=True)
        else:
            await message.reply_text("❌ This chat isn't connected to me!\nDo /connect to connect.", quote=True)


@Client.on_message(filters.private & filters.command(["connections"]))
async def connections(client, message):
    userid = message.from_user.id

    group_ids = await all_connections(str(userid))
    if group_ids is None:
        await message.reply_text(
            "❌ There are no active connections!! Connect to some groups first.",
            quote=True
        )
        return

    buttons = []
    for group_id in group_ids:
        try:
            ttl = await client.get_chat(int(group_id))
            title = ttl.title
            active = await if_active(str(userid), str(group_id))
            act = " - ACTIVE" if active else ""
            buttons.append(
                [
                    InlineKeyboardButton(
                        text=f"{title}{act}", callback_data=f"groupcb:{group_id}:{act}"
                    )
                ]
            )
        except:
            pass

    if buttons:
        await message.reply_text(
            "🔗 Your connected group details:\n\n",
            reply_markup=InlineKeyboardMarkup(buttons),
            quote=True
        )
    else:
        await message.reply_text(
            "❌ There are no active connections!! Connect to some groups first.",
            quote=True
        )
        