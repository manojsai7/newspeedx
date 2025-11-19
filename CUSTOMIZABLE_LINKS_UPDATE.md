# Customizable Links & Environment Variables Update

**Date**: November 19, 2025  
**Version**: 2.0.0  
**Type**: Feature Enhancement + Configuration Overhaul

---

## 🎯 What's New

### ✨ Customizable Links Feature

All channel and donation links are now **fully customizable via environment variables**! No more hardcoded links in the bot code.

**New Environment Variables:**
```env
UPDATES_CHANNEL_LINK=https://t.me/+_J90-7N-lk9iNDZl
DONATION_LINK=https://t.me/YourBot?start=donate
SUPPORT_LINK=https://t.me/+_J90-7N-lk9iNDZl
```

**Benefits:**
- ✅ Easy rebranding without code changes
- ✅ Update links by just changing env vars
- ✅ Perfect for multiple bot instances
- ✅ Professional deployment flexibility

---

## 📝 Changes Made

### 1. **Code Updates**

#### `Megatron/vars.py`
```python
# Added new customizable link variables
UPDATES_CHANNEL_LINK = _optional("UPDATES_CHANNEL_LINK", "https://t.me/+_J90-7N-lk9iNDZl")
DONATION_LINK = _optional("DONATION_LINK", "https://t.me/TG_FatherBoT?start=donate")
SUPPORT_LINK = _optional("SUPPORT_LINK", "https://t.me/+_J90-7N-lk9iNDZl")
```

#### `Megatron/bot/plugins/start.py`
- Updated `_home_keyboard()` to use `Var.UPDATES_CHANNEL_LINK` and `Var.DONATION_LINK`
- Replaced hardcoded URLs with environment variable references

#### `Megatron/utils/callbacks.py`
- Updated `_home_keyboard()` to use `Var.UPDATES_CHANNEL_LINK` and `Var.DONATION_LINK`
- Replaced hardcoded URLs with environment variable references

### 2. **New Documentation Files**

#### `ENV_VARIABLES_GUIDE.md` ⭐ NEW
- Comprehensive guide for all environment variables
- Step-by-step setup instructions for each variable
- Platform-specific deployment guides (Koyeb, Heroku, Local, Docker)
- Troubleshooting section
- Getting started tutorials (MongoDB, Channel ID, etc.)
- Security best practices

#### `koyeb.env.example` ⭐ NEW
- Simplified `.env` template for Koyeb deployment
- Contains only essential variables
- Optimized for quick Koyeb "File Upload" deployment
- Cleaner format with clear sections

#### `.env.example` (Updated)
- Complete template with all available variables
- Added new customizable link variables
- Updated PING_INTERVAL default to 240 (Koyeb optimized)
- Added Koyeb deployment instructions
- Categorized all variables for easier understanding

#### `README.md` (Updated)
- Added "Customizable Links & Branding" section
- Added quick links to new documentation
- Added "Environment File Templates" section
- Updated PING_INTERVAL default from 1200 to 240
- Added instructions for Koyeb file upload method

---

## 🚀 How to Use

### For New Deployments:

**Option 1: Koyeb File Upload (Recommended)**
```bash
1. Copy koyeb.env.example to .env
2. Edit your values in .env
3. Koyeb Dashboard → Service → Settings → Environment Variables
4. Select "File" option → Upload .env → Select "Plain Text" format
5. Deploy!
```

**Option 2: Manual Variable Entry**
```bash
1. Use .env.example as reference
2. Add variables one by one in Koyeb dashboard
3. Deploy!
```

### For Existing Deployments:

**To Update Links Only:**
```bash
1. Add these new variables to your environment:
   UPDATES_CHANNEL_LINK=https://t.me/your_channel
   DONATION_LINK=https://t.me/your_payment_link
   SUPPORT_LINK=https://t.me/your_support

2. Restart bot (automatic on Koyeb when vars change)
```

**Full Migration:**
```bash
1. Download current env vars or note them down
2. Copy koyeb.env.example
3. Fill in your existing values
4. Add new link variables
5. Upload as file or update manually
6. Deploy
```

---

## 🎨 Customization Examples

### Example 1: Personal Bot
```env
UPDATES_CHANNEL_LINK=https://t.me/+ABC123xyz
DONATION_LINK=https://www.paypal.me/yourname
SUPPORT_LINK=https://t.me/+ABC123xyz
```

### Example 2: Business Bot
```env
UPDATES_CHANNEL_LINK=https://t.me/CompanyUpdates
DONATION_LINK=https://buy.stripe.com/xyz123
SUPPORT_LINK=https://t.me/CompanySupport
```

### Example 3: Community Bot
```env
UPDATES_CHANNEL_LINK=https://t.me/joinchat/xyz123
DONATION_LINK=https://ko-fi.com/community
SUPPORT_LINK=https://t.me/CommunityHelp
```

