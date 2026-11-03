# Chrome DevTools Protocol (CDP) Reference

## Overview

Agent Browser uses CDP for browser communication, providing fine-grained control over browser behavior.

## Key Domains

### Page Domain

| Command | Description |
|---------|-------------|
| `Page.navigate` | Navigate to URL |
| `Page.reload` | Reload current page |
| `Page.captureScreenshot` | Take screenshot |
| `Page.printToPDF` | Generate PDF |
| `Page.setBypassCSP` | Bypass CSP |

### Runtime Domain

| Command | Description |
|---------|-------------|
| `Runtime.evaluate` | Execute JavaScript |
| `Runtime.callFunctionOn` | Call function on object |
| `Runtime.queryObjects` | Query JavaScript objects |

### DOM Domain

| Command | Description |
|---------|-------------|
| `DOM.getDocument` | Get DOM tree |
| `DOM.querySelector` | Find element |
| `DOM.querySelectorAll` | Find all elements |
| `DOM.getAttributes` | Get element attributes |
| `DOM.setAttributeValue` | Set attribute |

### Input Domain

| Command | Description |
|---------|-------------|
| `Input.dispatchMouseEvent` | Mouse events |
| `Input.dispatchKeyEvent` | Keyboard events |
| `Input.insertText` | Insert text |

## Event Streams

```javascript
// Subscribe to console messages
{ "method": "Runtime.consoleAPICalled", "params": {} }

// Subscribe to page errors
{ "method": "Page.javascriptDialogOpening", "params": {} }

// Subscribe to navigation
{ "method": "Page.navigationRequested", "params": {} }
```

## Error Handling

CDP returns errors with:

```json
{
  "id": 1,
  "error": {
    "code": -32601,
    "message": "Method not found"
  }
}
```

## Performance Considerations

- Batch multiple commands into single WebSocket message
- Use `Runtime.compileScript` for repeated scripts
- Disable unused domains to reduce overhead
