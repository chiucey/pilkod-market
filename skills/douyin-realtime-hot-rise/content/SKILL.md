---
name: douyin-realtime-hot-rise
description: "Douyin rising hot topics topic selector assistant. Use this skill when the user asks what to post next; the user asks which topics are rising; the user wants growth-oriented topic selection. Do not use when the user wants the absolute hottest list right now; the user wants benchmark accounts or creators."
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

## Current Skill: douyin-realtime-hot-rise

### Overview

Douyin rising hot topics topic selector assistant

### When to Use

**Applicable Scenarios**

- the user asks what to post next
- the user asks which topics are rising
- the user wants growth-oriented topic selection

**Typical User Questions**

- What content will get traffic recently?
- What rising hot topics are on Douyin this week?
- For parenting / beauty / career content, what topics should I follow recently?

**Not For**

- the user wants the absolute hottest list right now
- the user wants benchmark accounts or creators
- the user wants comment analysis

**Adjacent Skill Selection**

- use `douyin-hotlist-overall` for "what is hottest right now"
- use `douyin-traffic-dashboard` for "where traffic is flowing"

### Invocation Method

Directly call AI Skills API via exported Python runner:

### Command Examples

**Follow Hot Topics by Keyword**

```bash
python3 scripts/run.py --params '{"keyword":"Olympic Games","order":"rank_diff"}'
```

**View Hot Topics by Category**

```bash
python3 scripts/run.py --params '{"tag":"5000","order":"rank"}'
```

### Parameter Description

| Parameter | Type | Required | Default | Description |
| --- | --- | --- | --- | --- |
| `order` | string | No | `rank` | Sort method; options: heat sort (`rank`), change sort (`rank_diff`) |
| `tag` | string | No | - | Hot topic category tag, pass numeric id or comma-separated id combinations. Runtime follows the latest category interface. Current default mapping can be referenced in x-direction-map. See below for `tag` value reference |
| `keyword` | string | No | - | Search term |

For complete machine-readable parameter structure, see `references/form-schema.json`.

### Tag Value Reference

#### `tag`

Field description: Hot topic category

| Tag | Value |
| --- | --- |
| Entertainment | `2001,2002,2003,2004,2005,2006,2007,2008,2012` |
| Gaming | `12000,12001` |
| Anime | `13000` |
| Music | `29000,29001` |
| Dance | `28000,28001` |
| Drama | `18000` |
| Looks | `30000` |
| Food | `9000` |
| Travel | `10000` |
| Pets | `8000` |
| Fashion | `16000` |
| Sports | `5000` |
| Automotive | `11000` |
| Home & Living | `17000,17001` |
| Parenting | `19000` |
| Relationships | `23000` |
| Tech | `6000` |
| Finance | `7000` |
| Education | `14000,14001` |
| Health | `15000` |
| Humanities | `24000` |
| Law | `27000` |
| Career | `26000` |
| Society | `4003,4005` |
| Current Affairs | `3001,3002` |
| Military | `21000` |
| Platform Activities | `1001,1002,1003` |
| Topic Interaction | `20002,20003,20005` |
| Talent | `25000` |
| Agriculture | `22000` |
| Outdoor Sports | `31000` |
| Senior Living | `32000` |

### Supported Input Format

Current skill directly accepts JSON parameters, no share link parsing involved.

### Example Request

The example parameters below can be passed directly to `scripts/run.py`. The runner will send them to AI Skills API.

```bash
python3 scripts/run.py --params '{"keyword":"Olympic Games","order":"rank_diff"}'
```

Equivalent `--params` JSON:

```json
{
  "keyword": "Olympic Games",
  "order": "rank_diff"
}
```

### Response Example

```json
{
  "success": true,
  "data": {
    "title": "Douyin Real-time Rising Hot Topics",
    "updateTime": "2026-04-24T11:30:00.000Z",
    "pagination": {
      "page": 1,
      "pageSize": 30,
      "total": 100
    },
    "items": [
      {
        "rank": 1,
        "rankDiff": 12,
        "keyword": "Olympic Opening Ceremony",
        "id": 1234567890,
        "hotScore": 9876543,
        "videoCount": 1860,
        "tagId": 5000,
        "tagName": "Sports",
        "trends": [
          {
            "time": "10:00",
            "score": 6320000
          },
          {
            "time": "11:00",
            "score": 9876543
          }
        ],
        "createdAt": "2026-04-24T11:20:00.000Z"
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

- `data.items`: Hot topic entry list, focus on `keyword`, `rankDiff`, `tagName`
- `data.pagination`: Current returned page number, page size, and total count information
- `item.trends`: Time series of hot topic scores, suitable for judging whether it continues to rise

### Pre-run Preparation

- `AISKILLS_BASE_URL`: default `https://ai-skills.ai`
- `AISKILLS_API_KEY`: required for authentication calls
- `AISKILLS_TENANT_ID`: default `default`

### Notes

Current export package is automatically generated by AI Skills site directory. Runtime backend still points to the AI Skills API/workflow corresponding to `douyin-realtime-hot-rise`.
