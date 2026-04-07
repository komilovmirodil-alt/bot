const { DataTypes } = require('sequelize');
const sequelize = require('./database');

const Media = sequelize.define('Media', {
  code: { type: DataTypes.STRING, allowNull: false, unique: true },
  title: { type: DataTypes.STRING, allowNull: true },
  photo_id: { type: DataTypes.STRING, allowNull: true },
});

const Episode = sequelize.define('Episode', {
  code: { type: DataTypes.STRING, allowNull: false },
  ep_number: { type: DataTypes.INTEGER, allowNull: false },
  file_id: { type: DataTypes.STRING, allowNull: false },
});

const User = sequelize.define('User', {
  telegram_id: { type: DataTypes.STRING, allowNull: false, unique: true },
  username: { type: DataTypes.STRING, allowNull: true },
});

const Channel = sequelize.define('Channel', {
  channel_id: { type: DataTypes.STRING, allowNull: false, unique: true },
  link: { type: DataTypes.STRING, allowNull: true },
});

module.exports = { Media, Episode, User, Channel, sequelize };
