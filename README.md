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

## PythonAnywhere Deploy
1. Bash console oching va repodan kodni yuklang:
```bash
cd ~
git clone https://github.com/komilovmirodil-alt/bot.git botlarim
cd botlarim
```

2. Virtualenv yarating va dependency o'rnating:
```bash
python3.10 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

3. `.env` yarating:
```env
BOT_TOKEN=YOUR_BOT_TOKEN
ADMIN_ID=YOUR_TELEGRAM_ID
CHECK_SUB=true
DB_STORAGE=/home/YOUR_USERNAME/botlarim/database.sqlite
```

4. Start scriptga ruxsat bering:
```bash
chmod +x ~/botlarim/start_pythonanywhere.sh
```

5. PythonAnywhere -> `Tasks` -> `Always-on tasks` ga kiring va buyruq qo'shing:
```bash
bash /home/YOUR_USERNAME/botlarim/start_pythonanywhere.sh
```

6. `Logs`dan tekshiring:
- `Database connected and synced.`
- `Bot is running (Python)...`

## Token Yangilash
1. `@BotFather` -> `/revoke` (eski tokenni bekor qiling)
2. `@BotFather` -> `/token` (yangi token oling)
3. PythonAnywhere `.env` ichida `BOT_TOKEN`ni yangilang
4. Always-on taskni qayta ishga tushiring
