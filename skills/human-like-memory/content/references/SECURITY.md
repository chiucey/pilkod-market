# Security Documentation

## Transmitted Fields

### Recall/Search API

| Field | Description | Sensitivity |
|-------|-------------|-------------|
| `query` | User's search query | Medium - contains user intent |
| `user_id` | User identifier | Low - non-personal identifier |
| `agent_id` | Agent identifier | Low - system identifier |

### Save API

| Field | Description | Sensitivity |
|-------|-------------|-------------|
| `user_message` | User's message content | Variable - depends on content |
| `assistant_response` | Assistant's response | Low - generated content |
| `user_id` | User identifier | Low |
| `agent_id` | Agent identifier | Low |

### Save Batch API

| Field | Description | Sensitivity |
|-------|-------------|-------------|
| `messages` | Array of conversation messages | Variable - depends on content |
| `user_id` | User identifier | Low |
| `agent_id` | Agent identifier | Low |

## Best Practices

1. **Do NOT send**:
   - Passwords or authentication credentials
   - API keys or tokens
   - Personal identification numbers
   - Financial information
   - Medical records

2. **Only send content** you are comfortable storing on the configured memory service.

3. **User consent**: Ensure users understand their conversations may be stored when they explicitly request memory operations.

## Environment Variables

| Variable | Purpose | Required |
|----------|---------|----------|
| `HUMAN_LIKE_MEM_API_KEY` | Authentication key | Yes |
| `HUMAN_LIKE_MEM_BASE_URL` | Service endpoint | No (defaults to official service) |
| `HUMAN_LIKE_MEM_USER_ID` | User identifier | No |
| `HUMAN_LIKE_MEM_AGENT_ID` | Agent identifier | No |

## Data Retention

Data is stored on the Human-Like Memory service. Refer to their privacy policy at https://plugin.human-like.me for retention details.
