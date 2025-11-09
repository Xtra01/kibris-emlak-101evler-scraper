# Telegram Bot Setup Guide

## 🤖 Creating Your Bot

1. **Open Telegram** and search for `@BotFather`

2. **Create a new bot:**
   ```
   /newbot
   ```
   
3. **Choose a name** (e.g., "Emlak Scraper Control")

4. **Choose a username** (must end in 'bot', e.g., `emlak_scraper_bot`)

5. **Save your token** - BotFather will give you a token like:
   ```
   1234567890:ABCdefGHIjklMNOpqrsTUVwxyz123456789
   ```

## 🔑 Getting Your User ID

1. **Open Telegram** and search for `@userinfobot`

2. **Send any message** to the bot

3. **Save your ID** - it will respond with something like:
   ```
   Id: 123456789
   ```

## ⚙️ Configuration

1. **Copy the example env file:**
   ```bash
   cp .env.example .env
   ```

2. **Edit .env file:**
   ```bash
   nano .env
   ```

3. **Fill in your credentials:**
   ```bash
   TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz123456789
   TELEGRAM_USER_IDS=123456789,987654321  # Your user ID(s)
   ```

4. **Save and close** (Ctrl+X, Y, Enter)

## 🚀 Starting the Bot

### On Raspberry Pi:

```bash
cd /home/ekrem/projects/emlak-scraper

# Copy files
scp scripts/telegram_bot.py scripts/Dockerfile.telegram docker-compose.yml .env

# Build and start
docker compose build telegram-bot
docker compose up -d telegram-bot

# Check logs
docker logs emlak-telegram-bot -f
```

## 📱 Using the Bot

Once started, open Telegram and send `/start` to your bot.

### Available Commands:

**Status & Monitoring:**
- `/status` - Current scraper status
- `/temp` - Temperature and CPU info  
- `/health` - Full system health check
- `/stats` - Scraping statistics

**Control:**
- `/start_scrape` - Start the scraper
- `/pause` - Pause current operation
- `/resume` - Resume paused operation
- `/stop` - Stop scraping completely

**Info:**
- `/help` - Show help message

## 🌡️ Thermal Management

The bot works with the thermal manager to prevent Pi overheating:

- **> 65°C**: Scraper auto-pauses
- **< 60°C**: Scraper auto-resumes
- **> 75°C**: Emergency stop

Check temperature anytime with `/temp`

## 🔧 Troubleshooting

### Bot not responding:
```bash
# Check if container is running
docker ps | grep telegram-bot

# Check logs for errors
docker logs emlak-telegram-bot --tail 50

# Restart bot
docker compose restart telegram-bot
```

### Permission denied for vcgencmd:
The bot needs `privileged: true` and `network_mode: host` in docker-compose.yml (already configured)

### Bot token invalid:
- Make sure token is correct in .env
- No spaces or quotes around the token
- Token should be one continuous string

## 🔒 Security

- **NEVER** commit your `.env` file to git
- Only add trusted user IDs to `TELEGRAM_USER_IDS`
- Keep your bot token secret
- The bot only responds to authorized users

## 📊 Monitoring

View bot status:
```bash
# Check if running
docker ps | grep telegram-bot

# View logs
docker logs emlak-telegram-bot -f

# Check health
docker inspect emlak-telegram-bot | grep -A 5 Health
```
