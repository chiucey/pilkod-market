---
AIGC:
    ContentProducer: Minimax Agent AI
    ContentPropagator: Minimax Agent AI
    Label: AIGC
    ProduceID: 1480dc74bf41affd04216b71e451af06
    PropagateID: 1480dc74bf41affd04216b71e451af06
    ReservedCode1: 3046022100f3ac083ec066242c13b0f37fd6a834c244c2c85917cd79e6402bd9e724f8988e02210095cee0e1e0310967ca3525d1036270f86b86e35f782ce20469ff1e90d16b7e3e
    ReservedCode2: 304502201a080e776ec26edc4857defd1fbe6d0acbecf5cdae9fe40f169be1807117fbe8022100a4cbd854e4abf3f7accb5d3a4421c958e891cb86973a6f278441498fa3a968a9
description: Provides expert guidance on applying the Elliott Wave Principle to financial market analysis. Use when the user asks about wave counting, identifying impulse waves, corrective patterns (zigzags, flats, triangles), Fibonacci retracements, wave guidelines (alternation, channeling, volume), wave personality, or any Elliott Wave concepts. This skill includes detailed reference files covering rules, patterns, and examples.
name: elliott-wave-principle
---

# Elliott Wave Principle Skill

This skill helps you apply the Elliott Wave Principle to analyze financial market price data. It contains reference files with detailed rules, pattern descriptions, and guidelines.

## Quick Start

- If the user provides a chart or price data and asks for wave analysis, first determine the trend direction and look for the basic 5‑wave pattern (impulse) followed by a 3‑wave correction.
- Use the reference files to verify rules and identify specific patterns.

## Reference Files

The following files are available in the `references/` directory. Load them as needed based on the user’s question.

- **[basic-principles.md](references/basic-principles.md)** – Fundamental concepts: the 5‑3 wave structure, motive vs. corrective mode, wave degrees, labeling conventions.
- **[impulse-waves.md](references/impulse-waves.md)** – Rules for impulse waves (no overlap, wave 3 not shortest, etc.), extensions, truncations, diagonal triangles (ending and leading).
- **[corrective-patterns.md](references/corrective-patterns.md)** – Detailed descriptions of zigzags (single, double, triple), flats (regular, expanded, running), triangles (contracting, expanding), and combinations (double/triple threes).
- **[guidelines.md](references/guidelines.md)** – Key guidelines: alternation, channeling, volume characteristics, wave personality, and practical application tips.
- **[fibonacci-relationships.md](references/fibonacci-relationships.md)** – Fibonacci ratios in wave relationships (retracements, multiples, time sequences), how to apply them for price targets.
- **[glossary.md](references/glossary.md)** – Definitions of Elliott Wave terms (e.g., throw‑over, truncation, apex, etc.).

## How to Use This Skill

1. **Understand the user’s request**: Determine if they need wave counting, pattern identification, or explanation of concepts.
2. **Load relevant reference(s)**: For example, if the user asks about a specific corrective pattern, load `corrective-patterns.md`. If they ask about wave counting rules, load `impulse-waves.md` and `basic-principles.md`.
3. **Apply the rules**: Use the information to analyze the provided price data. Remember that the Wave Principle is probabilistic; multiple interpretations may be valid.
4. **Provide reasoning**: Explain your wave count, referencing the rules and guidelines used.

## Important Notes

- Always prioritize the **rules** (e.g., wave 3 cannot be shortest, wave 4 cannot overlap wave 1 in an impulse) over guidelines.
- When in doubt, consult the glossary for term definitions.
- The examples in the reference files illustrate typical patterns; actual market patterns may vary.
- For a comprehensive understanding, you may load multiple references. The files are designed to be modular; load only what you need to keep context efficient.