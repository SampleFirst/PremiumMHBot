# database.domain_dm.py
import pytz
import motor.motor_asyncio
from datetime import datetime
from info import DATABASE_NAME, DATABASE_URI

class Database:
    
    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.dm = self._client[database_name]
        self.dm = self.dm.domain

    async def add_domain(self, domain):
        tz = pytz.timezone('Asia/Kolkata')
        current_time = datetime.now(tz)
        domain_data = {
            'domain': domain,
            'timestamp': current_time
        }
        await self.dm.insert_one(domain_data)

    async def get_latest_domain(self):
        latest_domain = await self.dm.find_one({}, sort=[('timestamp', -1)])
        return latest_domain['domain'] if latest_domain else None

    async def get_all_domains(self):
        all_domains = []
        async for domain_data in self.dm.find({}, {'_id': 0}):
            all_domains.append(domain_data)
        return all_domains

dm = Database(DATABASE_URI, DATABASE_NAME)
