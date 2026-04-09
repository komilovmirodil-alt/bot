from typing import Optional

from aiogram import Bot
from aiogram.dispatcher.middlewares.base import BaseMiddleware
from aiogram.types import CallbackQuery, Message
from aiogram.utils.keyboard import InlineKeyboardBuilder

from storage import Database


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
