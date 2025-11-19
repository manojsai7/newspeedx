# Keepalive Configuration for Koyeb

## Problem
Koyeb puts instances into "deep sleep" after **300 seconds (5 minutes)** of no HTTP traffic, causing the bot to stop.

## Solution
The bot now automatically pings itself at regular intervals to prevent sleep on both Heroku and Koyeb platforms.

## Configuration

### Environment Variable
```bash
PING_INTERVAL=240  # Ping interval in seconds (default: 240s = 4 minutes)
```

### Recommended Settings

| Platform | Sleep After | Recommended PING_INTERVAL | Why |
|----------|-------------|---------------------------|-----|
| **Koyeb** | 300s (5min) | `240` (4 minutes) | Ping before the 5-minute threshold |
| **Heroku Free** | Never | `1200` (20 minutes) | Just for health monitoring |
| **Local/VPS** | Never | Not needed | No sleep mechanism |

### How It Works

1. **Automatic Detection**: The bot detects if running on Koyeb via `KOYEB_PUBLIC_DOMAIN` or `KOYEB_DEPLOYMENT_ID` environment variables
2. **Keepalive Service**: Starts automatically on Heroku and Koyeb platforms
3. **Self-Ping**: Makes HTTP GET request to `https://your-app.koyeb.app/` every `PING_INTERVAL` seconds
4. **Prevents Sleep**: Keeps the instance active by generating traffic

### Modified Files
- `Megatron/__main__.py` - Changed condition from `if Var.ON_HEROKU:` to `if Var.ON_HEROKU or Var.ON_KOYEB:`
- `Megatron/vars.py` - Changed default `PING_INTERVAL` from 1200s to 240s

### Logs to Expect
When keepalive is active, you'll see:
```
------------------ Starting Keep Alive Service ------------------
                        ping interval =>> 240s
```

Every 4 minutes:
```
2025-11-19 10:39:00,000 - root - INFO - Pinged server with response: 200
```

### Custom Configuration
If you need to adjust the ping interval, set it in your Koyeb environment variables:

```bash
# Ping every 3 minutes (more aggressive)
PING_INTERVAL=180

# Ping every 4.5 minutes (balanced)
PING_INTERVAL=270

# Ping every 2 minutes (most aggressive, prevents any sleep)
PING_INTERVAL=120
```

⚠️ **Important**: Keep `PING_INTERVAL` **less than 300 seconds** for Koyeb to prevent deep sleep!

### Troubleshooting

**Issue**: Bot still goes to sleep
- **Solution**: Reduce `PING_INTERVAL` to 120-180 seconds

**Issue**: Too many ping requests
- **Solution**: Increase `PING_INTERVAL` but keep it under 300 seconds

**Issue**: `Couldn't connect to the site URL..!` in logs
- **Solution**: Check that `FQDN` or `KOYEB_PUBLIC_DOMAIN` is correctly set in environment variables
