# Media Transcription Schema

This document describes the process and JSON schema for transcribing text from ComprehensiveCadaver card images.

## Overview

Each card has two images:
- **Question image** (field[0]): Shows an anatomy photo with a question prompt and a tagged structure
- **Answer image** (field[4]): Shows the same photo with labeled structures and details

Images are transcribed into structured JSON files stored in `media-transcriptions/`.

## JSON Schema

### Question Image

```json
{
  "file": "OsteologyLowerLimb1.jpeg",
  "type": "question",
  "question_en": "What is the origin and insertion of the tagged structure?",
  "title": "Anterior View of Right Femur",
  "attribution": "Modified from Anatomy: A Photographic Atlas (8th Ed.). © 2016 Schattauer GmbH and Wolters Kluwer."
}
```

**Fields:**
- `file`: Image filename (must match exactly)
- `type`: Always `"question"`
- `question_en`: The question text shown in the image. Transcribe exactly as written, preserving bold markers if meaningful.
- `title`: The anatomical view/caption shown below or near the image (if present)
- `attribution`: Source/copyright text (if present)

### Answer Image

```json
{
  "file": "OsteologyLowerLimb2.jpeg",
  "type": "answer",
  "answer_en": "Greater trochanter <br> Origin of gluteus medius and gluteus minimus <br> Insertion of piriformis and obturator internus",
  "labels": [
    {
      "text": "Greater trochanter",
      "note": "",
      "details": [
        "Origin of gluteus medius and gluteus minimus",
        "Insertion of piriformis and obturator internus"
      ]
    }
  ],
  "title": "Anterior View of Right Femur",
  "subtitle": "",
  "orientation": "Superior (top), Inferior (bottom), Medial (left), Lateral (right)",
  "attribution": "Modified from Anatomy: A Photographic Atlas (8th Ed.). © 2016 Schattauer GmbH and Wolters Kluwer."
}
```

**Fields:**
- `file`: Image filename
- `type`: Always `"answer"`
- `answer_en`: Flattened text of all labels. Construction rules:
  - Primary label text first
  - Parenthetical notes appended after the label
  - Each detail line (Origin, Insertion, etc.) separated by ` <br> `
  - Multiple labels separated by ` <br> `
- `labels`: Array of structured label objects:
  - `text`: The primary label/structure name
  - `note`: Parenthetical note, e.g. "(Removed on right side)". Empty string if none.
  - `details`: Array of detail strings (Origin, Insertion, bullet points, etc.). Empty array if none.
- `title`: Anatomical view caption (if present)
- `subtitle`: Secondary caption text (if present). Empty string if none.
- `orientation`: Orientation compass if present, format: "Direction (position), ...". Empty string if none.
- `attribution`: Source/copyright text (if present)

## Scripts

### `transcribe_images.py`

Generates a manifest of images to transcribe for a given deck. The manifest lists all question/answer images and their paths.

```bash
# Generate manifest for a single deck (run from project root)
python3 transcription/transcribe_images.py "Osteology: Upper Limb"
```

To generate a manifest for multiple decks at once, run the script for each deck sequentially — **note: each run overwrites `/tmp/transcription_manifest.json`**, so combine them with a small Python snippet:

```python
# Generate combined manifest for multiple decks
python3 -c "
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

### `transcribe_with_openai.py`

Reads the manifest and transcribes each image using the OpenAI GPT-4o-mini vision API. Writes one JSON file per image to `media-transcriptions/`.

```bash
# Prerequisites
pip install openai

# Set your API key (or hardcode it in the script)
export OPENAI_API_KEY="sk-proj-..."

# Run transcription
python3 transcription/transcribe_with_openai.py
```

**Configuration** (edit constants at top of script):
- `MODEL` — OpenAI model to use (default: `gpt-4o-mini`)
- `MAX_CONCURRENT` — parallel requests (default: `15`, reduce to `5` if rate limited)
- `detail` — image detail level in the API call (default: `low`, use `high` for better accuracy at ~13x token cost)

**Resuming:** The script is fully idempotent — it skips any image that already has a `.json` file in `media-transcriptions/`. Just re-run the same command to resume where you left off. No need to regenerate the manifest unless you want to add new decks.

### `update_deck_from_transcriptions.py`

Reads completed transcription JSONs and updates deck.json fields.

```bash
# Update Question_EN and Answer_EN from transcriptions (run from project root)
python3 transcription/update_deck_from_transcriptions.py "Osteology: Lower Limb"
```

## Full process

```bash
# 1. Generate manifest for the decks you want to transcribe
python3 transcription/transcribe_images.py "Osteology: Upper Limb"
#    (or use the multi-deck snippet above)

# 2. Run the OpenAI transcription (idempotent — safe to re-run / resume)
export OPENAI_API_KEY="sk-proj-..."
python3 transcription/transcribe_with_openai.py

# 3. Review transcriptions in media-transcriptions/

# 4. Update deck.json with the transcribed text
python3 transcription/update_deck_from_transcriptions.py "Osteology: Upper Limb"
```

## Notes

- The OpenAI script uses `detail: low` by default (~3K tokens/image, ~$0.40/1K images with gpt-4o-mini). Use `detail: high` (~37K tokens/image) for better accuracy on small text, but expect heavier rate limiting.
- Rate limits are handled automatically with exponential backoff and up to 5 retries per image.
- If heavily rate limited, reduce `MAX_CONCURRENT` (try `5` or even `3`).
- The manifest is stored at `/tmp/transcription_manifest.json` — this is a temp file. If the server reboots, regenerate it with `transcribe_images.py`.

## Stats

- **Osteology: Lower Limb** (pilot): 452 images, ~943k total tokens, ~5 min wall-clock (Claude Code agents)
- **OpenAI gpt-4o-mini (low detail)**: ~8 images/min at concurrency 15, ~3K tokens/image
