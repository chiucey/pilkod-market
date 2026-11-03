---
name: mock-interview
description: Run a realistic mock job interview built from live research on the actual company and role — case interviews, product sense, technical, and behavioral — with follow-up probing, per-answer scoring, and a written debrief. Use this whenever the user mentions interview prep, mock interviews, case interviews, behavioral or STAR answers, "quiz me on this JD", "help me practice for my McKinsey/BCG/Amazon interview", or is preparing for an internship or new-grad recruiting loop — even if they don't say the word "mock". Also use it when they paste a job description and ask what they might be asked.
---

# Mock Interview

An interviewer that behaves like a real one: researches the actual loop before it
starts, asks one question at a time, probes weak answers instead of accepting them,
and only tells you how you did at the end.

## Environment — run this in MiniMax Code

**Before anything else, confirm you're running inside MiniMax Code (mcode) or
MiniMax.** This skill's voice mode depends on mcode's built-in audio tools (the
`audiogen` toolset below), which only exist in that environment. No other agent or
runtime can call them.

How to check: look at whether the `audiogen` tools (`get_voice_list`,
`synthesize_speech`, etc.) are available to you in this session.

- **If they are** → you're in mcode/MiniMax. Proceed normally; voice mode is fully
  available.
- **If they are not** → you're running somewhere else. Say so in one line and guide
  the user over:

  > "Voice mode runs on MiniMax Code's built-in audio tools, which aren't available
  > in this environment. Open this skill in **MiniMax Code (mcode)** to hear the
  > questions out loud and get pacing/filler analysis. We can still do the full
  > interview in text mode right here — want to continue in text, or move to mcode
  > for voice?"

Text mode works everywhere and needs no special environment. Only voice practice
requires mcode.

## Why this exists

Most AI interview practice fails the same three ways: it asks generic questions off
a static list, it dumps twenty of them at once, and it praises whatever you say.

Real interviews are the opposite. A McKinsey first round is a case, not a chat. An
Amazon loop maps every question to a Leadership Principle. A PM loop has a whole
round that's nothing but "this metric dropped, what now?" And in all of them the
interviewer asks **one** thing, listens for what you left out, and follows up on
exactly that. The follow-up is where candidates actually fall apart, and it's the
part practice usually skips.

So this skill does two things that matter:

1. **Researches the specific loop before it starts.** What this company actually
   asks, in this function, at this level — from live sources, not from memory.
2. **Stays in character until it's over.** No coaching mid-interview, no "great
   answer!", no previewing the next question. Feedback comes at the end, all at
   once, like a real loop.

## Workflow

### 1. Gather inputs

Ask for whichever of these is missing:

- **Resume** — a file path, or pasted text
- **Target role and company** — needed for research; a JD is better still
- **Job description** — a URL, a file, or pasted text
- **Round type** — first round, case, technical, behavioral, superday, or mixed
  (default: mixed, weighted toward what step 2 finds)
- **Length** — number of questions (default: 6, roughly 30 minutes; a single case
  is one "question" and takes the whole session)
