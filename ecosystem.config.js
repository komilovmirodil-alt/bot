module.exports = {
  apps: [
    {
      name: 'aninexus-bot',
      script: 'index.js',
      cwd: '.',
      instances: 1,
      exec_mode: 'fork',
      autorestart: true,
      max_restarts: 20,
      restart_delay: 5000,
      watch: false,
      max_memory_restart: '300M',
      env: {
        NODE_ENV: 'production',
      },
    },
  ],
};
