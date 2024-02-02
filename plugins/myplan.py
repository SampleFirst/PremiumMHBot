from pyrogram import Client, filters
from pyrogram.types import Message
from database.users_chats_db import db
from info import ADMINS, LOG_CHANNEL


# Add this new command function after the existing commands in your command.py file
@Client.on_message(filters.command('myplan'))
async def get_my_plan_details(_, message):
    """Get plan details for the user who issued the command"""
    try:
        # Retrieve user details from the database using the user who issued the command
        user = await db.get_user_status(message.from_user.id)

        if user:
            # Check if the user has an active premium plan
            if user['premium_status']['premium_active']:
                plan_details = (
                    f"User ID: {user['id']}\n"
                    f"User Name: {user['name']}\n\n"
                    f"Plan: Active\n"
                    f"Bot Name: {user['premium_status']['bot_name']}\n"
                    f"Premium Date: {user['premium_status']['premium_date']}\n"
                    f"Validity: {user['premium_status']['premium_validity']}\n"
                    # Add any additional details as needed
                )
            else:
                plan_details = (
                    f"User ID: {user['id']}\n"
                    f"User Name: {user['name']}\n\n"
                    f"Plan: None\n"
                    # Add any additional details as needed
                )
            # Send the plan details as a reply
            await message.reply_text(plan_details)
        else:
            # User not found in the database
            await message.reply_text("User not found in the database.")

    except Exception as e:
        # Handle other exceptions
        await message.reply_text(str(e))
      
