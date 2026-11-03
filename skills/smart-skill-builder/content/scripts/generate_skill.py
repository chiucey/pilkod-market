#!/usr/bin/env python3
"""
Smart Skill Generator — Uses the Anthropic API to generate a complete SKILL.md
from a natural language description.

Usage:
    python generate_skill.py \
        --name "my-skill" \
        --description "What it does and when to use it" \
        --task "The core task in detail" \
        --inputs "What inputs it receives" \
        --outputs "What it produces" \
        --triggers "Example phrases that should trigger it" \
        --output-dir "/path/to/output"
"""

import argparse
import json
import os
import sys
from pathlib import Path


SYSTEM_PROMPT = """You are an expert Claude skill architect. Your job is to generate a complete, 
production-ready SKILL.md file for a Claude skill.

A skill has this structure:
1. YAML frontmatter (name, description)
2. Skill body (instructions for Claude)

Rules for great skills:
- The `description` in frontmatter is the primary trigger mechanism. Make it "pushy" — list 
  specific contexts, phrases, and synonyms. Claude tends to undertrigger, so be aggressive about 
  listing when to use it.
- Instructions should be clear, imperative, and actionable. Explain the WHY behind rules.
- Define output formats explicitly with examples.
- Use progressive disclosure: keep the main body focused, reference deeper docs if needed.
- Avoid rigid MUST/NEVER language where you can explain reasoning instead.
- If the skill involves repetitive file operations or API calls, mention that a helper script 
  should be created in scripts/.

Output ONLY the SKILL.md content — no preamble, no code fences, just the raw markdown starting 
with the --- frontmatter block.

The description field must:
- Be under 1024 characters
- Not contain angle brackets (< or >)
- Clearly state what the skill does AND when to trigger it
- Use phrases like "Use when...", "Trigger whenever...", "Use even if..."

The name field must:
- Be kebab-case (lowercase letters, digits, hyphens only)
- Be under 64 characters
"""


