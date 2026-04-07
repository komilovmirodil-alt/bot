const { Sequelize } = require('sequelize');
const fs = require('fs');
const path = require('path');

const defaultStorage = process.env.VERCEL ? '/tmp/database.sqlite' : 'database.sqlite';
const storagePath = process.env.DB_STORAGE || defaultStorage;
const storageDir = path.dirname(storagePath);

if (storageDir && storageDir !== '.' && !fs.existsSync(storageDir)) {
  fs.mkdirSync(storageDir, { recursive: true });
}

const sequelize = new Sequelize({
  dialect: 'sqlite',
  storage: storagePath,
  logging: false,
});

module.exports = sequelize;
