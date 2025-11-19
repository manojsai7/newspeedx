import asyncio
import datetime
import logging
from typing import Any, AsyncIterator, Dict, List, Optional, Tuple

import motor.motor_asyncio
from pymongo.errors import DuplicateKeyError, PyMongoError


UTC_NOW = datetime.datetime.utcnow


class Database:
    """Async Mongo helper with opinionated user/file state."""

    _client_cache: Dict[str, motor.motor_asyncio.AsyncIOMotorClient] = {}

    def __init__(self, uri: str, database_name: str):
        if not uri:
            raise RuntimeError(
                "DATABASE_URL is missing. Provide a MongoDB connection string to enable persistence and security features."
            )

        self._uri = uri
        self._db_name = database_name or "megatron"
        if uri not in self._client_cache:
            # Enhanced connection with pooling and timeout settings
            self._client_cache[uri] = motor.motor_asyncio.AsyncIOMotorClient(
                uri,
                maxPoolSize=50,  # Allow up to 50 connections
                minPoolSize=10,  # Maintain minimum 10 connections
                maxIdleTimeMS=45000,  # Close idle connections after 45s
                serverSelectionTimeoutMS=5000,  # 5s timeout for server selection
                connectTimeoutMS=10000,  # 10s connection timeout
                socketTimeoutMS=20000,  # 20s socket operation timeout
            )
        self._client = self._client_cache[uri]
        self.db = self._client[self._db_name]

        self.users = self.db.users
        self.files = self.db.files
        self.settings = self.db.settings
        self.shortlinks = self.db.shortlinks
        self.audit = self.db.audit

        self._indexes_ready = False
        self._index_lock = asyncio.Lock()
        
        # Performance: Cache frequently accessed data
        self._fsub_cache = None
        self._fsub_cache_time = None
        self._cache_ttl = 300  # 5 minutes cache TTL

    # ------------------------------------------------------------------
    # Index bootstrap
    # ------------------------------------------------------------------
    async def ensure_indexes(self) -> None:
        if self._indexes_ready:
            return

        async with self._index_lock:
            if self._indexes_ready:
                return

            await self._drain_user_duplicates()
            await self._ensure_user_id_index()
            await self.users.create_index([("status", 1)])
            await self.users.create_index([("last_seen_at", -1)])

            await self.files.create_index("message_id", unique=True)
            await self.files.create_index([("owner_id", 1), ("created_at", -1)])
            await self.files.create_index("expires_at", expireAfterSeconds=0)
            await self.files.create_index("token", unique=True)

            await self.shortlinks.create_index("slug", unique=True)
            await self.shortlinks.create_index("expires_at", expireAfterSeconds=0)

            # _id already has a unique index by default - no need to create one
            await self.audit.create_index([("created_at", -1)])

            self._indexes_ready = True

    # ------------------------------------------------------------------
    # User helpers
    # ------------------------------------------------------------------
    async def ensure_user(self, user: Any) -> Tuple[Dict[str, Any], bool]:
        await self.ensure_indexes()
        user_id = int(user.id)
        # Performance: Only fetch necessary fields
        existing = await self.users.find_one({"id": user_id})
        payload = {
            "id": user_id,
            "first_name": getattr(user, "first_name", "") or "Unknown",
            "last_name": getattr(user, "last_name", None),
            "username": getattr(user, "username", None),
            "language_code": getattr(user, "language_code", None),
            "status": "active",
            "joined_at": UTC_NOW(),
            "last_seen_at": UTC_NOW(),
            "stats": {
                "uploads": 0,
                "downloads": 0,
                "bytes_uploaded": 0,
                "bytes_downloaded": 0,
                "broadcast_success": 0,
                "broadcast_failures": 0,
            },
            "settings": {
                "link_ttl": None,
                "short_links": True,
                "password_required": False,
            },
            "flags": {
                "banned_at": None,
                "banned_reason": None,
                "banned_by": None,
            },
            "fsub": {
                "channel": None,
                "last_prompt_at": None,
                "state": "clear",
            },
        }
        if existing:
            try:
                await self.users.update_one(
                    {"id": user_id},
                    {
                        "$set": {
                            "first_name": payload["first_name"],
                            "last_seen_at": UTC_NOW(),
                            "username": payload["username"],
                        }
                    },
                )
                existing.update(
                    {
                        "first_name": payload["first_name"],
                        "last_seen_at": UTC_NOW(),
                        "username": payload["username"],
                    }
                )
                logging.debug(f"[DATABASE] Updated existing user {user_id}")
                return existing, False
            except Exception as e:
                logging.error(f"[DATABASE] Failed to update user {user_id}: {e}")
                raise

        try:
            payload["joined_at"] = UTC_NOW()
            payload["last_seen_at"] = payload["joined_at"]
            await self.users.insert_one(payload)
            logging.info(f"[DATABASE] Created new user {user_id} - {payload['first_name']}")
            return payload, True
        except Exception as e:
            logging.error(f"[DATABASE] Failed to create user {user_id}: {e}")
            raise

    async def mark_user_seen(self, user_id: int) -> None:
        await self.ensure_indexes()
        await self.users.update_one(
            {"id": int(user_id)},
            {"$set": {"last_seen_at": UTC_NOW()}},
        )

    async def is_user_banned(self, user_id: int) -> bool:
        await self.ensure_indexes()
        doc = await self.users.find_one({"id": int(user_id)}, {"status": 1})
        return bool(doc and doc.get("status") == "banned")

    async def set_user_status(
        self,
        user_id: int,
        status: str,
        *,
        reason: Optional[str] = None,
        actor_id: Optional[int] = None,
    ) -> None:
        await self.ensure_indexes()
        update = {
            "status": status,
            "flags.banned_reason": reason,
            "flags.banned_by": actor_id,
            "flags.banned_at": UTC_NOW() if status == "banned" else None,
        }
        await self.users.update_one({"id": int(user_id)}, {"$set": update})
        
        # Security: If banning user, mark all their files for deletion
        if status == "banned":
            try:
                # Update all files from this user to mark them as banned
                await self.files.update_many(
                    {"owner_id": int(user_id)},
                    {"$set": {"owner_banned": True, "banned_at": UTC_NOW()}}
                )
                logging.info(f"[SECURITY] Marked all files from banned user {user_id} as inaccessible")
            except Exception as e:
                logging.error(f"[SECURITY] Failed to mark banned user files: {e}")

    async def update_user_preferences(self, user_id: int, **prefs: Any) -> None:
        if not prefs:
            return
        await self.ensure_indexes()
        await self.users.update_one(
            {"id": int(user_id)},
            {"$set": {f"settings.{k}": v for k, v in prefs.items()}},
        )

    async def get_user_preferences(self, user_id: int) -> Dict[str, Any]:
        await self.ensure_indexes()
        doc = await self.users.find_one({"id": int(user_id)}, {"settings": 1})
        return doc.get("settings", {}) if doc else {}

    async def _drain_user_duplicates(self) -> None:
        while True:
            removed = await self._dedupe_users_by_id()
            if removed == 0:
                return

    async def _dedupe_users_by_id(self) -> int:
        pipeline = [
            {"$group": {"_id": "$id", "ids": {"$push": "$_id"}, "count": {"$sum": 1}}},
            {"$match": {"count": {"$gt": 1}}},
        ]
        cursor = self.users.aggregate(pipeline)
        removed_total = 0
        async for entry in cursor:
            object_ids = list(entry.get("ids", []))
            if len(object_ids) <= 1:
                continue
            _, *duplicates = object_ids
            if duplicates:
                result = await self.users.delete_many({"_id": {"$in": duplicates}})
                removed_total += result.deleted_count
        return removed_total

    async def _ensure_user_id_index(self) -> None:
        info = await self.users.index_information()
        existing = info.get("id_1")
        if existing and existing.get("unique"):
            return
        if existing:
            try:
                await self.users.drop_index("id_1")
            except PyMongoError:
                pass
        try:
            await self.users.create_index("id", unique=True)
        except (DuplicateKeyError, PyMongoError) as exc:
            if getattr(exc, "code", None) == 11000 or isinstance(exc, DuplicateKeyError):
                await self._drain_user_duplicates()
                try:
                    await self.users.drop_index("id_1")
                except PyMongoError:
                    pass
                await self.users.create_index("id", unique=True)
            else:
                raise

    async def total_users_count(self) -> int:
        await self.ensure_indexes()
        return await self.users.count_documents({})

    async def get_all_users(self) -> AsyncIterator[Dict[str, Any]]:
        await self.ensure_indexes()
        cursor = self.users.find({})
        async for doc in cursor:
            yield doc

    async def delete_user(self, user_id: int) -> None:
        await self.ensure_indexes()
        await self.users.delete_one({"id": int(user_id)})

    # ------------------------------------------------------------------
    # Force subscribe helpers
    # ------------------------------------------------------------------
    async def get_force_subscribe_settings(self) -> Dict[str, Any]:
        await self.ensure_indexes()
        
        # Use cache if available and fresh
        import time
        now = time.time()
        if self._fsub_cache and self._fsub_cache_time:
            if (now - self._fsub_cache_time) < self._cache_ttl:
                return self._fsub_cache
        
        # Fetch from database
        doc = await self.settings.find_one({"_id": "fsub"})
        if not doc:
            result = {"enabled": False, "channel": None}
        else:
            result = doc
        
        # Update cache
        self._fsub_cache = result
        self._fsub_cache_time = now
        return result

    async def set_force_subscribe(self, enabled: bool, channel: Optional[int | str]) -> None:
        await self.ensure_indexes()
        await self.settings.update_one(
            {"_id": "fsub"},
            {"$set": {"enabled": enabled, "channel": channel}},
            upsert=True,
        )
        # Invalidate cache
        self._fsub_cache = None
        self._fsub_cache_time = None

    async def get_force_subscribe_channel(self) -> Optional[int | str]:
        settings = await self.get_force_subscribe_settings()
        if settings.get("enabled"):
            return settings.get("channel")
        return None

    async def mark_user_fsub_state(self, user_id: int, state: str, *, channel: Optional[int | str] = None) -> None:
        await self.ensure_indexes()
        await self.users.update_one(
            {"id": int(user_id)},
            {
                "$set": {
                    "fsub.state": state,
                    "fsub.channel": channel,
                    "fsub.last_prompt_at": UTC_NOW(),
                }
            },
        )

    # ------------------------------------------------------------------
    # File and link helpers
    # ------------------------------------------------------------------
    async def record_file_upload(
        self,
        *,
        message_id: int,
        owner_id: int,
        file_name: str,
        file_size: int,
        mime_type: Optional[str],
        unique_id: str,
        token: str,
        expires_at: datetime.datetime,
        short_slug: Optional[str],
    ) -> None:
        await self.ensure_indexes()
        doc = {
            "message_id": int(message_id),
            "owner_id": int(owner_id),
            "file_name": file_name,
            "file_size": file_size,
            "mime_type": mime_type,
            "unique_id": unique_id,
            "token": token,
            "short_slug": short_slug,
            "access_count": 0,
            "created_at": UTC_NOW(),
            "expires_at": expires_at,
        }
        # Performance: Execute both operations concurrently
        await asyncio.gather(
            self.files.update_one({"message_id": int(message_id)}, {"$set": doc}, upsert=True),
            self.users.update_one(
                {"id": int(owner_id)},
                {
                    "$inc": {
                        "stats.uploads": 1,
                        "stats.bytes_uploaded": file_size,
                    },
                    "$set": {"last_seen_at": UTC_NOW()},
                },
            )
        )

    async def touch_file_access(self, message_id: int, *, bytes_served: int = 0) -> None:
        await self.ensure_indexes()
        update = {"$inc": {"access_count": 1}}
        if bytes_served:
            update["$inc"].update({"bytes_served": bytes_served})
        await self.files.update_one({"message_id": int(message_id)}, update)

    async def get_file_by_token(self, *, message_id: int, token: str) -> Optional[Dict[str, Any]]:
        await self.ensure_indexes()
        return await self.files.find_one({"message_id": int(message_id), "token": token})

    async def create_short_slug(
        self,
        slug: str,
        *,
        message_id: int,
        token: str,
        expires_at: datetime.datetime,
    ) -> None:
        await self.ensure_indexes()
        await self.shortlinks.update_one(
            {"slug": slug},
            {
                "$set": {
                    "message_id": int(message_id),
                    "token": token,
                    "expires_at": expires_at,
                    "created_at": UTC_NOW(),
                }
            },
            upsert=True,
        )

    async def resolve_short_slug(self, slug: str) -> Optional[Dict[str, Any]]:
        await self.ensure_indexes()
        return await self.shortlinks.find_one({"slug": slug})

    async def get_recent_files(self, owner_id: int, limit: int = 5) -> List[Dict[str, Any]]:
        await self.ensure_indexes()
        cursor = (
            self.files.find({"owner_id": int(owner_id)})
            .sort("created_at", -1)
            .limit(limit)
        )
        return [doc async for doc in cursor]

    # ------------------------------------------------------------------
    # Broadcast helpers
    # ------------------------------------------------------------------
    async def iter_active_users(self, batch_size: int = 500) -> AsyncIterator[List[int]]:
        await self.ensure_indexes()
        cursor = self.users.find({"status": {"$ne": "banned"}}, projection={"id": 1})
        batch: List[int] = []
        async for doc in cursor:
            batch.append(int(doc["id"]))
            if len(batch) >= batch_size:
                yield batch
                batch = []
        if batch:
            yield batch

    async def increment_broadcast_stats(self, user_id: int, success: bool) -> None:
        await self.ensure_indexes()
        field = "stats.broadcast_success" if success else "stats.broadcast_failures"
        await self.users.update_one({"id": int(user_id)}, {"$inc": {field: 1}})

    # ------------------------------------------------------------------
    # Analytics
    # ------------------------------------------------------------------
    async def store_audit_event(self, event: str, *, payload: Dict[str, Any]) -> None:
        await self.ensure_indexes()
        await self.audit.insert_one(
            {
                "event": event,
                "payload": payload,
                "created_at": UTC_NOW(),
            }
        )

    async def get_admin_snapshot(self) -> Dict[str, Any]:
        await self.ensure_indexes()
        total_users = await self.users.count_documents({})
        active_users = await self.users.count_documents({"status": {"$ne": "banned"}})
        banned_users = await self.users.count_documents({"status": "banned"})
        total_files = await self.files.count_documents({})
        expiring = await self.files.count_documents(
            {"expires_at": {"$lt": UTC_NOW() + datetime.timedelta(hours=6)}}
        )
        return {
            "total_users": total_users,
            "active_users": active_users,
            "banned_users": banned_users,
            "total_files": total_files,
            "expiring_soon": expiring,
        }
    
    async def get_total_users(self) -> int:
        """Get total user count"""
        await self.ensure_indexes()
        return await self.users.count_documents({})
    
    async def get_total_files(self) -> int:
        """Get total file count"""
        await self.ensure_indexes()
        return await self.files.count_documents({})
    
    async def get_banned_count(self) -> int:
        """Get banned user count"""
        await self.ensure_indexes()
        return await self.users.count_documents({"status": "banned"})
