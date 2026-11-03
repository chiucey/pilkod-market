# Watermark Configuration Guide

## Watermark Options

### Enabled Options

```yaml
watermark:
  enabled: true
  text: "@your_username"  # or any custom text
  position: bottom-right  # corners
  opacity: 0.3
```

### Position Options

| Position | Description |
|----------|-------------|
| top-left | Upper left corner |
| top-right | Upper right corner |
| bottom-left | Lower left corner |
| bottom-right | Lower right corner |

### Opacity Range

- 0.1 - Very subtle (barely visible)
- 0.2 - Light (visible but not distracting)
- 0.3 - Medium (recommended default)
- 0.5 - Strong (clearly visible)
- 1.0 - Full opacity

## Watermark in Prompts

When watermark is enabled, add to each image generation prompt:

```
Include a subtle watermark "[text]" positioned at [position].
The watermark should be legible but not distracting from the main content.
```

## Examples

### Corner Watermark

```
Include a subtle watermark "@xiaohongshu_creator" positioned at bottom-right corner.
The watermark should be legible but not distracting from the main content.
```

### Semi-Transparent Logo

```
Include a small semi-transparent logo/watermark at top-left.
Watermark opacity: 30%, white text with subtle shadow.
```

## Best Practices

1. **Position**: Bottom-right is least intrusive for content
2. **Opacity**: Keep below 0.4 to avoid distraction
3. **Size**: Small enough to not compete with content
4. **Color**: Use white or theme-matching colors
5. **Content**: Username, account name, or brand mark
