from pyrogram import Client, filters
from info import ADMINS


@Client.on_message(filters.command("group_info") & filters.user(ADMINS))
def group_info(client, message):
    chat = client.get_chat(message.chat.id)
    group_id = chat.id
    group_name = chat.title
    total_members = chat.members_count
    total_banned = len(client.get_chat_banned(chat.id))
    total_admins = len(client.get_chat_members(chat.id, filter="administrators"))
    total_bots = len(client.get_chat_members(chat.id, filter="bots"))

    info_text = f"Group ID: {group_id}\nGroup Name: {group_name}\nTotal Members: {total_members}\nTotal Banned Members: {total_banned}\nTotal Admins: {total_admins}\nTotal Bots: {total_bots}"

    client.send_message(message.chat.id, info_text)
    
