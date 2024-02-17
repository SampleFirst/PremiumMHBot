# attempt_db.py
from datetime import date, datetime
import calendar 
import pytz
import motor.motor_asyncio
from info import DATABASE_NAME, DATABASE_URI


class Database:
    
    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.att = self.db.attempt


    def new_attempt(self, id, name, is_att, att_active, att_name, att_type, att_date, att_validity):
        tz = pytz.timezone('Asia/Kolkata')  
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
        
    async def expire_attempts(self):
        tz = pytz.timezone('Asia/Kolkata')
        now = datetime.now(tz)
        expired_attempts = await self.att.find({'att_expiry': {'$lte': now}, 'att_active': True}).to_list(None)
        
        for attempt in expired_attempts:
            await self.att.update_one({'_id': attempt['_id']}, {'$set': {'att_active': False}})
            
    async def get_all_attempts(self):
        return self.att.find({})
        
        
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
        
        
db = Database(DATABASE_URI, DATABASE_NAME)
