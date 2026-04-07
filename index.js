const { bot, setupDatabase } = require('./bot');

function validateEnv() {
  const token = process.env.BOT_TOKEN || '';
  const adminId = process.env.ADMIN_ID || '';

  if (!token || token.includes('PASTE_YOUR_BOT_TOKEN_HERE')) {
    throw new Error('BOT_TOKEN .env faylida toliq kiritilmagan.');
  }

  if (!adminId || adminId.includes('PASTE_YOUR_TELEGRAM_ID_HERE')) {
    throw new Error('ADMIN_ID .env faylida toliq kiritilmagan.');
  }
}

async function start() {
  try {
    validateEnv();
    await setupDatabase();
    await bot.launch();
    console.log('Bot is running...');
  } catch (err) {
    console.error('Startup error:', err);
    process.exit(1);
  }
}

start();

process.once('SIGINT', () => bot.stop('SIGINT'));
process.once('SIGTERM', () => bot.stop('SIGTERM'));
