# users_chats_db.py
from datetime import date, datetime
import calendar  # Add this line to import the calendar module
import pytz
import motor.motor_asyncio
from info import DATABASE_NAME, DATABASE_URI

class Database:
    
    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.col = self.db.users
        self.grp = self.db.groups
        self.att = self.db.attempt
        self.con = self.db.confirm
        self.pre = self.db.premium

    def new_user(self, id, name):
        tz = pytz.timezone('Asia/Kolkata')  # Define tz here
        return dict(
            id=id,
            name=name,
            ban_status=dict(
                is_banned=False,
                ban_reason="",
            ),
            timestamp=datetime.now(tz)
        )

    # Request Verification => S - 1
    def new_group(self, id, title):
        tz = pytz.timezone('Asia/Kolkata')  # Define tz here
        return dict(
            id=id,
            title=title,
            chat_status=dict(
                is_disabled=False,
                is_verified=False,
                reason="",
            ),
            timestamp=datetime.now(tz)
        )

    def new_attempt(self, id, name, is_att, att_active, att_name, att_type, att_date, att_validity):
        tz = pytz.timezone('Asia/Kolkata')  # Define tz here
        return dict(
            id=id,
            name=name,
            is_att=is_att,
            att_active=att_active,
            att_name=att_name,
            att_type=att_type,
            att_date=att_date,
            att_validity=att_validity,
            cancel_status=dict(
                is_cancel=False,
                ban_reason="",
            ),
            timestamp=datetime.now(tz)
        )

    def new_confirm(self, id, name, is_con, con_active, con_name, con_type, con_date, con_validity):
        tz = pytz.timezone('Asia/Kolkata')  # Define tz here
        return dict(
            id=id,
            name=name,
            is_con=is_con,
            con_active=con_active,
            con_name=con_name,
            con_type=con_type,
            con_date=con_date,
            con_validity=con_validity,
            cancel_status=dict(
                is_cancel=False,
                ban_reason="",
            ),
            timestamp=datetime.now(tz)
        )

    def new_premium(self, id, name, is_pre, pre_active, pre_name, pre_type, pre_date, pre_validity):
        tz = pytz.timezone('Asia/Kolkata')  # Define tz here
        return dict(
            id=id,
            name=name,
            is_pre=is_pre,
            pre_active=pre_active,
            pre_name=pre_name,
            pre_type=pre_type,
            pre_date=pre_date,
            pre_validity=pre_validity,
            cancel_status=dict(
                is_cancel=False,
                ban_reason="",
            ),
            timestamp=datetime.now(tz)
        )
        
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
        
    async def daily_attempts_count(self, today, att_name=None):
        tz = pytz.timezone('Asia/Kolkata')
        start = tz.localize(datetime.combine(today, datetime.min.time()))
        end = tz.localize(datetime.combine(today, datetime.max.time()))
        query = {'timestamp': {'$gte': start, '$lt': end}}
        if att_name:
            query['att_name'] = att_name
        count = await self.att.count_documents(query)
        return count
    
    async def monthly_attempts_count(self, month, year, att_name=None):
        tz = pytz.timezone('Asia/Kolkata')
        start = tz.localize(datetime.combine(datetime(year, month, 1), datetime.min.time()))
        end = tz.localize(datetime.combine(datetime(year, month, calendar.monthrange(year, month)[1]), datetime.max.time()))
        query = {'timestamp': {'$gte': start, '$lt': end}}
        if att_name:
            query['att_name'] = att_name
        count = await self.att.count_documents(query)
        return count
        
    async def daily_confirms_count(self, today):
        tz = pytz.timezone('Asia/Kolkata')
        start = tz.localize(datetime.combine(today, datetime.min.time()))
        end = tz.localize(datetime.combine(today, datetime.max.time()))
        count = await self.con.count_documents({
            'timestamp': {'$gte': start, '$lt': end}
        })
        return count
        
    async def monthly_confirms_count(self, month, year):
        tz = pytz.timezone('Asia/Kolkata')
        start = tz.localize(datetime.combine(datetime(year, month, 1), datetime.min.time()))
        end = tz.localize(datetime.combine(datetime(year, month, calendar.monthrange(year, month)[1]), datetime.max.time()))
        count = await self.con.count_documents({
            'timestamp': {'$gte': start, '$lt': end}
        })
        return count
        
    async def daily_premiums_count(self, today):
        tz = pytz.timezone('Asia/Kolkata')
        start = tz.localize(datetime.combine(today, datetime.min.time()))
        end = tz.localize(datetime.combine(today, datetime.max.time()))
        count = await self.pre.count_documents({
            'timestamp': {'$gte': start, '$lt': end}
        })
        return count
    
    async def monthly_premiums_count(self, month, year):
        tz = pytz.timezone('Asia/Kolkata')
        start = tz.localize(datetime.combine(datetime(year, month, 1), datetime.min.time()))
        end = tz.localize(datetime.combine(datetime(year, month, calendar.monthrange(year, month)[1]), datetime.max.time()))
        count = await self.pre.count_documents({
            'timestamp': {'$gte': start, '$lt': end}
        })
        return count
        
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
    
    async def ban_user(self, user_id, ban_reason="No Reason"):
        ban_status = dict(
            is_banned=True,
            ban_reason=ban_reason
        )
        await self.col.update_one({'id': user_id}, {'$set': {'ban_status': ban_status}})

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
                
    async def get_banned(self):
        users = self.col.find({'ban_status.is_banned': True})
        chats = self.grp.find({'chat_status.is_disabled': True})
        is_verified = self.grp.find({'chat_status.is_verified': True})
        b_chats = [chat['id'] async for chat in chats]
        b_users = [user['id'] async for user in users]
        lz_verified = [chat['id'] async for chat in is_verified]
        return b_users, b_chats, lz_verified
    
    async def verify_chat(self, chat):
        chat_status=dict(
            is_verified=True,
            )
        await self.grp.update_one({'id': int(chat)}, {'$set': {'chat_status': chat_status}})
    
    async def add_chat(self, chat, title):
        chat = self.new_group(chat, title)
        await self.grp.insert_one(chat)
    
    async def get_chat(self, chat):
        chat = await self.grp.find_one({'id':int(chat)})
        return False if not chat else chat.get('chat_status')
    
    async def re_enable_chat(self, id):
        chat_status=dict(
            is_disabled=False,
            reason="",
            )
        await self.grp.update_one({'id': int(id)}, {'$set': {'chat_status': chat_status}})

    async def disable_chat(self, chat, reason="No Reason"):
        chat_status=dict(
            is_disabled=True,
            reason=reason,
            )
        await self.grp.update_one({'id': int(chat)}, {'$set': {'chat_status': chat_status}})

    async def total_chat_count(self):
        count = await self.grp.count_documents({})
        return count
        
    async def add_attempt(self, id, name, att_name, att_type, att_date, att_validity):
        attempt = self.new_attempt(
            id=id, 
            name=name,
            is_att=True,
            att_active=True,
            att_name=att_name, 
            att_type=att_type, 
            att_date=att_date,
            att_validity=att_validity,
        )
        await self.att.insert_one(attempt)

    async def is_attempt_active(self, id, att_name, att_type):
        last_attempt = await self.att.find_one({'att_name': att_name, 'att_type': att_type}, sort=[('_id', -1)])
        if last_attempt:
            return last_attempt['att_active']
        return None

    async def total_attempts_count(self, att_name=None, att_type=None):
        query = {}
        if att_name:
            query['att_name'] = att_name
        if att_type:
            query['att_type'] = att_type
        count = await self.att.count_documents(query)
        return count
        
    async def get_all_attempts(self):
        return self.att.find({})
        
    async def add_confirm(self, id, name, is_con, con_active, con_name, con_type, con_date, con_validity):
        confirm = self.new_confirm(id, name, is_con, con_active, con_name, con_type, con_date, con_validity)
        await self.con.insert_one(confirm)

    async def is_confirm_active(self, id, con_name, con_type):
        last_confirm = await self.con.find_one({'con_name': con_name, 'con_type': con_type}, sort=[('_id', -1)])
        if last_confirm:
            return last_confirm['con_active']
        return None

    async def total_confirms_count(self, con_name=None, con_type=None):
        query = {}
        if con_name:
            query['con_name'] = con_name
        if con_type:
            query['con_type'] = con_type
        count = await self.con.count_documents(query)
        return count
        
    async def get_all_confirms(self):
        return self.con.find({})
        
    async def add_premium(self, id, name, is_pre, pre_active, pre_name, pre_type, pre_date, pre_validity):
        premium = self.new_premium(id, name, is_pre, pre_active, pre_name, pre_type, pre_date, pre_validity)
        await self.pre.insert_one(premium)

    async def is_premium_active(self, id, pre_name, pre_type):
        last_premium = await self.pre.find_one({'pre_name': pre_name, 'pre_type': pre_type}, sort=[('_id', -1)])
        if last_premium:
            return last_premium['pre_active']
        return None
        
    async def total_premiums_count(self, pre_name=None, pre_type=None):
        query = {}
        if pre_name:
            query['pre_name'] = pre_name
        if pre_type:
            query['pre_type'] = pre_type
        count = await self.pre.count_documents(query)
        return count
        
    async def get_all_premiums(self):
        return self.pre.find({})
        
    async def get_db_size(self):
        return (await self.db.command("dbstats"))['dataSize']


db = Database(DATABASE_URI, DATABASE_NAME)

