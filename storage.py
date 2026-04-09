import os
from typing import Optional

import aiosqlite


class Database:
    def __init__(self, db_path: str) -> None:
        self.db_path = db_path

    async def init(self) -> None:
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True) if os.path.dirname(self.db_path) else None
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS media (
                    code TEXT PRIMARY KEY,
                    title TEXT,
                    photo_id TEXT
                )
                """
            )
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS episodes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    code TEXT NOT NULL,
                    ep_number INTEGER NOT NULL,
                    file_id TEXT NOT NULL
                )
                """
            )
            await db.execute("CREATE INDEX IF NOT EXISTS idx_episodes_code ON episodes(code)")
            await db.execute("CREATE UNIQUE INDEX IF NOT EXISTS uq_episodes_code_ep ON episodes(code, ep_number)")
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS users (
                    telegram_id TEXT PRIMARY KEY,
                    username TEXT
                )
                """
            )
            await db.execute(
                """
                CREATE TABLE IF NOT EXISTS channels (
                    channel_id TEXT PRIMARY KEY,
                    link TEXT
                )
                """
            )
            await db.commit()

    async def add_user(self, telegram_id: int, username: Optional[str]) -> None:
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT OR IGNORE INTO users (telegram_id, username) VALUES (?, ?)",
                (str(telegram_id), username or "unknown"),
            )
            await db.commit()

    async def upsert_media(self, code: str, title: Optional[str] = None, photo_id: Optional[str] = None) -> None:
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute(
                "INSERT OR IGNORE INTO media (code, title, photo_id) VALUES (?, ?, ?)",
                (code, title, photo_id),
            )

            if title is not None:
                await db.execute("UPDATE media SET title = ? WHERE code = ?", (title, code))
            if photo_id is not None:
                await db.execute("UPDATE media SET photo_id = ? WHERE code = ?", (photo_id, code))

            await db.commit()

    async def add_episode(self, code: str, ep_number: int, file_id: str) -> None:
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("DELETE FROM episodes WHERE code = ? AND ep_number = ?", (code, ep_number))
            await db.execute(
                "INSERT INTO episodes (code, ep_number, file_id) VALUES (?, ?, ?)",
                (code, ep_number, file_id),
            )
            await db.commit()

    async def add_channel(self, channel_id: str, link: str) -> bool:
        try:
            async with aiosqlite.connect(self.db_path) as db:
                await db.execute(
                    "INSERT INTO channels (channel_id, link) VALUES (?, ?)",
                    (channel_id, link),
                )
                await db.commit()
            return True
        except Exception:
            return False

    async def delete_code(self, code: str) -> None:
        async with aiosqlite.connect(self.db_path) as db:
            await db.execute("DELETE FROM episodes WHERE code = ?", (code,))
            await db.execute("DELETE FROM media WHERE code = ?", (code,))
            await db.commit()

    async def get_media(self, code: str) -> Optional[dict]:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("SELECT code, title, photo_id FROM media WHERE code = ?", (code,))
            row = await cursor.fetchone()
            return dict(row) if row else None

    async def get_episodes(self, code: str) -> list[dict]:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT id, code, ep_number, file_id FROM episodes WHERE code = ? ORDER BY ep_number ASC",
                (code,),
            )
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    async def get_episode_by_id(self, episode_id: int) -> Optional[dict]:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute(
                "SELECT id, code, ep_number, file_id FROM episodes WHERE id = ?",
                (episode_id,),
            )
            row = await cursor.fetchone()
            return dict(row) if row else None

    async def get_channels(self) -> list[dict]:
        async with aiosqlite.connect(self.db_path) as db:
            db.row_factory = aiosqlite.Row
            cursor = await db.execute("SELECT channel_id, link FROM channels")
            rows = await cursor.fetchall()
            return [dict(row) for row in rows]

    async def get_stats(self) -> tuple[int, int, int, int]:
        async with aiosqlite.connect(self.db_path) as db:
            user_count = (await (await db.execute("SELECT COUNT(*) FROM users")).fetchone())[0]
            media_count = (await (await db.execute("SELECT COUNT(*) FROM media")).fetchone())[0]
            episode_count = (await (await db.execute("SELECT COUNT(*) FROM episodes")).fetchone())[0]
            channel_count = (await (await db.execute("SELECT COUNT(*) FROM channels")).fetchone())[0]
            return user_count, media_count, episode_count, channel_count
