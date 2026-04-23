# Contributing

Thanks for helping extend the multilingual Comprehensive Cadaver deck!

## 1. How to Contribute

1. Make your changes to the cards in Anki.
2. Export the deck via **File → CrowdAnki: Export deck** and select the **Comprehensive Cadaver** deck.
3. Choose the folder that contains this repository as the export destination (this will overwrite `deck.json` and update the `media` folder). The repository folder must be named `Comprehensive Cadaver`.
4. The `media` folder is never committed, to keep this repository lean.
5. Commit your changes and open a pull request.

### 1.1 Rules

- Only modify translation-related fields. Do not change the original English content.
- Do not rearrange or rename subdecks.
- Place new media files in `media/`.
- Describe what you changed in your pull request.

## 2. Translation Progress

> Regenerate these numbers with `uv run python3 analyze_deck.py` (last update: 2026-04-23).

- **6,065 total cards** across 35 sections (7 regions)
- **54.4% of translation slots filled** (42,921 / 78,845)
- **35,924 translation slots remaining**

### 2.1 Field Completion Status

| Field                  | Filled | Missing   | Done   |
|------------------------|--------|-----------|--------|
| Question               | 6,065  | 0         | 100.0% |
| Question_EN            | 6,064  | 1         | ~100%  |
| Question_DE            | 6,064  | 1         | ~100%  |
| Question_FR            | 6,064  | 1         | ~100%  |
| **Text_Question_EN**   | **490**| **5,575** | **8.1%** |
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

### 2.2 Sections with `Text_Question_EN` completed

| Section                  | Cards | Status |
|--------------------------|-------|--------|
| Osteology: Lower Limb    | 226   | ✅ done |
| Osteology: Upper Limb    | 220   | ✅ done |
| Spinal Cord              | 37    | ✅ done |
| Pilot cards (scattered)  | ~7    | ✅ done |

All other 31 sections are pending for `Text_Question_EN`. Remaining sections by size (partial list): Osteology: Skull (325), Pelvic Cavity and Viscera (308), Perineum (306), Neck (292), Pharynx and Nasal Cavity (255), Orbit (251), Anterior Thorax, Axilla, and Anterior Arm (247), Forearm, Cubital Fossa, and Elbow Joint (227), Heart and Great Vessels (200), Osteology: Vertebral Column (194), Posterior Leg and Sole of Foot (187), Scalp, Face, and Parotid Region (187), Back (183), Posterior Abdominal Wall (180), Infratemporal Fossa (173), Pelvic Diaphragm (171), CT Scans: Abdomen (163), Posterior and Superior Mediastinum (162), Anterior Thigh (155), Cranial Nerves (149 remaining), Celiac Trunk (137), Thoracic Wall and Lungs (135), Larynx (122), Hip Joint / Gluteal (118), Anterior Abdominal Wall (95 remaining), Brain (95), Anterior Leg (90), Mesenteric Vessels (81), Oral Cavity (77), CT Scans: Thorax (65), Osteology: Sternum and Ribs (41). `Text_Question_DE` and `Text_Question_FR` are untouched in every section.

## 3. What Needs To Be Done

### 3.1 Priority 1: Six bulk translation tasks

~6,040 cards share the same pattern of six missing fields. The remaining ~25 have the same six missing plus one or two extra gaps (see 3.2).

| Task | Missing Field       | Source to translate from                   | Approx. Count |
|------|---------------------|--------------------------------------------|---------------|
| **A** | `Answer_FR`        | `Answer_EN` (or `Answer_LA`) → French     | 6,063 |
| **B** | `Description_EN`   | `Description_DE` → English                | 6,065 |
| **C** | `Description_FR`   | `Description_DE` → French                 | 6,063 |
| **D** | `Text_Question_EN` | `Description_DE` + `Answer_*` (see `todo_fill_text_question.md`) | 5,575 |
| **E** | `Text_Question_DE` | Mirror of Task D into German              | 6,065 |
| **F** | `Text_Question_FR` | Mirror of Task D into French              | 6,065 |

The full style guide, agent workflow, validation rules, and scaling approach for Task D live in [`todo_fill_text_question.md`](todo_fill_text_question.md). Use it as the handoff document for any new batch.

### 3.2 Priority 2: Fix scattered gaps (~27 non-bulk slots across ~22 cards)

