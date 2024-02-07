from pyrogram import Client, filters
from pyrogram.types import Message, User

from info import ADMINS  

# Define your command handler
@Client.on_message(filters.command("userinfo") & filters.user(ADMINS))
async def user_info(client, message: Message):
    # Check if the message contains an argument (user ID)
    if len(message.command) != 2:
        await message.reply("Please specify a user ID.")
        return

    # Extract the user ID from the command
    user_id = message.command[1]

    # Get the user object based on the provided user ID
    user = await client.get_users(user_id)

    # Display the user information
    user_info = f"User ID: {user.id}\n"
    user_info += f"Is self: {user.is_self}\n"
    user_info += f"Is contact: {user.is_contact}\n"
    user_info += f"Is mutual contact: {user.is_mutual_contact}\n"
    user_info += f"Is deleted: {user.is_deleted}\n"
    user_info += f"Is bot: {user.is_bot}\n"
    user_info += f"Is verified: {user.is_verified}\n"
    user_info += f"Is restricted: {user.is_restricted}\n"
    user_info += f"Is scam: {user.is_scam}\n"
    user_info += f"Is fake: {user.is_fake}\n"
    user_info += f"Is support: {user.is_support}\n"
    user_info += f"Is premium: {user.is_premium}\n"
    user_info += f"First name: {user.first_name}\n"
    user_info += f"Last name: {user.last_name}\n"
    user_info += f"Status: {user.status}\n"
    user_info += f"Last online date: {user.last_online_date}\n"
    user_info += f"Next offline date: {user.next_offline_date}\n"
    user_info += f"Username: {user.username}\n"
    user_info += f"Language code: {user.language_code}\n"
    user_info += f"Emoji status: {user.emoji_status}\n"
    user_info += f"DC ID: {user.dc_id}\n"
    user_info += f"Phone number: {user.phone_number}\n"
    user_info += f"Photo: {user.photo}\n"
    user_info += f"Restrictions: {user.restrictions}\n"

    await message.reply(user_info)
