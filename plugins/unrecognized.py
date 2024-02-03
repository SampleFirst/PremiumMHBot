from pyrogram import Client, filters
from pyrogram.types import Message

# Handle unrecognized commands
@Client.on_message(filters.command)
def unrecognized_command(client: Client, message: Message):
    client.send_message(message.chat.id, "Unrecognized command. Type /help for a list of available commands.")

