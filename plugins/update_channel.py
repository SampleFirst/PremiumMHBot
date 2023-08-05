import logging
import re
import base64
import asyncio
from struct import pack
from pyrogram.file_id import FileId
from pymongo.errors import DuplicateKeyError
from umongo import Instance, Document, fields
from motor.motor_asyncio import AsyncIOMotorClient
from marshmallow.exceptions import ValidationError
from info import (
    DATABASE_URI,
    DATABASE_NAME,
    COLLECTION_NAME,
    USE_CAPTION_FILTER,
    MAX_B_TN,
    UPDATE_CHANNEL,
    NOR_IMG
)
from utils import get_settings, save_group_settings

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

client = AsyncIOMotorClient(DATABASE_URI)
db = client[DATABASE_NAME]
instance = Instance.from_db(db)


@instance.register
class Media(Document):
    file_id = fields.StrField(attribute='_id')
    file_ref = fields.StrField(allow_none=True)
    file_name = fields.StrField(required=True)
    file_size = fields.IntField(required=True)
    file_type = fields.StrField(allow_none=True)
    mime_type = fields.StrField(allow_none=True)
    caption = fields.StrField(allow_none=True)

    class Meta:
        indexes = ('$file_name', )
        collection_name = COLLECTION_NAME


async def save_media_to_database(media):
    """Save media in the database and send a log to the update channel"""
    file_id, file_ref = unpack_new_file_id(media.file_id)
    file_name = re.sub(r"(_|\-|\.|\+)", " ", str(media.file_name))
    try:
        file = Media(
            file_id=file_id,
            file_ref=file_ref,
            file_name=file_name,
            file_size=media.file_size,
            file_type=media.file_type,
            mime_type=media.mime_type,
            caption=media.caption.html if media.caption else None,
        )
    except ValidationError:
        logger.exception('Error occurred while saving media in the database')
        return False, 2
    else:
        try:
            await file.commit()
        except DuplicateKeyError:
            logger.warning(
                f'{getattr(media, "file_name", "NO_MEDIA")} is already saved in the database'
            )
            return False, 0
        else:
            logger.info(f'{getattr(media, "file_name", "NO_MEDIA")} is saved to the database')

            # Send log to the update channel
            await send_update_log(media)

            return True, 1


async def send_update_log(media):
    """Send log to the update channel for newly added media"""
    file_name = getattr(media, "file_name", "NO_MEDIA")
    file_id = getattr(media, "file_id", "")
    file_type = getattr(media, "file_type", "")
    caption = getattr(media, "caption", "")
    imdb_poster = await get_poster(search, file=(files[0]).file_name) if settings.get("imdb") else None
    if imdb_poster and imdb_poster.get('poster'):
        poster = imdb_poster['poster']
        update_message = (
            f"New media added to the database:\n"
            f"File Name: {file_name}\n"
            f"File ID: {file_id}\n"
            f"File Type: {file_type}\n"
            f"Caption: {caption}\n"
            f"IMDb Poster: {poster}\n"
        )
    else:
        update_message = (
            f"New media added to the database:\n"
            f"File Name: {file_name}\n"
            f"File ID: {file_id}\n"
            f"File Type: {file_type}\n"
            f"Caption: {caption}\n"
            f"IMDb Poster: {NOR_IMG}\n"
        )

    await bot.send_message(UPDATE_CHANNEL, update_message)
    
    
