import motor.motor_asyncio
from info import DATABASE_NAME, DATABASE_URI, IMDB, IMDB_TEMPLATE, MELCOW_NEW_USERS, P_TTI_SHOW_OFF, SINGLE_BUTTON, SPELL_CHECK_REPLY, PROTECT_CONTENT, AUTO_DELETE, MAX_BTN, AUTO_FFILTER, SHORTLINK_API, SHORTLINK_URL, DATABASE_LIMIT, BOT_LIMIT, IS_SHORTLINK, PREMIUM_PRICE
import pytz
from datetime import date, datetime, timedelta

class Database:

    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.col = self.db.users
        self.grp = self.db.groups
        self.dot = self.db.users_dot
        self.udb = self.db.users_db
        self.pro = self.db.premium_dot
        self.pre = self.db.premium_db

    # verification 
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
        user = await self.col.find_one({'id': int(id)})
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
        
    # all dot related functions
    async def add_attempt_dot(self, user_id, user_name, selected_bot, attempt_number, attempt_number_selected_bot, current_date_time, validity_date):
        attempt_data = {
            'user_id': user_id,
            'user_name': user_name,
            'selected_bot': selected_bot,
            'attempt_number': attempt_number,
            'attempt_number_selected_bot': attempt_number_selected_bot,
            'current_date_time': current_date_time,
            'validity_date': validity_date
        }
        await self.dot.insert_one(attempt_data)
    

    async def get_user_attempts_dot(self, user_id, selected_bot):
        attempts = await self.dot.count_documents({'user_id': user_id, 'selected_bot': selected_bot})
        return attempts
        
    async def get_latest_attempt_dot(self, user_id):
        latest_attempt = await self.dot.find_one(
            {'user_id': user_id},
            sort=[('current_date_time', -1)]  # Sort by datetime in descending order
        )
        return latest_attempt

    async def get_total_attempts_dot(self, selected_bot):
        total_attempts = await self.dot.count_documents({'selected_bot': selected_bot})
        return total_attempts

    async def get_daily_attempts_dot(self, today):
        tz = pytz.timezone('Asia/Kolkata')
        start = tz.localize(datetime.combine(today, datetime.min.time()))
        end = tz.localize(datetime.combine(today, datetime.max.time()))
        daily_count = await self.dot.count_documents({
            'current_date_time': {'$gte': start, '$lt': end}
        })
        return daily_count
    
    async def get_single_daily_attempts_dot(self, today, selected_bot):
        tz = pytz.timezone('Asia/Kolkata')
        start = tz.localize(datetime.combine(today, datetime.min.time()))
        end = tz.localize(datetime.combine(today, datetime.max.time()))
        daily_bot_count = await self.dot.count_documents({
            'selected_bot': selected_bot,
            'current_date_time': {'$gte': start, '$lt': end}
        })
        return daily_bot_count
        
    async def get_monthly_attempts_dot(self, year, month):
        tz = pytz.timezone('Asia/Kolkata')
        first_day_of_month = tz.localize(datetime(year, month, 1, 0, 0, 0))
        last_day_of_month = tz.localize(datetime(year, month + 1, 1, 0, 0, 0)) - timedelta(microseconds=1)        
        monthly_count = await self.dot.count_documents({
            'current_date_time': {'$gte': first_day_of_month, '$lt': last_day_of_month}
        })
        return monthly_count

    async def get_monthly_attempts_dot(self, year, month, selected_bot):
        tz = pytz.timezone('Asia/Kolkata')
        first_day_of_month = tz.localize(datetime(year, month, 1, 0, 0, 0))
        last_day_of_month = tz.localize(datetime(year, month + 1, 1, 0, 0, 0)) - timedelta(microseconds=1)
        
        monthly_bot_count = await self.dot.count_documents({
            'selected_bot': selected_bot,
            'current_date_time': {'$gte': first_day_of_month, '$lt': last_day_of_month}
        })
        return monthly_bot_count
        
    async def add_user_cancel_dot(self, user_id, user_name, selected_bot, current_date_time):
        cancel_data = {
            'user_id': user_id,
            'user_name': user_name,
            'selected_bot': selected_bot,
            'current_date_time': current_date_time,
        }
        await self.dot.insert_one(cancel_data)

    async def get_user_cancels_dot(self, user_id):
        cancels = await self.dot.count_documents({'user_id': user_id, 'current_date_time': {'$exists': True}})
        return cancels
        
    async def get_total_cancels_dot(self):
        total_cancel_users = await self.dot.count_documents({'cancel_data': {'$exists': True}})
        return total_cancel_users
    
    # all pro related functions
    async def add_user_premium_dot(self, user_id, user_name, selected_bot, current_date_time, validity_months):
        expiry_date = current_date_time + timedelta(days=validity_months * 30)
        premium_data = {
            'user_id': user_id,
            'user_name': user_name,
            'selected_bot': selected_bot,
            'current_date_time': current_date_time,
            'validity_months': validity_months,
            'expiry_date': expiry_date
        }
        await self.pro.insert_one(premium_data)

    async def get_user_total_premium_dot(self, user_id):
        premium_count = await self.pro.count_documents({'user_id': user_id})
        return premium_count
        
    async def get_user_premium_active_dot(self, user_id):
        tz = pytz.timezone('Asia/Kolkata')
        now = datetime.now(tz) 
        active_premium = await self.pro.count_documents({'user_id': user_id, 'expiry_date': {'$gt': now}})
        return active_premium
        
    async def get_user_total_payments_dot(self, user_id):
        total_user_payments = await self.pro.count_documents({'user_id': user_id}) * PREMIUM_PRICE
        return total_user_payments
        
    async def get_total_premium_dot(self):
        total_premium_users = await self.pro.count_documents({})
        return total_premium_users
        
    async def get_total_earnings_dot(self):
        total_earnings = await self.pro.count_documents({}) * PREMIUM_PRICE
        return total_earnings

    # all udb related function
    async def add_attempt_db(self, user_id, user_name, selected_db, attempt_number, current_date_time, validity_date):
        attempt_data = {
            'user_id': user_id,
            'user_name': user_name,
            'selected_db': selected_db,
            'attempt_number': attempt_number,
            'current_date_time': current_date_time,
            'validity_date': validity_date
        }
        await self.udb.insert_one(attempt_data)
    
    async def get_user_attempts_db(self, user_id):
        attempts = await self.udb.count_documents({'user_id': user_id})
        return attempts

    async def get_latest_attempt_db(self, user_id):
        latest_attempt = await self.udb.find_one(
            {'user_id': user_id},
            sort=[('current_date_time', -1)]  # Sort by datetime in descending order
        )
        return latest_attempt

    async def get_total_attempts_db(self, selected_db):
        total_attempts = await self.udb.count_documents({'selected_db': selected_db})
        return total_attempts

    async def add_user_cancel_db(self, user_id, user_name, selected_db, current_date_time):
        cancel_data = {
            'user_id': user_id,
            'user_name': user_name,
            'selected_db': selected_db,
            'current_date_time': current_date_time,
        }
        await self.udb.insert_one(cancel_data)

    async def get_user_cancels_db(self, user_id):
        cancels = await self.udb.count_documents({'user_id': user_id, 'current_date_time': {'$exists': True}})
        return cancels

    async def get_total_cancels_db(self):
        total_cancel_users = await self.udb.count_documents({'cancel_data': {'$exists': True}})
        return total_cancel_users
        
    # all pre related functions
    async def add_user_premium_db(self, user_id, user_name, selected_db, current_date_time, validity_months):
        expiry_date = current_date_time + timedelta(days=validity_months * 30)
        premium_data = {
            'user_id': user_id,
            'user_name': user_name,
            'selected_db': selected_db,
            'current_date_time': current_date_time,
            'validity_months': validity_months,
            'expiry_date': expiry_date
        }
        await self.pre.insert_one(premium_data)

    async def get_user_total_premium_db(self, user_id):
        premium_count = await self.pre.count_documents({'user_id': user_id})
        return premium_count
        
    async def get_user_premium_active_db(self, user_id):
        tz = pytz.timezone('Asia/Kolkata')
        now = datetime.now(tz) 
        active_premium = await self.pre.count_documents({'user_id': user_id, 'expiry_date': {'$gt': now}})
        return active_premium
        
    async def get_user_total_payments_db(self, user_id):
        total_user_payments = await self.pre.count_documents({'user_id': user_id}) * PREMIUM_PRICE
        return total_user_payments
        
    async def get_total_premium_db(self):
        total_premium_users = await self.pro.count_documents({})
        return total_premium_users
    
    async def get_total_earnings_db(self):
        total_earnings = await self.pre.count_documents({}) * PREMIUM_PRICE
        return total_earnings
    
    async def update_settings(self, id, settings):
        await self.grp.update_one({'id': int(id)}, {'$set': {'settings': settings}})
    
    async def get_settings(self, id):
        default = {
            'button': SINGLE_BUTTON,
            'botpm': P_TTI_SHOW_OFF,
            'file_secure': PROTECT_CONTENT,
            'imdb': IMDB,
            'spell_check': SPELL_CHECK_REPLY,
            'welcome': MELCOW_NEW_USERS,
            'auto_delete': AUTO_DELETE,
            'auto_ffilter': AUTO_FFILTER,
            'max_btn': MAX_BTN,
            'template': IMDB_TEMPLATE,
            'shortlink': SHORTLINK_URL,
            'shortlink_api': SHORTLINK_API,
            'is_shortlink': IS_SHORTLINK
        }
        chat = await self.grp.find_one({'id': int(id)})
        if chat:
            return chat.get('settings', default)
        return default
    
    async def get_db_size(self):
        return (await self.db.command("dbstats"))['dataSize']    

db = Database(DATABASE_URI, DATABASE_NAME)
