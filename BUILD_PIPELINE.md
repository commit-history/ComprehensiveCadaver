# Build Pipeline: Cards → deck.json

This document describes how to convert individual card definition files into the final `deck.json` format that can be imported into Anki.

---

## 1. Overview

**Input:**
- Individual card JSON files (one per card)
- `decks.json` (deck hierarchy)
- Image files (JPEG/PNG)

**Output:**
- `deck.json` (CrowdAnki format, ready for Anki import)
- Media files organized in `media/` folder

**Process:**
```
Card files      │
decks.json      ├──> Build Pipeline ──> deck.json + media/
Images          │
```

---

## 2. Card File Organization

```
cards/
  abdomen/
    vessels/
      AbdomenCeliac_Anterior.json
      AbdomenCeliac_Posterior.json
      AbdomenSMA_Anterior.json
    nerves/
      AbdomenVagus_Anterior.json
    organs/
      AbdomenLiver_Anterior.json
  upper-limb/
    osteology/
      UpperLimbHumerus_Anterior.json
      UpperLimbRadius_Anterior.json
    nerves/
      UpperLimbBrachialPlexus_Anterior.json
  ...

images/
  abdomen/
    celiac_anterior.jpg
    celiac_posterior.jpg
    sma_anterior.jpg
  upper-limb/
    humerus_anterior.jpg
    radius_anterior.jpg
  ...

decks.json
```

---

## 3. Build Process

### Step 1: Validate Input

**Check all card files:**
- All required fields present (id, title, deck, subdeck, cards, image)
- Card IDs are unique
- Image files exist
- Annotation bounds within image dimensions
- At least one language per text field

**Check deck hierarchy:**
- All referenced deck/subdeck IDs match decks.json
- All cardIds in subdecks match actual card files
- No orphaned cards (cards not in any subdeck)

### Step 2: Parse Cards

**Load all card JSON files:**
```python
cards = {}
for deck_folder in cards/:
    for subdeck_folder in deck_folder:
        for card_file in subdeck_folder:
            card = json.load(card_file)
            cards[card['id']] = card
```

### Step 3: Copy Images

**Copy all images to `media/`:**
```
images/abdomen/celiac_anterior.jpg
  → media/abdomen_celiac_anterior.jpg

images/upper-limb/humerus_anterior.jpg
  → media/upper-limb_humerus_anterior.jpg
```

**Generate image filename mapping:**
```python
image_map = {
  'abdomen/celiac_anterior.jpg': 'abdomen_celiac_anterior.jpg',
  'upper-limb/humerus_anterior.jpg': 'upper-limb_humerus_anterior.jpg',
  ...
}
```

### Step 4: Create Note Type

**Add a custom note type to the deck:**
```json
{
  "name": "Image Q/A - ComprehensiveCadaver",
  "type": 0,
  "flds": [
    {"name": "Question", "ord": 0},
    {"name": "Question_EN", "ord": 1},
    {"name": "Question_DE", "ord": 2},
    {"name": "Question_FR", "ord": 3},
    {"name": "Question_PL", "ord": 4},
    {"name": "Question_LA", "ord": 5},
    {"name": "Answer", "ord": 6},
    {"name": "Answer_EN", "ord": 7},
    {"name": "Answer_DE", "ord": 8},
    {"name": "Answer_FR", "ord": 9},
    {"name": "Answer_PL", "ord": 10},
    {"name": "Answer_LA", "ord": 11},
    {"name": "Description_EN", "ord": 12},
    {"name": "Description_DE", "ord": 13},
    {"name": "Description_FR", "ord": 14},
    {"name": "Description_PL", "ord": 15},
    {"name": "Keywords", "ord": 16},
    {"name": "Source", "ord": 17}
  ],
  "tmpls": [
    {
      "name": "Card 1",
      "qfmt": "...",  // Front template (with language toggle)
      "afmt": "..."   // Back template (with language toggle)
    }
  ]
}
```

### Step 5: Convert Cards to Notes

**For each card definition:**
1. Create an Anki note
2. Populate fields from card data:
   - `Question` → card image reference (front side image)
   - `Question_EN/DE/FR/PL/LA` → card.cards[0].text[lang]
   - `Answer` → card image reference (back side image)
   - `Answer_EN/DE/FR/PL/LA` → card.cards[1].text[lang]
   - `Description_*` → (empty, or from future description field)
   - `Keywords` → comma-separated tags
   - `Source` → card.credits.source

**Image field format (CrowdAnki):**
```html
<img src="abdomen_celiac_anterior.jpg" />
<!-- or with rendered annotations (future) -->
```

