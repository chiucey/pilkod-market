---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 4feec809e135efa86fbf4c2f95df86e0
    PropagateID: 4feec809e135efa86fbf4c2f95df86e0
    ReservedCode1: 3045022100cfa4fda60e8b56fe22fb7ed3bf84d302473fd0a5a48baa9a3464dd83886f0f0102200ad13d8a479ecd9fd885f95246f2edd6912de7699526a512b7f3866fe0da1ba4
    ReservedCode2: 3045022100d350a285bcadd89701f97238ff62bd91a185be04865177ba78404f088f723f83022012ce1e8d658fbe43805c43903a0b4126e70d656c48c1c547a0ff7e01e6696f0a
---

# OpenClaw Troubleshooting Guide

## Gateway Issues

### Gateway Won't Start

**Symptom**: Port already in use error

```bash
# Check what's using the port
lsof -i :18789

# Kill the process
kill -9 <PID>

# Or use a different port
openclaw gateway --port 18790
```

**Symptom**: Permission denied

```bash
# Run with proper permissions
sudo openclaw gateway --port 18789
```

### Gateway Crashes on Startup

1. Check Node.js version (requires >= 22):
   ```bash
   node --version
   ```

2. Clear cache:
   ```bash
   rm -rf ~/.openclaw/cache/*
   openclaw gateway --port 18789
   ```

3. Check logs for errors:
   ```bash
   cat ~/.openclaw/logs/openclaw.log
   ```

## Channel Issues

### WhatsApp Not Connecting

1. Logout and login again:
   ```bash
   openclaw channels logout
   openclaw channels login
   ```

2. Delete WhatsApp session:
   ```bash
   rm ~/.openclaw/sessions/whatsapp*
   openclaw channels login
   ```

3. Check allowFrom config:
   ```json
   {
     "channels": {
       "whatsapp": {
         "allowFrom": ["+1234567890"]
       }
     }
   }
   ```

### Telegram Bot Not Responding

1. Verify bot token:
   ```bash
   openclaw config show | grep telegram
   ```

2. Check webhook status:
   ```bash
   openclaw channels telegram webhook-status
   ```

3. Re-register bot:
   ```bash
   openclaw channels telegram register
   ```

### Discord Bot Offline

1. Check bot token in config
2. Verify intents are enabled in Discord Developer Portal:
   - Server Members Intent
   - Message Content Intent
3. Re-invite bot with correct permissions

## Skills Issues

### Skill Not Loading

1. Verify file location:
   ```bash
   ls ~/.openclaw/skills/<skill-name>/
   ls /skills/<skill-name>/
   ```

2. Check SKILL.md syntax:
   ```bash
   # Must have valid YAML frontmatter
   head -10 ~/.openclaw/skills/<skill-name>/SKILL.md
   ```

3. Check gating requirements:
   ```bash
   openclaw skills list --verbose
   ```

### ClawHub Install Fails

```bash
# Disable telemetry and retry
export CLAWHUB_DISABLE_TELEMETRY=1
clawhub install <skill-name>

# Check network connectivity
curl -I https://clawhub.ai
```

## Performance Issues

### High Memory Usage

1. Enable skills watcher (auto-refresh):
   ```json
   {
     "skills": {
       "load": {
         "watch": true
       }
     }
   }
   ```

2. Limit concurrent sessions:
   ```json
   {
     "sessions": {
       "maxConcurrent": 3
     }
   }
   ```

### Slow Response Times

1. Check model configuration:
   ```bash
   openclaw config show | grep model
   ```

2. Use streaming:
   ```json
   {
     "streaming": {
       "enabled": true
     }
   }
   ```

## Configuration Issues

### Config Validation Errors

```bash
# Validate current config
openclaw config validate

# Reset to defaults
mv ~/.openclaw/openclaw.json ~/.openclaw/openclaw.json.bak
openclaw onboard
```

### Environment Variables Not Loading

1. Check variable names match exactly:
   ```bash
   echo $YOUR_VAR_NAME
   ```

2. Add to shell profile:
   ```bash
   echo 'export YOUR_VAR_NAME="value"' >> ~/.bashrc
   source ~/.bashrc
   ```

## Network Issues

### Remote Access Not Working

1. Check Tailscale status:
   ```bash
   tailscale status
   ```

2. Use SSH tunnel:
   ```bash
   ssh -L 18789:localhost:18789 user@remote-host
   ```

3. Check firewall rules:
   ```bash
   sudo ufw status
   ```

## Recovery Procedures

### Full Reset

```bash
# Stop all services
openclaw stop

# Backup config
cp ~/.openclaw/openclaw.json ~/openclaw.json.bak

# Remove state
rm -rf ~/.openclaw/cache/*
rm -rf ~/.openclaw/sessions/*

# Restart
openclaw onboard
```

### Rollback Update

```bash
# Check available versions
openclaw --version

# Rollback to previous version
npm install -g openclaw@previous

# Or via git
cd ~/.openclaw
git checkout <previous-tag>
```
