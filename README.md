# AniNexus_bot (Telegraf + SQLite)

Telegram kino/serial boti: kod orqali video yoki serial qismlarini topib beradi.

## Imkoniyatlar
- Bitta video qo'shish (`/add`) va kod orqali olish
- Serial smart mode: bir kod ostida ko'p qism, inline tugmalar bilan
- Poster biriktirish (`/setposter`)
- Majburiy obuna (`CHECK_SUB=true` va `/addchannel`)
- User tracking va statistika (`/stats`)
- Kod bo'yicha o'chirish (`/delete`)
- Admin-only boshqaruv (`ADMIN_ID`)

## O'rnatish
1. Paketlarni o'rnating:
```bash
npm install
```
2. `.env` faylini to'ldiring:
```env
BOT_TOKEN=YOUR_BOT_TOKEN
ADMIN_ID=YOUR_TELEGRAM_ID
CHECK_SUB=true
```
3. Botni ishga tushiring:
```bash
npm start
```

## Python Versiya (Yangi)
Loyiha Python varianti ham qo'shildi: `bot_python.py`

1. Virtual environment yarating (ixtiyoriy, tavsiya):
```bash
python -m venv .venv
```
2. Paketlarni o'rnating:
```bash
pip install -r requirements.txt
```
3. Botni ishga tushiring:
```bash
python bot_python.py
```

## Railway (Python) Deploy
Python variantni Railway'da ishlatish uchun loyiha ichida `Procfile` qo'shilgan:
```text
worker: python bot_python.py
```

Railway Python startni majburan ishlatishi uchun qo'shimcha configlar ham bor:
- `railway.json`
- `nixpacks.toml`

Qadamlar:
1. Kodni GitHub'ga push qiling.
2. Railway -> `New Project` -> `Deploy from GitHub`.
3. `Variables` ga kiriting:
```env
BOT_TOKEN=YOUR_BOT_TOKEN
ADMIN_ID=YOUR_TELEGRAM_ID
CHECK_SUB=true
DB_STORAGE=database.sqlite
```
4. Deploy tugagach `Logs`da `Bot is running (Python)...` ni tekshiring.

Eslatma:
- Railway'da SQLite ba'zi holatda ephemeral bo'lishi mumkin.
- Uzoq muddat production uchun Postgres tavsiya qilinadi.

## Tokenni Keyin Yangilash
1. `@BotFather` -> `/revoke` (eski tokenni bekor qiling)
2. `@BotFather` -> `/token` (yangi token oling)
3. Railway `Variables` ichida `BOT_TOKEN` ni yangilang
4. `Redeploy` qiling

## Admin buyruqlari
- `/setposter <code> <title>`: rasmga reply qilib yuboriladi
- `/add <code> <ep_number>`: videoga reply qilib yuboriladi
- `/addchannel <channel_id> <link>`
- `/delete <code>`
- `/stats`

## Foydalanish
Foydalanuvchi botga kod yuboradi. Bot:
- bitta video bo'lsa to'g'ridan-to'g'ri yuboradi
- bir nechta qism bo'lsa tugmalar bilan tanlashni chiqaradi

## Eslatma
- Bot majburiy obuna tekshiruvida ishlashi uchun bot homiy kanallarda admin bo'lishi kerak.
- `channel_id` odatda `-100...` formatida bo'ladi.

## 24/7 Serverga Ulash (Ubuntu VPS)
Quyidagi qadamlar bilan bot serverda doimiy ishlaydi.

1. Serverga ulaning:
```bash
ssh user@SERVER_IP
```

2. Node.js 20 va git o'rnating:
```bash
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt update
sudo apt install -y nodejs git
```

3. Loyihani serverga yuklang:
```bash
git clone <REPO_URL> botlarim
cd botlarim
npm install
```

4. `.env` yarating:
```bash
cat > .env << 'EOF'
BOT_TOKEN=YOUR_BOT_TOKEN
ADMIN_ID=YOUR_TELEGRAM_ID
CHECK_SUB=true
EOF
```

5. PM2 o'rnating va botni ishga tushiring:
```bash
sudo npm install -g pm2
npm run start:pm2
pm2 save
```

6. Server qayta yoqilganda ham avtomatik turishi uchun:
```bash
pm2 startup systemd
```
`pm2 startup systemd` chiqargan oxirgi `sudo ...` buyruqni ham aynan ishga tushiring, keyin yana:
```bash
pm2 save
```

7. Monitoring:
```bash
pm2 status
pm2 logs aninexus-bot
```

## Tezkor PM2 Buyruqlari
- Ishga tushirish: `npm run start:pm2`
- Qayta ishga tushirish: `npm run restart:pm2`
- To'xtatish: `npm run stop:pm2`
- Loglar: `npm run logs:pm2`

## Render'ga Deploy Qilish (24/7)
Ha, bo'ladi. Telegram bot uchun Render'da `Web Service` emas, `Background Worker` ishlatiladi.

1. Kodni GitHub'ga push qiling.
2. Render'da `New +` -> `Blueprint` tanlang.
3. Reponi ulang, Render `render.yaml` ni o'qib worker yaratadi.
4. Environment qiymatlarni kiriting:
```env
BOT_TOKEN=YOUR_BOT_TOKEN
ADMIN_ID=YOUR_TELEGRAM_ID
CHECK_SUB=true
DB_STORAGE=/var/data/database.sqlite
```
5. Deploy tugagach `Logs` bo'limida `Bot is running...` yozuvini tekshiring.

Muhim:
- SQLite saqlanib qolishi uchun `Persistent Disk` kerak. Shu sabab `render.yaml` ichida disk mount (`/var/data`) allaqachon berilgan.
- Agar Free planda disk bo'lmasa, SQLite o'rniga Postgres ishlatish tavsiya qilinadi.

## Vercel'ga Ulanish (Webhook Mode)
Vercel serverless bo'lgani uchun `bot.launch()` (polling) emas, webhook ishlatiladi.

1. Loyihani Vercel'ga import qiling.
2. Environment Variables qo'shing:
```env
BOT_TOKEN=YOUR_BOT_TOKEN
ADMIN_ID=YOUR_TELEGRAM_ID
CHECK_SUB=true
WEBHOOK_URL=https://your-project.vercel.app
WEBHOOK_SECRET=optional_random_secret
DB_STORAGE=/tmp/database.sqlite
```
3. Deploy bo'lgach browserda quyini bir marta oching:
```text
https://your-project.vercel.app/api/set-webhook
```
4. JSON javobda `ok: true` bo'lsa webhook o'rnatilgan.

Muhim cheklov:
- Vercel fayl tizimi doimiy emas, `SQLite` ma'lumotlari yo'qolishi mumkin.
- Production uchun `Postgres` ishlatish tavsiya qilinadi.
