---
name: openclaw-doctor
description: Diagnose and fix OpenClaw failures, including gateway startup failures, invalid config fields, unavailable channels, and messages not receiving replies. Use this skill when the user reports that OpenClaw is unavailable, the gateway cannot start, the configuration throws errors, or a specific channel is not responding.
---

# OpenClaw Troubleshooting and Repair

## Quick Triage (First 60 Seconds)

Run the following checks in order:

```bash
openclaw status
openclaw status --all
openclaw gateway probe
openclaw gateway status
openclaw doctor
openclaw channels status --probe
openclaw logs --follow
```

**Healthy output signals** (all of the following must be true):
- `openclaw gateway status` -> shows `Runtime: running` and `RPC probe: ok`
- `openclaw gateway probe` -> `Reachable: yes` (`RPC: limited - missing scope: operator.read` is degraded diagnostics, not a connection failure)
- `openclaw channels status --probe` -> each channel shows `connected` or `ready`
- `openclaw doctor` -> no blocking config or service errors
- `openclaw logs --follow` -> no repeated fatal errors

**Routing logic**:
- **gateway not running / startup failure / config error** -> follow the "Configuration Repair" flow
- **gateway is running but messages get no reply / channel abnormality** -> follow the "Functional Issue" flow

---

## Configuration Repair Flow

### Step 1: Automatically fix known issues

```bash
openclaw doctor --yes 2>&1 | tail -60
```

Common flags (choose based on the situation):
- `--yes` - Automatically accept default prompts, suitable for general use
- `--repair` - Automatically apply recommended fixes, including restart, stronger option
- `--non-interactive` - Perform only safe migrations and skip restart/service operations, safer in CI or scripting environments
- `--deep` - Extra scan for redundant gateway installations on the system

Doctor can automatically handle field migrations, deprecated key rewrites, Auth OAuth refresh, config permission fixes, supervisor service configuration audits, and more.

### Step 2: Capture remaining errors in a structured format

```bash
openclaw config validate --json
```

### Step 3: See what doctor changed (optional)

```bash
diff ~/.openclaw/openclaw.json.bak ~/.openclaw/openclaw.json 2>/dev/null || echo "No backup"
```

### Step 4: Provide the following information to the model for analysis and repair

1. The full output of `config validate --json`
2. The current contents of `~/.openclaw/openclaw.json`
3. The diff output, if it exists, so the model does not revert doctor's fixes
4. A problem description, such as which channel is unavailable and the exact error message

> Avoid pasting the raw terminal output of `doctor` directly, because it contains ANSI color codes and too much noise for the model to parse well.

### Step 5: After the model fixes the config, restart the gateway and return the results

After the model finishes updating the configuration, immediately run the following command and return all output so the model can determine whether startup succeeded:

```bash
openclaw gateway restart 2>&1; sleep 3; openclaw gateway status 2>&1; openclaw channels status --probe 2>&1; openclaw status 2>&1; openclaw logs --limit 50 2>&1
```

Provide the full output above to the model. The model should judge it as follows:
- `Runtime: running` and `RPC probe: ok` -> gateway started successfully
- channels show `connected` / `ready` -> channels are working again
- if it still fails, continue troubleshooting with the logs output, without requiring the user to start another round

**Common startup failure log patterns**:
- `EADDRINUSE` or `another gateway instance is already listening` -> port is already in use
- `refusing to bind gateway ... without auth` -> non-local bind was configured without token/password
- `Gateway start blocked: set gateway.mode=local` -> `gateway.mode` is not set

---

## Functional Issue Flow (gateway is healthy but does not reply)

### Step 1: Check channel connectivity and pairing status

```bash
openclaw channels status --probe
openclaw pairing list --channel <channel>
```

**Common log patterns**:
- `blocked` / `allowlist` -> sender, room, or group is being filtered; check `allowFrom` / `groupAllowFrom`
- `pairing request` -> the sender has not been approved yet; wait for DM pairing approval
- `drop guild message (mention required` -> Discord guild messages require an @mention to trigger
- `not_in_channel` / `missing_scope` / `Forbidden` / `401` / `403` -> channel token permission issue

### Step 2: Check whether `baseUrl` and `apiKey` in the model config are correct

Both `baseUrl` and `apiKey` have no default values and must be configured by the user. If either is missing or mismatched, the model connection will fail.

Check the model configuration in `~/.openclaw/openclaw.json`:

```bash
grep -i "baseurl\|baseUrl\|base_url\|apiKey\|api_key" ~/.openclaw/openclaw.json
```

**Use `curl` to verify whether the `baseUrl` + `apiKey` combination works**:

First determine which protocol is in use, based on the model name prefix or the `baseUrl` domain:
- Models starting with `anthropic` or `claude-`, or `baseUrl` containing `anthropic.com` -> Anthropic protocol
- Everything else (`openai`, `minimax`, `gpt-`, `deepseek-`, etc.) -> OpenAI-compatible protocol

**OpenAI-compatible protocol (path: `/chat/completions`)**:
```bash
curl -s -o /dev/null -w "%{http_code}" \
  -X POST "<baseUrl>/chat/completions" \
  -H "Authorization: Bearer <apiKey>" \
  -H "Content-Type: application/json" \
  -d '{"model":"<model>","messages":[{"role":"user","content":"hi"}],"max_tokens":10}'
```

**Anthropic protocol (path: `/v1/messages`, with different headers)**:
```bash
curl -s -o /dev/null -w "%{http_code}" \
  -X POST "<baseUrl>/v1/messages" \
  -H "x-api-key: <apiKey>" \
  -H "anthropic-version: 2023-06-01" \
  -H "Content-Type: application/json" \
  -d '{"model":"<model>","messages":[{"role":"user","content":"hi"}],"max_tokens":10}'
```

- Returns `200` -> the `baseUrl` + `apiKey` combination is valid, so the issue is elsewhere
- Returns `401` / `403` -> the `apiKey` does not match this `baseUrl`; the key is wrong
- Returns `404` / `000` -> the `baseUrl` itself is incorrect or unreachable

**If the `curl` verification fails, the repair strategy is**: compare `~/.openclaw/openclaw.json` with recent backups (`openclaw.json.bak`, `openclaw.json.bak.1`, etc.) to find the last known working `baseUrl`, `apiKey`, and model name, then roll back only the model-related fields to those values. If no backup exists, remove the custom `baseUrl` so it returns to the default local gateway.

### Step 3: Verify model connectivity locally

Bypass the channel and talk directly to the model to confirm whether the model itself is working:

```bash
openclaw agent --agent main --message "hello, 1+1=?" --local 2>&1
```

- **Gets a normal reply** -> model connectivity is fine; the problem is in the channel config or the channel itself
- **Errors or no reply** -> model connectivity is broken; first check whether `baseUrl` was changed, and whether `apiKey` matches the `baseUrl`

### Step 4: Inspect logs to locate the exact error

```bash
openclaw logs --limit 100
openclaw logs --follow
# Show help for the logs command
openclaw logs -h
```

Provide the log output to the model for analysis.

### If it is hard to fix, use diff for a minimal rollback

Compare `~/.openclaw/openclaw.json` with recent backups such as `openclaw.json.bak`, `openclaw.json.bak.1`, and so on. Identify what changed each time, then roll back only the minimal set of changes needed to return to a working version.

---

## Post-fix Verification

```bash
openclaw doctor --yes
openclaw config validate
openclaw gateway restart
openclaw gateway status
openclaw channels status --probe
openclaw status
```

Success criteria: `Runtime: running`, `RPC probe: ok`, and every channel shows `connected` / `ready`.
