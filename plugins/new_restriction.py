import asyncio
from pyrogram import Client, filters, enums
from info import ADMINS, LOG_CHANNEL  
import logging
from pyrogram.enums import MessageEntityType

# Define allowed entity types (adjust as needed)
allowed_entity_types = [
    MessageEntityType.MENTION,
    MessageEntityType.HASHTAG,
    MessageEntityType.CASHTAG,
    MessageEntityType.BOT_COMMAND,
    MessageEntityType.URL,
    MessageEntityType.EMAIL,
    MessageEntityType.PHONE_NUMBER,
    MessageEntityType.BOLD,
    MessageEntityType.ITALIC,
    MessageEntityType.UNDERLINE,
    MessageEntityType.STRIKETHROUGH,
    MessageEntityType.SPOILER,
    MessageEntityType.CODE,
    MessageEntityType.PRE,
    MessageEntityType.BLOCKQUOTE,
    MessageEntityType.TEXT_LINK,
    MessageEntityType.TEXT_MENTION,
    MessageEntityType.CUSTOM_EMOJI,
]


@Client.on_message(filters.group & filters.text)
async def restrict_entity(client: Client, message: types.Message):
    """
    Restricts links and logs deleted messages in a group.

    Args:
        client: The Pyrogram client instance.
        message: The incoming message object.
    """

    if message.from_user.id in ADMINS or message.from_user.status in (
        enums.ChatMemberStatus.ADMINISTRATOR,
        enums.ChatMemberStatus.OWNER,
    ):
        return  # Skip processing for admins or owners

    deleted_entities = []
    for entity in message.entities:
        if entity.type in allowed_entity_types:  # Use a defined list
            deleted_entities.append(entity.type)  # Track deleted entities

    if deleted_entities:
        # Construct formatted log message with specific entity types
        log_message = f"Deleted message from chat {message.chat.title} (ID: {message.chat.id}) containing:"
        for entity_type in deleted_entities:
            log_message += f" '{entity_type}'"

        try:
            # Delete the message, handling potential exceptions
            await message.delete()
            await client.send_message(
                LOG_CHANNEL,
                log_message + f"\nThis message sent by {message.from_user.username}: \"{message.text}\"",
            )
        except Exception as e:
            logging.error(f"Error deleting message: {e}")


