---
name: heart-sutra
description: Provides the text and translation of the Heart Sutra (般若波罗蜜多心经). Use this skill when the user asks for the content, translation, or meaning of the Heart Sutra, or wants to read, recite, or understand this Buddhist text.
---

# Heart Sutra (般若波罗蜜多心经)

## Overview

This skill provides the complete original text of the Heart Sutra (般若波罗蜜多心经) along with its modern translation. It enables Manus to accurately recite, explain, or discuss the Heart Sutra based on the provided reference material.

## Capabilities

1. **Provide Original Text**: Retrieve and provide the exact original text of the Heart Sutra (Tang Dynasty, translated by Xuanzang).
2. **Provide Translation**: Retrieve and provide a modern, accessible translation of the Heart Sutra.
3. **Explain Meaning**: Use the translation to explain the meaning of specific verses or concepts (like "色即是空" - form is emptiness) to the user.

## How to Use

When a user requests information about the Heart Sutra:

1. Read the reference file located at `references/sutra_text.md` using the `file` tool.
2. Extract the relevant portion (Original Text or Translation) based on the user's request.
3. Present the text clearly to the user, maintaining the formatting and structure.
4. If the user asks for an explanation, use the provided translation to form your response.

## Bundled Resources

- `references/sutra_text.md`: Contains the complete original text and modern translation of the Heart Sutra. **Always read this file** to get the accurate text when triggered.
