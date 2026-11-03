---
name: th-b-web-ui-skill
description: Generate enterprise backend web UI prototypes with restrained, professional design patterns. Use when users ask to create admin dashboards, list pages, detail pages, search forms, dialogs, drawers, tables, tabs, or any frontend mockups that should look like an internal enterprise system rather than consumer apps. Triggers: "后台原型", "企业界面", "管理页面", "admin UI", "企业后台", "内部系统风格", "web UI".
---

# TH B UI Skill

Generate prototypes that feel like a mature internal business system rather than a generic consumer app.

Treat this skill as a design-rules layer. Reproduce the structure, density, hierarchy, naming habits, and component selection patterns of the internal system.

## Workflow

Follow this sequence:

1. **Identify the page type** - Determine if it's a list page, detail page, form page, drawer, or dashboard
2. **Infer the dominant component pattern** - Match the request to the appropriate page pattern
3. **Apply the layout and density rules** - Use the rules defined in this skill
4. **Generate the prototype** - Output in the requested format (mockup description, Figma prompt, or code)
5. **Self-check** - Verify the result still feels like an internal enterprise UI

If requirements are incomplete, infer the most likely enterprise pattern:

| Missing Info | Default Pattern |
|-------------|-----------------|
| List page | Search area + action area + data table + pagination |
| Detail page | Summary header + sectioned blocks + related tabs |
| Form page | Form sections + sticky actions + validation hints |
| Dialog workflow | Compact form + clear primary action + cancel path |
| Dashboard | Restrained cards + summary metrics + filters + table |

## Naming Semantics

Use these naming families to organize UI components:

### Base Family
Foundational components for page construction:
- `Base*`: layout containers, forms, tables, drawers, modals, tabs, pagination, selectors, date pickers, tags, cards

### Business Family
Domain-aware components:
- `Business*`: specialized selectors, organization selectors, location selectors, resource selectors, category selectors

### Standard* Family
Configuration-driven standardized blocks:
- Standardized search forms, tables, button groups, fixed footer actions

Mental model:
- Use `Base*` for foundational containers or interaction primitives
- Use `Business*` when pages benefit from domain-aware selectors
- Use `Standard*` when pages should feel strongly standardized and repetitive

## Layout Rules

Prefer calm, structured, rectangular layouts:

- **Clear top-to-bottom hierarchy**
- **Group controls into containers with obvious boundaries**
- **Prefer**: card, panel, table, form, tab, drawer, modal patterns
- **Avoid**: hero sections, marketing banners, oversized illustrations, playful landing-page patterns

### List Page Structure
1. Page title and primary action
2. Search/filter panel
3. Batch or row-level actions
4. Main data table
5. Pagination and totals

### Form Page Structure
1. Page title and status
2. Sectioned form groups
3. Inline validation or helper text
4. Sticky or clearly separated footer actions

## Visual Rules

Use restrained enterprise styling:

- **Neutral backgrounds**, white panels, subtle borders
- **One accent color** for primary actions and interaction focus
- **Semantic colors** for status (success, warning, error, info)
- **Clear button hierarchy**: primary → secondary → tertiary/danger
- **Compact spacing** with consistent rhythm

### Color Palette
| Element | Style |
|---------|-------|
| Background | Very light neutral |
| Panel | White or near-white |
| Primary text | Dark neutral |
| Secondary text | Medium neutral |
| Border | Light neutral |
| Primary action | One accent color |
| Status | Semantic colors only |

### Interaction Patterns
| Pattern | Use Case |
|---------|----------|
| Drawer | Quick create, quick edit, side-panel inspection |
| Modal | Confirmation and short tasks |
| Tabs | Peer content sections |
| Pagination | Predictable and persistent navigation |
| Status tags | Concise lifecycle state display |

## Page Patterns

### List Page
**Default sections:** Title + primary action → Filter panel → Secondary actions → Data table → Pagination

**Typical filters:** keyword, business type, status, owner, date range

**Typical columns:** name, code, category, status, owner, updated time, actions

### Detail Page
**Default sections:** Title + status + actions → Summary card → Basic information block → Related records/tabs → Operation log

### Create/Edit Page
**Default sections:** Title + context → Grouped form sections → Inline validation → Footer actions

### Drawer Flow
**Use for:** Quick create, quick edit, side-panel inspection

**Structure:** Drawer container → Compact form body → Limited fields → Sticky footer with primary/secondary actions

### Dashboard
**Use cautiously** - Keep it operational

**Default sections:** Title + global filters → Small summary cards → Supporting charts → Operational table/alerts

## Code Generation Guidance

When generating frontend code (HTML, Vue, React):

- Use neutral color surfaces
- Implement compact forms with clear labels
- Create clear button hierarchy
- Include loading, empty, and error states
- Use status tags/indicators for lifecycle states
- Keep tables stable with predictable interactions

## Prompt Examples

```
请用 $th-b-web-ui-skill 生成一个资源管理列表页原型。
要求：
- 页面结构贴近内部后台系统
- 顶部使用标准筛选区结构
- 中间使用标准数据表格式区域
- 状态使用标签式方式表达
- 操作区保持企业后台风格，紧凑、规整
```

```
Create a desktop admin form page with grouped sections, compact labels, and a stable footer action area.
```

## References

See `/references/` directory for detailed specifications:
- `page-patterns.md` - Page templates and prompt snippets
- `ui-spec.md` - Colors, buttons, forms, tables, spacing rules
- `internal-mapping.md` - Component naming and mapping
