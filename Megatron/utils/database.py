import datetime
import motor.motor_asyncio


class Database:
    def __init__(self, uri, database_name):
        self._client = motor.motor_asyncio.AsyncIOMotorClient(uri)
        self.db = self._client[database_name]
        self.col = self.db.users
        self.settings = self.db.settings

    def new_user(self, id):
        return dict(
            id=id,
            join_date=datetime.date.today().isoformat()
        )

    async def add_user(self, id):
        user = self.new_user(id)
        await self.col.insert_one(user)

    async def is_user_exist(self, id):
        user = await self.col.find_one({'id': int(id)})
        return True if user else False

    async def total_users_count(self):
        count = await self.col.count_documents({})
        return count

    async def get_all_users(self):
        all_users = self.col.find({})
        return all_users

    async def delete_user(self, user_id):
        await self.col.delete_many({'id': int(user_id)})

    # Force Subscribe Settings
    async def get_fsub_settings(self):
        """Get force subscribe settings"""
        settings = await self.settings.find_one({'_id': 'fsub'})
        if not settings:
            return {'enabled': False, 'channel': None}
        return settings

    async def set_fsub(self, enabled: bool, channel: int = None):
        """Enable or disable force subscribe"""
        await self.settings.update_one(
            {'_id': 'fsub'},
            {'$set': {'enabled': enabled, 'channel': channel}},
            upsert=True
        )

    async def get_fsub_channel(self):
        """Get force subscribe channel ID"""
        settings = await self.get_fsub_settings()
        return settings.get('channel') if settings.get('enabled') else None
