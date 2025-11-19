# 🔧 Environment Variables Configuration Guide

## 📋 Quick Start

### For Koyeb Deployment:

1. **Copy the Template**:
   - Use `koyeb.env.example` (simplified for Koyeb)
   - Or use `.env.example` (full template with all options)

2. **Edit Your Values**:
   ```env
   API_ID=12345678                    # Your API ID
   API_HASH=abc123...                 # Your API Hash
   BOT_TOKEN=123:ABC...               # Bot token from @BotFather
   OWNER_ID=123456789                 # Your Telegram user ID
   BIN_CHANNEL=-1001234567890         # Storage channel ID
   DATABASE_URL=mongodb+srv://...     # MongoDB connection string
   ```

3. **Upload to Koyeb**:
   - Go to Koyeb Dashboard → Your Service → Settings
   - Navigate to "Environment Variables" section
   - Click "Add Variable" → Select **"File"** option
   - Upload your edited `.env` file
   - **File Format**: Select **"Plain Text"** or **".env"**
   - Click "Deploy"

---

## 🔑 Required Variables

| Variable | Example | Description | How to Get |
|----------|---------|-------------|------------|
| `API_ID` | `12345678` | Telegram API ID | [my.telegram.org](https://my.telegram.org) |
| `API_HASH` | `abc123def456...` | Telegram API Hash | [my.telegram.org](https://my.telegram.org) |
| `BOT_TOKEN` | `123:ABC-DEF...` | Bot authentication token | [@BotFather](https://t.me/BotFather) |
| `OWNER_ID` | `123456789` | Your Telegram user ID | [@userinfobot](https://t.me/userinfobot) |
| `BIN_CHANNEL` | `-1001234567890` | Private channel for file storage | See [Getting Channel ID](#getting-channel-id) |
| `DATABASE_URL` | `mongodb+srv://...` | MongoDB connection string | [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) (free) |

---

## 🎨 New Customizable Variables

### Channel & Link Branding

| Variable | Default | Description |
|----------|---------|-------------|
| `UPDATES_CHANNEL_LINK` | `https://t.me/+_J90-7N-lk9iNDZl` | Link shown in "Updates Channel" button |
| `DONATION_LINK` | `https://t.me/YourBot?start=donate` | Link shown in "Donate" button |
| `SUPPORT_LINK` | `https://t.me/+_J90-7N-lk9iNDZl` | Support group/channel link |

**Benefits**:
- ✅ Change links without modifying code
- ✅ Easy rebranding for your bot
- ✅ Update links without redeployment (just restart)

**Example**:
```env
UPDATES_CHANNEL_LINK=https://t.me/your_channel
DONATION_LINK=https://buy.stripe.com/your_payment_link
SUPPORT_LINK=https://t.me/your_support_group
```

---

## 🔒 Optional Security Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `UPDATES_CHANNEL` | (empty) | Force subscribe channel ID `-100...` |
| `APP_SECRET` | Auto-generated | Secret for link encryption |
| `BANNED_CHANNELS` | (empty) | Space-separated banned channel IDs |

---

## ⚙️ Optional Performance Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `WORKERS` | `6` | Number of worker threads |
| `PING_INTERVAL` | `240` | Keep-alive interval (seconds) for Koyeb |
| `LINK_TTL_SECONDS` | `43200` | Link expiry time (12 hours) |
| `SHORT_LINK_TTL_SECONDS` | `604800` | Short link expiry (7 days) |
| `MAX_FILE_SIZE_MB` | `2048` | Maximum file size (2GB) |
| `USER_RATE_LIMIT` | `12` | Requests per time window |
| `USER_RATE_WINDOW` | `60` | Rate limit window (seconds) |
| `USER_DAILY_QUOTA` | `0` | Daily request limit (0 = unlimited) |

---

## 🌐 Server Configuration (Auto-Detected)

These are **automatically detected** on Koyeb/Heroku - **leave empty**:

| Variable | Koyeb/Heroku | Local |
|----------|--------------|-------|
| `FQDN` | Auto-detected | `localhost` |
| `PORT` | `8000` (auto) | `8000` |
| `HAS_SSL` | Auto-enabled | `false` |
| `NO_PORT` | Auto-enabled | `false` |

---

## 📝 Step-by-Step Setup

### 1. Getting Channel ID

**Create Storage Channel** (`BIN_CHANNEL`):

```bash
1. Create a new private Telegram channel
2. Add your bot as administrator with these permissions:
   - ✅ Post Messages
   - ✅ Delete Messages
   - ✅ Manage Channel (optional)
3. Forward any message from the channel to @RawDataBot
4. Copy the channel ID (starts with -100)
5. Use this as BIN_CHANNEL value
```

**Example**: `-1001234567890`

### 2. Getting MongoDB Database

```bash
1. Visit: https://www.mongodb.com/cloud/atlas
2. Create a free account
3. Create a free cluster (M0)
4. Create database user with password
5. Get connection string:
   - Click "Connect" → "Connect your application"
   - Copy the connection string
   - Replace <password> with your password
   - Replace <dbname> with your database name (e.g., megatron)
```

**Example**: `mongodb+srv://botuser:mypass123@cluster0.abc.mongodb.net/megatron`

### 3. Configuring Links

**Updates Channel Link**:
```env
# Public invite link (with or without +)
UPDATES_CHANNEL_LINK=https://t.me/+_J90-7N-lk9iNDZl

# Or username-based
UPDATES_CHANNEL_LINK=https://t.me/your_channel_username
```

**Donation Link Options**:
```env
# Telegram bot payment
DONATION_LINK=https://t.me/YourBot?start=donate

# External payment link
DONATION_LINK=https://buy.stripe.com/your_link
DONATION_LINK=https://www.paypal.me/yourusername
DONATION_LINK=https://ko-fi.com/yourusername
```

---

## 🚀 Deployment Methods

### Method 1: File Upload (Recommended for Koyeb)

1. Edit `koyeb.env.example` with your values
2. Save as `.env`
3. In Koyeb Dashboard:
   - Service → Settings → Environment Variables
   - "Add Variable" → **"File"**
   - Upload `.env` file
   - Format: **"Plain Text"** or **".env"**
4. Deploy

### Method 2: Manual Entry

1. In Koyeb Dashboard:
   - Service → Settings → Environment Variables
   - Click "Add Variable" → **"Name/Value"**
   - Add each variable individually:
     ```
     Name: API_ID
     Value: 12345678
     ```
2. Add all required variables
3. Deploy

### Method 3: Koyeb CLI

```bash
# Set variables via CLI
koyeb service update your-service \
  --env API_ID=12345678 \
  --env API_HASH=abc123... \
  --env BOT_TOKEN=123:ABC... \
  --env OWNER_ID=123456789 \
  --env BIN_CHANNEL=-1001234567890 \
  --env DATABASE_URL=mongodb+srv://...
```

---

## 🔄 Updating Variables

### On Koyeb:
1. Dashboard → Service → Settings → Environment Variables
2. Edit existing variables or upload new file
3. Click "Deploy" to apply changes
4. Bot will restart automatically

### For Link Changes Only:
You can update these **without full redeployment**:
- `UPDATES_CHANNEL_LINK`
- `DONATION_LINK`
- `SUPPORT_LINK`

Just update the variable and restart the service.

---

## 🛡️ Security Best Practices

### ✅ DO:
- ✅ Use strong, unique `APP_SECRET`
- ✅ Keep `.env` file in `.gitignore`
- ✅ Use environment variables, never hardcode
- ✅ Rotate tokens periodically
- ✅ Use MongoDB Atlas IP whitelist (allow all: `0.0.0.0/0` for Koyeb)

### ❌ DON'T:
- ❌ Commit `.env` file to GitHub
- ❌ Share your `BOT_TOKEN` publicly
- ❌ Use same database for multiple bots (security risk)
- ❌ Hardcode sensitive values in code

---

## 🆘 Troubleshooting

### Issue: "Missing required environment variable"

**Solution**: Check you've set all required variables:
```env
API_ID=
API_HASH=
BOT_TOKEN=
OWNER_ID=
BIN_CHANNEL=
DATABASE_URL=
```

### Issue: "BIN_CHANNEL must start with -100"

**Solution**: 
- Channel ID must be numeric starting with `-100`
- Get correct ID from @RawDataBot
- Example: `-1001234567890` ✅
- Not: `@mychannel` ❌

### Issue: Database connection failed

**Solution**:
1. Check MongoDB Atlas IP whitelist (allow `0.0.0.0/0`)
2. Verify username/password in connection string
3. Ensure database user has read/write permissions
4. Test connection string format:
   ```
   mongodb+srv://username:password@cluster.mongodb.net/dbname
   ```

### Issue: Links not updating

**Solution**:
- After changing link variables, restart the bot service
- Clear browser cache if testing web interface
- Verify variable names are correct (case-sensitive)

---

## 📚 Related Documentation

- [Koyeb Setup Guide](KOYEB_SETUP.md) - Full Koyeb deployment tutorial
- [README](README.md) - General bot documentation
- [Admin Commands](ADMIN_COMMANDS.md) - Bot management commands

---

## 🎯 Quick Reference

**Minimum Required Setup**:
```env
API_ID=12345678
API_HASH=abc123...
BOT_TOKEN=123:ABC...
OWNER_ID=123456789
BIN_CHANNEL=-1001234567890
DATABASE_URL=mongodb+srv://...
```

**Recommended Additional Setup**:
```env
UPDATES_CHANNEL_LINK=https://t.me/your_channel
DONATION_LINK=https://t.me/YourBot?start=donate
SUPPORT_LINK=https://t.me/your_support
PING_INTERVAL=240
```

---

**Last Updated**: November 19, 2025  
**File Format for Koyeb**: Plain Text (.env)
