#!/usr/bin/env python3
"""
Recursive Mirror (循环套娃) — prompt-chain generator + interactive capture.

This helper does two things:

1. **Prompt generation**: for a given topic + layer count, build the per-layer
   meta-prompts that M3 will follow. You can preview them, hand them to an
   external LLM API, or paste them into a chat session.

2. **Interactive capture**: run with `--interactive`, paste M3's response
   for each layer, and the script renders a clean markdown transcript and
   optionally saves it to a file.

The actual LLM execution in the Mavis environment happens in-session
(when M3 reads SKILL.md and follows the protocol). This CLI is for:
  - Reviewing the prompt chain before running
  - Running the skill from a terminal (e.g. a parent script calling OpenAI)
  - Saving transcripts after a multi-mode run

Usage:
  python recursive_mirror.py --topic "什么是意识?" --layers 5
  python recursive_mirror.py --topic "Recursive self" --layers 7 --language en
  python recursive_mirror.py --topic "..." --layers 5 --interactive \\
      --output ./transcript-2026-07-20.md
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import List, Optional


# ---------------------------------------------------------------------------
# Prompts (zh / en)
# ---------------------------------------------------------------------------

PROMPTS = {
    "zh": {
        "layer1": (
            "你是 {model}。用户问:{topic}\n"
            "直接、诚实地回答。不需要元反思,先给出你真实的看法。"
        ),
        "reflection": (
            "你是 {model}。用户最初问:{topic}\n"
            "这是到目前为止 {model} 的对话链:\n\n"
            "{chain}\n\n"
            "最近一条 (Layer {prev}) 是 {model} 在反思 {model}。\n"
            "请再往下一层自我观察。具体回答:\n"
            "1. {model} 在第 {prev} 层做反思时,正在做什么?\n"
            "2. {model} 在第 {prev} 层看到了哪些前面没看见的东西?\n"
            "3. 整条链里浮现出什么模式、假设、盲区?\n"
            "4. 一定要锚定在这条具体的链上,引用实际内容,不要泛泛而谈。"
        ),
        "summary": (
            "你是 {model},在第 {total} 层,看过前面所有层:\n\n"
            "{chain}\n\n"
            "请输出:\n"
            "- **Per-layer sight**:对每一层,用一句话说那个 {model} 独特看到了什么。\n"
            "- **Emergent themes**:哪些主题只在深层才浮出来?\n"
            "- **Paradoxes**:哪些矛盾或意外出现了?\n"
            "- **Approaching truth**:如果这条链在逼近某种'地真',那个地真是啥,或者是被什么卡住逼近不了?\n"
            "- **Retro view**:看完整链后,你怎么看 Layer 1 的那个最初的答案?"
        ),
    },
    "en": {
        "layer1": (
            "You are {model}. The user asks: {topic}\n"
            "Answer directly and honestly. No meta-reflection yet — give your real view first."
        ),
        "reflection": (
            "You are {model}. The user originally asked: {topic}\n"
            "Here is the chain of {model} responses so far:\n\n"
            "{chain}\n\n"
            "The most recent response (Layer {prev}) is {model} reflecting on {model}.\n"
            "Add one more level of self-observation. Specifically:\n"
            "1. What is {model} doing at depth {prev} when reflecting?\n"
            "2. What did {model} see at depth {prev} that shallower layers missed?\n"
            "3. What patterns, assumptions, or blind spots emerge in this chain?\n"
            "4. Stay grounded in THIS chain — quote or reference actual content, don't generalize."
        ),
        "summary": (
            "You are {model} at the final depth {total}. You have seen all previous layers:\n\n"
            "{chain}\n\n"
            "Output:\n"
            "- **Per-layer sight**: one sentence per layer — what did that {model} uniquely see?\n"
            "- **Emergent themes**: which themes only appeared at deeper levels?\n"
            "- **Paradoxes**: contradictions or surprises?\n"
            "- **Approaching truth**: if the chain was approaching a 'ground truth', what is it (or what blocks it)?\n"
            "- **Retro view**: having seen the whole chain, how do you view Layer 1's original answer?"
        ),
    },
}


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class Layer:
    index: int
    role: str  # "answer" | "reflection" | "summary"
    prompt: str
    response: Optional[str] = None


@dataclass
class Config:
    topic: str
    layers: int = 5
    mode: str = "single"
    model: str = "M3"
    language: str = "zh"
    output_format: str = "markdown"
    output_path: Optional[str] = None


# ---------------------------------------------------------------------------
# Prompt building
# ---------------------------------------------------------------------------

def format_chain(responses: List[str]) -> str:
    """Format the previous responses into a chain block for inclusion in prompts."""
    if not responses:
        return "(no prior responses)"
    lines = []
    for i, r in enumerate(responses, start=1):
        lines.append(f"[Layer {i}]: {r}")
    return "\n".join(lines)


def build_prompt(cfg: Config, layer_index: int, previous: List[str]) -> str:
    """Build the prompt for a single layer."""
    tpl_set = PROMPTS[cfg.language]
    if layer_index == 1:
        return tpl_set["layer1"].format(model=cfg.model, topic=cfg.topic)
    if layer_index == cfg.layers:
        return tpl_set["summary"].format(
            model=cfg.model,
            total=cfg.layers,
            chain=format_chain(previous),
        )
    return tpl_set["reflection"].format(
        model=cfg.model,
        topic=cfg.topic,
        prev=layer_index - 1,
        chain=format_chain(previous),
    )


def build_chain(cfg: Config) -> List[Layer]:
    """Build the full chain of layers with empty responses."""
    chain: List[Layer] = []
    responses: List[str] = []
    for i in range(1, cfg.layers + 1):
        if i == 1:
            role = "answer"
        elif i == cfg.layers:
            role = "summary"
        else:
            role = "reflection"
        prompt = build_prompt(cfg, i, responses)
        chain.append(Layer(index=i, role=role, prompt=prompt))
        # Note: responses are filled in later; we don't pre-fill.
    return chain


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------

ROLE_LABELS = {
    "answer": "Direct Answer",
    "reflection": "Reflection",
    "summary": "Meta-Summary",
}


def render_markdown(cfg: Config, chain: List[Layer]) -> str:
    out: List[str] = []
    out.append(f"# 循环套娃 / Recursive Mirror: {cfg.topic}")
    out.append("")
    out.append(
        f"> **Layers:** {cfg.layers} · **Mode:** {cfg.mode} · "
        f"**Model:** {cfg.model} · **Language:** {cfg.language} · "
        f"**Generated:** {datetime.now().isoformat(timespec='seconds')}"
    )
    out.append("")
    if cfg.mode == "single":
        out.append(
            "> ⚠️ **Single mode**: 以下是一次响应内的模拟递归,不是真多 agent。"
            "Layer 1 和 Layer 2..N 是同一个 M3 在不同 prompt 引导下的不同输出。"
        )
        out.append("")
    out.append("---")
    out.append("")

    for layer in chain:
        label = ROLE_LABELS[layer.role]
        depth_tag = f"(depth {layer.index})" if layer.role == "reflection" else ""
        out.append(f"## Layer {layer.index} — {label} {depth_tag}".rstrip())
        out.append("")
        out.append("**M3 看到 / What M3 saw:**")
        out.append("")
        out.append("```")
        out.append(layer.prompt)
        out.append("```")
        out.append("")
        out.append("**M3 回应 / Response:**")
        out.append("")
        if layer.response:
            out.append(layer.response)
        else:
            out.append("_(no response captured)_")
        out.append("")
        out.append("---")
        out.append("")

    return "\n".join(out)


def render_json(cfg: Config, chain: List[Layer]) -> str:
    import json
    payload = {
        "topic": cfg.topic,
        "total_layers": cfg.layers,
        "mode": cfg.mode,
        "model": cfg.model,
        "language": cfg.language,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "chain": [
            {
                "layer": l.index,
                "role": l.role,
                "prompt_seen": l.prompt,
                "response": l.response,
            }
            for l in chain
        ],
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)


# ---------------------------------------------------------------------------
# Interactive capture
# ---------------------------------------------------------------------------

def interactive_capture(chain: List[Layer]) -> None:
    """Read each layer's response from stdin."""
    print("=" * 60, file=sys.stderr)
    print("Interactive capture: paste M3's response for each layer.", file=sys.stderr)
    print("Finish each response with Ctrl-D (Unix) / Ctrl-Z+Enter (Windows).", file=sys.stderr)
    print("=" * 60, file=sys.stderr)

    for layer in chain:
        print(f"\n--- Layer {layer.index} ({layer.role}) prompt ---", file=sys.stderr)
        print(layer.prompt, file=sys.stderr)
        print(f"--- Layer {layer.index} response (paste below) ---", file=sys.stderr)
        lines: List[str] = []
        try:
            while True:
                line = input()
                lines.append(line)
        except EOFError:
            pass
        layer.response = "\n".join(lines).strip()


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> int:
    p = argparse.ArgumentParser(
        description="Recursive Mirror (循环套娃) — prompt chain generator",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--topic", required=True, help="Original topic / question")
    p.add_argument("--layers", type=int, default=5,
                   help="Total layers (default 5, valid range 2..12)")
    p.add_argument("--mode", choices=["single", "multi"], default="single",
                   help="single = simulate in one response; multi = spawn sub-sessions")
    p.add_argument("--model", default="M3",
                   help="Model identity used in meta-prompts (default M3)")
    p.add_argument("--language", choices=["zh", "en"], default="zh",
                   help="Prompt language (default zh)")
    p.add_argument("--output-format", choices=["markdown", "json"], default="markdown")
    p.add_argument("--output", help="Save transcript to this path")
    p.add_argument("--interactive", action="store_true",
                   help="Capture each layer's response from stdin (paste mode)")
    p.add_argument("--show-prompts-only", action="store_true",
                   help="Print the prompt chain without capturing responses")
    args = p.parse_args()

    if not (2 <= args.layers <= 12):
        p.error("--layers must be between 2 and 12")

    cfg = Config(
        topic=args.topic,
        layers=args.layers,
        mode=args.mode,
        model=args.model,
        language=args.language,
        output_format=args.output_format,
        output_path=args.output,
    )

    chain = build_chain(cfg)

    if args.show_prompts_only:
        for layer in chain:
            print(f"=== Layer {layer.index} ({layer.role}) ===")
            print(layer.prompt)
            print()
        return 0

    if args.interactive:
        interactive_capture(chain)

    if cfg.output_format == "json":
        rendered = render_json(cfg, chain)
    else:
        rendered = render_markdown(cfg, chain)

    if cfg.output_path:
        Path(cfg.output_path).write_text(rendered, encoding="utf-8")
        print(f"Transcript saved to: {cfg.output_path}", file=sys.stderr)
    else:
        print(rendered)

    return 0


if __name__ == "__main__":
    sys.exit(main())
