from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def episodes_keyboard(episodes: list[dict]) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for ep in episodes:
        kb.button(text=f"{ep['ep_number']}-qism", callback_data=f"ep:{ep['id']}")
    kb.adjust(4)
    return kb.as_markup()