**Note structure:**
```json
{
  "guid": "unique-guid-for-cardid",
  "fields": [
    "<img src=\"abdomen_celiac_anterior.jpg\" />",  // Question
    "Identify the vessel highlighted on the anterior view...",  // Question_EN
    "Identifizieren Sie das hervorgehobene Blutgefäß...",      // Question_DE
    "Identifier le vaisseau mis en évidence...",                // Question_FR
    "Zidentyfikuj naczynia podświetlone...",                    // Question_PL
    "Identifica vas luminis...",                                 // Question_LA
    "<img src=\"abdomen_celiac_anterior.jpg\" />",  // Answer
    "Celiac Trunk (Truncus coeliacus) - branches...",           // Answer_EN
    "Zöliakalstamm - verzweigt sich in...",                     // Answer_DE
    "Tronc coeliaque - se divise en...",                        // Answer_FR
    "Pień trzewny - rozgałęzia się na...",                      // Answer_PL
    "Truncus coeliacus - rami in...",                           // Answer_LA
    "",                                                          // Description_EN
    "",                                                          // Description_DE
    "",                                                          // Description_FR
    "",                                                          // Description_PL
    "artery, vessel, abdominal",                                 // Keywords
    "Comprehensive Cadaver"                                      // Source
  ],
  "tags": ["abdomen::vessels::celiac"],
  "modelName": "Image Q/A - ComprehensiveCadaver"
}
```

### Step 6: Create Deck Structure

**Organize notes into subdecks:**

```
ComprehensiveCadaver/
  Abdomen/
    Vessels/
      Celiac Trunk
      SMA Trunk
      ...
    Nerves/
      Vagus Nerve
      ...
    Organs/
      Liver
      ...
  Upper Limb/
    Osteology/
      Humerus
      Radius
      ...
    Nerves/
      Brachial Plexus
      ...
  Head and Neck/
    Brain/
      ...
```

**In deck.json:**
```json
{
  "name": "ComprehensiveCadaver",
  "subdecks": [
    {
      "name": "Abdomen",
      "subdecks": [
        {
          "name": "Vessels",
          "cards": [
            { "id": "..." },  // Celiac note
            { "id": "..." }   // SMA note
          ]
        },
        {
          "name": "Nerves",
          "cards": [...]
        }
      ]
    },
    {
      "name": "Upper Limb",
      "subdecks": [...]
    }
  ]
}
```

### Step 7: Add Metadata

**Deck-level metadata (in deck.json root):**
```json
{
  "name": "ComprehensiveCadaver",
  "desc": "Comprehensive cadaver-based anatomy with language translations",
  "vers": 1,
  "muid": 1234567890,
  "usn": -1,
  "ls": 0,
  "nextpos": 1,
  "conf": {
    "id": 1,
    "name": "Default",
    // ... rest of deck config
  }
}
```

---

## 4. Annotation Rendering (Future)

Currently, annotations are stored in card definitions but not rendered in Anki. Future enhancement:

**Option A: Server-side rendering**
- When building deck.json, render annotations onto image
- Save rendered image to media/
- Reference rendered image in card

**Option B: Client-side rendering**
- Store annotation data in card field
- Anki template renders annotations client-side (JavaScript)
- Requires Anki JavaScript support (limited)

**Option C: Hybrid**
- Render labels and overlays server-side
- Render arrows as SVG overlay in template

---

## 5. Build Script

**Python build script pseudocode:**

