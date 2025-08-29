# SciDoc Telegram Bot

A production-ready Telegram bot for content archiving and distribution with Persian (fa-IR) interface. The bot allows admins to create content bundles in private archive channels and distribute them via deep-links with mandatory channel join requirements.

## Features

- **Archive Management**: Create content bundles with `/add` and `/done` commands
- **Deep-link Distribution**: Generate unique links for each bundle
- **Join Gate**: Enforce mandatory channel memberships before content delivery  
- **Auto-deletion**: Automatically delete delivered content after 180 seconds
- **Admin Panel**: Comprehensive Persian interface for managing all aspects
- **Statistics**: Weekly, monthly, and total analytics
- **Broadcast System**: Send messages to all users with rate limiting
- **Manual Backup**: Create and download database backups
- **Request System**: Users can submit requests to admins

## Project Structure

```
bot/
├── app/
│   ├── main.py              # Application entry point
│   ├── config.py            # Configuration settings
│   ├── handlers/            # Message and callback handlers
│   │   ├── admin.py         # Admin panel functionality
│   │   ├── archive.py       # /add and /done commands
│   │   └── user.py          # User interactions and deep-links
│   ├── models/              # SQLAlchemy database models
│   ├── repo/                # Database repository layer
│   ├── services/            # Business logic services
│   ├── ui/                  # Persian UI texts and keyboards
│   ├── utils/               # Utility functions
│   └── jobs/                # Scheduled jobs (auto-deletion)
├── alembic/                 # Database migrations
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── env.example              # Environment variables template
```

## Windows Local Setup

### Prerequisites

1. **Install Python 3.11+**
   - Download from https://python.org/downloads/
   - During installation, check "Add Python to PATH"
   - Verify: Open Command Prompt and run `python --version`

2. **Install Git** (optional but recommended)
   - Download from https://git-scm.com/download/win

### Step-by-Step Setup

1. **Download the project**
   ```cmd
   # If using Git:
   git clone <repository-url>
   cd bot

   # Or download and extract the zip file, then navigate to the bot folder
   ```

2. **Create virtual environment**
   ```cmd
   python -m venv venv
   venv\Scripts\activate
   ```

3. **Install dependencies**
   ```cmd
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```cmd
   copy env.example .env
   # Edit .env file with your settings (see Configuration section below)
   ```

5. **Run database migrations**
   ```cmd
   alembic upgrade head
   ```

6. **Start the bot**
   ```cmd
   python -m app.main
   ```

## Configuration

Edit the `.env` file with your settings:

```env
# Bot Configuration
BOT_TOKEN=1234567890:AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
ADMIN_IDS=123456789,987654321
ARCHIVE_CHAT_IDS=-1001234567890,-1009876543210

# Database
DB_URL=sqlite:///data/app.db

# Timezone and Logging
TZ=Asia/Tehran
LOG_LEVEL=INFO

# Auto-deletion delay in seconds (default: 180 = 3 minutes)
AUTO_DELETE_DELAY=180
```

### Getting Required Values

1. **BOT_TOKEN**: 
   - Message @BotFather on Telegram
   - Send `/newbot` and follow instructions
   - Copy the token provided

2. **ADMIN_IDS**: 
   - Your Telegram user ID (comma-separated for multiple admins)
   - Get your ID from @userinfobot

3. **ARCHIVE_CHAT_IDS**:
   - Create a private channel or supergroup for archiving content
   - Add your bot as admin with "Post Messages" permission
   - Get the chat ID using @userinfobot or check bot logs when you send a message

## Usage Guide

### Creating Your First Bundle

1. **Set up archive channel**:
   - Create a private channel/group
   - Add the bot as admin
   - Add the channel ID to `ARCHIVE_CHAT_IDS` in `.env`

2. **Create a bundle**:
   - In the archive channel, send `/add`
   - Send the content you want to include (text, images, videos, etc.)
   - Send `/done` when finished
   - Enter a title for the bundle
   - Bot will reply with the bundle number and deep-link

3. **Test the deep-link**:
   - Open the generated link
   - If you haven't joined required channels, you'll see join buttons
   - After joining, click "✅ جوین شدم"
   - Content will be delivered and auto-deleted after 180 seconds

### Admin Panel

Send `/admin` to the bot in a private message to access the admin panel:

- **📦 مدیریت بسته‌ها**: Search, activate/deactivate bundles, copy links
- **📢 کانال‌های اجباری**: Add/remove mandatory channels
- **💬 پیام‌های سیستم**: Set starting message and ending messages
- **📝 درخواست‌های کاربران**: View and resolve user requests
- **📡 ارسال همگانی**: Broadcast messages to all users
- **💾 پشتیبان‌گیری**: Create manual database backups
- **📊 آمار**: View weekly, monthly, and total statistics

### Statistics

The statistics feature provides three types of reports:

- **📅 هفتگی (Weekly)**: Downloads, active users, and top bundle for last 7 days
- **📅 ماهانه (Monthly)**: Same metrics for last 30 days  
- **📅 کل زمان (Total)**: All-time downloads, total users, total bundles, and top bundle

### Manual Backup

1. Go to Admin Panel → **💾 پشتیبان‌گیری**
2. Click **▶️ اجرای پشتیبان‌گیری**
3. The bot will create a zip file containing the database
4. The backup file will be sent to you as a Telegram document
5. The file is also saved in the `./backups/` folder

**Backup files are named**: `backup-YYYYMMDD-HHMM.zip`

### Disaster Recovery

If you need to restore from a backup:

1. **Stop the bot** (Ctrl+C in terminal or stop Docker container)
2. **Replace the database file**:
   ```cmd
   # Extract the backup zip
   # Copy app.db from the zip to ./data/app.db
   copy backup-extracted\app.db data\app.db
   ```
3. **Restart the bot**
4. **Verify functionality**: All deep-links should continue to work

## Docker Deployment

### Local Docker Setup

1. **Install Docker Desktop for Windows**
   - Download from https://docker.com/products/docker-desktop
   - Install and start Docker Desktop

2. **Prepare environment**
   ```cmd
   copy env.example .env
   # Edit .env with your configuration
   ```

3. **Build and run**
   ```cmd
   docker-compose up -d
   ```

4. **View logs**
   ```cmd
   docker-compose logs -f
   ```

5. **Stop the bot**
   ```cmd
   docker-compose down
   ```

### Dockploy Deployment

**Dockploy** is a simple Docker deployment platform. Here's how to deploy:

#### Step 1: Prepare Your Server

1. **Install Dockploy on your server**:
   ```bash
   curl -sSL https://dockploy.com/install.sh | sh
   ```

2. **Access Dockploy web interface**:
   - Open `http://your-server-ip:3000` in your browser
   - Complete the initial setup

