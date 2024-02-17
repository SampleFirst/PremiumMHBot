# users_chats_db.py
from datetime import date, datetime
import calendar 
import pytz
import motor.motor_asyncio
from info import DATABASE_NAME, DATABASE_URI


class Database:
    
    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.col = self.db.users
        self.grp = self.db.groups


    def new_user(self, id, name):
        tz = pytz.timezone('Asia/Kolkata')
        return dict(
            id = id,
            name = name,
            ban_status=dict(
                is_banned=False,
                ban_reason="",
            ),
            timestamp=datetime.now(tz)
        )

    def new_group(self, id, title):
        tz = pytz.timezone('Asia/Kolkata')
        return dict(
            id = id,
            title = title,
            chat_status=dict(
                is_disabled=False,
                is_verified=False,
                reason="",
            ),
            timestamp=datetime.now(tz)
        )
    
    async def update_verification(self, id, date, time):
        status = {
            'date': str(date),
            'time': str(time)
        }
        await self.col.update_one({'id': int(id)}, {'$set': {'verification_status': status}})

    async def get_verified(self, id):
        default = {
            'date': "1999-12-31",
            'time': "23:59:59"
        }
        user = await self.col.find_one({'id': int(id)})
        if user:
            return user.get("verification_status", default)
        return default
    
    # All Users Database Functions 
    
    async def add_user(self, id, name):
        user = self.new_user(id, name)
        await self.col.insert_one(user)
    
    async def is_user_exist(self, id):
        user = await self.col.find_one({'id':int(id)})
        return bool(user)
    
    async def total_users_count(self):
        count = await self.col.count_documents({})
        return count
    
    async def ban_user(self, user_id, ban_reason="No Reason"):
        ban_status = dict(
            is_banned=True,
            ban_reason=ban_reason
        )
        await self.col.update_one({'id': user_id}, {'$set': {'ban_status': ban_status}})
    
    async def remove_ban(self, id):
        ban_status = dict(
            is_banned=False,
            ban_reason=''
        )
        await self.col.update_one({'id': id}, {'$set': {'ban_status': ban_status}})

    async def get_ban_status(self, id):
        default = dict(
            is_banned=False,
            ban_reason=''
        )
        user = await self.col.find_one({'id':int(id)})
        if not user:
            return default
        return user.get('ban_status', default)

    async def get_all_users(self):
        return self.col.find({})
    
    async def delete_user(self, user_id):
        await self.col.delete_many({'id': int(user_id)})

    async def daily_users_count(self, today):
        tz = pytz.timezone('Asia/Kolkata')
        start = tz.localize(datetime.combine(today, datetime.min.time()))
        end = tz.localize(datetime.combine(today, datetime.max.time()))
        count = await self.col.count_documents({
            'timestamp': {'$gte': start, '$lt': end}
        })
        return count
    
    async def monthly_users_count(self, month, year):
        tz = pytz.timezone('Asia/Kolkata')
        start = tz.localize(datetime.combine(datetime(year, month, 1), datetime.min.time()))
        end = tz.localize(datetime.combine(datetime(year, month, calendar.monthrange(year, month)[1]), datetime.max.time()))
        count = await self.col.count_documents({
            'timestamp': {'$gte': start, '$lt': end}
        })
        return count
        
    async def get_banned(self):
        users = self.col.find({'ban_status.is_banned': True})
        chats = self.grp.find({'chat_status.is_disabled': True})
        is_verified = self.grp.find({'chat_status.is_verified': True})
        b_chats = [chat['id'] async for chat in chats]
        b_users = [user['id'] async for user in users]
        v_chats = [chat['id'] async for chat in is_verified]
        return b_users, b_chats, v_chats
    
    
    # All Group Database Functions 
    
    async def add_chat(self, chat, title):
        chat = self.new_group(chat, title)
        await self.grp.insert_one(chat)
    
    async def is_chat_exist(self, id):
        user = await self.grp.find_one({'id':int(id)})
        return bool(user)
    
    async def total_chats_count(self):
        count = await self.grp.count_documents({})
        return count
        
    async def disable_chat(self, chat, reason="No Reason"):
        chat_status=dict(
            is_disabled=True,
            reason=reason,
            )
        await self.grp.update_one({'id': int(chat)}, {'$set': {'chat_status': chat_status}})
   
    async def enable_chat(self, id):
        chat_status=dict(
            is_disabled=False,
            reason="",
            )
        await self.grp.update_one({'id': int(id)}, {'$set': {'chat_status': chat_status}})
        
    async def verify_chat(self, chat):
        chat_status=dict(
            is_verified=True,
            )
        await self.grp.update_one({'id': int(chat)}, {'$set': {'chat_status': chat_status}})
    
    async def get_chat_status(self, id):
        default = dict(
            is_disabled=False,
            ban_reason=''
        )
        user = await self.grp.find_one({'id':int(id)})
        if not user:
            return default
        return user.get('chat_status', default)
        
    async def get_all_chats(self):
        return self.grp.find({})
        
    async def delete_chat(self, id):
        await self.grp.delete_many({'id': int(id)})

    async def daily_chats_count(self, today):
        tz = pytz.timezone('Asia/Kolkata')
        start = tz.localize(datetime.combine(today, datetime.min.time()))
        end = tz.localize(datetime.combine(today, datetime.max.time()))
        count = await self.grp.count_documents({
            'timestamp': {'$gte': start, '$lt': end}
        })
        return count
        
    async def monthly_chats_count(self, month, year):
        tz = pytz.timezone('Asia/Kolkata')
        start = tz.localize(datetime.combine(datetime(year, month, 1), datetime.min.time()))
        end = tz.localize(datetime.combine(datetime(year, month, calendar.monthrange(year, month)[1]), datetime.max.time()))
        count = await self.grp.count_documents({
            'timestamp': {'$gte': start, '$lt': end}
        })
        return count
        
    async def get_db_size(self):
        return (await self.db.command("dbstats"))['dataSize']

db = Database(DATABASE_URI, DATABASE_NAME)
