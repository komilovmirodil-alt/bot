import asyncio

from aiogram import Bot, Dispatcher
from aiogram.exceptions import TelegramNetworkError

from loader import ADMIN_ID, BOT_TOKEN, CHECK_SUB, DB_STORAGE
from middlewares import UserAndSubscriptionMiddleware
from storage import Database
from handlers import admin, user


db = Database(DB_STORAGE)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

dp.update.middleware(UserAndSubscriptionMiddleware(db=db, admin_id=ADMIN_ID, check_sub=CHECK_SUB))

admin.bind_database(db)
user.bind_database(db)

dp.include_router(admin.router)
dp.include_router(user.router)


async def main() -> None:
    await db.init()
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