```python
import json
import os
import shutil
from pathlib import Path
from uuid import uuid4

def build_deck(cards_dir, images_dir, decks_file, output_file):
    """
    Build deck.json from card definitions.
    
    Args:
        cards_dir: Path to cards/ directory
        images_dir: Path to images/ directory
        decks_file: Path to decks.json
        output_file: Output deck.json path
    """
    
    # Step 1: Load deck hierarchy
    with open(decks_file) as f:
        decks_structure = json.load(f)
    
    # Step 2: Load all cards
    cards = load_cards(cards_dir)
    
    # Step 3: Validate
    validate_cards(cards, decks_structure)
    
    # Step 4: Copy images and build filename map
    image_map = copy_images(images_dir, './media')
    
    # Step 5: Convert cards to notes
    notes = []
    for card_id, card in cards.items():
        note = card_to_note(card, image_map)
        notes.append(note)
    
    # Step 6: Build deck structure
    deck_json = build_deck_json(decks_structure, notes, cards)
    
    # Step 7: Write output
    with open(output_file, 'w') as f:
        json.dump(deck_json, f, indent=2, ensure_ascii=False)
    
    print(f"✓ Built deck.json with {len(notes)} notes")
    print(f"✓ Copied {len(image_map)} images to media/")

def load_cards(cards_dir):
    """Load all card JSON files recursively."""
    cards = {}
    for root, dirs, files in os.walk(cards_dir):
        for file in files:
            if file.endswith('.json'):
                path = os.path.join(root, file)
                with open(path) as f:
                    card = json.load(f)
                    cards[card['id']] = card
    return cards

def validate_cards(cards, decks_structure):
    """Validate all cards against deck structure."""
    # Check for orphaned cards
    all_deck_card_ids = set()
    for deck in decks_structure['decks']:
        for subdeck in deck.get('subdecks', []):
            all_deck_card_ids.update(subdeck['cardIds'])
    
    card_ids = set(cards.keys())
    orphaned = card_ids - all_deck_card_ids
    if orphaned:
        raise ValueError(f"Orphaned cards: {orphaned}")
    
    missing = all_deck_card_ids - card_ids
    if missing:
        raise ValueError(f"Missing cards: {missing}")
    
    # Check card validity
    for card in cards.values():
        assert 'id' in card
        assert 'title' in card
        assert 'cards' in card and len(card['cards']) == 2
        assert card['cards'][0]['side'] == 'front'
        assert card['cards'][1]['side'] == 'back'

def copy_images(images_dir, media_dir):
    """Copy images to media folder, return filename map."""
    os.makedirs(media_dir, exist_ok=True)
    image_map = {}
    
    for root, dirs, files in os.walk(images_dir):
        for file in files:
            if file.endswith(('.jpg', '.jpeg', '.png')):
                src = os.path.join(root, file)
                # Create flat filename: subdirs -> underscores
                rel_path = os.path.relpath(src, images_dir)
                flat_name = rel_path.replace(os.sep, '_')
                dst = os.path.join(media_dir, flat_name)
                shutil.copy2(src, dst)
                image_map[rel_path] = flat_name
    
    return image_map

def card_to_note(card, image_map):
    """Convert card definition to Anki note."""
    front_img = image_map[card['image']['path']]
    back_img = front_img  # Same image on both sides for now
    
    # Get text for each language
    front_text = card['cards'][0]['text']
    back_text = card['cards'][1]['text']
    
    # Create note
    note = {
        "guid": f"card-{card['id']}",
        "fields": [
            f"<img src=\"{front_img}\" />",
            front_text.get('EN', ''),
            front_text.get('DE', ''),
            front_text.get('FR', ''),
            front_text.get('PL', ''),
            front_text.get('LA', ''),
            f"<img src=\"{back_img}\" />",
            back_text.get('EN', ''),
            back_text.get('DE', ''),
            back_text.get('FR', ''),
            back_text.get('PL', ''),
            back_text.get('LA', ''),
            '',  # Description_EN
            '',  # Description_DE
            '',  # Description_FR
            '',  # Description_PL
            ','.join(card.get('tags', [])),
            card.get('credits', {}).get('source', '')
        ],
        "tags": [f"{card['deck']}::{card['subdeck']}"],
        "modelName": "Image Q/A - ComprehensiveCadaver"
    }
    
    return note

def build_deck_json(decks_structure, notes, cards):
    """Assemble final deck.json."""
    # Map notes by card ID for easy lookup
    notes_map = {note['guid'].replace('card-', ''): note for note in notes}
    
    def build_deck_recursive(deck_def):
        deck = {
            'id': uuid4().int,
            'name': deck_def['name'],
            'desc': deck_def.get('description', ''),
            'cards': [],
            'subdecks': []
        }
        
        # Add subdecks
        for subdeck_def in deck_def.get('subdecks', []):
            subdeck = build_deck_recursive(subdeck_def)
            
            # Add notes for this subdeck
            for card_id in subdeck_def['cardIds']:
                if card_id in notes_map:
                    subdeck['cards'].append(notes_map[card_id])
            
            deck['subdecks'].append(subdeck)
        
        return deck
    
    # Build main deck
    main_deck = {
        'name': 'ComprehensiveCadaver',
        'desc': 'Comprehensive cadaver-based anatomy with language translations',
        'vers': 1,
        'muid': 1234567890,
        'usn': -1,
        'ls': 0,
        'nextpos': 1,
        'conf': {
            'id': 1,
            'name': 'Default',
            'lapse': {},
            'rev': {},
            'timer': 0,
            'maxTaken': 60,
            'new': {},
            'dyn': False,
            'autoplay': True,
            'replayq': True,
            'usn': -1
        },
        'decks': []
    }
    
    # Add subdecks
    for deck_def in decks_structure['decks']:
        deck = build_deck_recursive(deck_def)
        main_deck['decks'].append(deck)
    
    return main_deck

if __name__ == '__main__':
    build_deck('./cards', './images', './decks.json', './deck.json')
```

---

## 6. Running the Build

**Command:**
```bash
python build_deck.py
```

**Output:**
```
Validating cards...
  ✓ 247 cards found
  ✓ All cards referenced in deck hierarchy
  ✓ All required fields present

Building deck...
  ✓ Copied 247 images to media/
  ✓ Converted 247 cards to notes
  ✓ Organized into 12 decks, 34 subdecks

Writing output...
  ✓ Built deck.json (1.2 MB)

Build complete!
```

---

## 7. Integration with Anki

**Import into Anki:**
1. Place `deck.json` in project root
2. In Anki: File → CrowdAnki: Import from disk
3. Select project folder
4. CrowdAnki merges cards with existing deck

**Update existing deck:**
- Re-run build script
- Re-import deck.json via CrowdAnki
- CrowdAnki updates matching cards by GUID
- User review history preserved

---

## Notes

- Build script should be idempotent (safe to run multiple times)
- Image filenames flattened to avoid nested media folders
- Each card gets unique GUID based on card ID
- Tags stored in Anki format: `deck::subdeck`
- All text fields optional except one language per field
