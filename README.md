# Comprehensive Cadaver – Translations

This repository provides multilingual translations for the [Comprehensive Cadaver](https://www.reddit.com/r/medicalschoolanki/comments/1b5xt0q/comprehensivecadaver_the_ultimate_cadavericbased/) Anki deck, a cadaveric-image-based resource widely used by medical students for learning gross anatomy. The original deck covers anatomical structures through photographs of real cadaveric specimens, radiological images, and diagrams.

The translations currently cover **Latin (LA)**, **English (EN)**, **German (DE)**, and **French (FR)**, allowing learners to study in their preferred language or in parallel with the anatomical Latin nomenclature. Translated fields are delivered as a [CrowdAnki](https://github.com/Stvad/CrowdAnki) package that merges with an existing installation of the base deck while preserving your review history and scheduling data.

This repository also contains a transcription pipeline (Python + OpenAI vision) used to extract text from card images and seed the translation fields — see the technical setup section at the end if you are interested in contributing to that workflow.

## 1. Installing the Translations

### 1.1 Prerequisites

1. Install the [CrowdAnki](https://github.com/Stvad/CrowdAnki) add-on for Anki from [AnkiWeb](https://ankiweb.net/shared/info/1788670778).
2. Install the original [Comprehensive Cadaver](https://www.reddit.com/r/medicalschoolanki/comments/1b5xt0q/comprehensivecadaver_the_ultimate_cadavericbased/) deck in Anki.

### 1.2 Import from Disk

1. Clone or download this repository.
2. In Anki, go to **File → CrowdAnki: Import from disk**.
3. Select the repository root folder.
4. Import the changes.

### 1.3 Import from GitHub

1. In Anki, go to **File → CrowdAnki: Import git repository**.
2. Enter the repository URL: `https://github.com/commit-history/ComprehensiveCadaver`.

CrowdAnki will update the existing cards with the translated fields while preserving your scheduling data.

### 1.4 Media Files

Media files (images, audio) are **not tracked in this repository**. When you install the original [Comprehensive Cadaver](https://www.reddit.com/r/medicalschoolanki/comments/1b5xt0q/comprehensivecadaver_the_ultimate_cadavericbased/) deck (see 1.1), Anki adds the media to your collection —- the translations can be installed on top of the media files.

If you want to populate the `media/` folder in this repository (e.g. for backup or to make it self-contained), export the deck from Anki:

1. In Anki, go to **File → CrowdAnki: Snapshot** (or **CrowdAnki: Export** → choose **CrowdAnki JSON representation**).
2. Select the **ComprehensiveCadaver** deck.
3. Point the export destination to the folder containing this repository. CrowdAnki will copy the deck's media files into `media/`.

The files themselves stay ignored by git.

### 1.5 How It Works

The deck uses a single note type, **Image Q/A - ComprehensiveCadaver**, which extends the original Comprehensive Cadaver note with translation, plain-text, and description fields. This repository populates those added fields; the original image-based `Question` and `Answer`, along with `Keywords` and `Source`, are left untouched so your existing cards and review history remain intact on import.

Each note carries the following fields:

| Field              | Description |
|--------------------|-------------|
| `Question`         | Original question image reference from the base deck (untouched). |
| `Question_EN`      | Transcribed question in English, as HTML-formatted text. |
| `Question_DE`      | Translated question in German, as HTML-formatted text. |
| `Question_FR`      | Translated question in French, as HTML-formatted text. |
| `Text_Question_EN` | Plain-text English question, used where HTML rendering isn't available (e.g. TTS, field search). |
| `Text_Question_DE` | Plain-text German question. |
| `Text_Question_FR` | Plain-text French question. |
| `Answer`           | Original answer image reference from the base deck (untouched). |
| `Answer_LA`        | Latin answer text — see [Answer formatting from labels](#answer-formatting-from-labels). |
| `Answer_EN`        | English answer text — same formatting. |
| `Answer_DE`        | German answer text — same formatting. |
| `Answer_FR`        | French answer text — same formatting. |
| `Description_EN`   | Optional explanatory text in English, shown below the answer. |
| `Description_DE`   | Optional explanatory text in German. |
| `Description_FR`   | Optional explanatory text in French. |
| `Keywords`         | Original keywords from the base deck (untouched). |
| `Source`           | Original source reference from the base deck (untouched). |

Only the answer is translated into Latin; the Latin question is carried implicitly by the original `Question` image, which already labels structures using anatomical Latin nomenclature. Which languages actually render on the card is controlled by CSS classes — see [Section 2](#2-setting-the-language).


## 2. Setting the Language

1. Go to `Browse` → `Cards ...` → tab `Styling`. You will find the following lines of code:

```
.lang_de {}

.lang_en {display: none;}

.lang_fr {display: none;}

.lang_la {}
```

If you add `display: none` within the curly brackets `{...}`, that language will be hidden from the card. In the example above, Latin (`lang_la`) and German (`lang_de`) will display on the card while English (`lang_en`) and French (`lang_fr`) are hidden.

## 3. Contributing

If you want to contribute translations or corrections:

1. Make your changes to the cards in Anki.
2. Export the deck via **File → CrowdAnki: Export deck** and select the **Comprehensive Cadaver** deck.
3. Choose folder that contains this repository as the export destination (this will overwrite `deck.json` and update the `media` folder). The repository folder must be named `Comprehensive Cadaver`.
4. The media folder is never committed to keep this repository lean.
5. Commit your changes and open a pull request.

### 3.1 Rules

- Only modify translation-related fields. Do not change the original English content.
- Do not rearrange or rename subdecks.
- Place new media files in `media/`.
- Describe what you changed in your pull request.

## 4. Technical Setup

The following sections are only relevant if you want to run the transcription pipeline or otherwise work with the Python tooling in this repository. They are **not** required for installing or using the translated deck.

### 4.1 Python Setup

This project uses [uv](https://docs.astral.sh/uv/) to manage Python dependencies.

```bash
# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install dependencies (creates .venv automatically)
uv sync
```

All Python scripts should then be run with `uv run` to use the managed environment:

```bash
uv run python3 transcription/transcribe_images.py "Osteology: Upper Limb"
```

### 4.2 Transcription Pipeline

The `transcription/` directory contains scripts for transcribing text from card images and populating fields in `deck.json`. See [`transcription/transcription_schema.md`](transcription/transcription_schema.md) for the full JSON schema and details.

#### 4.2.1 Generate manifest

Build a manifest listing all images to transcribe for one or more decks:

```bash
# Single deck
uv run python3 transcription/transcribe_images.py "Osteology: Upper Limb"

# Multiple decks (combine into one manifest)
uv run python3 -c "
import json, sys
sys.path.insert(0, 'transcription')
from transcribe_images import build_manifest, get_pending

decks = [
    'Osteology: Upper Limb',
    'Osteology: Skull',
    'Osteology: Sternum and Ribs',
    'Osteology: Vertebral Column',
]

all_pending = []
for deck_name in decks:
    manifest = build_manifest(deck_name)
    pending = get_pending(manifest)
    all_pending.extend(pending)
    print(f'{deck_name}: {len(pending)} pending')

with open('/tmp/transcription_manifest.json', 'w') as f:
    json.dump(all_pending, f, indent=2, ensure_ascii=False)
print(f'Total: {len(all_pending)} images saved to /tmp/transcription_manifest.json')
"
```

#### 4.2.2 Run transcription (OpenAI vision API)

```bash
# Set your OpenAI API key
export OPENAI_API_KEY="sk-proj-..."

# Run transcription (idempotent — re-run to resume where you left off)
uv run python3 transcription/transcribe_with_openai.py
```

The script skips images that already have a `.json` in `media-transcriptions/`, so it is safe to interrupt and re-run at any time.

**Tuning** (edit constants at top of `transcribe_with_openai.py`):
- `MODEL` — default `gpt-4o-mini`
- `MAX_CONCURRENT` — default `15`, reduce to `5` if rate limited
- `detail` — default `low` (~3K tokens/image), set to `high` for better accuracy at ~13x token cost

#### 4.2.3 Fill deck.json from transcriptions

```bash
# Only fill empty Question_EN and Answer_EN fields (default)
uv run python3 transcription/fill_en_from_transcriptions.py

# Overwrite existing values
uv run python3 transcription/fill_en_from_transcriptions.py --overwrite

# Also fill Question_DE and Question_FR from the built-in vocabulary
uv run python3 transcription/fill_en_from_transcriptions.py --fill-german-question --fill-french-question

# Combine: overwrite all fields including translated questions
uv run python3 transcription/fill_en_from_transcriptions.py --overwrite --fill-german-question --fill-french-question

# Custom paths
uv run python3 transcription/fill_en_from_transcriptions.py \
  --deck path/to/deck.json \
  --transcriptions path/to/media-transcriptions
```

The script reads each note in `deck.json`, matches the question and answer images to their corresponding transcription files in `media-transcriptions/`, and fills in the `Question_EN` and `Answer_EN` fields.

The `--fill-german-question` and `--fill-french-question` flags additionally populate `Question_DE` and `Question_FR` using a built-in vocabulary dictionary (`QUESTIONS_EN_VOCAB`) that maps each unique English question to its German and French translation. To update translations, edit the dictionary directly in the script.

##### Answer formatting from labels

| Labels | Details | Result |
|--------|---------|--------|
| 1 label, no details | — | `Calcaneus` |
| 1 label, with details | 1 detail | `Pectineal Line \| Pectineus m.` |
| 1 label, with details | multiple | `Linea Aspera \| Adductor brevis m.; Adductor longus m.` |
| multiple labels, no details | — | `Ilium \| AIIS` |
| multiple labels, with details | mixed | `Ilium \| AIIS; Rectus femoris m.` |

`|` separates labels; `;` separates alternative names or multiple details. In multi-label cards the label-to-detail boundary uses `;` to avoid collision with the label separator.
