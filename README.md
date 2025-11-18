# MegatronFileStream

Megatron File Stream Telegram Bot

## Deploy Megatron to Heroku

[![Deploy to Heroku](https://img.shields.io/badge/Deploy%20To%20Heroku-black?style=for-the-badge&logo=heroku)](https://heroku.com/deploy?template=https://github.com/xzinc/newspeedx)

## Configuration

Copy `.env.example` to `.env` (or configure your hosting provider) and fill in the values listed below. The bot will refuse to boot if any required variable is missing.

### Required environment variables

| Variable | Description |
| --- | --- |
| `API_ID` | Your Telegram API ID from [my.telegram.org](https://my.telegram.org) |
| `API_HASH` | API hash paired with the `API_ID` |
| `BOT_TOKEN` | Bot token from @BotFather (regenerate if Telegram says it expired) |
| `OWNER_ID` | Numeric Telegram user ID allowed to run owner commands |
| `BIN_CHANNEL` | **Numeric** channel ID (must start with `-100`) where uploads are stored |
| `DATABASE_URL` | MongoDB connection string (Motor) used for users, files, force-subscribe state, audits, short links |

> ℹ️  `DATABASE_URL` is now mandatory. All security features (signed links, rate limiting, ban sync, analytics) depend on it and the bot exits early if it is missing.

### Optional behaviour toggles

| Variable | Default | Description |
| --- | --- | --- |
| `SESSION_NAME` | `AvishkarPatil` | Custom Pyrogram session file name |
| `WORKERS` | `6` | Number of Pyrogram worker threads |
| `SLEEP_THRESHOLD` | `60` | Seconds to sleep when Telegram returns slow flood waits |
| `PING_INTERVAL` | `1200` | Interval (seconds) for keep-alive pings |
| `BROADCAST_AS_COPY` | `false` | Set `true` to send broadcasts as copies instead of forwarded messages |
| `UPDATES_CHANNEL` | unset | Legacy fallback for force-subscribe; `/fsub` command stored in DB overrides this |
| `BANNED_CHANNELS` | unset | Space separated list of channel IDs to ignore when forwarding |
| `MULTI_CLIENT` | `false` | Experimental multi-session mode for high volume deployments |

### Security, link, and quota controls

| Variable | Default | Purpose |
| --- | --- | --- |
| `APP_SECRET` | Bot token | Overrides the secret used to sign download tokens (set a random string for extra security) |
| `LINK_TTL_SECONDS` | `43200` (12 h) | Lifetime for full download links before they expire |
| `SHORT_LINK_TTL_SECONDS` | `604800` (7 d) | TTL for generated short slugs (when enabled) |
| `USER_RATE_LIMIT` | `12` | Maximum actions allowed within `USER_RATE_WINDOW` seconds per user |
| `USER_RATE_WINDOW` | `60` | Sliding window size (seconds) for the rate limiter |
| `USER_DAILY_QUOTA` | `0` | Optional hard cap on daily downloads/uploads per user (`0` disables the quota) |
| `MAX_FILE_SIZE_MB` | `2048` | Reject uploads larger than this many megabytes |

### Network and hosting knobs

| Variable | Default | Description |
| --- | --- | --- |
| `PORT` | `8000` | Aiohttp server port (honour your platform’s expectations) |
| `WEB_SERVER_BIND_ADDRESS` | `0.0.0.0` | Bind address for the web server |
| `HAS_SSL` | auto | Force HTTPS generation for self-hosted deployments |
| `NO_PORT` | auto | Drop `:<port>` from generated links when behind a proxy/load balancer |
| `APP_NAME` | auto | Optional friendly name reported in logs |
| `FQDN` | auto | Override detected domain (set when using a custom domain) |
| `MAX_LOGIN_FLOODWAIT` | `900` | Maximum flood wait (seconds) tolerated at login time |
| `LOGIN_FLOODWAIT_PADDING` | `5` | Extra seconds added to flood waits to stay safe |

### Practical examples

- `APP_SECRET` — Set a random 32+ character string whenever your bot is exposed to the public internet. Every download link is signed with this secret; if it leaks, regenerate it to invalidate all old links instantly.
- `LINK_TTL_SECONDS` / `SHORT_LINK_TTL_SECONDS` — Shorten these (for example, `3600` / `86400`) when you want links to auto-expire within an hour or a day. Lengthen them for trusted private deployments that need week-long access.
- `USER_RATE_LIMIT` & `USER_RATE_WINDOW` — Limit how many actions a user can trigger in the given window. Keep the default `12` per `60` seconds for light use, drop it (e.g., `6` per `60`) on free tiers, or increase it for paid users.
- `USER_DAILY_QUOTA` — Set to a non-zero number (e.g., `100`) to cap uploads/downloads a user can perform in 24 hours. Leave it at `0` to disable quotas entirely.
- `MAX_FILE_SIZE_MB` — Align it with the storage you can afford. Lower it for lightweight media bots; raise cautiously if you store larger archives in the channel.

The runtime uses [PyroBlack 2.6.x](https://pypi.org/project/pyroblack/) (a maintained Pyrogram 2.x fork) so Telegram's 64-bit identifiers and recent API changes are handled without hacks.

## Feature Highlights

- Signed download links backed by HMAC tokens (`APP_SECRET`) with configurable expiries and optional short slugs.
- Dynamic force-subscribe: change the updates channel at runtime with `/fsub` and track user join status in Mongo.
- Broadcast tooling with flood-wait aware retries and per-user success/failure counters.
- Per-user rate limiting and optional daily quotas to protect your bandwidth.
- Rich user telemetry: uploads/download counters, audit log, and upcoming admin dashboard hooks.

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
| `DATABASE_URL` | `mongodb+srv://user:pass@cluster.mongodb.net/megatron` | MongoDB URI (Atlas, Compose, etc.). Required for signed links, rate limiting, and force-subscribe sync |

### Optional Environment Variables for Koyeb

| Variable | Recommended Value | Description |
| --- | --- | --- |
| `FQDN` | `your-app-name.koyeb.app` | **Auto-detected** from `KOYEB_PUBLIC_DOMAIN` if not set. Only set manually if using custom domain |
| `APP_NAME` | `megatron-bot` | Custom name for logs (optional) |
| `PORT` | `8000` | Web server port (default: 8000) |
| `UPDATES_CHANNEL` | `-1001234567890` | Force users to join your channel before using bot. `/fsub` command (stored in DB) overrides this |
| `APP_SECRET` | random 32–64 chars | Overrides download-token signer; set to a strong random string for public deployments |
| `LINK_TTL_SECONDS` | `43200` | Tune link lifespan if you need longer/shorter lived downloads |
| `USER_RATE_LIMIT` | `12` | Raise/lower per-user throughput limits. Pair with `USER_RATE_WINDOW` and `USER_DAILY_QUOTA` |

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

---

## Bot Owner Commands

### Dynamic Force Subscribe Control

Control force subscribe without restarting the bot! Requires `DATABASE_URL` to be configured.

**Enable force subscribe:**
```
/fsub on @your_channel
/fsub on -1001234567890
```

**Disable force subscribe:**
```
/fsub off
```

**Check status:**
```
/fsub status
```

**Features:**
- ✅ Change channel anytime without restart
- ✅ Turn on/off instantly
- ✅ Bot must be admin in the channel
- ✅ Works alongside environment variable `UPDATES_CHANNEL`
- ✅ Database settings override environment variable

**Requirements:**
- Bot must be admin in target channel with:
  - Ban users permission
  - Invite users permission
- `DATABASE_URL` must be configured
