import re
from pyrogram import Client, filters


@Client.on_message(filters.command)
def check_command(client, message):
    # Get the list of bot commands
    bot_commands = [command.command for command in client.bot.get_my_bots_commands()]
    
    # Check if the user's message is a command and not in the list of bot commands
    if message.text.split()[0] in bot_commands:
        return
    else:
        client.send_message(message.chat.id, "This command is not assigned in the bot.")

