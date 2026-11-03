---
name: diamond-sutra
description: "Domain knowledge and text reference for the Diamond Sutra (金刚经). Use for answering questions, extracting quotes, or comparing translations of the Diamond Sutra. Includes three classical Chinese translations: Kumarajiva (姚秦鸠摩罗什), Xuanzang (唐玄奘), and Bodhiruci (元魏留支)."
---

# Diamond Sutra (金刚经) Analysis

This skill provides full text and reference workflows for analyzing the Diamond Sutra, one of the most important texts in Mahayana Buddhism.

## Core Workflows

When a user asks about the Diamond Sutra, follow these steps:

1. **Identify Intent**: Determine if the user wants:
   - A general explanation or summary of a concept
   - A specific quote or passage
   - A comparison between different translations
   - An analysis of the sutra's structure (e.g., chapter divisions)

2. **Select the Appropriate Translation**:
   - For the most famous, widely-recited version (default): Read `references/kumarajiva.md`
   - For a more literal, scholarly translation: Read `references/xuanzang.md`
   - For a version with explicit chapter divisions: Read `references/bodhiruci.md`

3. **Extract and Analyze**:
   - Read the relevant reference file(s) using the `file` tool.
   - Extract the exact text needed to support your answer.
   - Provide the answer, quoting the text where appropriate.

## Available References

The full text of three major Chinese translations are bundled with this skill:

- **[references/kumarajiva.md](references/kumarajiva.md)**: Translated by Kumarajiva (姚秦三藏法师鸠摩罗什译). This is the standard, most commonly chanted version. It is known for its poetic flow and profound simplicity.
- **[references/xuanzang.md](references/xuanzang.md)**: Translated by Xuanzang (唐三藏法师玄奘奉诏译). Known as "能断金刚般若波罗蜜多经", it is highly precise and adheres closely to the original Sanskrit phrasing.
- **[references/bodhiruci.md](references/bodhiruci.md)**: Translated by Bodhiruci (元魏三藏留支译). This version includes explicit section/chapter titles (e.g., 序分第一, 护念付嘱分第二), which are useful for structural analysis.

## Best Practices

- **Always quote the source**: When explaining a concept like "无住生心" (non-abiding mind) or "四相" (four marks: self, person, sentient being, lifespan), quote the exact phrasing from the sutra.
- **Acknowledge translation differences**: If the user asks a deep philosophical question, consider comparing how Kumarajiva translates a phrase versus Xuanzang, as this often yields deeper insights.
- **Keep it concise**: The Diamond Sutra is famous for its brevity. Reflect this in your answers by being direct and profound.
