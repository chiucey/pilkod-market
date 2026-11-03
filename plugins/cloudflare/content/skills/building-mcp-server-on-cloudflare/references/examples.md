# Project Bootstrapping

Instructions for creating new MCP server projects.

---

## Create Commands

Execute in terminal to generate a new project:

**Without authentication:**

```bash
npm create cloudflare@latest -- my-mcp-server \
  --template=cloudflare/ai/demos/remote-mcp-authless
```

**With GitHub login:**

```bash
npm create cloudflare@latest -- my-mcp-server \
  --template=cloudflare/ai/demos/remote-mcp-github-oauth
```

**With Google login:**

```bash
npm create cloudflare@latest -- my-mcp-server \
  --template=cloudflare/ai/demos/remote-mcp-google-oauth
```

---

## Additional Boilerplate Locations

**Main repository:** `github.com/cloudflare/ai` (check demos directory)

Other authentication providers:
- Auth0
- WorkOS AuthKit
- Logto
- Descope
- Stytch

**Cloudflare tooling:** `github.com/cloudflare/mcp-server-cloudflare`

---

## Selection Matrix

| Goal | Boilerplate |
|------|-------------|
| Testing/learning | authless |
| GitHub API access | github-oauth |
| Google API access | google-oauth |
| Enterprise auth | auth0 / authkit |
| Slack apps | slack-oauth |
| Zero Trust | cf-access |

---

## Platform Documentation

- developers.cloudflare.com/agents/model-context-protocol/
- developers.cloudflare.com/agents/guides/remote-mcp-server/
- developers.cloudflare.com/agents/guides/test-remote-mcp-server/
- developers.cloudflare.com/agents/model-context-protocol/authorization/

---

## Commands Reference

**Local execution:**

```bash
cd my-mcp-server
npm install
npm start
# Accessible at http://localhost:8788/mcp
```

**Production push:**

```bash
npx wrangler deploy
# Accessible at https://[worker-name].[subdomain].workers.dev/mcp
```

**MCP client setup:**

Use a client supporting Streamable HTTP and the generated server's authentication. Test the actual deployed endpoint with Inspector below. This is a separate connection from the official Cloudflare App; see the [Pilkod guide](../../cloudflare/references/minimax-connection.md).

**Inspector testing:**

```bash
npx @modelcontextprotocol/inspector@latest
# Launch browser at http://localhost:5173
# Input your server URL: http://localhost:8788/mcp
```

---

## Help Channels

- Cloudflare Discord
- GitHub discussions on cloudflare/ai repository