| Field               | Missing | Notes |
|---------------------|---------|-------|
| Question_EN/DE/FR   | 1 each  | One card in "Heart and Great Vessels" |
| Answer_LA           | 1       | One card in "Osteology: Sternum and Ribs" |
| Answer_EN           | 15      | Mostly in "Osteology: Vertebral Column" |
| Answer_DE           | 4       | "Osteology: Lower Limb" (3), "Pharynx and Nasal Cavity" (1) |
| Description_DE      | 5       | "Osteology: Lower Limb" (4), "Pharynx and Nasal Cavity" (1) |

Find them with: `uv run python3 analyze_deck.py -v`

## 4. Field Semantics and Translation Strategy

Each card is an anatomy flashcard with an image-based question and answer:

- **Question** / **Question_EN** / **Question_DE** / **Question_FR**: The question prompt in the original language, English, German, and French. Usually short (e.g. "Identify the tagged structure.").
- **Text_Question_EN** / **Text_Question_DE** / **Text_Question_FR**: A descriptive, image-independent variant of the question. The full style guide lives in [`todo_fill_text_question.md`](todo_fill_text_question.md).
- **Answer** (index 7): An image showing the answer (HTML `<img>` tag).
- **Answer_LA**: The anatomical term in Latin (the standard international nomenclature, *Terminologia Anatomica*).
- **Answer_EN** / **Answer_DE** / **Answer_FR**: The common name for the structure in English, German, and French.
- **Description_EN** / **Description_DE** / **Description_FR**: A detailed anatomical description — origin, insertion, innervation, blood supply, relations, clinical significance. Written in rich HTML with `<em>` tags for anatomical terms.
- **Keywords**: Semicolon-separated keywords for search.
- **Source**: Attribution for the image.

### 4.1 Task A — Generate `Answer_FR` (French answer term)

- **Input**: `Answer_LA`, `Answer_EN`
- **Output**: Standard French anatomical term
- **Rules**:
  - Use the official French equivalent from *Terminologia Anatomica* where available.
  - Keep Latin terms that are used as-is in French medical terminology.
  - Match the capitalization style of `Answer_EN` (typically lowercase except proper nouns).
  - Output is a short term/phrase, not a sentence.
- **Example**: `arteria epigastrica inferior` / `Inferior Epigastric a.` → **`artère épigastrique inférieure`**

### 4.2 Task B — Generate `Description_EN` (English description)

- **Input**: `Description_DE`, `Answer_LA`, `Answer_EN`
- **Output**: English anatomical description with equivalent detail and structure
- **Rules**:
  - Translate the full content of `Description_DE` into English.
  - Preserve all `<em>` HTML tags around anatomical terms.
  - Inside `<em>` tags, use the standard English (or Latin) anatomical term — do not transliterate the German term.
  - Maintain the same sentence structure and level of detail.
  - Use standard English anatomical terminology (*Terminologia Anatomica* English equivalents).
  - Do not add or remove information compared to the German source.
- **Example**:
  - DE: `Die <em>arteria epigastrica inferior</em> entspringt aus der <em>arteria iliaca externa</em>…`
  - EN: `The <em>inferior epigastric artery</em> arises from the <em>external iliac artery</em>…`

### 4.3 Task C — Generate `Description_FR` (French description)

- **Input**: `Description_DE`, `Answer_LA`, `Answer_FR` (once generated), optionally `Description_EN` once available.
- **Output**: French anatomical description
- **Rules**: same as Task B but translating to French. Inside `<em>` tags, use standard French anatomical terms.
- **Example (FR)**: `L'<em>artère épigastrique inférieure</em> naît de l'<em>artère iliaque externe</em>…`

### 4.4 Tasks D / E / F — `Text_Question_*`

See [`todo_fill_text_question.md`](todo_fill_text_question.md) for the full task guide (style, banned wording, agent prompt template, validation, resume instructions). Current state: 490 / 6,065 English questions filled; German and French not started.

## 5. Processing Approach

1. **Extract** cards from `deck.json` programmatically (use `analyze_deck.py` or similar).
2. **Batch** by section — groups of cards from the same anatomical region keep terminology consistent.
3. **Prompt** an LLM (or sub-agent) with the card's existing fields and the rules above.
4. **Validate** output: HTML tags balanced, anatomical terms consistent, no empty fields.
5. **Write back** the translated fields into `deck.json` and open a PR.

### 5.1 Suggested LLM Prompt Template (Tasks A–C)

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
