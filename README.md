# MegatronFileStream

Megatron File Stream Telegram Bot

## Deploy Megatron to Heroku

[![Deploy to Heroku](https://img.shields.io/badge/Deploy%20To%20Heroku-black?style=for-the-badge&logo=heroku)](https://heroku.com/deploy?template=https://github.com/xzinc/newspeedx)

## Configuration

Before running or deploying the bot you **must** provide your own Telegram credentials via environment variables (a leaked default token triggers `ACCESS_TOKEN_EXPIRED` errors). Set the following variables in your `.env`, hosting dashboard, or shell:

| Variable | Required | Description |
| --- | --- | --- |
| `API_ID` | ✅ | Your Telegram API ID from [my.telegram.org](https://my.telegram.org) |
| `API_HASH` | ✅ | The API hash paired with the API ID |
| `BOT_TOKEN` | ✅ | Bot token from @BotFather; regenerate if Telegram says it expired |
| `BIN_CHANNEL` | ✅ | **Numeric** channel ID (must start with `-100`, e.g. `-1001234567890`) where files are stored |
| `OWNER_ID` | ✅ | Numeric Telegram user ID used for admin operations |
| `DATABASE_URL` | optional | MongoDB/Postgres connection string for persistence |
| `SESSION_NAME` | optional | Custom Pyrogram session filename (defaults to `MegatronBot`) |
| `PORT` | optional | TCP port for the aiohttp server (defaults to `8000`; set it to whatever your platform expects) |
| `HAS_SSL`, `NO_PORT`, etc. | optional | Advanced hosting/network toggles |
| `MAX_LOGIN_FLOODWAIT` | optional | Upper bound (in seconds) Megatron will wait when Telegram throttles bot logins (defaults to 900) |
| `SKIP_BIN_VALIDATION` | optional | Set to `true` only if you understand the risks and want to bypass BIN channel checks (not recommended) |

Copy `.env.example` to `.env` (or configure your hosting provider) and fill in the required values before starting the bot. The runtime now uses [PyroBlack 2.6.x](https://pypi.org/project/pyroblack/) (a maintained Pyrogram 2.x fork) so Telegram's 64-bit identifiers and recent API changes are handled without hacks.

### Channel setup checklist

1. Create (or pick) a Telegram channel that will store the uploaded files.
2. Add your bot to that channel and promote it to **admin** with “Post Messages” permission.
3. Copy the channel ID using `@userinfobot`/`@RawDataBot` (numeric IDs start with `-100`) or note the public username (prefix with `@`).
4. Set `BIN_CHANNEL` to that ID/username in `.env` or your hosting secrets.
5. Redeploy/restart Megatron. The startup guard now verifies the channel and will fail fast with a descriptive error if access is missing.
6. If you *must* skip validation (for example, while the channel is being provisioned), set `SKIP_BIN_VALIDATION=true`. The bot may still crash later if the channel remains inaccessible.

## Koyeb Deployment Guide

### Quick Deploy to Koyeb

1. **Fork this repository** to your GitHub account
2. **Create a new service** on [Koyeb](https://app.koyeb.com)
3. **Select GitHub** as the deployment source and choose your forked repository
4. **Configure build settings:**
   - Builder: `Buildpack`
   - Build command: (leave empty, auto-detected)
   - Run command: `python -m Megatron`

### Required Environment Variables

In Koyeb's **Environment Variables** section, add these:

| Variable | Example Value | How to Get |
| --- | --- | --- |
| `API_ID` | `12345678` | Get from [my.telegram.org](https://my.telegram.org) |
| `API_HASH` | `abcdef1234567890abcdef1234567890` | Get from [my.telegram.org](https://my.telegram.org) |
| `BOT_TOKEN` | `1234567890:ABCdefGHIjklMNOpqrsTUVwxyz` | Create bot with [@BotFather](https://t.me/BotFather) |
| `BIN_CHANNEL` | `-1001234567890` | [See Channel Setup below](#channel-setup-for-koyeb) |
| `OWNER_ID` | `123456789` | Your Telegram user ID from [@userinfobot](https://t.me/userinfobot) |

### Optional Environment Variables for Koyeb

| Variable | Recommended Value | Description |
| --- | --- | --- |
| `FQDN` | `your-app-name.koyeb.app` | **Auto-detected** from `KOYEB_PUBLIC_DOMAIN` if not set. Only set manually if using custom domain |
| `APP_NAME` | `megatron-bot` | Custom name for logs (optional) |
| `PORT` | `8000` | Web server port (default: 8000) |
| `DATABASE_URL` | `mongodb+srv://...` | MongoDB connection string for user tracking |
| `UPDATES_CHANNEL` | `-1001234567890` | Force users to join your channel before using bot |

**Note:** You do NOT need to set `HAS_SSL` or `NO_PORT` for Koyeb - they're auto-detected!

### Channel Setup for Koyeb

1. **Create a Telegram channel** (any name, can be private)
2. **Add your bot to the channel:**
   - Open channel → Add Members → Search for your bot's username → Add
3. **Make bot an admin:**
   - Channel Settings → Administrators → Add Admin → Select your bot
   - Enable "Post Messages" permission
4. **Get the channel ID:**
   - Forward any message from the channel to [@userinfobot](https://t.me/userinfobot)
   - Copy the "Forward from chat" ID (starts with `-100`)
   - Example: `-1003315873977`
5. **Set `BIN_CHANNEL`** in Koyeb environment variables with this ID

### Domain Configuration

#### Option A: Use Koyeb's Default Domain (Recommended)

**Do nothing!** The bot automatically detects Koyeb's domain from `KOYEB_PUBLIC_DOMAIN` environment variable.

Your links will look like:
```
https://your-service-name-your-org.koyeb.app/123/filename.mp4?hash=AbCdEf
```

#### Option B: Use Custom Domain

1. **Add custom domain in Koyeb:**
   - Service Settings → Domains → Add Domain
   - Enter your domain (e.g., `files.yourdomain.com`)
   - Update DNS records as instructed

2. **Set FQDN environment variable:**
   ```
   FQDN=files.yourdomain.com
   ```

3. **Optional: Set custom app name:**
   ```
   APP_NAME=mybot
   ```

### Port Configuration

Koyeb automatically exposes your service on port 8000. To change:

1. **In Koyeb Dashboard:**
   - Service Settings → Ports
   - Set **Public Port**: `80` or `443`
   - Set **Private Port**: `8000` (your app's port)

2. **If you change the app port in code**, update the environment variable:
   ```
   PORT=8080
   ```

### Health Checks

Koyeb automatically monitors your service. The bot provides a health check endpoint at:
- `GET /` - Returns JSON with server status

Optionally configure in Koyeb:
- **Health Check Path:** `/`
- **Port:** `8000`
- **Protocol:** `HTTP`

### Deployment Steps

1. **Push your code to GitHub**
2. **Koyeb auto-deploys** when you push to main branch
3. **Check logs** in Koyeb dashboard for startup messages:
   ```
   ✓ BIN_CHANNEL validated
   ✓ Service Started - bot =>> ⚡ File to Link Stream
   ✓ Web server started on 0.0.0.0:8000
   ```
4. **Test the bot:**
   - Send `/start` to your bot on Telegram
   - Upload a file
   - You should receive a download link like:
     ```
     https://your-app.koyeb.app/123/filename.mp4?hash=AbCdEf
     ```

### Troubleshooting

| Issue | Solution |
| --- | --- |
| Links show `http://0.0.0.0:8000/...` | Koyeb hasn't set `KOYEB_PUBLIC_DOMAIN`. Manually set `FQDN=your-app.koyeb.app` |
| "upstream connect error" | Check port is set to `8000` in Koyeb port mapping |
| "BIN_CHANNEL validation failed" | Make sure bot is admin in the channel with "Post Messages" permission |
| "Invalid hash" error | Your `BIN_CHANNEL` ID is incorrect or bot can't access the channel |
| Bot doesn't respond | Check `BOT_TOKEN` is valid. Regenerate with @BotFather if needed |

### Finding Your Koyeb App Domain

**Method 1: From Koyeb Dashboard**
- Go to your service page
- Look for "Public URL" or "Endpoint"
- Copy the domain part only: `your-service-your-org.koyeb.app`

**Method 2: From Logs**
- Check Koyeb logs for: `KOYEB_PUBLIC_DOMAIN=your-service-your-org.koyeb.app`
- If you see this, the bot auto-detects it!

**Method 3: From Environment Tab**
- Koyeb → Service → Environment
- Look for `KOYEB_PUBLIC_DOMAIN` (auto-injected by Koyeb)

### Example Complete Configuration

```bash
# Required
API_ID=12345678
API_HASH=your_api_hash_here
BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrs
BIN_CHANNEL=-1001234567890
OWNER_ID=123456789

# Optional (auto-detected for Koyeb)
# FQDN=my-filebot.koyeb.app
# HAS_SSL=true
# NO_PORT=true

# Optional extras
DATABASE_URL=mongodb+srv://user:pass@cluster.mongodb.net/
UPDATES_CHANNEL=-1001234567890
APP_NAME=megatron-filebot
```
