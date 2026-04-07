require('dotenv').config();
const { Telegraf, Markup } = require('telegraf');
const { Media, Episode, User, Channel, sequelize } = require('./models');

const bot = new Telegraf(process.env.BOT_TOKEN);
const ADMIN_ID = (process.env.ADMIN_ID || '').toString();

async function isAdmin(ctx) {
  return ctx.from && ctx.from.id.toString() === ADMIN_ID;
}

async function setupDatabase() {
  await sequelize.authenticate();
  await sequelize.sync();
  console.log('Database connected and synced.');
}

bot.use(async (ctx, next) => {
  if (ctx.from) {
    try {
      await User.findOrCreate({
        where: { telegram_id: ctx.from.id.toString() },
        defaults: { username: ctx.from.username || 'unknown' },
      });
    } catch (err) {
      console.error('User create error:', err.message);
    }
  }

  if (ctx.from && process.env.CHECK_SUB === 'true') {
    try {
      const channels = await Channel.findAll();
      const notSubscribed = [];

      for (const channel of channels) {
        try {
          const member = await ctx.telegram.getChatMember(channel.channel_id, ctx.from.id);
          if (['left', 'kicked'].includes(member.status)) {
            notSubscribed.push(channel);
          }
        } catch (err) {
          notSubscribed.push(channel);
        }
      }

      if (notSubscribed.length > 0) {
        const buttons = notSubscribed.map((ch, index) => [
          Markup.button.url(`Kanal ${index + 1}`, ch.link),
        ]);

        if (ctx.callbackQuery) {
          return ctx.answerCbQuery("Siz kanallarga obuna bo'lmagansiz.", { show_alert: true });
        }

        buttons.push([Markup.button.callback("Obunani tekshirish", 'check_sub')]);
        return ctx.reply("Davom etish uchun kanallarga obuna bo'ling.", Markup.inlineKeyboard(buttons));
      }
    } catch (err) {
      console.error('Subscription middleware error:', err.message);
    }
  }

  return next();
});

bot.action('check_sub', async (ctx) => {
  await ctx.answerCbQuery();
  try {
    await ctx.deleteMessage();
  } catch (err) {
    // Ignore delete failures for old or inaccessible messages.
  }
  return ctx.reply('Endi kino yoki serial kodini yuboring.');
});

bot.start((ctx) => ctx.reply('Assalomu alaykum. Kino yoki serial kodini yuboring.'));

bot.command('help', (ctx) => {
  return ctx.reply([
    'Buyruqlar:',
    '/start - Botni boshlash',
    '/help - Yordam',
    '',
    'Admin buyruqlari:',
    '/setposter <code> <title> (rasmga reply qilib)',
    '/add <code> <ep> (videoga reply qilib)',
    '/addchannel <channel_id> <link>',
    '/delete <code>',
    '/stats',
  ].join('\n'));
});

bot.command('setposter', async (ctx) => {
  if (!(await isAdmin(ctx)) || !ctx.message.reply_to_message || !ctx.message.reply_to_message.photo) return;

  const args = ctx.message.text.trim().split(/\s+/);
  const code = args[1];
  const title = args.slice(2).join(' ') || '';

  if (!code) {
    return ctx.reply('Foydalanish: /setposter <code> <title>');
  }

  const photo = ctx.message.reply_to_message.photo;
  const photoSize = photo[photo.length - 1];

  try {
    const [media, created] = await Media.findOrCreate({
      where: { code },
      defaults: { title, photo_id: photoSize.file_id },
    });

    if (!created) {
      await Media.update(
        { photo_id: photoSize.file_id, title: title || media.title },
        { where: { code } }
      );
    }

    return ctx.reply('Poster saqlandi.');
  } catch (err) {
    console.error('setposter error:', err.message);
    return ctx.reply('Xatolik yuz berdi.');
  }
});

bot.command('add', async (ctx) => {
  if (!(await isAdmin(ctx)) || !ctx.message.reply_to_message || !ctx.message.reply_to_message.video) return;

  const args = ctx.message.text.trim().split(/\s+/);
  const code = args[1];
  const epNumber = Number.parseInt(args[2], 10) || 1;

  if (!code) {
    return ctx.reply('Foydalanish: /add <code> <ep_number>');
  }

  try {
    await Media.findOrCreate({
      where: { code },
      defaults: { title: ctx.message.reply_to_message.caption || null },
    });

    await Episode.create({
      code,
      ep_number: epNumber,
      file_id: ctx.message.reply_to_message.video.file_id,
    });

    return ctx.reply(`Video saqlandi. Kod: ${code}, qism: ${epNumber}`);
  } catch (err) {
    console.error('add error:', err.message);
    return ctx.reply('Xatolik yuz berdi.');
  }
});

