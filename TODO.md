# ComprehensiveCadaver Deck — Translation TODO

> Generated 2026-04-19 by `python3 analyze_deck.py`

## Summary

- **6,065 total cards** across 35 sections (7 regions)
- **53.8% of translation slots filled** (42,431 / 78,845)
- **36,414 translation slots remaining**

## Field Completion Status

| Field                  | Filled | Missing   | Done   |
|------------------------|--------|-----------|--------|
| Question               | 6,065  | 0         | 100.0% |
| Question_EN            | 6,064  | 1         | ~100%  |
| Question_DE            | 6,064  | 1         | ~100%  |
| Question_FR            | 6,064  | 1         | ~100%  |
| **Text_Question_EN**   | **0**  | **6,065** | **0.0%** |
| **Text_Question_DE**   | **0**  | **6,065** | **0.0%** |
| **Text_Question_FR**   | **0**  | **6,065** | **0.0%** |
| Answer (image)         | 6,065  | 0         | 100.0% |
| Answer_LA              | 6,064  | 1         | ~100%  |
| Answer_EN              | 6,050  | 15        | 99.8%  |
| Answer_DE              | 6,061  | 4         | 99.9%  |
| **Answer_FR**          | **2**  | **6,063** | **0.0%** |
| **Description_EN**     | **0**  | **6,065** | **0.0%** |
| Description_DE         | 6,060  | 5         | 99.9%  |
| **Description_FR**     | **2**  | **6,063** | **0.0%** |
| Keywords               | 6,065  | 0         | 100.0% |
| Source                 | 6,065  | 0         | 100.0% |

## What Needs To Be Done

### Priority 1: Six bulk translation tasks (36,383 of 36,414 missing slots)

6,040 cards share the exact same pattern of six missing fields. The remaining ~25 have
the same six missing plus one or two extra gaps (see Priority 2).

| Task | Missing Field     | Source to translate from                 | Count |
|------|-------------------|------------------------------------------|-------|
| **A** | `Answer_FR`       | `Answer_EN` (or `Answer_LA`) → French   | 6,063 |
| **B** | `Description_EN`  | `Description_DE` → English              | 6,065 |
| **C** | `Description_FR`  | `Description_DE` → French               | 6,063 |
| **D** | `Text_Question_EN`| TBD — source not yet decided (see note) | 6,065 |
| **E** | `Text_Question_DE`| TBD — source not yet decided (see note) | 6,065 |
| **F** | `Text_Question_FR`| TBD — source not yet decided (see note) | 6,065 |

**Note on Text_Question_\***: these fields were added in commit `5dc4b85` but no
source/generation strategy has been documented yet. Candidate sources include the
existing `Question_*` prompts combined with `Answer_*` / image context, or a separate
textual description of each card. Decide the source before running bulk generation.

### Priority 2: Fix scattered gaps (27 non-bulk slots across ~22 cards)

| Field               | Missing | Notes |
|---------------------|---------|-------|
| Question_EN/DE/FR   | 1 each  | One card in "Heart and Great Vessels" section |
| Answer_LA           | 1       | One card in "Osteology: Sternum and Ribs" |
| Answer_EN           | 15      | Mostly in "Osteology: Vertebral Column" |
| Answer_DE           | 4       | Scattered in "Osteology: Lower Limb" (3) and "Pharynx and Nasal Cavity" (1) |
| Description_DE      | 5       | Scattered: "Osteology: Lower Limb" (4), "Pharynx and Nasal Cavity" (1) |

Find them with: `python3 analyze_deck.py -v`

### Missing Field Patterns (from latest run)

```
 6040x  Text_Question_EN, Text_Question_DE, Text_Question_FR, Answer_FR, Description_EN, Description_FR
   15x  + Answer_EN
    3x  + Answer_DE, Description_DE
    2x  + Description_DE
    2x  Text_Question_*, Description_EN only (Answer_FR & Description_FR already filled — the 2 example cards)
    1x  + Answer_DE
    1x  + Question_EN, Question_DE, Question_FR (the Heart card)
    1x  + Answer_LA
```

---

## How to Fill the Missing Fields (LLM Translation Guide)

### Field Semantics

Each card is an anatomy flashcard with an image-based question and answer:

