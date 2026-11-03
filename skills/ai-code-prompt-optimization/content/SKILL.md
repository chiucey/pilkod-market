---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 2555967eda3eb2313a6a8c600c38eda2
    PropagateID: 2555967eda3eb2313a6a8c600c38eda2
    ReservedCode1: 3045022100c10f62297f75fdf44bd230cf37e283b3ae1b2a9a2a5ed9eb2fea519f30c82ade02205d00ab4704d1cbd8ad0f5eb49ba40932c39d5bb68afa30c0785f957ec7a15eae
    ReservedCode2: 304402205415223429f156a146fd9afe738eb474969e5c374a77b58b850cf71255a8d6ab02207cfda202d720c601a90a90a149ade796201d172d95a57e51af5d6b4bfdd6ddc4
description: Help users optimize AI code writing prompts. Use when users need to improve code prompts, enhance generation quality, create more effective prompts, or analyze prompt effectiveness.
name: ai-code-prompt-optimization
---

# AI Code Prompt Optimization

## Skill Overview

This skill helps users optimize prompts for AI code generation, improving code quality, accuracy, and practicality through structured analysis and refinement.

## Core Capabilities

### 1. Prompt Structure Analysis
- Identify key components of prompts
- Evaluate completeness of context information
- Check clarity of constraints

### 2. Optimization Dimensions

| Dimension | Description | Key Points |
|-----------|-------------|------------|
| Role Definition | Specify AI persona | Tech stack, language, experience level |
| Task Description | Clear explanation of task | Input, output, expected results |
| Context Information | Necessary background | Code environment, dependencies, limitations |
| Constraints | Boundary conditions | Performance, security, compatibility |
| Output Format | Specified return format | Code style, comment requirements |

### 3. Optimization Strategies

#### 3.1 Enhance Specificity
- Use specific tech stack and versions
- Define input/output data structures clearly
- Provide example inputs and outputs

#### 3.2 Add Constraints
```markdown
Constraint Examples:
- Only use Python 3.9+ standard library
- Code must pass PEP 8 style checks
- Functions must not exceed 50 lines
- Add complete type annotations
```

#### 3.3 Role Definition Optimization
```markdown
Role Definition Example:
"You are a senior Python backend engineer specializing in Flask framework and SQLAlchemy ORM,
with 10 years of development experience and familiarity with RESTful API design best practices."
```

### 4. Optimization Process

1. **Input Analysis**: Parse the original prompt provided by user
2. **Structure Extraction**: Identify key components
3. **Problem Diagnosis**: Find deficiencies and improvement points
4. **Optimization Suggestions**: Provide specific improvement solutions
5. **Optimized Output**: Generate improved prompt

## Use Cases

- Optimize code generation prompts
- Improve debugging and error fixing prompts
- Enhance code review and refactoring prompts
- Create domain-specific code generation templates

## Optimization Examples

### Original Prompt
```markdown
Write a sorting function
```

### Optimized Prompt
```markdown
You are a Python algorithm engineer. Please implement an efficient sorting algorithm function:
- Input: Integer list [int]
- Output: Ascending sorted integer list [int]
- Requirement: Use quicksort algorithm, average time complexity O(n log n)
- Constraint: Do not use Python's built-in sorted() function
- Code standards: Add type annotations, docstrings, and complexity comments
```

## Output Format

The optimized prompt should include:
1. **Role Definition**: Clear AI persona
2. **Task Description**: Clear target description
3. **Input/Output**: Specific data format
4. **Technical Constraints**: Tech stack and limitations
5. **Quality Requirements**: Code style and standards
