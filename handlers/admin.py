from aiogram import Router
from aiogram.filters import Command, CommandObject
from aiogram.types import Message

from keyboards.episodes import episodes_keyboard
from loader import ADMIN_ID
from storage import Database


router = Router()


def is_admin(message: Message) -> bool:
    return bool(message.from_user and message.from_user.id == ADMIN_ID)


def bind_database(db: Database) -> None:
    router.db = db


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

    await router.db.upsert_media(code=code, title=title, photo_id=photo_id)
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

    await router.db.upsert_media(code=code, title=reply.caption)
    await router.db.add_episode(code=code, ep_number=ep_number, file_id=reply.video.file_id)
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

    media = await router.db.get_media(code)
    if not media or not media.get("photo_id"):
        await message.answer(
            "Bu kod uchun avval poster qoying. Rasmga reply qilib: /setposter <code> <title>"
        )
        return

    await router.db.add_episode(code=code, ep_number=ep_number, file_id=reply.video.file_id)
    await message.answer(f"Serial qismi saqlandi. Kod: {code}, qism: {ep_number}")


@router.message(Command("addchannel"))
async def addchannel_handler(message: Message, command: CommandObject) -> None:
    if not is_admin(message):
        return

    parts = (command.args or "").strip().split()
    if len(parts) < 2:
        await message.answer("Foydalanish: /addchannel <channel_id> <link>")
        return

    ok = await router.db.add_channel(channel_id=parts[0], link=parts[1])
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

    await router.db.delete_code(code)
    await message.answer("Kod boyicha malumotlar ochirildi.")


@router.message(Command("stats"))
async def stats_handler(message: Message) -> None:
    if not is_admin(message):
        return

    users, media_count, episodes, channels = await router.db.get_stats()
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
