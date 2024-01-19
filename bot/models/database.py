"""Bot database."""
import os
from typing import Dict, Optional
from motor.motor_asyncio import AsyncIOMotorClient as Client

class Database:
    def __init__(self) -> None:
        self.client = Client(os.environ.get("MONGO_URL"))
        self.db = self.client["FeedbackBot"]

    async def get_database_stats(self):
        stats = await self.db.command("dbStats")
        return stats

    async def get_user_by_id(self, id: Optional[int]) -> bool:
        users = await self.db["users"].find_one(
            {"user_id": id}
        )
        if not users:
            return False
        return True

    async def get_all_users(self) -> list:
        list_users = []
        async for user in self.db["users"].find({"user_id": {"$gt": 0}}):
            list_users.append(user)
        return list_users

    async def register_user_by_dict(self, info: Dict) -> Dict:
        id = info["id"]

        if await self.get_user_by_id(id):
            return 
        return await self.db["users"].insert_one({"user_id": id})

    async def user_is_banned(self, user_id: int) -> bool:
        return bool(await self.db["ban"].find_one({"user_id": user_id}))

    async def ban_user(self, user_id: int):
        return await self.db["ban"].insert_one({"user_id": user_id})

    async def unban_user(self, user_id: int):
        is_banned = await self.user_is_banned(user_id)
        if not is_banned:
            return
        return await self.db["ban"].delete_one({"user_id": user_id})

    async def get_banned_users(self) -> list:
        results = []
        async for user in self.db["ban"].find({"user_id": {"$gt": 0}}):
            results.append(user["user_id"])
        return results
