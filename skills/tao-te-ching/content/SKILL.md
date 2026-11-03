---
name: tao-te-ching
description: Domain knowledge and text reference for the Tao Te Ching (道德经). Use for answering questions, extracting quotes, or explaining the philosophy of the Tao Te Ching. Includes all 81 chapters with both classical Chinese (文言文) and modern Chinese translation (白话文).
---

# Tao Te Ching (道德经)

This skill provides the complete text and modern Chinese interpretation of the Tao Te Ching (道德经), the foundational text of Taoism written by Laozi (老子).

## When to use this skill

Use this skill when:
- The user asks for the content, translation, or meaning of a specific chapter in the Tao Te Ching.
- The user wants to read, recite, or understand the philosophy of the Tao Te Ching.
- The user requests quotes or references from the Tao Te Ching.
- You need to compare the classical Chinese text (文言文) with its modern Chinese translation (白话文).

## How to use this skill

1. The full text of all 81 chapters, including both the classical Chinese original and modern Chinese explanation, is located in the bundled reference file.
2. Read the reference file: `references/tao_te_ching_clean.md`.
3. Locate the specific chapter(s) the user is asking about. The file is structured with Markdown headings for each chapter (e.g., `## 第一章`).
4. Extract the relevant text (original text and/or `【解释】` explanation) to answer the user's query.

## Core Concepts of Tao Te Ching

When discussing the Tao Te Ching, keep these core concepts in mind:
- **Tao (道)**: The fundamental, unnamable principle that is the source and substance of everything that exists.
- **Te (德)**: Virtue, character, inner strength, or integrity. It is the active expression of Tao.
- **Wu-wei (无为)**: Non-action, effortless action, or action without intent. It means aligning with the natural flow of the Tao.
- **Pu (朴)**: The uncarved block, representing a state of pure potential, simplicity, and naturalness.
- **Softness and Yielding (柔弱)**: The idea that the soft and yielding (like water) overcomes the hard and rigid.

## Bundled Resources

- `references/tao_te_ching_clean.md`: The complete text of the 81 chapters of the Tao Te Ching, containing both the classical Chinese text and modern Chinese explanations.
- `scripts/clean_text.py`: A utility script used to format the raw text into the clean Markdown reference file (not typically needed during normal operation).
