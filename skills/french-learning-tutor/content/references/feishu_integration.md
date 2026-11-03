---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: "00000000000000000000000000000000"
    PropagateID: "00000000000000000000000000000000"
    ReservedCode1: 3046022100f2290db202e2d725faa00ff86a8785cc13454f625588475dbb402167005e7f8c022100c7f228bdee9843a0744ea98efa395fc649f1dd9cd8dfedac8ddd5b57b9892afa
    ReservedCode2: 3045022100b9af321399b4b81212f6222211e7b03fe8aa421c255c34467fc57c67d427350a02203b37efc29a08a555743a1c7003a67a59f056c65b166dbdba459ed05aed6db3f3
---

# Feishu Integration Guide (Feishu/Bitebot Webhook Configuration)

## 📋 Overview

This skill supports pushing French learning content to Feishu (Lark), including:
- Daily learning plan notifications
- Study reminders
- Progress reports
- Auto dialogue interaction (optional, with latency)

---

## 🔧 Configuration Steps

### Step 1: Get Feishu Webhook URL

1. **Open Feishu desktop or web version**
2. **Go to target group chat**
3. **Click Group Settings** (top right `...`)
4. **Select "Group Bots"**
5. **Click "Add Bot"**
6. **Choose "Custom Bot"**
7. **Set bot name** (e.g., French Learning Assistant)
8. **Copy Webhook URL**

> ⚠️ Important: Webhook URL format:
> `https://open.feishu.cn/open-apis/bot/v2/hook/xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx`

### Step 2: Provide Webhook URL

Send the Webhook URL to the French learning bot:

```
Please configure Feishu integration:
Webhook: https://open.feishu.cn/open-apis/bot/v2/hook/xxx...xxx
```

### Step 3: (Optional) Configure Push Time

```
Daily push time: 09:00
Timezone: Asia/Shanghai (GMT+8)
```

---

## 📱 Message Formats

### Daily Learning Card

```json
{
  "msg_type": "interactive",
  "card": {
    "header": {
      "title": {
        "tag": "plain_text",
        "content": "🎓 French Learning - Day {day}"
      },
      "color": "#3A86FF"
    },
    "elements": [
      {
        "tag": "markdown",
        "content": "**📅 Date**：{date}\n**📊 Progress**：{progress}%\n**🔥 Streak**：{streak} days"
      },
      {
        "tag": "hr"
      },
      {
        "tag": "markdown",
        "content": "**🎯 Today's Topic**：{topic}\n**⏱️ Estimated Duration**：{duration}"
      },
      {
        "tag": "action",
        "actions": [
          {
            "tag": "button",
            "text": {
              "tag": "plain_text",
              "content": "📚 Start Exercise"
            },
            "type": "primary",
            "url": "{exercise_link}"
          },
          {
            "tag": "button",
            "text": {
              "tag": "plain_text",
              "content": "🎧 Listening Practice"
            },
            "type": "default",
            "url": "{listening_link}"
          }
        ]
      },
      {
        "tag": "hr"
      },
      {
        "tag": "markdown",
        "content": "**🔄 Pending Review**：{review_count} items\n**💡 Memory Tip**：{tip}"
      },
      {
        "tag": "note",
        "elements": [
          {
            "tag": "plain_text",
            "content": "Keep going, you're making progress! 🇫🇷"
          }
        ]
      }
    ]
  }
}
```

### Review Reminder Card

```json
{
  "msg_type": "interactive",
  "card": {
    "header": {
      "title": {
        "tag": "plain_text",
        "content": "🔄 Review Reminder"
      },
      "color": "#FF9500"
    },
    "elements": [
      {
        "tag": "markdown",
        "content": "Based on the forgetting curve, the following content needs review:\n\n{review_list}"
      },
      {
        "tag": "action",
        "actions": [
          {
            "tag": "button",
            "text": {
              "tag": "plain_text",
              "content": "Start Review"
            },
            "type": "primary",
            "url": "{review_link}"
          }
        ]
      }
    ]
  }
}
```

### Learning Summary Card

```json
{
  "msg_type": "interactive",
  "card": {
    "header": {
      "title": {
        "tag": "plain_text",
        "content": "📊 Daily Learning Summary"
      },
      "color": "#34C759"
    },
    "elements": [
      {
        "tag": "markdown",
        "content": "**✅ Completion**：{completion}%\n**⏱️ Duration**：{duration} min\n**📚 New Vocabulary**：{new_words}"
      },
      {
        "tag": "hr"
      },
      {
        "tag": "markdown",
        "content": "**🎯 Key Vocabulary**：\n{words_list}"
      },
      {
        "tag": "hr"
      },
      {
        "tag": "markdown",
        "content": "**⚠️ Need Improvement**：\n{improvements}"
      },
      {
        "tag": "note",
        "elements": [
          {
            "tag": "plain_text",
            "content": "Keep it up tomorrow! 🇫🇷"
          }
        ]
      }
    ]
  }
}
```

---

## 🔄 Push Schedule

| Time | Content |
|------|---------|
| 09:00 | Daily learning plan |
| 12:00 | Review reminder (if applicable) |
| 20:00 | Learning summary/tomorrow preview |

---

## ⚠️ Limitations and Notes

### Latency Issue
> Due to Feishu API limitations, AI dialogue response may have 5-30 second latency.
> Suggestion: Use Feishu push for one-way notifications, complex dialogue still through main platform.

### Webhook Security
- Do not share Webhook URL in public places
- If leaked, reset immediately in group settings

### Message Frequency
- Feishu limits max 20 messages per minute
- This skill automatically rate-limits to avoid triggering limits

---

## 🛠️ Troubleshooting

| Problem | Solution |
|---------|----------|
| Message send failed | Check if Webhook URL is correct |
| Card display abnormal | Update Feishu client to latest version |
| No response | Check if bot is muted |
| Push delay | Feishu API rate limit, wait and retry |

---

## 🔐 Security Notes

1. **Data Storage**: Webhook URL stored in user's local config
2. **Privacy Protection**: No user learning data uploaded to third parties
3. **Notification Only**: Feishu integration only for message push, no sensitive operations

---

## 📝 Configuration Example

### Full Configuration Command

```
Configure Feishu integration:
- Webhook: https://open.feishu.cn/open-apis/bot/v2/hook/abc123...
- Push time: 09:00 daily
- Language: English

Enable features:
[✓] Daily learning plan
[✓] Review reminders
[✓] Progress reports
[ ] AI dialogue interaction (high latency, off by default)
```

### Disable Feishu

```
To disable Feishu integration, send:
"Disable Feishu push"
```

---

## 📚 Related Resources

- Feishu Open Platform: https://open.feishu.cn/
- Bot Development Docs: https://open.feishu.cn/document/ukTMukTMukTM/ucTM5YjL3ETO24yNxkjN
- Webhook Message Format: https://open.feishu.cn/document/ukTMukTMukTM/ugTN1YjL4UTN2COyUjN

---

*Last updated: 2025-01-01*