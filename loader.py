import os
from dotenv import load_dotenv


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
load_dotenv(os.path.join(BASE_DIR, ".env"))

BOT_TOKEN = (os.getenv("BOT_TOKEN") or "").strip()
_admin_id_raw = (os.getenv("ADMIN_ID") or "0").strip() or "0"
try:
    ADMIN_ID = int(_admin_id_raw)
except ValueError as err:
    raise RuntimeError("ADMIN_ID raqam bo'lishi kerak.") from err

CHECK_SUB = (os.getenv("CHECK_SUB") or "false").lower() == "true"
DB_STORAGE = (os.getenv("DB_STORAGE") or os.path.join(BASE_DIR, "database.sqlite")).strip()

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN kiritilmagan.")
if ADMIN_ID <= 0:
    raise RuntimeError("ADMIN_ID notogri yoki kiritilmagan.")
