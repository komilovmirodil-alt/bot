const { bot, setupDatabase } = require('../bot');

function parseBody(body) {
  if (!body) return {};
  if (typeof body === 'string') {
    try {
      return JSON.parse(body);
    } catch (err) {
      return {};
    }
  }
  return body;
}

module.exports = async (req, res) => {
  if (req.method !== 'POST') {
    return res.status(405).json({ ok: false, error: 'Method not allowed' });
  }

  const secret = process.env.WEBHOOK_SECRET;
  if (secret) {
    const headerSecret = req.headers['x-telegram-bot-api-secret-token'];
    if (headerSecret !== secret) {
      return res.status(401).json({ ok: false, error: 'Invalid webhook secret' });
    }
  }

  try {
    await setupDatabase();
    const update = parseBody(req.body);
    await bot.handleUpdate(update);

    if (!res.headersSent) {
      return res.status(200).json({ ok: true });
    }
    return undefined;
  } catch (err) {
    console.error('Webhook error:', err);
    return res.status(500).json({ ok: false, error: 'Webhook processing failed' });
  }
};