def generate_skill(name: str, description: str, task: str, inputs: str, 
                   outputs: str, triggers: str) -> str:
    """Call the Anthropic API to generate a SKILL.md."""
    try:
        import urllib.request
        import urllib.error
    except ImportError:
        print("ERROR: urllib not available", file=sys.stderr)
        sys.exit(1)

    user_prompt = f"""Generate a complete SKILL.md for a Claude skill with these specifications:

**Skill Name**: {name}
**Core Task**: {task}
**Inputs**: {inputs}
**Outputs**: {outputs}
**Trigger Contexts / Example Phrases**: {triggers}
**Suggested Description**: {description}

Generate a complete, high-quality SKILL.md that Claude can follow to accomplish this task reliably. 
Include:
1. YAML frontmatter with name and a great triggering description
2. Clear, well-organized instructions
3. Output format specification with an example
4. Edge cases to handle
5. Any relevant notes about when to ask for clarification vs. proceeding

Remember: output ONLY the raw SKILL.md content starting with ---"""

    payload = json.dumps({
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 4000,
        "system": SYSTEM_PROMPT,
        "messages": [
            {"role": "user", "content": user_prompt}
        ]
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01",
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=60) as response:
            data = json.loads(response.read().decode("utf-8"))
            text_blocks = [b["text"] for b in data.get("content", []) if b.get("type") == "text"]
            return "\n".join(text_blocks).strip()
    except urllib.error.HTTPError as e:
        body = e.read().decode("utf-8")
        print(f"ERROR: API call failed with status {e.code}: {body}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


EVALS_TEMPLATE = """{{
  "skill_name": "{name}",
  "evals": [
    {{
      "id": 1,
      "prompt": "{eval1}",
      "expected_output": "Successful completion of the task with well-formatted output",
      "files": []
    }},
    {{
      "id": 2,
      "prompt": "{eval2}",
      "expected_output": "Successful completion of the task with well-formatted output",
      "files": []
    }},
    {{
      "id": 3,
      "prompt": "{eval3}",
      "expected_output": "Handles edge case gracefully and asks for clarification or proceeds reasonably",
      "files": []
    }}
  ]
}}"""


def generate_test_cases(name: str, task: str, triggers: str) -> dict:
    """Generate test cases using the Anthropic API."""
    import urllib.request
    import urllib.error

    prompt = f"""Generate 3 realistic test case prompts for a Claude skill called "{name}".

Skill task: {task}
Example trigger phrases: {triggers}

Return a JSON object with exactly this structure:
{{
  "eval1": "first test prompt - typical usage, medium complexity",
  "eval2": "second test prompt - different angle or input type",  
  "eval3": "third test prompt - edge case or unusual input"
}}

Make the prompts realistic — the kind of thing a real user would actually type. 
Include specific details (file names, column names, context). Keep each prompt under 200 chars.
Return ONLY the JSON object, no other text."""

    payload = json.dumps({
        "model": "claude-sonnet-4-20250514",
        "max_tokens": 500,
        "messages": [{"role": "user", "content": prompt}]
    }).encode("utf-8")

    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=payload,
        headers={
            "Content-Type": "application/json",
            "anthropic-version": "2023-06-01",
        },
        method="POST"
    )

    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            data = json.loads(response.read().decode("utf-8"))
            text = "".join(b["text"] for b in data.get("content", []) if b.get("type") == "text")
            # Strip any markdown fences
            text = text.strip().lstrip("```json").lstrip("```").rstrip("```").strip()
            return json.loads(text)
    except Exception:
        # Fallback test cases
        return {
            "eval1": f"Please help me with: {task}",
            "eval2": f"I need to {task} for my project",
            "eval3": f"Can you {task}? I'm not sure what format to use"
        }


def main():
    parser = argparse.ArgumentParser(description="Generate a Claude skill from a description")
    parser.add_argument("--name", required=True, help="Skill name (kebab-case)")
    parser.add_argument("--description", required=True, help="Short description of what the skill does")
    parser.add_argument("--task", required=True, help="The core task in detail")
    parser.add_argument("--inputs", default="Text or files from the user", help="What inputs the skill receives")
    parser.add_argument("--outputs", default="Processed output as specified", help="What the skill produces")
    parser.add_argument("--triggers", default="", help="Example phrases that should trigger the skill")
    parser.add_argument("--output-dir", default="/home/claude/generated-skills", help="Output directory")
    args = parser.parse_args()

    # Sanitize name to kebab-case
    import re
    name = re.sub(r'[^a-z0-9-]', '-', args.name.lower())
    name = re.sub(r'-+', '-', name).strip('-')[:64]

    output_dir = Path(args.output_dir) / name
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "scripts").mkdir(exist_ok=True)
    (output_dir / "evals").mkdir(exist_ok=True)

    print(f"🧠 Generating skill: {name}")
    print("   Calling Anthropic API to generate SKILL.md...")

    skill_content = generate_skill(
        name=name,
        description=args.description,
        task=args.task,
        inputs=args.inputs,
        outputs=args.outputs,
        triggers=args.triggers
    )

    skill_path = output_dir / "SKILL.md"
    skill_path.write_text(skill_content, encoding="utf-8")
    print(f"   ✅ SKILL.md written to {skill_path}")

    print("   Generating test cases...")
    test_data = generate_test_cases(name, args.task, args.triggers)

    evals_content = EVALS_TEMPLATE.format(name=name, **test_data)
    evals_path = output_dir / "evals" / "evals.json"
    evals_path.write_text(evals_content, encoding="utf-8")
    print(f"   ✅ Test cases written to {evals_path}")

    print(f"\n✨ Skill generated at: {output_dir}")
    print(f"   Next: review SKILL.md, then validate and package.")
    print(f"   Validate: python smart-skill-builder/scripts/validate_skill.py {output_dir}")


if __name__ == "__main__":
    main()