#### Step 2: Create Application

1. **Click "Create Application"**
2. **Choose "Docker Compose"**
3. **Fill in application details**:
   - **Name**: `scidoc-bot`
   - **Description**: `Telegram content distribution bot`

#### Step 3: Configure Docker Compose

In the Docker Compose section, paste this configuration:

```yaml
version: '3.8'

services:
  bot:
    image: ghcr.io/yourusername/scidoc-bot:latest  # Replace with your image
    container_name: scidoc-bot
    restart: unless-stopped
    volumes:
      - ./data:/app/data
      - ./logs:/app/logs  
      - ./backups:/app/backups
    environment:
      - BOT_TOKEN=${BOT_TOKEN}
      - ADMIN_IDS=${ADMIN_IDS}
      - ARCHIVE_CHAT_IDS=${ARCHIVE_CHAT_IDS}
      - DB_URL=sqlite:///data/app.db
      - TZ=Asia/Tehran
      - LOG_LEVEL=INFO
      - AUTO_DELETE_DELAY=180
```

#### Step 4: Set Environment Variables

In the Environment Variables section, add:

```
BOT_TOKEN=1234567890:AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
ADMIN_IDS=123456789,987654321
ARCHIVE_CHAT_IDS=-1001234567890,-1009876543210
```

#### Step 5: Configure Volumes

In the Volumes section, add these persistent volumes:

- **Source**: `/data` → **Target**: `/app/data` (Database storage)
- **Source**: `/logs` → **Target**: `/app/logs` (Log files)  
- **Source**: `/backups` → **Target**: `/app/backups` (Backup files)

#### Step 6: Deploy

1. Click **"Deploy Application"**
2. Wait for the deployment to complete
3. Check logs to ensure the bot started successfully

#### Step 7: Access Backups

To download backup files from Dockploy:

1. Go to your application in Dockploy
2. Click **"Files"** tab
3. Navigate to `/backups` folder
4. Download backup files as needed

### Building Custom Docker Image

If you want to build your own image:

1. **Build the image**:
   ```cmd
   docker build -t scidoc-bot:latest .
   ```

2. **Push to registry** (optional):
   ```cmd
   docker tag scidoc-bot:latest your-registry/scidoc-bot:latest
   docker push your-registry/scidoc-bot:latest
   ```

## Troubleshooting

### Common Issues

1. **Bot doesn't respond**:
   - Check BOT_TOKEN is correct
   - Verify bot is started with `/start` command
   - Check logs for errors

2. **Deep-links don't work**:
   - Ensure bundles are active
   - Check ARCHIVE_CHAT_IDS configuration
   - Verify bot has admin permissions in archive channels

3. **Auto-deletion not working**:
   - Check bot logs for scheduler errors
   - Ensure database is writable
   - Verify AUTO_DELETE_DELAY setting

4. **Join gate issues**:
   - Verify bot can access mandatory channels
   - Check channel links are valid
   - Ensure channels exist and bot has permissions

### Log Files

- **Local setup**: Check `./logs/bot.log`
- **Docker**: Use `docker-compose logs -f`
- **Dockploy**: Check logs in the web interface

### Database Issues

If you encounter database errors:

1. **Reset database** (⚠️ This deletes all data):
   ```cmd
   # Stop bot first
   rm data/app.db
   alembic upgrade head
   # Restart bot
   ```

2. **Check database integrity**:
   ```cmd
   sqlite3 data/app.db "PRAGMA integrity_check;"
   ```

## Technical Details

### Architecture Decisions

1. **Single Service Design**: Simplified deployment and maintenance
2. **SQLite Database**: File-based storage for easy backup/restore
3. **Polling Mode**: No webhook complexity, works behind firewalls
4. **APScheduler**: Persistent job scheduling for auto-deletion
5. **copyMessage API**: Ensures file links persist across server moves

### Security Considerations

- Admin access controlled by Telegram user IDs
- No file uploads to bot server (uses copyMessage)
- Environment variables for all secrets
- Rate limiting on broadcasts
- Input validation on all user inputs

### Performance Notes

- Supports concurrent users
- Batch processing for broadcasts
- Efficient database queries with proper indexing
- Memory-efficient message handling
- Automatic cleanup of expired data

## Support

For issues or questions:

1. Check the troubleshooting section above
2. Review bot logs for error messages
3. Verify configuration settings
4. Test with a minimal setup first

## License

This project is provided as-is for educational and personal use.
