import motor.motor_asyncio
from info import DATABASE_NAME, DATABASE_URI
import pytz
from date import add_date
from datetime import date, datetime, timedelta

class Database:

    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.col = self.db.users
        self.grp = self.db.groups

    def new_user(self, id, name):
        return dict(
            id=id,
            name=name,
            file_id=None,
            bot_name=None,
            ban_status=dict(
                is_banned=False,
                ban_reason="",
            ),
            attempt_status=dict(
                is_attempt=False,
                attempt_active=False,
                attempt_date=None,
                attempt_validity=None,
            ),
            confirm_status=dict(
                is_confirm=False,
                confirm_active=False,
                confirm_date=None,
                confirm_validity=None,
            ),
            premium_status=dict(
                is_premium=False,
                premium_active=False,
                premium_date=None,
                premium_validity=None,
            ),
            cancel_status=dict(
                is_cancel=False,
                cancel_date=None,
            ),
        )

    def new_group(self, id, title, username):
        return dict(
            id=id,
            title=title,
            username=username,
            chat_status=dict(
                is_disabled=False,
                reason="",
            ),
        )

    # all col related functions
    async def add_user(self, id, name):
        user = self.new_user(id, name)
        await self.col.insert_one(user)

    async def is_user_exist(self, id):
        user = await self.col.find_one({'id': int(id)})
        return bool(user)

    async def total_users_count(self):
        count = await self.col.count_documents({})
        return count

    async def remove_ban(self, id):
        ban_status = dict(
            is_banned=False,
            ban_reason=''
        )
        await self.col.update_one({'id': id}, {'$set': {'ban_status': ban_status}})

    async def ban_user(self, id, ban_reason="No Reason"):
        ban_status = dict(
            is_banned=True,
            ban_reason=ban_reason
        )
        await self.col.update_one({'id': id}, {'$set': {'ban_status': ban_status}})

    async def get_ban_status(self, id):
        default = dict(
            is_banned=False,
            ban_reason=''
        )
        user = await self.col.find_one({'id': int(id)})
        if not user:
            return default
        return user.get('ban_status', default)

    async def get_all_users(self):
        return self.col.find({})

    async def delete_user(self, id):
        await self.col.delete_many({'id': int(id)})

    async def get_banned(self):
        users = self.col.find({'ban_status.is_banned': True})
        chats = self.grp.find({'chat_status.is_disabled': True})
        b_chats = [chat['id'] async for chat in chats]
        b_users = [user['id'] async for user in users]
        return b_users, b_chats

    # all grp related functions
    async def add_chat(self, chat, title, username):
        new_group_data = self.new_group(chat, title, username)
        await self.grp.insert_one(new_group_data)

    async def get_chat(self, chat):
        chat = await self.grp.find_one({'id': int(chat)})
        return False if not chat else chat.get('chat_status')

    async def re_enable_chat(self, id):
        chat_status = dict(
            is_disabled=False,
            reason="",
        )
        await self.grp.update_one({'id': int(id)}, {'$set': {'chat_status': chat_status}})

    async def disable_chat(self, chat, reason="No Reason"):
        chat_status = dict(
            is_disabled=True,
            reason=reason,
        )
        await self.grp.update_one({'id': int(chat)}, {'$set': {'chat_status': chat_status}})

    async def total_chat_count(self):
        count = await self.grp.count_documents({})
        return count

    async def get_all_chats(self):
        return self.grp.find({})

    async def delete_chat(self, chat_id):
        await self.grp.delete_many({'id': int(chat_id)})

    # New functions for attempt status

    async def add_attempt(self, id, attempt_active, bot_name, attempt_validity):
        now_date = add_date()
        attempt_status = dict(
            is_attempt=True,
            attempt_active=True,
            bot_name=bot_name,
            attempt_date=now_date,
            attempt_validity=attempt_validity,
        )
        await self.col.update_one({"id": id}, {"$set": {"attempt_status": attempt_status}})

    async def clear_attempt(self, id):
        attempt_status = dict(
            attempt_active=False,
            bot_name=None,
            attempt_date=None,
            attempt_validity=None,
        )
        await self.col.update_one({"id": id}, {"$set": {"attempt_status": attempt_status}})

    async def is_attempt_active(self, id, bot_name):
        user = await self.col.find_one({"id": id, "attempt_status.is_attempt": True, "attempt_status.bot_name": bot_name})
        return bool(user)

    async def get_user_attempts(self, id, bot_name=None):
        if bot_name:
            filter_params = {'id': id, 'bot_name': bot_name}
        else:
            filter_params = {'id': id}

        attempts = await self.dot.count_documents(filter_params)
        return attempts

    async def get_latest_attempt(self, id):
        latest_attempt = await self.dot.find_one(
            {'id': id},
            sort=[('attempt_date', -1)]  # Sort by attempt date in descending order
        )
        return latest_attempt

    async def total_attempts(self, bot_name=None):
        if bot_name:
            count = await self.col.count_documents({"attempt_status.attempt_active": True, "attempt_status.bot_name": bot_name})
        else:
            count = await self.col.count_documents({"attempt_status.attempt_active": True})
        return count

    # New functions for confirm status

    async def add_confirm(self, id, bot_name, file_id):
        now_date = add_date()
        confirm_status = dict(
            is_confirm=True,
            confirm_active=True,
            bot_name=bot_name,
            file_id=file_id,
            confirm_date=now_date,
        )
        await self.col.update_one({"id": id}, {"$set": {"confirm_status": confirm_status}})

    async def clear_confirm(self, id):
        confirm_status = dict(
            confirm_active=False,
            bot_name=None,
            file_id=None,
            confirm_date=None,
        )
        await self.col.update_one({"id": id}, {"$set": {"confirm_status": confirm_status}})

    async def is_confirm_active(self, id, bot_name):
        user = await self.col.find_one({"id": id, "confirm_status.is_confirm": True, "confirm_status.bot_name": bot_name})
        return bool(user)

    async def get_user_confirms(self, id, bot_name=None):
        if bot_name:
            filter_params = {'id': id, 'bot_name': bot_name}
        else:
            filter_params = {'id': id}

        attempts = await self.dot.count_documents(filter_params)
        return attempts

    async def get_latest_confirm(self, id):
        latest_attempt = await self.dot.find_one(
            {'id': id},
            sort=[('confirm_date', -1)]  # Sort by attempt date in descending order
        )
        return latest_attempt

    async def total_confirm(self, bot_name=None):
        if bot_name:
            count = await self.col.count_documents({"confirm_status.confirm_active": True, "confirm_status.bot_name": bot_name})
        else:
            count = await self.col.count_documents({"confirm_status.confirm_active": True})
        return count

    # New functions for premium status

    async def add_premium(self, id, bot_name, file_id, premium_validity):
        now_date = add_date()
        premium_status = dict(
            is_premium=True,
            premium_active=True,
            bot_name=bot_name,
            file_id=file_id,
            premium_date=now_date,
            premium_validity=premium_validity,
        )
        await self.col.update_one({"id": id}, {"$set": {"premium_status": premium_status}})

    async def clear_premium(self, id):
        premium_status = dict(
            premium_active=False,
            bot_name=None,
            file_id=None,
            premium_date=None,
            premium_validity=None,
        )
        await self.col.update_one({"id": id}, {"$set": {"premium_status": premium_status}})

    async def is_premium_active(self, id, bot_name):
        user = await self.col.find_one({"id": id, "premium_status.is_premium": True, "premium_status.bot_name": bot_name})
        return bool(user)

    async def get_user_premiums(self, id, bot_name=None):
        if bot_name:
            filter_params = {'id': id, 'bot_name': bot_name}
        else:
            filter_params = {'id': id}

        attempts = await self.dot.count_documents(filter_params)
        return attempts

    async def get_latest_premium(self, id):
        latest_attempt = await self.dot.find_one(
            {'id': id},
            sort=[('premium_date', -1)]  # Sort by attempt date in descending order
        )
        return latest_attempt

    async def total_premium(self, bot_name=None):
        if bot_name:
            count = await self.col.count_documents({"premium_status.premium_active": True, "premium_status.bot_name": bot_name})
        else:
            count = await self.col.count_documents({"premium_status.premium_active": True})
        return count

    # New functions for cancel status

    async def add_cancel(self, id, bot_name, file_id, cancel_date):
        cancel_status = dict(
            is_cancel=True,
            bot_name=bot_name,
            file_id=file_id,
            cancel_date=cancel_date,
        )
        await self.col.update_one({"id": id}, {"$set": {"cancel_status": cancel_status}})

    async def clear_cancel(self, id):
        cancel_status = dict(
            is_cancel=False,
            bot_name=None,
            file_id=None,
            cancel_date=None,
        )
        await self.col.update_one({"id": id}, {"$set": {"cancel_status": cancel_status}})

    async def is_cancel_active(self, id, bot_name):
        user = await self.col.find_one({"id": id, "cancel_status.is_cancel": True, "cancel_status.bot_name": bot_name})
        return bool(user)

    async def get_user_cancel(self, id, bot_name=None):
        if bot_name:
            filter_params = {'id': id, 'bot_name': bot_name}
        else:
            filter_params = {'id': id}

        cancels = await self.col.count_documents(filter_params)
        return cancels

    async def get_latest_cancel(self, id):
        latest_cancel = await self.col.find_one(
            {'id': id},
            sort=[('cancel_date', -1)]  # Sort by cancel date in descending order
        )
        return latest_cancel

    async def total_cancel(self, bot_name=None):
        if bot_name:
            count = await self.col.count_documents({"cancel_status.is_cancel": True, "cancel_status.bot_name": bot_name})
        else:
            count = await self.col.count_documents({"cancel_status.is_cancel": True})
        return count

    async def get_user_premium_stats(self, id):
        user = await self.col.find_one({'id': int(id)})
        if not user:
            return None
        premium_stats = user.get('premium_status', {})
        return premium_stats

    async def get_user_premium_status(self, id):
        user = await self.col.find_one({'id': int(id)})
        if not user:
            return None
        return user

    async def get_db_size(self):
        return (await self.db.command("dbstats"))['dataSize']

db = Database(DATABASE_URI, DATABASE_NAME)
