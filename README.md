# AniNexus_bot (Python)

Telegram kino/serial boti. Bu repository hozir faqat Python versiyani saqlaydi.

## Imkoniyatlar
- Bitta video qo'shish: `/add <code> <ep_number>`
- Serial smart mode: bitta kod ostida ko'p qism, inline tugmalar bilan
- Serial-safe qo'shish: `/addserial <code> <ep_number>` (avval poster qo'yiladi)
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

## Render Worker Deploy
1. Kodni GitHub'ga push qiling.
2. Render'da `New +` -> `Blueprint` tanlang va repo ulang.
3. `render.yaml` bo'yicha worker avtomatik yaratiladi.
4. Render `Environment`da qiymatlarni kiriting:
```env
BOT_TOKEN=YOUR_BOT_TOKEN
ADMIN_ID=YOUR_TELEGRAM_ID
CHECK_SUB=true
DB_STORAGE=/var/data/database.sqlite
```
5. Deploydan keyin logda tekshiring:
- `Database connected and synced.`
- `Bot is running (Python)...`

## Token Yangilash
1. `@BotFather` -> `/revoke` (eski tokenni bekor qiling)
2. `@BotFather` -> `/token` (yangi token oling)
3. PythonAnywhere `.env` ichida `BOT_TOKEN`ni yangilang
4. Always-on taskni qayta ishga tushiring

Render ishlatayotgan bo'lsangiz:
- Render `Environment` ichida `BOT_TOKEN`ni yangilang
- `Manual Deploy` -> `Deploy latest commit`

## Serial Qo'shish Tartibi
1. Avval serial posterini qo'ying:
`/setposter <code> <title>` (rasmga reply qilib)
2. Har bir qismni videoga reply qilib qo'shing:
`/addserial <code> <ep_number>`
3. User kod yuborganda poster chiqadi va barcha qism tugmalari ko'rinadi (masalan 12 qism bo'lsa 12 tugma).
