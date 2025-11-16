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
| `BIN_CHANNEL` | ✅ | Channel ID (prefixed with `-100`) or public username (e.g. `@MyChannel`) where files are stored |
| `OWNER_ID` | ✅ | Numeric Telegram user ID used for admin operations |
| `DATABASE_URL` | optional | MongoDB/Postgres connection string for persistence |
| `SESSION_NAME` | optional | Custom Pyrogram session filename (defaults to `MegatronBot`) |
| `HAS_SSL`, `NO_PORT`, etc. | optional | Advanced hosting/network toggles |
| `SKIP_BIN_VALIDATION` | optional | Set to `true` only if you understand the risks and want to bypass BIN channel checks (not recommended) |

Copy `.env.example` to `.env` (or configure your hosting provider) and fill in the required values before starting the bot.

### Channel setup checklist

1. Create (or pick) a Telegram channel that will store the uploaded files.
2. Add your bot to that channel and promote it to **admin** with “Post Messages” permission.
3. Copy the channel ID using `@userinfobot`/`@RawDataBot` (numeric IDs start with `-100`) or note the public username (prefix with `@`).
4. Set `BIN_CHANNEL` to that ID/username in `.env` or your hosting secrets.
5. Redeploy/restart Megatron. The startup guard now verifies the channel and will fail fast with a descriptive error if access is missing.
6. If you *must* skip validation (for example, while the channel is being provisioned), set `SKIP_BIN_VALIDATION=true`. The bot may still crash later if the channel remains inaccessible.

## Koyeb deployment tips

1. Use the **default Python buildpack** (no need for a Dockerfile) and ensure `.python-version` exists with your desired major version (this repo ships with `3.13`).
2. In the Koyeb service’s Environment tab, add all required variables listed above (API credentials, bot token, BIN_CHANNEL, OWNER_ID, DATABASE_URL, etc.).
3. After each redeploy, watch the instance logs: if BIN_CHANNEL isn’t accessible, the startup guard will stop the app and print the exact fix (add the bot to the channel, grant admin rights, or correct the ID).
4. Once healthy, DM the bot `/start` and upload a sample file to confirm forwarding works in your BIN_CHANNEL.