bot.command('addchannel', async (ctx) => {
  if (!(await isAdmin(ctx))) return;

  const args = ctx.message.text.trim().split(/\s+/);
  const channelId = args[1];
  const link = args[2];

  if (!channelId || !link) {
    return ctx.reply('Foydalanish: /addchannel <channel_id> <link>');
  }

  try {
    await Channel.create({ channel_id: channelId, link });
    return ctx.reply('Kanal qoshildi.');
  } catch (err) {
    console.error('addchannel error:', err.message);
    return ctx.reply('Kanalni qoshishda xatolik yuz berdi. Ehtimol oldin qoshilgan.');
  }
});

bot.command('delete', async (ctx) => {
  if (!(await isAdmin(ctx))) return;

  const code = (ctx.message.text.trim().split(/\s+/)[1] || '').trim();
  if (!code) {
    return ctx.reply('Foydalanish: /delete <code>');
  }

  try {
    await Episode.destroy({ where: { code } });
    await Media.destroy({ where: { code } });
    return ctx.reply('Kod boyicha malumotlar ochirildi.');
  } catch (err) {
    console.error('delete error:', err.message);
    return ctx.reply('Ochirishda xatolik yuz berdi.');
  }
});

bot.command('stats', async (ctx) => {
  if (!(await isAdmin(ctx))) return;

  try {
    const [users, serials, episodes, channels] = await Promise.all([
      User.count(),
      Media.count(),
      Episode.count(),
      Channel.count(),
    ]);

    return ctx.reply([
      'Statistika:',
      `Foydalanuvchilar: ${users}`,
      `Media kodlar: ${serials}`,
      `Video qism-lar: ${episodes}`,
      `Majburiy obuna kanallari: ${channels}`,
    ].join('\n'));
  } catch (err) {
    console.error('stats error:', err.message);
    return ctx.reply('Statistikani olishda xatolik yuz berdi.');
  }
});

bot.on('text', async (ctx) => {
  if (ctx.message.text.startsWith('/')) return;

  const code = ctx.message.text.trim();

  try {
    const media = await Media.findOne({ where: { code } });
    const episodes = await Episode.findAll({
      where: { code },
      order: [['ep_number', 'ASC']],
    });

    if (!media && episodes.length === 0) {
      return ctx.reply('Bunday kod topilmadi.');
    }

    if (episodes.length === 1 && !(media && media.photo_id)) {
      return ctx.replyWithVideo(episodes[0].file_id, { caption: media ? media.title : undefined });
    }

    const buttons = [];
    let row = [];

    episodes.forEach((ep, index) => {
      row.push(Markup.button.callback(`${ep.ep_number}-qism`, `ep_${ep.id}`));
      if (row.length === 4 || index === episodes.length - 1) {
        buttons.push(row);
        row = [];
      }
    });

    const text = media && media.title ? `*${media.title}*\n\nQismni tanlang:` : 'Qismni tanlang:';

    if (media && media.photo_id) {
      return ctx.replyWithPhoto(media.photo_id, {
        caption: text,
        parse_mode: 'Markdown',
        ...Markup.inlineKeyboard(buttons),
      });
    }

    return ctx.reply(text, {
      parse_mode: 'Markdown',
      ...Markup.inlineKeyboard(buttons),
    });
  } catch (err) {
    console.error('search error:', err.message);
    return ctx.reply('Qidirishda xatolik yuz berdi.');
  }
});

bot.action(/ep_(\d+)/, async (ctx) => {
  try {
    const ep = await Episode.findByPk(ctx.match[1]);
    if (!ep) {
      await ctx.answerCbQuery('Qism topilmadi.', { show_alert: true });
      return;
    }

    await ctx.replyWithVideo(ep.file_id);
    await ctx.answerCbQuery();
  } catch (err) {
    console.error('episode action error:', err.message);
    await ctx.answerCbQuery('Xatolik yuz berdi.', { show_alert: true });
  }
});

module.exports = { bot, setupDatabase };