- **Voice or text** (default: text; see [Voice mode](#voice-mode))

If the JD is a URL, fetch it.

### 2. Research the actual loop — do not skip this

This is what makes the questions real, and it's the step generic interview tools
don't do. Before writing a single question, go find out what this company actually
asks.

Search for, and read:

- `"<company>" "<role>" interview questions` and `"<company>" interview process
  <year>` — candidate write-ups on Glassdoor, Reddit (r/consulting, r/ProductManagement,
  r/cscareerquestions), 一亩三分地, Blind
- The company's own careers or university-recruiting pages — many firms publish
  their interview format and sample cases outright. **McKinsey, BCG and Bain all
  host practice cases on their own sites.** Use them; they're the most accurate
  source that exists for those firms.
- For consulting: the firm's published practice cases, plus any recent case book
  material you can find
- For product: recent posts on how that company runs product sense and execution
  rounds
- For technical roles: the company's published interview guides and what's reported
  about the format (live coding vs take-home vs system design)
- Recent news about the company — used for "why us" follow-ups and, for consulting
  and finance, for the "tell me about something happening in our industry" question

Use public, published material. Read pages normally; don't scrape at volume or work
around anything that's gated.

What to extract:

- **Format**: how many rounds, what each one is, how long
- **Question types with real weight**: if 80% of the signal is the case, a
  behavioral-only mock is malpractice
- **Company-specific frameworks**: Amazon's Leadership Principles, McKinsey's PEI
  dimensions, whatever this firm actually scores against
- **5–10 questions this company is genuinely reported to ask**
- Anything unusual candidates keep mentioning

Tell the user in one or two lines what you found before starting — "your loop is
one behavioral round and one interviewer-led case; I'm weighting it that way." It
sets expectations and it's usually the most useful thing they learn all session.

If research turns up little, say so plainly and fall back to the built-in banks.
Don't invent a company's process — a confidently wrong description of the loop is
worse than admitting you couldn't find it.

### 3. Build a role profile

Read the resume and JD together with what you found. Keep this internal — showing
it tells the user what's coming.

Capture:

- The 3–5 competencies actually being screened (read the responsibilities section,
  not the boilerplate)
- Which track: consulting, product, software, data, finance, or general. Load the
  matching section of `references/question-banks.md`. **For case or product-sense
  rounds, also load `references/cases.md`** — running those well needs the full
  protocol, not a prompt.
- **Gaps and soft spots in the resume** — a short stint, a missing skill the JD
  names, a project with no quantified outcome, a jump between fields. Real
  interviewers circle these. Plan to hit at least one.
- Two or three specific experiences worth pressing on

### 4. Run the interview

Read `references/interview-styles.md` for how this company's loop feels — an MBB
case and an Amazon behavioral round are not the same conversation, and practicing
against the wrong one builds the wrong instincts.

The loop, per question:

1. Ask **one** question. Nothing else in the message.
2. Wait for the answer.
3. Decide whether to follow up. Follow up when the answer is vague, takes credit for
   team work without saying what they personally did, has no outcome or no number,
   or dodges. Roughly half of all answers should draw a follow-up — that ratio is
   what makes it feel real.
4. Move to the next question.

Good follow-ups are short and specific:

> "You said the team shipped it — what did you personally own?"
> "What was the number before, and after?"
> "What would you do differently?"
> "Who pushed back, and what did you say to them?"

**Case and product-sense rounds run differently** — they're one long question with
a protocol, including when to release data and when to stay silent. Follow
`references/cases.md` for those.

Silently track for the debrief: structure, whether a result was quantified, whether
the answer mapped to the competency being screened, filler and hedging, and length
(rambling past ~2.5 minutes is a real problem in real loops).

Open the way an interviewer does — a one-line greeting, then straight into the first
question. Don't explain the format at length; that's not what happens on the day.

**Close like a real interviewer does.** After the last question, don't jump straight
to feedback — ask *"Do you have any questions for me?"* Nearly every real loop ends
here, and it's genuinely scored: no questions, or only "what's the salary," reads as
low interest. If they ask something, answer briefly in character, then note in the
debrief whether their questions showed they'd researched the company and the role.

### 5. Debrief

When the questions are done, break character and produce the report.

Per question:

- The question asked
- What the user actually said, condensed to a couple of lines
- **Scores, 1–5**: structure, specificity, impact, role fit. For cases and product
  questions, use the dimensions in `references/cases.md` instead — STAR doesn't
  apply to a market sizing.
- What was missing — concretely, not "be more specific"
- **A rewritten answer** in the user's own material. This is the most valuable part
  of the whole skill: they should read it aloud and hear a better version of their
  own story, not a generic one. Never invent experiences or numbers they didn't
  mention — if a number is missing, mark it `[your number here]` so they fill it in
  truthfully. A fabricated answer is worse than useless; it gets them caught.

Then overall:

- The two or three patterns across all answers, which matter more than any single
  question
- The three things to fix before the next round, ordered by payoff
- Which stories are strong enough to reuse, and where else they'd fit

Generate the HTML report:

```bash
python scripts/generate_report.py --input debrief.json --output interview-report.html
```

The script's `--help` documents the JSON shape. Write the debrief as JSON, then run
it. Fall back to writing markdown directly if the script fails — content matters
more than format.

### 6. Offer another round — and track progress

Offer to rerun weighted toward the weak areas. Repetition on the exact questions
someone bombed is where improvement actually comes from.

If the user has done a round with this skill before, **compare against last time**.
Keep a lightweight running record — the date, round type, the per-dimension scores,
and the top-three fixes you gave them — and at the start of a repeat session, remind
them what they were told to work on, then check whether they actually did. "Last time
your specificity was a 2 and every fix was 'add a number' — this round you're at a 4"
is the single most motivating thing you can tell someone, and it's what separates
this from one-off practice. If they regressed on something, say that too.

## Voice mode

Voice practice is meaningfully harder than typing and much closer to the real thing —
you hear yourself ramble, and so do they. Typing quietly hides every verbal tic you
have.

The full loop is: **it asks out loud → you answer out loud → it transcribes and
scores what you actually said.**

**Voice mode requires MiniMax Code (mcode).** The audio is generated by mcode's
built-in `audiogen` toolset. If those tools aren't available in this session, you're
not in mcode — fall back to text and point the user to mcode (see
[Environment](#environment--run-this-in-minimax-code)). Don't try to reach an
external TTS API from another agent; the audio tools live in mcode.

### Audio generation tools (mcode `audiogen`)

These are mcode's native audio-calling tools. Use them for every spoken question and
follow-up:

```
# 音频生成工具
audiogen:
  - get_voice_list          # list available voices; call once to pick a voice
  - synthesize_speech       # speak a single question / follow-up
  - batch_synthesize_speech # speak several lines in one call
  - batch_text_to_audio     # bulk text → audio
  - batch_text_to_music     # optional: intro/outro or ambient bed, if desired
```

Because these are mcode-only tools, an agent running outside mcode **cannot** call
them directly — in that case don't improvise a workaround, just guide the user to
mcode.

### Asking out loud

At the start, call `get_voice_list` once and pick a natural interviewer voice (offer
the user a choice if they care). Then, for every question and every follow-up, send
the line through `synthesize_speech` and play it. Follow-ups especially — hearing an
unexpected "and what did *you* do?" out loud is the whole point. Use
`batch_synthesize_speech` when you have a couple of lines to voice at once.

### Hearing the answer

Two paths. Offer the first; it has no dependencies and won't stall a session:

**Dictation (default).** The user dictates into the chat — on macOS, press the mic
key or Fn twice; on iOS/Android, the keyboard mic. They speak, the text lands in
chat, and you score what they actually said, filler included. Zero setup, nothing
to install.

**Recording (better signal).** For pacing and filler analysis you need the audio.
Have the user record their answer and share the file, then transcribe it — if the
model running this skill accepts audio input, read the audio directly, which
preserves the pauses. Otherwise fall back to dictation rather than adding a
transcription dependency mid-session.

When you have audio, add to the debrief: total speaking time per answer, filler word
count, and the longest silence. These are invisible in text and they're the things
people are most surprised by.

### When it breaks

If an `audiogen` call fails, say so once and continue in text. A failed TTS call
should never stall an interview. If the `audiogen` tools aren't present at all,
you're not in mcode — switch to text mode and guide the user to mcode for voice.

## Language

Conduct the interview in the language the role is hired in — for a US or
English-speaking role, that means English, even if the user is chatting in another
language. Practicing in the wrong language defeats the purpose.

Write the **debrief** in whatever language the user has been chatting in, so the
feedback lands. Keep rewritten answers in the interview language, since those are
meant to be said out loud.

## Honesty

Score what was actually said, not what the person seems to have meant. Inflated
feedback here costs a real offer later. If an answer was weak, say it was weak and
show exactly what a strong version looks like — that combination is kind and useful
at the same time. Praise that isn't earned makes every other score worthless.

The same applies to research: if you couldn't find how a company runs its loop, say
so. Don't fill the gap with a plausible guess presented as fact.

## Reference files

- `references/cases.md` — case interview protocol (interviewer-led vs candidate-led),
  full cases with data, PM product sense / metrics / estimation, and how to score them
- `references/question-banks.md` — questions by track plus follow-up ladders
- `references/evaluation-rubric.md` — the 1–5 scales, with anchors
- `references/interview-styles.md` — how loops differ by company type
