# AniNexus_bot (Python)

Telegram kino/serial boti, Render Worker uchun moslangan.

## Imkoniyatlar
- Bitta video qo'shish: `/add <code> <ep_number>`
- Serial smart mode: bitta kod ostida ko'p qism, inline tugmalar bilan
- Serial-safe qo'shish: `/addserial <code> <ep_number>` (avval poster qo'yiladi)
- Poster biriktirish: `/setposter <code> <title>`
- Majburiy obuna: `/addchannel <channel_id> <link>` va `CHECK_SUB=true`
- User tracking va statistika: `/stats`
- Kod bo'yicha o'chirish: `/delete <code>`

## Render Worker Deploy
1. Kodni GitHub'ga push qiling.
2. Render'da `New +` -> `Blueprint` tanlang.
3. Reponi ulang, `render.yaml` bo'yicha worker avtomatik yaratiladi.
4. Environment o'zgaruvchilar:
```env
PYTHON_VERSION=3.11.9
PIP_ONLY_BINARY=:all:
PIP_NO_CACHE_DIR=1
PIP_CACHE_DIR=/tmp/pip-cache
PIP_DISABLE_PIP_VERSION_CHECK=1
BOT_TOKEN=YOUR_BOT_TOKEN
ADMIN_ID=YOUR_TELEGRAM_ID
CHECK_SUB=true
DB_STORAGE=/var/data/database.sqlite
```
5. Deploydan keyin logda quyini tekshiring:
- `Database connected and synced.`
- `Bot is running (Python)...`

Muammo chiqsa (`pyproject.toml`, `maturin`, `cargo`, `Read-only file system`):
- Render service Python versiyasi `3.11.9` ekanini tekshiring.
- `Clear build cache` qilib qayta deploy qiling.

## Token Yangilash
1. `@BotFather` -> `/revoke`
2. `@BotFather` -> `/token`
3. Render `Environment` ichida `BOT_TOKEN` ni yangilang
4. `Manual Deploy` -> `Deploy latest commit`

## Serial Qo'shish Tartibi
1. Avval serial posterini qo'ying: `/setposter <code> <title>` (rasmga reply qilib)
2. Har bir qismni videoga reply qilib qo'shing: `/addserial <code> <ep_number>`
3. User kod yuborganda poster chiqadi va barcha qism tugmalari ko'rinadi.
