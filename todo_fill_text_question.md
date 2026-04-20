# Fill `Text_Question_EN` — Task Guide

> Purpose: self-contained handoff document. A future LLM or human should be
> able to pick up this task cold by reading only this file plus the linked
> source files.

## 1. Goal

Fill the `Text_Question_EN` field on every card in
`deck.json` (6,065 cards total). Each filled value must be
a single English study question whose **answer is the existing `Answer` field
of the card**.

## 2. Hard constraints

1. **Answer fit** — the existing Answer field must be a valid answer to the
   generated Text_Question_EN.
2. **Do not modify the Answer** (or any other existing field). Only write to
   `Text_Question_EN` (index 4 in the card's `fields` array).
3. **No image references** — the question must read standalone, without words
   like: `tagged`, `highlighted`, `indicated`, `shown`, `below`, `pictured`,
   `image`, `this` (referring to an unspecified visual), `the tag`.
4. **End with a question mark**.

## 3. Data model

- File: `deck.json` (CrowdAnki format).
- Each card has a `fields` array (indices per the NoteModel):

  | Index | Name             | Source/Target |
  |-------|------------------|---------------|
  | 0     | Question         | image HTML (current on-card question) |
  | 1     | Question_EN      | short image-referencing prompt, e.g. "Identify the tagged structure." |
  | 2     | Question_DE      | German equivalent of Question_EN |
  | 3     | Question_FR      | French equivalent of Question_EN |
  | **4** | **Text_Question_EN** | **target field — this task** |
  | 5     | Text_Question_DE | (future task) |
  | 6     | Text_Question_FR | (future task) |
  | 7     | Answer           | image HTML (answer image) |
  | 8     | Answer_LA        | Latin anatomical term |
  | 9     | Answer_EN        | English term — **answer to match** |
  | 10    | Answer_DE        | German term |
  | 11    | Answer_FR        | French term (mostly empty) |
  | 12    | Description_EN   | (mostly empty) |
  | 13    | Description_DE   | rich HTML anatomical description — **main source for cues** |
  | 14    | Description_FR   | (mostly empty) |
  | 15    | Keywords         | search keywords |
  | 16    | Source           | attribution |

- Use `analyze_deck.py` for completion stats; `python3 analyze_deck.py -v`
  lists incomplete cards.

## 4. Input sources per card

To draft one Text_Question_EN, read from the card:

- `Question_EN` (index 1) — tells you **what the question is asking about**
  (identification, innervation, actions, origin/insertion, embryological
  origin, foramen, etc.).
- `Answer_EN` (index 9) — the English answer you need to produce a question for.
  Often formatted as `Structure // property1; property2` when the question
  asks for a property.
- `Answer_LA` (index 8) — fall back for Latin naming.
- `Answer_DE` (index 10) — cross-check.
- `Description_DE` (index 13) — **primary source of anatomical cues** (origin,
  insertion, innervation, relations, branches, embryology). This is where the
  material for the question's descriptive content comes from. Translate cues
  into English anatomical terminology using *Terminologia Anatomica*.

## 5. Style guide (approved by user, 2026-04-19)

- **Describe the structure, don't name it.** The reader should have to figure
  out the structure from cues (attachments, relations, branches, embryology).
- **"AND" questions for compound answers.** When the Answer is formatted as
  `Structure // property` (e.g. `Rectus Abdominis m. // Intercostal nn.
  (T7-T11); Subcostal n.`), write the question so that both halves are
  elicited: *"Which paired vertical muscle lying within the rectus sheath
  between the pubic symphysis and the xiphoid process, and what segmental
  nerves provide its motor innervation?"*
- **Length**: 20–50 words; enough anatomical specificity to narrow the answer
  uniquely.
- **Terminology**: standard English anatomical terms (Terminologia Anatomica).
  Keep Latin only when idiomatic in English usage.
- **Siding cards** (`"Based on the image below, identify whether the bone is
  from the left or right side of the body."`): the Answer contains orientation
  landmarks. Frame the question around those landmarks, e.g. *"When examining
  an isolated os coxae in standard anatomical orientation, which three
  anatomical landmarks indicate its superior, lateral, and anterior aspects
  (thereby revealing which side of the body it comes from)?"*

## 6. Strategy per Question_EN pattern

The deck contains ~90 unique `Question_EN` strings; ~4,500 cards use one of
these 5 dominant patterns:

| Pattern                                            | Strategy |
|----------------------------------------------------|----------|
| *"Identify the tagged structure."* / *"…bony feature."* / *"…bone."* | Describe the structure via attachments, relations, branches; ask "Which …?" |
| *"What is the innervation of the tagged structure?"* | AND question: describe the structure + ask for its innervation |
| *"What is the origin and insertion of the tagged structure?"* | AND question: describe the structure + ask for O/I |
| *"What are the actions of the tagged structure?"* / *"…action…"* | AND question: describe the structure + ask for its actions |
| *"What is the embryological origin of the tagged structure?"* | Describe the adult structure, ask for its embryonic origin |

Less common patterns (foramen, cranial-nerve fibers, hernia types, etc.) should
be handled analogously: read Question_EN to see what the ask is, then reframe
without image references.

## 7. Scaling approach

User preference (see `memory/feedback_use_agents_not_sdk.md`): **spawn agents,
don't use the Anthropic SDK directly**.

Recommended workflow:

1. **Batch by section**. The deck has 35 sections; each has 37–325 cards.
   Sections give terminology consistency.
2. **One section at a time** for the first few batches, to keep user review
   feasible.
3. **For each section**:
   - Extract cards with empty `Text_Question_EN` from that section.
   - Spawn an agent with the card data, the style guide (§5), and the
     constraints (§2) in its prompt.
   - Agent returns a JSON list of `{guid: "...", Text_Question_EN: "..."}`.
   - Validate (§9) before writing.
   - Write back via a small Python script (pattern: see
     `pilot_text_questions.py`).
4. **User review** after each section until style is locked in.

## 8. Suggested agent prompt template

```
You are a medical anatomy expert. For each of the cards below, write a single
English study question to fill the `Text_Question_EN` field.

Rules:
- The existing Answer_EN field must be a valid answer to your question.
- Do NOT modify the Answer. You are only generating Text_Question_EN.
- Do NOT reference an image: avoid the words tagged, highlighted, indicated,
  shown, below, pictured, image.
- Describe the structure by its attachments, relations, branches, or
  embryology — not by its name.
- If the Answer has "Structure // property" format, write an "AND" question
  that asks for both halves (e.g. "Which muscle ... and what nerves ...").
- Length: 20–50 words.
- End with '?'.
- Use standard English anatomical terminology (Terminologia Anatomica).

Input cards: <JSON array of cards with guid, Question_EN, Answer_LA, Answer_EN,
Answer_DE, Description_DE>

Output: JSON array `[{"guid": "...", "Text_Question_EN": "..."}]`.
```

## 9. Validation checks

Before writing agent output to disk, validate each draft:

- Non-empty, non-whitespace.
- Ends with `?`.
- Does not contain any banned word (case-insensitive): `tagged`, `highlighted`,
  `indicated`, `shown below`, `pictured`, `image`, `the tag`, `this image`.
- Length between roughly 15 and 80 words (loose sanity bound).
- Corresponding GUID exists and has empty `Text_Question_EN` currently
  (otherwise you're overwriting prior work).

A failed draft goes back to the agent with the failure reason.

## 10. Current state (2026-04-19)

- **Pilot complete**: 8 cards filled, spanning the 8 most common Question_EN
  patterns. Style approved by the user.
- **Osteology: Lower Limb complete**: 225 cards filled (+pilot = 226/226).
  User reviewed samples on 2026-04-19 and approved.
- **Style decision locked in (2026-04-19)**: uniform descriptive
  "don't name the structure" style applies to every card.
- **Filled**: 233 / 6,065 (3.8%). **Remaining**: 5,832 cards.
- **Sections done**: Osteology: Lower Limb.

## 11. Resume instructions for a new session

1. Read this file.
2. Read `TODO.md` for overall deck-translation status.
3. `git log --oneline -15` for recent history.
4. `python3 analyze_deck.py | grep Text_Question_EN` to confirm current
   completion count.
5. Look up one filled card (any pilot GUID) to sanity-check the approved style:
   ```python
   import json
   d = json.load(open('deck.json'))
   # walk d['children'] / d['notes'] tree, find note by guid
   ```
6. Pick the next unfinished section, follow §7 workflow, start with a small
   agent batch for user review.

## 12. Related files

- `deck.json` — the data.
- `analyze_deck.py` — completion analysis.
- `pilot_text_questions.py` — template script for writing back drafts by GUID.
- `TODO.md` — overall translation plan (Tasks A/B/C and D/E/F).
- `memory/feedback_use_agents_not_sdk.md` — user's agents-over-SDK preference.
