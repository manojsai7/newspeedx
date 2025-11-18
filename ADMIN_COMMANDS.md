# Admin Commands Quick Reference

## 🚫 Ban/Unban Users

```bash
# Ban a user
/ban 123456789
/ban 123456789 Spamming links

# Unban a user
/unban 123456789

# Get user details
/userinfo 123456789
```

## 📢 Force Subscribe

```bash
# Enable with username
/fsub on @your_channel

# Enable with ID
/fsub on -1001234567890

# Check status
/fsub status

# Disable
/fsub off
```

## 📊 Statistics & Info

```bash
# Total users
/status

# User details
/userinfo <user_id>

# Show all commands
/admin
```

## 📣 Broadcasting

```bash
# Reply to a message and send
/broadcast
```

## 💡 Quick Tips

### Getting User IDs:
1. Check BIN_CHANNEL when users upload files
2. Forward user's message to @userinfobot
3. Use ban/unban buttons in BIN_CHANNEL

### Force Subscribe Setup:
1. Make bot admin in channel
2. Give "Ban users" + "Invite users" permissions
3. Use `/fsub on @channel` or `/fsub on -100xxx`
4. Test with regular user account

### Ban/Unban:
- Always provide reason when banning
- Check `/userinfo` before banning
- Unban also removes channel ban
- Owner cannot be banned

## ⚠️ Important Notes

- All commands work only in bot DM
- Only bot owner can use these commands
- Commands are instant (no restart needed)
- All actions are logged in console

## 🔗 Related Files

- `admin.py` - Ban/unban/userinfo commands
- `fsub_control.py` - Force subscribe management
- `database.py` - User data storage
- `LATEST_UPDATES.md` - Detailed documentation
