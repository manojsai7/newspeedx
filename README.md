# MegatronFileStream
Megatron File Stream Telegram Bot

# Deploy Megatron to Heroku
<p align="center"><a href="https://heroku.com/deploy?template=https://github.com/xzinc/newspeedx"> <img src="https://img.shields.io/badge/Deploy%20To%20Heroku-black?style=for-the-badge&logo=heroku" width="220" height="38.45"/></a></p>


## Configuration

Before running or deploying the bot you **must** provide your own Telegram credentials via environment variables (a leaked default token triggers `ACCESS_TOKEN_EXPIRED` errors). Set the following variables in your `.env`, hosting dashboard, or shell:

| Variable | Required | Description |
| --- | --- | --- |
| `API_ID` | ✅ | Your Telegram API ID from [my.telegram.org](https://my.telegram.org) |
| `API_HASH` | ✅ | The API hash paired with the API ID |
| `BOT_TOKEN` | ✅ | Bot token from @BotFather; regenerate if Telegram says it expired |
| `BIN_CHANNEL` | ✅ | Channel ID (prefixed with `-100`) where files are stored |
| `OWNER_ID` | ✅ | Numeric Telegram user ID used for admin operations |
| `DATABASE_URL` | optional | MongoDB/Postgres connection string for persistence |
| `SESSION_NAME` | optional | Custom Pyrogram session filename (defaults to `MegatronBot`) |
| `HAS_SSL`, `NO_PORT`, etc. | optional | Advanced hosting/network toggles |

Copy `.env.example` to `.env` (or configure your hosting provider) and fill in the required values before starting the bot.

