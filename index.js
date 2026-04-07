require('dotenv').config();

function validateEnv() {
  const token = (process.env.BOT_TOKEN || '').trim();
  const adminId = (process.env.ADMIN_ID || '').trim();

  if (!token || token.includes('PASTE_YOUR_BOT_TOKEN_HERE')) {
    throw new Error('BOT_TOKEN kiritilmagan yoki notogri.');
  }

  if (!adminId || adminId.includes('PASTE_YOUR_TELEGRAM_ID_HERE')) {
    throw new Error('ADMIN_ID kiritilmagan yoki notogri.');
  }
}

function delay(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function launchWithRetry(bot, retries = 5) {
  for (let attempt = 1; attempt <= retries; attempt += 1) {
    try {
      await bot.launch();
      return;
    } catch (err) {
      const message = (err && err.message) || '';
      const isConflict = message.includes('409') || message.toLowerCase().includes('conflict');

      if (attempt === retries || !isConflict) {
        throw err;
      }

      console.error(`Launch conflict detected. Retry ${attempt}/${retries} in 5s...`);
      await delay(5000);
    }
  }
}

async function start() {
  try {
    validateEnv();

    const { bot, setupDatabase } = require('./bot');
    await setupDatabase();
    await launchWithRetry(bot);
    console.log('Bot is running...');

    process.once('SIGINT', () => bot.stop('SIGINT'));
    process.once('SIGTERM', () => bot.stop('SIGTERM'));
  } catch (err) {
    console.error('Startup error:', err);
    process.exit(1);
  }
}

start();

process.on('unhandledRejection', (reason) => {
  console.error('Unhandled rejection:', reason);
});

process.on('uncaughtException', (error) => {
  console.error('Uncaught exception:', error);
});
