# Quick Koyeb Setup Guide

## 🚀 TL;DR - What You Need

**Just 5 environment variables in Koyeb dashboard:**

```env
API_ID=12345678                          # From my.telegram.org
API_HASH=your_api_hash                   # From my.telegram.org
BOT_TOKEN=1234567890:ABCdef...           # From @BotFather
BIN_CHANNEL=-1001234567890               # Your storage channel ID
OWNER_ID=123456789                       # Your Telegram user ID
```

**That's it!** No need to set FQDN, HAS_SSL, NO_PORT, or APP_NAME - they're auto-detected! ✨

---

## 📍 Where is .env File?

**There is NO .env file in this project!**

- ❌ **NOT** in your local code
- ❌ **NOT** hidden by git
- ❌ **NOT** uploaded to Koyeb
- ✅ **Environment variables are set in Koyeb dashboard**

### Why No .env File?

Because Koyeb (and Heroku) use **platform environment variables** instead of files:

```
Your Local Machine          Koyeb Platform
─────────────────          ──────────────
   .env file        ──X──>  ❌ Doesn't use .env
                            ✅ Uses dashboard variables
```

---

## 🔧 How to Set Variables in Koyeb

### Step 1: Open Koyeb Dashboard
1. Go to https://app.koyeb.com
2. Select your service (the bot)
3. Click **"Settings"** tab
4. Click **"Environment"** section

### Step 2: Add Variables
Click **"Add Variable"** button for each:

```
┌─────────────────────────────────────────┐
│ Key:   API_ID                           │
│ Value: 12345678                         │
│ ☐ Secret                                │  ← Leave unchecked
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│ Key:   API_HASH                         │
│ Value: your_api_hash_here               │
│ ☐ Secret                                │  ← Leave unchecked
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│ Key:   BOT_TOKEN                        │
│ Value: 1234567890:ABCdef...             │
│ ☑ Secret                                │  ← Check this!
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│ Key:   BIN_CHANNEL                      │
│ Value: -1001234567890                   │
│ ☐ Secret                                │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│ Key:   OWNER_ID                         │
│ Value: 123456789                        │
│ ☐ Secret                                │
└─────────────────────────────────────────┘
```

### Step 3: Save and Redeploy
- Click **"Update service"** or **"Save"**
- Koyeb will automatically redeploy your bot
- Wait 1-2 minutes for deployment

---

## 🎯 Auto-Detection Magic

The bot automatically detects and configures:

| What | Auto-Detected From | You Set |
|------|-------------------|---------|
| **Domain** | `KOYEB_PUBLIC_DOMAIN` | ❌ Nothing! |
| **HTTPS** | Koyeb platform | ❌ Nothing! |
| **Port Mapping** | Koyeb platform | ❌ Nothing! |
| **App URL** | Built automatically | ❌ Nothing! |

**Your bot will generate links like:**
```
https://your-service-your-org.koyeb.app/123/filename.mp4?hash=AbCdEf
```

No configuration needed! 🎉

---

## 🆘 Troubleshooting

### Problem: Links show `http://0.0.0.0:8000/...`

**Cause:** Koyeb hasn't injected `KOYEB_PUBLIC_DOMAIN`

**Solution:** Manually set FQDN:
```env
FQDN=your-app-name.koyeb.app
```

**How to find your domain:**
- Koyeb dashboard → Your service → Look for "Public URL"
- Copy only the domain part (without `https://`)

---

### Problem: "upstream connect error"

**Cause:** Port configuration mismatch

**Solution:**
1. Go to Koyeb → Service → Settings → **Ports**
2. Make sure:
   - **Public Port:** 80 (or 443 for HTTPS)
   - **Private Port:** 8000
   - **Protocol:** HTTP

---

### Problem: "BIN_CHANNEL validation failed"

**Cause:** Bot can't access the channel

**Solution:**
1. Open your Telegram channel
2. Add your bot: Channel → Add Members → Search bot → Add
3. Make bot admin: Channel Settings → Administrators → Add Admin → Your bot
4. Enable **"Post Messages"** permission
5. Redeploy on Koyeb

---

### Problem: Links not working (404 error)

**Cause:** BIN_CHANNEL ID is wrong

**Solution:**
1. Forward any message from your channel to [@userinfobot](https://t.me/userinfobot)
2. Copy the **"Forward from chat"** ID (starts with `-100`)
3. Update `BIN_CHANNEL` in Koyeb with correct ID
4. Must be numeric ID, not username!

---

## 📝 Optional Variables

Only set these if you need them:

```env
# Custom domain (only if not using Koyeb's default)
FQDN=files.yourdomain.com

# Custom app name (for logs)
APP_NAME=my-filebot

# Database for user tracking
DATABASE_URL=mongodb+srv://user:pass@cluster.mongodb.net/

# Force users to join your channel
UPDATES_CHANNEL=-1001234567890
```

---

## ✅ Complete Setup Checklist

- [ ] Created Telegram bot with @BotFather
- [ ] Got API credentials from my.telegram.org
- [ ] Created storage channel on Telegram
- [ ] Added bot to channel as admin with "Post Messages"
- [ ] Got channel ID from @userinfobot (starts with `-100`)
- [ ] Set 5 required variables in Koyeb dashboard
- [ ] Deployed service on Koyeb
- [ ] Checked logs - should see "Service Started"
- [ ] Tested bot with `/start` command
- [ ] Uploaded test file - received working link
- [ ] Link downloads file successfully

---

## 🎓 Understanding the System

```
User uploads file to bot
         ↓
Bot forwards to BIN_CHANNEL (storage)
         ↓
Bot generates link using:
  - Koyeb domain (auto-detected)
  - Message ID from BIN_CHANNEL
  - Secure hash for validation
         ↓
User gets link like:
https://your-app.koyeb.app/123/file.mp4?hash=AbCdEf
         ↓
When clicked, Koyeb routes to your bot's web server
         ↓
Bot fetches file from BIN_CHANNEL
         ↓
Bot streams file to user's browser
```

**Key Points:**
- ✅ All files stored in your BIN_CHANNEL
- ✅ Links are secure (hash-validated)
- ✅ Supports streaming (no full download needed)
- ✅ Works with any file type
- ✅ No file size limits (from Telegram's side)

---

## 🔗 Useful Links

- [Get API Credentials](https://my.telegram.org)
- [Create Bot](https://t.me/BotFather)
- [Get User ID](https://t.me/userinfobot)
- [Get Channel ID](https://t.me/RawDataBot)
- [Koyeb Dashboard](https://app.koyeb.com)
- [GitHub Repo](https://github.com/manojsai7/newspeedx)

---

## 💡 Pro Tips

1. **Use a private channel** for BIN_CHANNEL (more secure)
2. **Enable DATABASE_URL** to track user statistics
3. **Set UPDATES_CHANNEL** to grow your channel
4. **Monitor Koyeb logs** to debug issues
5. **Keep BOT_TOKEN secret** - mark as "Secret" in Koyeb

---

Need help? Check the main [README.md](README.md) or open an issue on GitHub!