---

## 📊 Variable Reference

### New Variables (Optional)

| Variable | Type | Default | Description |
|----------|------|---------|-------------|
| `UPDATES_CHANNEL_LINK` | URL | `https://t.me/+_J90-7N-lk9iNDZl` | Updates channel button link |
| `DONATION_LINK` | URL | `https://t.me/TG_FatherBoT?start=donate` | Donate button link |
| `SUPPORT_LINK` | URL | `https://t.me/+_J90-7N-lk9iNDZl` | Support contact link |

### Updated Defaults

| Variable | Old Default | New Default | Reason |
|----------|-------------|-------------|--------|
| `PING_INTERVAL` | 1200 (20 min) | 240 (4 min) | Koyeb sleeps after 5min; 4min ping prevents it |

---

## 🔄 Migration Path

### From Hardcoded Links → Environment Variables

**Before** (Hardcoded in code):
```python
InlineKeyboardButton("✵ Updates Channel ✵", url="https://t.me/+uW4Saio7cmYwNjk1")
```

**After** (From environment):
```python
InlineKeyboardButton("✵ Updates Channel ✵", url=Var.UPDATES_CHANNEL_LINK)
```

**Result**: Change link anytime by just updating env var!

---

## ✅ Testing Checklist

After deployment, verify:

- [ ] Bot starts successfully
- [ ] `/start` command shows correct updates channel link
- [ ] `/start` command shows correct donation link
- [ ] Buttons are clickable and lead to correct URLs
- [ ] Links work in all bot messages
- [ ] Force subscribe works (if enabled)
- [ ] Database connection successful
- [ ] File upload/download works

---

## 📚 Documentation Structure

```
newspeedx/
├── .env.example              ← Full template with all options
├── koyeb.env.example         ← Simplified Koyeb template (NEW!)
├── ENV_VARIABLES_GUIDE.md    ← Complete configuration guide (NEW!)
├── README.md                 ← Updated with new sections
├── KOYEB_SETUP.md           ← Existing Koyeb deployment guide
└── PERFORMANCE_IMPROVEMENTS.md ← Previous performance fixes
```

---

## 🔒 Security Notes

### What to Keep Private:
- ❌ `BOT_TOKEN`
- ❌ `API_HASH`
- ❌ `DATABASE_URL`
- ❌ `APP_SECRET`
- ❌ `.env` file (add to `.gitignore`)

### Safe to Share:
- ✅ `UPDATES_CHANNEL_LINK` (public anyway)
- ✅ `DONATION_LINK` (meant to be public)
- ✅ `SUPPORT_LINK` (public support contact)

---

## 💡 Pro Tips

1. **Use Koyeb File Upload**: Fastest way to deploy with all vars
2. **Keep Backup**: Save your `.env` file securely offline
3. **Version Control**: Use different `.env` files for staging/production
4. **Link Shorteners**: Use bit.ly/tinyurl for cleaner donation links
5. **Testing**: Always test links after changing env vars

---

## 🐛 Troubleshooting

### Issue: Links still showing old hardcoded URLs

**Solution**: 
```bash
1. Clear any browser cache
2. Restart bot service completely
3. Verify env vars are actually set in platform
4. Check spelling of variable names (case-sensitive!)
```

### Issue: "Missing required environment variable"

**Solution**:
```bash
Only these are REQUIRED:
- API_ID
- API_HASH
- BOT_TOKEN
- OWNER_ID
- BIN_CHANNEL
- DATABASE_URL

New link variables are OPTIONAL (have defaults)
```

### Issue: Buttons not updating

**Solution**:
```bash
1. Environment changes require bot restart
2. On Koyeb: Auto-restarts when env changes
3. Manually: Stop → Update Vars → Start
4. Clear Telegram cache: Settings → Data → Clear Cache
```

---

## 🎉 Summary

This update makes your bot **infinitely more flexible** for:
- ✅ Multiple instances with different branding
- ✅ Easy channel/link changes without code edits
- ✅ Professional deployment workflows
- ✅ Better configuration management
- ✅ Simplified Koyeb deployment

**Backwards Compatible**: If you don't set the new variables, defaults are used automatically!

---

## 📞 Support

- 📖 **Full Guide**: [ENV_VARIABLES_GUIDE.md](ENV_VARIABLES_GUIDE.md)
- 🚀 **Koyeb Setup**: [KOYEB_SETUP.md](KOYEB_SETUP.md)
- 📋 **Main Docs**: [README.md](README.md)
- 🐛 **Issues**: GitHub Issues
- 💬 **Community**: Your configured SUPPORT_LINK

---

**Made with ❤️ for easier bot deployment and management**
