module.exports = async (req, res) => {
  if (req.method !== 'GET' && req.method !== 'POST') {
    return res.status(405).json({ ok: false, error: 'Method not allowed' });
  }

  const token = (process.env.BOT_TOKEN || '').trim();
  if (!token) {
    return res.status(400).json({ ok: false, error: 'BOT_TOKEN missing' });
  }

  const baseUrl = (process.env.WEBHOOK_URL || '').trim() ||
    (process.env.VERCEL_URL ? `https://${process.env.VERCEL_URL}` : '');

  if (!baseUrl) {
    return res.status(400).json({ ok: false, error: 'WEBHOOK_URL or VERCEL_URL missing' });
  }

  const webhookUrl = `${baseUrl}/api/webhook`;
  const payload = {
    url: webhookUrl,
    allowed_updates: ['message', 'callback_query'],
  };

  if (process.env.WEBHOOK_SECRET) {
    payload.secret_token = process.env.WEBHOOK_SECRET;
  }

  try {
    const tgResponse = await fetch(`https://api.telegram.org/bot${token}/setWebhook`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload),
    });

    const data = await tgResponse.json();

    if (!data.ok) {
      return res.status(500).json({ ok: false, error: data.description || 'setWebhook failed', data });
    }

    return res.status(200).json({ ok: true, webhookUrl, data });
  } catch (err) {
    console.error('setWebhook error:', err);
    return res.status(500).json({ ok: false, error: 'setWebhook request failed' });
  }
};
