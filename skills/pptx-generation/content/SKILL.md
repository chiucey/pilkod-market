---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 7ac8c289ddc1e9084ec1184ece2070c7
    PropagateID: 7ac8c289ddc1e9084ec1184ece2070c7
    ReservedCode1: 30460221009276660b0a3e91d93ff94cfad248f080fc587d154735880436214c86e0921510022100c64a3912bfc64124d3d2683b7b41e375749275175179f0f03f62d8377be50356
    ReservedCode2: 3044022077003d2de6946f8ca943736d57445ee18196fc8b4b12fa6f490647327bd5320602203ae85bc9738afe06b3305d3178fc4b94194d684e138c3539f5f0ee803652da3d
---

# PPTX Generation Skill

Generate .pptx files from structured slide content using Node.js + pptxgenjs.

## When to Use
- User asks for a PowerPoint/.pptx file
- User wants a local/installer version of a presentation
- When HTML presentation is not enough

## Workflow

### Step 1: Plan the slides
Design the slide structure first (title, sections, content). PPT should be concise:
- 1 core idea per slide
- Use bullet points, keywords, short phrases — NOT long paragraphs
- Dark theme: dark navy background + colored accent cards
- 16:9 aspect ratio (LAYOUT_16x9)

### Step 2: Install pptxgenjs (if not already)
```js
// pptxgenjs is already installed at /workspace/node_modules/pptxgenjs
// If needed: cd /workspace && npm install pptxgenjs
```

### Step 3: Write the script
Create a `.js` file in `/workspace/`, e.g. `/workspace/gen_ppt.js`

Key template structure:
```javascript
const PptxGenJS = require('pptxgenjs');
const pptx = new PptxGenJS();
pptx.layout = 'LAYOUT_16x9';
pptx.title = 'Project Name';
pptx.author = 'Your Company';

const C = {
  dark:'0F172A', blue:'3B82F6', cyan:'06B6D4',
  red:'EF4444', orange:'F97316', yellow:'EAB308',
  green:'22C55E', purple:'A855F7', white:'FFFFFF',
  gray:'94A3B8', slate:'334155', slateDark:'1E293B'
};

function bg(s){ s.background = { color: C.dark }; }
function part(s, t, col){ s.addText(t, { x:0.4, y:0.28, w:5, h:0.25, fontSize:8, color:col||C.blue, bold:true, charSpacing:3 }); }
function h1(s, t, y){ s.addText(t, { x:0.4, y:y||0.58, w:9, h:0.55, fontSize:26, bold:true, color:C.white }); }

// S1 Cover
(function(){
  var s = pptx.addSlide(); bg(s);
  // ... cover elements
})();

// S2 Table of Contents
// ... etc.

// Write output
pptx.writeFile({ fileName: '/workspace/ppt/OUTPUT_NAME.pptx' })
  .then(function(){ console.log('SUCCESS: /workspace/ppt/OUTPUT_NAME.pptx'); })
  .catch(function(err){ console.error('ERROR:', err); });
```

### Step 4: Run it
```bash
cd /workspace && node gen_ppt.js
```

### Step 5: Send file
```javascript
// Use message tool
message({ action: 'send', channel: 'feishu', filePath: '/workspace/ppt/OUTPUT_NAME.pptx' })
```

## Common Patterns

### Text element (bullet)
```javascript
s.addText('▸ 你的文字内容', { x:0.55, y:y, w:4, h:0.47, fontSize:9, color:'CBD5E1' });
```

### Card/box
```javascript
s.addShape('rect', { x:x, y:y, w:2.9, h:2.0, fill:{color:C.slateDark}, line:{color:C.blue,pt:0.5} });
```

### Colored header bar
```javascript
s.addShape('rect', { x:x, y:y, w:w, h:0.38, fill:{color:C.blue} });
s.addText('标题', { x:x, y:y, w:w, h:0.38, align:'center', fontSize:10, bold:true, color:C.white });
```

### 2-column layout
```javascript
var col = i % 2, row = Math.floor(i / 2);
var x = 0.4 + col * 4.8, y = 1.5 + row * 1.28;
```

## Tips
- Use `var` instead of `const` inside loops for closures
- Use IIFEs `(function(){ ... }());` to isolate each slide's scope
- Color warnings in output are harmless (text placed in wrong color field) — file is still valid
- Keep each slide's JS code in one `IIFE` to avoid variable conflicts
- Test with 3-4 slides first before scaling up
