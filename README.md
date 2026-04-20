# Comprehensive Cadaver – Translations

This repository contains translated cards for the [Comprehensive Cadaver](https://www.reddit.com/r/medicalschoolanki/comments/1b5xt0q/comprehensivecadaver_the_ultimate_cadavericbased/) Anki deck, managed with [CrowdAnki](https://github.com/Stvad/CrowdAnki).

## Setup

1. Install the [CrowdAnki](https://github.com/Stvad/CrowdAnki) add-on for Anki from [AnkiWeb](https://ankiweb.net/shared/info/1788670778).
2. Install the original [Comprehensive Cadaver](https://www.reddit.com/r/medicalschoolanki/comments/1b5xt0q/comprehensivecadaver_the_ultimate_cadavericbased/) deck in Anki.

## Importing the Translations

After you have the Comprehensive Cadaver deck installed, import the translations using one of the following methods:

### Import from Disk

1. Clone or download this repository.
2. In Anki, go to **File → CrowdAnki: Import from disk**.
3. Select the repository root folder
4. Import the cahnges

### Import from GitHub

1. In Anki, go to **File → CrowdAnki: Import git repository**.
2. Enter the repository URL: `https://github.com/commit-history/ComprehensiveCadaver

CrowdAnki will update the existing cards with the translated fields while preserving your scheduling data.

## Setting the language

1. Go to `Browse` -> `Cards ...` -> Tab `Styling`. You will find the following lines of code:
```
.lang_de {}

.lang_en {display: none;}

.lang_fr {display: none;}

.lang_la {}
```
if you add `display: none` within the curly brackets `{...}` , the language will be hidden from the card. In the case above, the languages Latin (`lang_la`) and Deutsch (`lang_de`) will display on the card and the languages English (`lang_en`) and Français (`lang_fr`) will be hidden.

## Contributing

If you want to contribute translations or corrections:

1. Make your changes to the cards in Anki.
2. Export the deck via **File → CrowdAnki: Export deck** and select the **Comprehensive Cadaver** deck.
3. Choose the top level folder folder in this repository as the export destination (this will overwrite `deck.json` and update the `media` folder).
4. The media folder is never commited to keep this repository lean.
5. Commit your changes and open a pull request.

### Rules

- Only modify translation-related fields. Do not change the original English content.
- Do not rearrange or rename subdecks.
- Place new media files in `media/`.
- Describe what you changed in your pull request.

## Python Setup

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

## Transcription Pipeline

The `transcription/` directory contains scripts for transcribing text from card images and populating fields in `deck.json`. See [`transcription/transcription_schema.md`](transcription/transcription_schema.md) for the full JSON schema and details.

### 1. Generate manifest

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

### 2. Run transcription (OpenAI vision API)

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

### 3. Fill deck.json from transcriptions

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

**Answer formatting from labels:**

| Labels | Details | Result |
|--------|---------|--------|
| 1 label, no details | — | `Calcaneus` |
| 1 label, with details | 1 detail | `Pectineal Line \| Pectineus m.` |
| 1 label, with details | multiple | `Linea Aspera \| Adductor brevis m.; Adductor longus m.` |
| multiple labels, no details | — | `Ilium \| AIIS` |
| multiple labels, with details | mixed | `Ilium \| AIIS; Rectus femoris m.` |

`|` separates labels; `;` separates alternative names or multiple details. In multi-label cards the label-to-detail boundary uses `;` to avoid collision with the label separator.

