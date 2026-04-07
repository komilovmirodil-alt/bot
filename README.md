# AniNexus_bot (Python)

Telegram kino/serial boti. Bu repository hozir faqat Python versiyani saqlaydi.

## Imkoniyatlar
- Bitta video qo'shish: `/add <code> <ep_number>`
- Serial smart mode: bitta kod ostida ko'p qism, inline tugmalar bilan
- Poster biriktirish: `/setposter <code> <title>`
- Majburiy obuna: `/addchannel <channel_id> <link>` va `CHECK_SUB=true`
- User tracking va statistika: `/stats`
- Kod bo'yicha o'chirish: `/delete <code>`
- Admin-only boshqaruv: `.env` dagi `ADMIN_ID`

## Lokal Ishga Tushirish
1. Python virtual environment yarating (tavsiya):
```bash
python -m venv .venv
```

2. Paketlarni o'rnating:
```bash
pip install -r requirements.txt
```

3. `.env` ni to'ldiring:
```env
BOT_TOKEN=YOUR_BOT_TOKEN
ADMIN_ID=YOUR_TELEGRAM_ID
CHECK_SUB=true
DB_STORAGE=database.sqlite
```

4. Botni ishga tushiring:
```bash
python bot_python.py
```

## Railway Deploy
Loyiha Python worker sifatida deploy bo'lishga tayyor:
- `Procfile`
- `railway.json`
- `nixpacks.toml`

Railway `Variables`:
```env
BOT_TOKEN=YOUR_BOT_TOKEN
ADMIN_ID=YOUR_TELEGRAM_ID
CHECK_SUB=true
DB_STORAGE=database.sqlite
```

Deploydan keyin logda quyini tekshiring:
- `Database connected and synced.`
- `Bot is running (Python)...`

## Token Yangilash
1. `@BotFather` -> `/revoke` (eski tokenni bekor qiling)
2. `@BotFather` -> `/token` (yangi token oling)
3. Railway `BOT_TOKEN`ni yangilang
4. `Redeploy` qiling
