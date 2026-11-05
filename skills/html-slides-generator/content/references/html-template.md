# HTML Presentation Template

Reference architecture for generating slide presentations. Every presentation follows this structure.

---

## Base HTML Structure

```html
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Presentation Title</title>
  <link href="https://fonts.googleapis.com/css2?family=..." rel="stylesheet">
  <style>
    /* [viewport-base.css content here] */
    /* [custom styles here] */
  </style>
</head>
<body>
  <main class="slides">
    <section class="slide">
      <div class="slide-content">
        <!-- Slide content -->
      </div>
    </section>
    <!-- More slides... -->
  </main>

  <!-- Navigation -->
  <nav class="nav-dots">...</nav>
  <div class="progress-bar">...</div>

  <script>
    // [SlidePresentation class]
    // [Intersection Observer]
    // [Optional enhancements]
  </script>
</body>
</html>
```

---

## Required JavaScript Features

Every presentation must include:

### 1. **SlidePresentation Class** — Main controller with:
- Keyboard navigation (arrows, space, page up/down)
- Touch/swipe support
- Mouse wheel navigation
- Progress bar updates
- Navigation dots

### 2. **Intersection Observer** — For scroll-triggered animations:
- Add `.visible` class when slides enter viewport
- Trigger CSS transitions efficiently

### 3. **Optional Enhancements** (match to chosen style):
- Custom cursor with trail
- Particle system background (canvas)
- Parallax effects
- 3D tilt on hover
- Magnetic buttons
- Counter animations

### 4. **Inline Editing** (only if user opted in during Phase 1 — skip entirely if they said No):
- Edit toggle button (hidden by default, revealed via hover hotzone or `E` key)
- Auto-save to localStorage
- Export/save file functionality
- See "Inline Editing Implementation" section below

---

## Inline Editing Implementation (Opt-In Only)

**If the user chose "No" for inline editing in Phase 1, do NOT generate any edit-related HTML, CSS, or JS.**

**Do NOT use CSS `~` sibling selector for hover-based show/hide.** The CSS-only approach (`edit-hotzone:hover ~ .edit-toggle`) fails because `pointer-events: none` on the toggle button breaks the hover chain.

**Required approach: JS-based hover with 400ms delay timeout.**

### HTML:

```html
<div class="edit-hotzone"></div>
<button id="editToggle" class="edit-toggle" title="Toggle Edit Mode">
  ✏️
</button>
```

### CSS (visibility controlled by JS classes only):

```css
/* Do NOT use CSS ~ sibling selector for this!
pointer-events: none breaks the hover chain.
Must use JS with delay timeout. */
.edit-hotzone {
  position: fixed; top: 0; left: 0;
  width: 80px; height: 80px;
  z-index: 10000;
  cursor: pointer;
}
.edit-toggle {
  opacity: 0;
  pointer-events: none;
  transition: opacity 0.3s ease;
  z-index: 10001;
}
.edit-toggle.show,
.edit-toggle.active {
  opacity: 1;
  pointer-events: auto;
}
```

### JS (four interaction methods):

```javascript
// 1. Click handler on the toggle button
document.getElementById('editToggle').addEventListener('click', () => {
  editor.toggleEditMode();
});

// 2. Hotzone hover with 400ms grace period
const hotzone = document.querySelector('.edit-hotzone');
const editToggle = document.getElementById('editToggle');
let hideTimeout = null;

hotzone.addEventListener('mouseenter', () => {
  clearTimeout(hideTimeout);
  editToggle.classList.add('show');
});

hotzone.addEventListener('mouseleave', () => {
  hideTimeout = setTimeout(() => {
    if (!editor.isActive) editToggle.classList.remove('show');
  }, 400);
});

editToggle.addEventListener('mouseenter', () => {
  clearTimeout(hideTimeout);
});

editToggle.addEventListener('mouseleave', () => {
  hideTimeout = setTimeout(() => {
    if (!editor.isActive) editToggle.classList.remove('show');
  }, 400);
});

// 3. Hotzone direct click
hotzone.addEventListener('click', () => {
  editor.toggleEditMode();
});

// 4. Keyboard shortcut (E key, skip when editing text)
document.addEventListener('keydown', (e) => {
  if ((e.key === 'e' || e.key === 'E') && !e.target.getAttribute('contenteditable')) {
    editor.toggleEditMode();
  }
});
```

---

## Image Pipeline (Skip If No Images)

If user chose "No images" in Phase 1, skip this entirely. If images were provided, process them before generating HTML.

**Dependency:** `pip install Pillow`

### Image Processing (Python)

```python
from PIL import Image, ImageDraw

# Circular crop (for logos on modern/clean styles)
def crop_circle(input_path, output_path):
    img = Image.open(input_path).convert('RGBA')
    w, h = img.size
    size = min(w, h)
    left, top = (w - size) // 2, (h - size) // 2
    img = img.crop((left, top, left + size, top + size))
    mask = Image.new('L', (size, size), 0)
    ImageDraw.Draw(mask).ellipse([0, 0, size, size], fill=255)
    img.putalpha(mask)
    img.save(output_path, 'PNG')

# Resize (for oversized images that inflate HTML)
def resize_max(input_path, output_path, max_dim=1200):
    img = Image.open(input_path)
    img.thumbnail((max_dim, max_dim), Image.LANCZOS)
    img.save(output_path, quality=85)
```

| Situation | Operation |
|-----------|------------|
| Square logo on rounded aesthetic | `crop_circle()` |
| Image > 1MB | `resize_max(max_dim=1200)` |
| Wrong aspect ratio | Manual crop with `img.crop()` |

Save processed images with `_processed` suffix. Never overwrite originals.

### Image Placement

**Use direct file paths** (not base64) — presentations are viewed locally:

```html
<img src="https://raw.githubusercontent.com/..." alt="Logo" class="slide-image logo">
<img src="https://raw.githubusercontent.com/..." alt="Screenshot" class="slide-image screenshot">
```

```css
.slide-image {
  max-width: 100%;
  max-height: min(50vh, 400px);
  object-fit: contain;
  border-radius: 8px;
}
.slide-image.screenshot {
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 12px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.3);
}
.slide-image.logo {
  max-height: min(30vh, 200px);
}
```

**Adapt border/shadow colors to match the chosen style's accent.** Never repeat the same image on multiple slides (except logos on title + closing).

**Placement patterns:**
- Logo centered on title slide
- Screenshots in two-column layouts with text
- Full-bleed images as slide backgrounds with text overlay (use sparingly)

---

## Code Quality

- **Comments:** Every section needs clear comments explaining what it does and how to modify it.
- **Accessibility:** Semantic HTML should be used for proper structure and navigation.
