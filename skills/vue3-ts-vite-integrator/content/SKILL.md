---
name: vue3-ts-vite-integrator
description: Use this skill when users want to develop projects based on Vue3 + TypeScript + Vite. Applicable scenarios include: automatically generating or modifying TypeScript interfaces and type definitions based on backend entity classes (such as DTO/Model from Java/Python/Go); adjusting frontend component props, emits, and business logic based on data models; optimizing existing page interaction logic and performance; beautifying page styles and user experience. This skill is triggered when users mention keywords like "backend entity class", "DTO", "data model", "modify frontend logic", "optimize page", or "beautify interface".
---

# Vue3 + TypeScript + Vite Project Integration Assistant

## Core Capabilities

This skill helps developers modify frontend logic, optimize page interactions, and beautify user interfaces based on Vue3 + TypeScript + Vite projects, using backend entity classes as references.

## Workflow

### Phase 1: Project Analysis

**Objective**: Comprehensively understand the project structure and backend data models.

**Steps**:

1. **Project Structure Scanning**
   - Identify the project directory structure (src/components, src/views, src/api, src/types, etc.)
   - Confirm the UI framework in use (Element Plus, Ant Design Vue, Naive UI, Tailwind CSS, etc.)
   - Analyze the location of existing TypeScript type definition files

2. **Backend Entity Class Parsing**
   - If users provide backend code, extract field definitions from all entity classes
   - Identify field types (string, number, boolean, array, date, enum, etc.)
   - Analyze field validation rules and constraints
   - Identify relationships between entities (OneToMany, ManyToOne, etc.)

3. **Existing Frontend Type Mapping**
   - Find existing TypeScript interfaces/type definitions
   - Analyze API request and response data structures
   - Identify fields that need synchronization

### Phase 2: Type Definition Generation

**Objective**: Convert backend entity classes to TypeScript type definitions.

**Steps**:

1. **Type Mapping Rules**
   - Java to TypeScript mapping:
     - `String` → `string`
     - `Integer`/`Long`/`Double` → `number`
     - `Boolean` → `boolean`
     - `List<T>` → `T[]`
     - `LocalDateTime`/`Date` → `string` (ISO format)
     - `BigDecimal` → `number`

   - Python to TypeScript mapping:
     - `str` → `string`
     - `int`/`float` → `number`
     - `bool` → `boolean`
     - `List[T]` → `T[]`
     - `datetime` → `string`

   - Go to TypeScript mapping:
     - `string` → `string`
     - `int`/`float64` → `number`
     - `bool` → `boolean`
     - `[]T` → `T[]`
     - `time.Time` → `string`

2. **Generate TypeScript Types**
   - Create complete interface definitions
   - Add optional field markers
   - Generate generic constraints
   - Create necessary enum types

3. **Validation and Optimization**
   - Ensure type definitions fully correspond to backend entities
   - Add reasonable JSDoc comments
   - Export all required types

### Phase 3: Frontend Logic Modification

**Objective**: Adjust frontend code based on new type definitions and business requirements.

**Steps**:

1. **API Layer Adjustment**
   - Update API request parameter types
   - Adjust API response type parsing
   - Add necessary type conversion logic

2. **Component Props and Emits**
   - Update component Props type definitions
   - Adjust Emits type constraints
   - Optimize props validation logic

3. **Business Logic Refactoring**
   - Adjust business logic based on new data models
   - Update form validation rules
   - Adjust data processing and transformation logic

4. **State Management Update**
   - If using Pinia/Vuex, update Store State types
   - Adjust Getter return types
   - Update Mutations/Actions parameter types

### Phase 4: Page Optimization

**Objective**: Improve page performance, usability, and user experience.

**Steps**:

1. **Logic Optimization**
   - Use `computed` instead of redundant `ref` dependencies
   - Optimize `watch` dependencies to reduce unnecessary updates
   - Use `shallowRef` for large arrays/objects reactivity
   - Add appropriate `v-memo` to reduce unnecessary re-renders
   - Implement virtual scrolling for long list rendering

2. **Performance Optimization**
   - Use `defineAsyncComponent` for async component loading
   - Implement route-level code splitting
   - Optimize image loading (lazy loading, responsive images)
   - Add appropriate caching strategies

3. **Interaction Optimization**
   - Add skeleton screen loading states
   - Implement debounce/throttle for high-frequency operations
   - Add appropriate error boundaries and fallback handling
   - Optimize form submission flow (loading state, prevent duplicate submissions)

### Phase 5: Page Beautification

**Objective**: Improve page visual effects and user experience.

**Steps**:

1. **Style Standards**
   - Ensure consistent color system
   - Standardize spacing and layout (use design system or Tailwind spacing)
   - Unify font sizes and weights

2. **Visual Effects Enhancement**
   - Add appropriate shadows and border-radius
   - Implement smooth transition animations
   - Add hover and focus state styles
   - Use micro-interactions to enhance experience

3. **Responsive Design**
   - Ensure pages perform well on different screen sizes
   - Optimize mobile experience
   - Test layouts at various breakpoints

4. **Accessibility**
   - Ensure color contrast meets WCAG standards
   - Add appropriate ARIA labels
   - Ensure keyboard navigation is available

## Quality Checklist

After completing any modifications, verify:

- [ ] TypeScript compilation has no errors
- [ ] Component Props types are correct
- [ ] API call parameter and response types match
- [ ] Form validation rules are consistent with backend
- [ ] Pages perform normally in major browsers
- [ ] Responsive layouts work correctly
- [ ] Performance has no significant degradation
- [ ] Code style is consistent with the project

## Output Standards

After completing work, provide:

1. **Modification Summary**
   - List which files were modified
   - Main changes made
   - New type definitions added

2. **Code Snippets**
   - Show key type definitions
   - Show important logic modifications

3. **Follow-up Suggestions**
   - Potential further optimizations needed
   - Potential testing suggestions

## Notes

- Always maintain type consistency with backend entity classes
- Prioritize Composition API best practices
- Ensure modifications do not affect existing functionality
- Follow project code standards and style guides
- Before making significant modifications, backup or use version control
