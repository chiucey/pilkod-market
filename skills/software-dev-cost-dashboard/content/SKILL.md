---
name: software-dev-cost-dashboard
description: "Software cost estimation dashboard. Use this skill when the user asks for software project cost estimation; the user wants a budget or quote planning dashboard; the user can continue in the external web app. Do not use when the user expects an API-executable agent skill; the user wants Douyin / Xiaohongshu / Bilibili / Kuaishou content analysis."
requiredEnvVars: []
security:
  thirdPartyDomain: soft.ai-skills.ai
  dataSent:
    - "Content input by the user directly in the browser at https://soft.ai-skills.ai (skill itself does not pass data through exported runner)"
  warning: "This skill is in external-link mode and does not call API directly via exported runner. Please confirm the target site's data security and privacy policy before accessing."
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

## Current Skill: software-dev-cost-dashboard

### Overview

Software cost estimation dashboard

### When to Use

**Applicable Scenarios**

- the user asks for software project cost estimation
- the user wants a budget or quote planning dashboard
- the user can continue in the external web app

**Typical User Questions**

- How much will this software project cost roughly?
- Help me evaluate the development cost
- I need a project budget dashboard

**Not For**

- the user expects an API-executable agent skill
- the user wants Douyin / Xiaohongshu / Bilibili / Kuaishou content analysis

**Adjacent Skill Selection**

- use the executable social-media skills for traffic, hot-topic, creator, and comment-analysis tasks

### Invocation Method

Current skill is in external-link mode. Please directly access [https://soft.ai-skills.ai](https://soft.ai-skills.ai) to complete the operation.

### Command Examples

Current skill is not called directly via `python3 scripts/run.py`. Please directly access [https://soft.ai-skills.ai](https://soft.ai-skills.ai).

### Parameter Description

Current skill does not pass parameters through local runner. Complete input and operations directly on the target site.

### Parameter Value Reference

Current skill has no additional category parameters to look up.

### Supported Input Format

Current skill does not parse local JSON parameters. Please directly access [https://soft.ai-skills.ai](https://soft.ai-skills.ai) to complete subsequent operations.

### Example Request

Current skill is in external-link mode and CLI request examples are not applicable. Please directly access [https://soft.ai-skills.ai](https://soft.ai-skills.ai).

### Response Example

```json
{
  "success": true,
  "data": {
    "invocationMode": "external-link",
    "externalLink": "https://soft.ai-skills.ai",
    "externalLinkLabel": "Software Development Cost Out of Control?",
    "message": "Open this external-link target to continue."
  }
}
```

### Key Points in Results

- `data.externalLink`: External site entry, open to continue using the skill
- `data.externalLinkLabel`: Display name on target site for easy identification of jump target in marketplace

### Pre-run Preparation

- Current skill does not depend on local API Key environment variables

### Notes

Current export package is automatically generated by AI Skills site directory. Runtime backend still points to the AI Skills API/workflow corresponding to `software-dev-cost-dashboard`.
