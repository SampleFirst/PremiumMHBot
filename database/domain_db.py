# database.domain_db.py
import pytz
import motor.motor_asyncio
from datetime import datetime
from info import DATABASE_NAME, DATABASE_URI

class Database:
    
    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.dm = self._client[database_name]
        self.dm = self.dm.domain

    async def add_domain(self, site, domain):
        tz = pytz.timezone('Asia/Kolkata')
        current_time = datetime.now(tz)
        domain_data = {
            'site': site,
            'domain': domain,
            'timestamp': current_time
        }
        await self.dm.insert_one(domain_data)

    async def get_latest_domain(self, site):
        latest_domain = await self.dm.find_one({'site': site}, sort=[('timestamp', -1)])
        return latest_domain['domain'] if latest_domain else None

    async def get_all_domains(self):
        all_domains = []
        async for domain_data in self.dm.find({}, {'_id': 0}):
            all_domains.append(domain_data)
        return all_domains
    
    async def delete_all_domains(self, site):
        await self.dm.delete_many({'site': site})

dm = Database(DATABASE_URI, DATABASE_NAME)
