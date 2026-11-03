# Decision Tree

## When to Use Each Strategy

```
[User Request]
       │
       ▼
┌──────────────┐
│ Can I do    │
│ this directly?│
└──────────────┘
    │ Yes        │ No
    ▼           ▼
[Execute]   [Has similar
           │ request been
           │ seen before?]
           │ Yes      │ No
           ▼         ▼
      [Cache]    [Is this
                 │ multi-part?
                 │] Yes    │ No
                 ▼        ▼
            [Batch]  [Load
                   │ skill?
                   │] Yes   │ No
                      ▼      ▼
                 [Invoke] [Use
                        general
                        knowledge]
```

## Strategy Selection

| Scenario | Best Strategy | Why |
|----------|------------|-----|
| Same query repeated | Cache-first | Skip execution |
| Multiple similar ops | Batching | One API call |
| Simple task | Self-exec | No skill load cost |
| Complex domain | Delegate | Skill expertise |
| Multi-step workflow | Batching | Group by skill |

## Token Savings Calculator

| Approach | Cost (tokens) | Savings |
|----------|-------------|---------|
| No caching (5 skills) | 5 × 2000 = 10000 | baseline |
| Cached 3 of 5 | 2 × 2000 = 4000 | 60% |
| Batched to 2 | 2 × 2000 = 4000 | 60% |
| Best combo | 1 × 2000 = 2000 | 80% |