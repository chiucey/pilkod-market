---
name: lambda
description: Remotion Lambda cloud rendering, serverless batch video generation.
tags: lambda, cloud, aws, serverless, deploy
---

# Remotion Lambda Cloud Rendering

## Deploy

```bash
npm install @remotion/lambda
export AWS_ACCESS_KEY_ID=xxx
export AWS_SECRET_ACCESS_KEY=xxx
export AWS_REGION=us-east-1
npx remotion lambda deploy
```

## Render

```bash
# List deployed sites
npx remotion lambda sites ls

# Render to S3
npx remotion lambda render \
  --site-name=my-site-123 \
  --composition-id=MyVideo \
  --out-mp4=output.mp4 \
  --props='{"title":"Hello"}'
```

## Notes

- Lambda has timeout limits (split large videos)
- S3 bucket needs CORS configured
- Rendered files auto-upload to S3 path
