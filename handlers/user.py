from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message

from keyboards.episodes import episodes_keyboard

router = Router()


def bind_database(db) -> None:
    router.db = db


@router.message(Command("start"))
async def start_handler(message: Message) -> None:
    await message.answer("Assalomu alaykum. Kino yoki serial kodini yuboring.")


@router.callback_query(F.data == "check_sub")
async def check_sub_callback(callback: CallbackQuery) -> None:
    await callback.answer()
    try:
        await callback.message.delete()
    except Exception:
        pass
    await callback.message.answer("Endi kino yoki serial kodini yuboring.")


@router.callback_query(F.data.startswith("ep:"))
async def episode_callback(callback: CallbackQuery) -> None:
    raw_id = callback.data.split(":", maxsplit=1)[1]
    try:
        episode_id = int(raw_id)
    except ValueError:
        await callback.answer("Qism topilmadi.", show_alert=True)
        return

    episode = await router.db.get_episode_by_id(episode_id)
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

    media = await router.db.get_media(text)
    episodes = await router.db.get_episodes(text)

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
