import asyncio
import os
from typing import Optional

import aiosqlite
from aiogram import Bot, Dispatcher, F, Router
from aiogram.dispatcher.middlewares.base import BaseMiddleware
from aiogram.exceptions import TelegramNetworkError
from aiogram.filters import Command, CommandObject
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from dotenv import load_dotenv


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


class UserAndSubscriptionMiddleware(BaseMiddleware):
    def __init__(self, db: Database, admin_id: int, check_sub: bool) -> None:
        self.db = db
        self.admin_id = admin_id
        self.check_sub = check_sub

    async def __call__(self, handler, event, data):
        user = data.get("event_from_user")
        bot: Bot = data["bot"]

        if user:
            try:
                await self.db.add_user(user.id, user.username)
            except Exception:
                pass

        if not self.check_sub or not user or user.id == self.admin_id:
            return await handler(event, data)

        channels = await self.db.get_channels()
        if not channels:
            return await handler(event, data)

        not_subscribed = []
        for channel in channels:
            try:
                member = await bot.get_chat_member(chat_id=channel["channel_id"], user_id=user.id)
                if member.status in ("left", "kicked"):
                    not_subscribed.append(channel)
            except Exception:
                not_subscribed.append(channel)

        if not not_subscribed:
            return await handler(event, data)

        kb = InlineKeyboardBuilder()
        for idx, ch in enumerate(not_subscribed, start=1):
            kb.button(text=f"Kanal {idx}", url=ch["link"])
        kb.button(text="Obunani tekshirish", callback_data="check_sub")
        kb.adjust(1)

        if isinstance(event, CallbackQuery):
            await event.answer("Siz kanallarga obuna bolmagansiz.", show_alert=True)
            return

        if isinstance(event, Message):
            await event.answer(
                "Davom etish uchun kanallarga obuna boling.",
                reply_markup=kb.as_markup(),
            )
            return

        return


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))
BOT_TOKEN = (os.getenv("BOT_TOKEN") or "").strip()
ADMIN_ID = int((os.getenv("ADMIN_ID") or "0").strip() or "0")
CHECK_SUB = (os.getenv("CHECK_SUB") or "false").lower() == "true"
DEFAULT_DB = os.path.join(BASE_DIR, "database.sqlite")
DB_STORAGE = (os.getenv("DB_STORAGE") or DEFAULT_DB).strip()

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN kiritilmagan.")
if ADMIN_ID <= 0:
    raise RuntimeError("ADMIN_ID notogri yoki kiritilmagan.")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
router = Router()
db = Database(DB_STORAGE)

dp.update.middleware(UserAndSubscriptionMiddleware(db=db, admin_id=ADMIN_ID, check_sub=CHECK_SUB))


def is_admin(message: Message) -> bool:
    return bool(message.from_user and message.from_user.id == ADMIN_ID)


def episodes_keyboard(episodes: list[dict]) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for ep in episodes:
        kb.button(text=f"{ep['ep_number']}-qism", callback_data=f"ep:{ep['id']}")
    kb.adjust(4)
    return kb.as_markup()


@router.callback_query(F.data == "check_sub")
async def check_sub_callback(callback: CallbackQuery) -> None:
    await callback.answer()
    try:
        await callback.message.delete()
    except Exception:
        pass
    await callback.message.answer("Endi kino yoki serial kodini yuboring.")


@router.message(Command("start"))
async def start_handler(message: Message) -> None:
    await message.answer("Assalomu alaykum. Kino yoki serial kodini yuboring.")


@router.message(Command("help"))
async def help_handler(message: Message) -> None:
    await message.answer(
        "\n".join(
            [
                "Buyruqlar:",
                "/start - Botni boshlash",
                "/help - Yordam",
                "",
                "Admin buyruqlari:",
                "/setposter <code> <title> (rasmga reply qilib)",
                "/add <code> <ep> (videoga reply qilib)",
                "/addserial <code> <ep> (videoga reply, poster avval qo'yilgan bo'lishi kerak)",
                "/addchannel <channel_id> <link>",
                "/delete <code>",
                "/stats",
            ]
        )
    )


@router.message(Command("setposter"))
async def setposter_handler(message: Message, command: CommandObject) -> None:
    if not is_admin(message):
        return

    reply = message.reply_to_message
    if not reply or not reply.photo:
        await message.answer("Avval rasmga reply qilib yuboring.")
        return

    parts = (command.args or "").strip().split()
    if not parts:
        await message.answer("Foydalanish: /setposter <code> <title>")
        return

    code = parts[0]
    title = " ".join(parts[1:]) if len(parts) > 1 else None
    photo_id = reply.photo[-1].file_id

    await db.upsert_media(code=code, title=title, photo_id=photo_id)
    await message.answer("Poster saqlandi.")


@router.message(Command("add"))
async def add_handler(message: Message, command: CommandObject) -> None:
    if not is_admin(message):
        return

    reply = message.reply_to_message
    if not reply or not reply.video:
        await message.answer("Avval videoga reply qilib yuboring.")
        return

    parts = (command.args or "").strip().split()
    if not parts:
        await message.answer("Foydalanish: /add <code> <ep_number>")
        return

    code = parts[0]
    ep_number = 1
    if len(parts) > 1:
        try:
            ep_number = int(parts[1])
        except ValueError:
            ep_number = 1

    await db.upsert_media(code=code, title=reply.caption)
    await db.add_episode(code=code, ep_number=ep_number, file_id=reply.video.file_id)
    await message.answer(f"Video saqlandi. Kod: {code}, qism: {ep_number}")


