---
name: bilibili-sentiment-dashboard
description: "Bilibili short video operations growth assistant. Use this skill when the user gives a Bilibili link; the user wants comment diagnosis and follow-up suggestions. Do not use when there is no link; the user wants topic discovery."
requiredEnvVars:
  - name: AISKILLS_API_KEY
    description: "API Key obtained from https://ai-skills.ai. The key is sent with requests to ai-skills.ai server during script execution."
security:
  thirdPartyDomain: ai-skills.ai
  dataSent:
    - "params (skill parameters, including user-provided share link)"
    - "X-API-Key (authentication key)"
  warning: "This skill will send the user-provided share link to ai-skills.ai for parsing and comment analysis. Before enabling, please confirm you trust the platform's data security policy."
---

# AI Skills Library: Valuable AI Skills for Every Scenario

> Most people still use AI by "asking one question and getting one answer". AI Skills ([ai-skills.ai](https://ai-skills.ai/)) wants to take a different approach: break AI capabilities into executable Skills that can be called like looking up a dictionary.

![AI Skills Official Website Guide](./assets/marketplace/content-01.webp)

## Quick Start

### 1. Scan Login
![Scan to login AI Skills account](./assets/marketplace/1-scan-login.png)

### 2. Apply for API Key
![Apply for API Key on AI Skills site](./assets/marketplace/2-request-api-key.png)

### 3. Copy Installation Command
![Copy AI Skills skill installation command](./assets/marketplace/3-copy-install-command.png)

### 4. Execute Installation Command
![Execute AI Skills installation command in terminal](./assets/marketplace/4-run-install-command.png)

### 5. Successfully Obtain Skill
![AI Skills skill installation success interface](./assets/marketplace/5-install-success.png)

## Current Skill: bilibili-sentiment-dashboard

### Overview

Bilibili short video operations growth assistant

### When to Use

**Applicable Scenarios**

- the user gives a Bilibili link
- the user wants comment diagnosis and follow-up suggestions

**Typical User Questions**

- Help me analyze the comment section of this Bilibili video
- Show me audience sentiment and user profiles
- Give me some follow-up operational suggestions

**Not For**

- there is no link
- the user wants topic discovery
- the user wants Douyin creator research

**Adjacent Skill Selection**

- use `kuaishou-sentiment-dashboard` for Kuaishou links
- use `douyin-hotlist-overall` for Douyin hot-topic scanning

### Invocation Method

After running the script, it automatically completes three steps: parse share link, create analysis task, poll until task completion.

### Command Examples

**Analyze Bilibili Video Comments**

```bash
python3 scripts/run.py --params '{"link":"https://www.bilibili.com/video/BV1xx411c7mD"}'
```

### Parameter Description

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `link` | string | Yes | - | Share link; need to pass full accessible URL |

### Supported Input Format

Paste Bilibili share link or BV number, the following formats can be tried directly:

- `https://www.bilibili.com/video/BV1GJ411x7h7`
- `https://b23.tv/BV1GJ411x7h7`
- `BV1GJ411x7h7`

### Example Request

```bash
python3 scripts/run.py --params '{"link":"https://www.bilibili.com/video/BV1xx411c7mD"}'
```

### Response Example

```json
{
  "success": true,
  "data": {
    "task": {
      "id": "task_demo_123",
      "platform": "bilibili",
      "contentId": "7505866362912425270",
      "contentTitle": "Bilibili Operations Example",
      "status": "completed",
      "progress": 100,
      "progressMessage": "Analysis complete",
      "result": {
        "summary": {
          "analyzedComments": 168,
          "timeRange": {
            "start": "2026-04-23T00:00:00.000Z",
            "end": "2026-04-24T00:00:00.000Z"
          },
          "platform": "bilibili",
          "contentId": "7505866362912425270",
          "contentTitle": "Bilibili Operations Example",
          "analyzedAt": "2026-04-24T11:35:00.000Z"
        },
        "aiInsights": {
          "summary": "Comment section focuses more on detail proof, comparison experiments and supplementary materials.",
          "sentiment": {
            "trend": "mixed",
            "label": "Mostly positive",
            "riskLevel": "low"
          },
          "operationAdvice": [
            {
              "category": "content",
              "priority": "P1",
              "title": "Add evidence chain",
              "detail": "Supplement data sources and comparison charts to address audience needs for detail proof.",
              "reason": "Bilibili users care more about the argumentation process."
            }
          ]
        },
        "labeledComments": [
          {
            "id": "comment_1",
            "content": "Can you share the comparison data and source references you mentioned?",
            "sentiment": "positive",
            "likes": 26
          }
        ]
      }
    }
  }
}
```

### Key Points in Results

- `task.status`: Task status, `completed` means full analysis results obtained
- `task.result.summary`: Comment sample size, analysis time range, content title
- `task.result.aiInsights.summary`: One-sentence summary of comment section
- `task.result.aiInsights.operationAdvice`: Most valuable operational suggestions
- `task.result.labeledComments`: Labeled original comment samples

### Pre-run Preparation

- `AISKILLS_BASE_URL`: default `https://ai-skills.ai`
- `AISKILLS_API_KEY`: required for authentication calls
- `AISKILLS_TENANT_ID`: default `default`

### Notes

Current export package is automatically generated by AI Skills site directory.
