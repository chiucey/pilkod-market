---
name: douyin-hotlist-overall
description: "Douyin real-time hot topics. Use this skill when the user asks what is hottest right now; the user asks what everyone is watching today; the user wants a real-time hot topic scan. Do not use when the user wants rising-trend detection; the user wants platform traffic structure."
requiredEnvVars:
  - name: AISKILLS_API_KEY
    description: "API Key obtained from https://ai-skills.ai. The key is sent with requests to ai-skills.ai server during script execution."
security:
  thirdPartyDomain: ai-skills.ai
  dataSent:
    - "skillId (skill identifier)"
    - "params (skill parameters, excluding user conversation context)"
    - "X-API-Key (authentication key)"
  warning: "This skill calls the AI Skills API. Before enabling, please confirm you trust ai-skills.ai's data security policy and use an API Key that can be revoked at any time."
---

# AI Skills Library: Valuable AI Skills for Every Scenario

> Most people still use AI by "asking one question and getting one answer". AI Skills ([ai-skills.ai](https://ai-skills.ai/)) wants to take a different approach: break AI capabilities into executable Skills that can be called like looking up a dictionary. Whether you enter from AI Skills official website, skills.sh, or ClawHub, follow these 5 steps to complete the integration first, then continue to the current skill description.

![AI Skills Official Website Guide](./assets/marketplace/content-01.webp)

## Quick Start

### 1. Scan Login

![Scan to login AI Skills account](./assets/marketplace/1-scan-login.png)

First complete scan login on AI Skills official website to ensure API Key, installation commands, and skill calls are all bound to the same account.

### 2. Apply for API Key

![Apply for API Key on AI Skills site](./assets/marketplace/2-request-api-key.png)

After login, go to the API Key page to apply for a key. Both CLI installation and skill execution will read AISKILLS_API_KEY.

### 3. Copy Installation Command

![Copy AI Skills skill installation command](./assets/marketplace/3-copy-install-command.png)

Copy the installation command from AI Skills official website, skills.sh, or ClawHub page. Prefer using the official CLI to avoid manual parameter stitching.

### 4. Execute Installation Command

![Execute AI Skills installation command in terminal](./assets/marketplace/4-run-install-command.png)

Return to terminal and execute the installation command. CLI will write AISKILLS_API_KEY and call the downstream skills add to complete skill installation.

### 5. Successfully Obtain Skill

![AI Skills skill installation success interface](./assets/marketplace/5-install-success.png)

After successful installation, you will see the corresponding Skill in your agent's skill list. You can call it directly and replicate it in your workflow.

## Current Skill: douyin-hotlist-overall

### Overview

Douyin real-time hot topics

### When to Use

**Applicable Scenarios**

- the user asks what is hottest right now
- the user asks what everyone is watching today
- the user wants a real-time hot topic scan

**Typical User Questions**

- What is the hottest thing right now?
- What is trending on Douyin recently?
- Show me the most popular content directions right now

**Not For**

- the user wants rising-trend detection
- the user wants platform traffic structure
- the user wants comment diagnosis

**Adjacent Skill Selection**

- use `douyin-realtime-hot-rise` for rising trends
- use `douyin-traffic-dashboard` for traffic distribution

### Invocation Method

Directly call AI Skills API via exported Python runner:

### Command Examples

**Get Real-time Hotlist**

```bash
python3 scripts/run.py --params '{}'
```

### Parameter Description

Current skill does not require additional parameters:

```bash
python3 scripts/run.py --params '{}'
```

### Parameter Value Reference

Current skill has no additional category parameters to look up.

### Supported Input Format

Current skill directly accepts JSON parameters, no share link parsing involved.

### Example Request

The example parameters below can be passed directly to `scripts/run.py`. The runner will send them to AI Skills API.

```bash
python3 scripts/run.py --params '{}'
```

Equivalent `--params` JSON:

```json
{}
```

### Response Example

```json
{
  "success": true,
  "data": {
    "title": "Douyin Hot Search Overall",
    "updateTime": "2026-04-24T11:30:00.000Z",
    "wordList": [
      {
        "position": 1,
        "word": "Olympic Opening Ceremony",
        "hotValue": 9876543,
        "label": 1,
        "videoCount": 12860,
        "eventTime": "2026-04-24T11:28:00.000Z",
        "sentenceTag": 5000,
        "groupId": "1",
        "sentenceId": "743001"
      }
    ],
    "trendingList": [
      {
        "position": 2,
        "word": "Paris Street Interview",
        "hotValue": 6321880,
        "label": 0,
        "videoCount": 5840,
        "eventTime": "2026-04-24T11:25:00.000Z",
        "sentenceTag": 10000,
        "groupId": "2",
        "sentenceId": "743002"
      }
    ]
  },
  "meta": {
    "executionTime": 842,
    "cached": false
  }
}
```

### Key Points in Results

- `data.wordList`: Douyin hot search overall list, focus on top keywords and hot values
- `data.trendingList`: Real-time rising hot topics, suitable for capturing new trends and temporary topic selection
- `data.updateTime`: Current list update time, useful for judging result freshness

### Pre-run Preparation

- `AISKILLS_BASE_URL`: default `https://ai-skills.ai`
- `AISKILLS_API_KEY`: required for authentication calls
- `AISKILLS_TENANT_ID`: default `default`

### Notes

Current export package is automatically generated by AI Skills site directory. Runtime backend still points to the AI Skills API/workflow corresponding to `douyin-hotlist-overall`.