@router.message(Command("addserial"))
async def addserial_handler(message: Message, command: CommandObject) -> None:
    if not is_admin(message):
        return

    reply = message.reply_to_message
    if not reply or not reply.video:
        await message.answer("Avval videoga reply qilib yuboring.")
        return

    parts = (command.args or "").strip().split()
    if not parts:
        await message.answer("Foydalanish: /addserial <code> <ep_number>")
        return

    code = parts[0]
    ep_number = 1
    if len(parts) > 1:
        try:
            ep_number = int(parts[1])
        except ValueError:
            ep_number = 1

    media = await db.get_media(code)
    if not media or not media.get("photo_id"):
        await message.answer(
            "Bu kod uchun avval poster qoying. Rasmga reply qilib: /setposter <code> <title>"
        )
        return

    await db.add_episode(code=code, ep_number=ep_number, file_id=reply.video.file_id)
    await message.answer(f"Serial qismi saqlandi. Kod: {code}, qism: {ep_number}")


@router.message(Command("addchannel"))
async def addchannel_handler(message: Message, command: CommandObject) -> None:
    if not is_admin(message):
        return

    parts = (command.args or "").strip().split()
    if len(parts) < 2:
        await message.answer("Foydalanish: /addchannel <channel_id> <link>")
        return

    ok = await db.add_channel(channel_id=parts[0], link=parts[1])
    if ok:
        await message.answer("Kanal qoshildi.")
    else:
        await message.answer("Kanalni qoshishda xatolik. Ehtimol oldin qoshilgan.")


@router.message(Command("delete"))
async def delete_handler(message: Message, command: CommandObject) -> None:
    if not is_admin(message):
        return

    code = (command.args or "").strip()
    if not code:
        await message.answer("Foydalanish: /delete <code>")
        return

    await db.delete_code(code)
    await message.answer("Kod boyicha malumotlar ochirildi.")


@router.message(Command("stats"))
async def stats_handler(message: Message) -> None:
    if not is_admin(message):
        return

    users, media_count, episodes, channels = await db.get_stats()
    await message.answer(
        "\n".join(
            [
                "Statistika:",
                f"Foydalanuvchilar: {users}",
                f"Media kodlar: {media_count}",
                f"Video qism-lar: {episodes}",
                f"Majburiy obuna kanallari: {channels}",
            ]
        )
    )


@router.callback_query(F.data.startswith("ep:"))
async def episode_callback(callback: CallbackQuery) -> None:
    raw_id = callback.data.split(":", maxsplit=1)[1]
    try:
        episode_id = int(raw_id)
    except ValueError:
        await callback.answer("Qism topilmadi.", show_alert=True)
        return

    episode = await db.get_episode_by_id(episode_id)
    if not episode:
        await callback.answer("Qism topilmadi.", show_alert=True)
        return

    await callback.message.answer_video(episode["file_id"])
    await callback.answer()


@router.message(F.text)
async def text_search_handler(message: Message) -> None:
    text = (message.text or "").strip()
    if not text or text.startswith("/"):
        return

    media = await db.get_media(text)
    episodes = await db.get_episodes(text)

    if not media and not episodes:
        await message.answer("Bunday kod topilmadi.")
        return

    if media and not episodes:
        title = media.get("title")
        body = f"*{title}*\n\nQismlar hali qoshilmagan." if title else "Qismlar hali qoshilmagan."
        if media.get("photo_id"):
            await message.answer_photo(media["photo_id"], caption=body, parse_mode="Markdown")
        else:
            await message.answer(body, parse_mode="Markdown")
        return

    if len(episodes) == 1 and not (media and media.get("photo_id")):
        caption = media.get("title") if media else None
        await message.answer_video(episodes[0]["file_id"], caption=caption)
        return

    title = media.get("title") if media else None
    body = f"*{title}*\n\nQismni tanlang:" if title else "Qismni tanlang:"
    markup = episodes_keyboard(episodes)

    if media and media.get("photo_id"):
        await message.answer_photo(media["photo_id"], caption=body, parse_mode="Markdown", reply_markup=markup)
    else:
        await message.answer(body, parse_mode="Markdown", reply_markup=markup)


async def main() -> None:
    await db.init()
    dp.include_router(router)
    print("Database connected and synced.")
    print("Bot is running (Python)...")

    retry_delay = 5
    while True:
        try:
            await dp.start_polling(bot)
            break
        except TelegramNetworkError as err:
            print(f"Network error: {err}. Reconnecting in {retry_delay}s...")
            await asyncio.sleep(retry_delay)
            retry_delay = min(retry_delay * 2, 60)
        except Exception as err:
            print(f"Unexpected error: {err}. Reconnecting in {retry_delay}s...")
            await asyncio.sleep(retry_delay)
            retry_delay = min(retry_delay * 2, 60)


if __name__ == "__main__":
    asyncio.run(main())