- **Question** / **Question_EN** / **Question_DE** / **Question_FR**: The question prompt in the original language, English, German, and French. Usually short (e.g., "Identify the tagged structure.").
- **Text_Question_EN** / **Text_Question_DE** / **Text_Question_FR**: A textual variant of the question (source/purpose TBD — see Priority 1 note).
- **Answer** (index 7): An image showing the answer (HTML `<img>` tag).
- **Answer_LA**: The anatomical term in Latin (the standard international nomenclature, *Terminologia Anatomica*).
- **Answer_EN** / **Answer_DE** / **Answer_FR**: The common name for the structure in English, German, and French.
- **Description_EN** / **Description_DE** / **Description_FR**: A detailed anatomical description of the structure — its origin, insertion, innervation, blood supply, relations, clinical significance, etc. Written in rich HTML with `<em>` tags for anatomical terms.
- **Keywords**: Semicolon-separated keywords for search.
- **Source**: Attribution for the image.

### Translation Strategy for Each Missing Field

#### Task A: Generate `Answer_FR` (French answer term)

- **Input**: `Answer_LA` (Latin name) and `Answer_EN` (English name)
- **Output**: The standard French anatomical term
- **Rules**:
  - Use the official French equivalent from *Terminologia Anatomica* where available
  - Keep Latin terms that are used as-is in French medical terminology
  - Match the capitalization style of `Answer_EN` (typically lowercase except proper nouns)
  - Output is a short term/phrase, not a sentence
- **Example**:
  - Answer_LA: `arteria epigastrica inferior` → Answer_EN: `Inferior Epigastric a.` → **Answer_FR**: `artère épigastrique inférieure`

#### Task B: Generate `Description_EN` (English description)

- **Input**: `Description_DE` (German description), `Answer_LA`, `Answer_EN`
- **Output**: English anatomical description with equivalent detail and structure
- **Rules**:
  - Translate the full content of `Description_DE` into English
  - Preserve all `<em>` HTML tags around anatomical terms
  - Inside `<em>` tags, use the standard English (or Latin) anatomical term — do not transliterate the German term
  - Maintain the same sentence structure and level of detail
  - Use standard English anatomical terminology (e.g., *Terminologia Anatomica* English equivalents)
  - Do not add or remove information compared to the German source
- **Example**:
  - Input (DE): `Die <em>arteria epigastrica inferior</em> entspringt aus der <em>arteria iliaca externa</em>...`
  - Output (EN): `The <em>inferior epigastric artery</em> arises from the <em>external iliac artery</em>...`

#### Task C: Generate `Description_FR` (French description)

- **Input**: `Description_DE` (German description), `Answer_LA`, `Answer_FR` (once generated), and optionally `Description_EN` (once generated)
- **Output**: French anatomical description
- **Rules**:
  - Same rules as Task B but translating to French
  - Inside `<em>` tags, use standard French anatomical terms
  - If `Description_EN` has already been generated, it can serve as an additional reference
- **Example**:
  - Output (FR): `L'<em>artère épigastrique inférieure</em> naît de l'<em>artère iliaque externe</em>...`

#### Tasks D / E / F: Generate `Text_Question_EN` / `Text_Question_DE` / `Text_Question_FR`

- **Status**: source and generation strategy **to be decided**.
- Once decided, document input fields, output expectations, and example pairs here in the same format as Tasks A–C.

### Processing Approach

1. **Extract** cards from `deck.json` programmatically (use `analyze_deck.py` or similar)
2. **Batch** cards for LLM processing — group by section for consistent terminology within anatomical regions
3. **Prompt** the LLM with the card's existing fields and the rules above
4. **Validate** output: check that HTML tags are balanced, anatomical terms are consistent, and no fields were left empty
5. **Write back** the translated fields into `deck.json`

### Suggested LLM Prompt Template

```
You are a medical translator specializing in anatomy. Translate the following
anatomical flashcard fields.

Card context:
- Latin name: {Answer_LA}
- English name: {Answer_EN}
- German name: {Answer_DE}
- German description: {Description_DE}

Tasks:
1. Provide the French anatomical term (Answer_FR)
2. Translate the German description to English (Description_EN)
3. Translate the German description to French (Description_FR)

Rules:
- Use standard Terminologia Anatomica terms in each language
- Preserve all <em> HTML tags, placing the correct term for the target language inside
- Do not add or remove information
- Keep the same structure and level of detail as the German source

Return as JSON:
{"Answer_FR": "...", "Description_EN": "...", "Description_FR": "..."}
```
