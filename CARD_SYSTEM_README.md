# Card Definition System — Documentation

Complete reference for the anatomical card creation, editing, and building system.

---

## Overview

This system enables non-technical users to create multilingual, annotated anatomical cards and automatically generate Anki decks.

**Three main components:**
1. **Data Models** — How cards and decks are structured
2. **Web UI** — Interface for creating/editing cards
3. **Build Pipeline** — Convert cards → Anki deck

---

## Documentation Index

### 1. **[DATA_MODEL.md](DATA_MODEL.md)** — Data Structures
   
   Defines the complete data model with examples:
   - **Deck Model** (decks.json) — Deck hierarchy
   - **Card Model** (individual JSON files) — Card definitions
   - **File Layout** — Directory organization
   - **View Axes** — 16 anatomical view directions
   - **Tag Taxonomy** — Standard tags for filtering
   
   **Start here if:** You're setting up a new deck or understanding the data structure.

### 2. **[UI_REQUIREMENTS.md](UI_REQUIREMENTS.md)** — Web Interface Specification

   Complete UI design with wireframes:
   - **Layout** — Sidebar, card list, editor
   - **Deck Navigation** — Hierarchical tree with search
   - **Card Editor** — Front/Back tabs with multi-language support
   - **Annotation Tools** — Visual editor for labels, arrows, overlays
   - **Filters & Search** — Find cards by deck, tags, translation status
   - **Interaction Patterns** — How users create/edit cards
   - **Keyboard Shortcuts** — Power user features
   - **Mobile Responsive** — Tablet/mobile layouts
   
   **Start here if:** You're building the web UI or want to understand user workflows.

### 3. **[BUILD_PIPELINE.md](BUILD_PIPELINE.md)** — From Cards to Anki

   The automated process for generating deck.json:
   - **Overview** — Input/output/process
   - **Build Steps** — Validation, image copying, note conversion
   - **Note Structure** — How cards become Anki notes
   - **Deck Organization** — Subdeck hierarchy in Anki
   - **Build Script** — Complete Python pseudocode
   - **Integration** — Importing into Anki via CrowdAnki
   
   **Start here if:** You're implementing the build pipeline or deploying to Anki.

### 4. **[ARCHITECTURE.md](ARCHITECTURE.md)** — System Design

   High-level overview of the entire system:
   - **System Diagram** — Data flow from PPT → Anki
   - **Core Components** — UI, data models, build pipeline
   - **File Organization** — Directory structure rationale
   - **Data Validation** — What's checked and when
   - **Design Decisions** — Why choices were made
   - **Development Workflow** — Step-by-step for adding cards
   - **Technology Stack** — Recommended tools
   - **Future Enhancements** — Planned features
   
   **Start here if:** You're new to the system or need the big picture.

### 5. **[CARD_SCHEMA_V3.json](card_schema_v3.json)** — JSON Schema

   Formal schema definition for card validation:
   - All card properties and their types
   - Required vs. optional fields
   - Annotation types (label, arrow, overlay)
   - Enum values (views, languages)
   
   **Use this to:** Validate card files or auto-complete in editors.

### 6. **[card_example_v3.json](card_example_v3.json)** — Example Card

   Complete working example with all features:
   - Multilingual text (5 languages)
   - All 3 annotation types
   - Bounding boxes, colors, styling
   
   **Use this as:** Template for creating new cards.

---

## Quick Start

### For Content Creators

1. Read: **[UI_REQUIREMENTS.md](UI_REQUIREMENTS.md)** sections 1-4
2. Use the web UI to create/edit cards
3. The system auto-saves to `cards/{deck}/{subdeck}/{cardId}.json`

### For Developers

1. Read: **[ARCHITECTURE.md](ARCHITECTURE.md)** for the big picture
2. Read: **[DATA_MODEL.md](DATA_MODEL.md)** to understand data structures
3. Read: **[UI_REQUIREMENTS.md](UI_REQUIREMENTS.md)** to build the web UI
4. Read: **[BUILD_PIPELINE.md](BUILD_PIPELINE.md)** to implement the build script

### For Anki Integration

1. Have web UI create cards in `cards/` directory
2. Run the build pipeline: `python build_deck.py`
3. In Anki: File → CrowdAnki: Import from disk
4. Select project root folder

---

## Directory Structure

```
ComprehensiveCadaver/
├── ARCHITECTURE.md                  (System overview)
├── BUILD_PIPELINE.md                (Build process)
├── CARD_SYSTEM_README.md            (This file)
├── DATA_MODEL.md                    (Data structures)
├── UI_REQUIREMENTS.md               (UI specification)
├── card_schema_v3.json              (JSON schema)
├── card_example_v3.json             (Example card)
│
├── decks.json                       (Deck hierarchy — single source of truth)
│
├── cards/                           (Individual card definitions)
│   ├── abdomen/
│   │   ├── vessels/
│   │   │   ├── AbdomenCeliac_Anterior.json
│   │   │   └── AbdomenCeliac_Posterior.json
│   │   ├── nerves/
│   │   └── organs/
│   ├── upper-limb/
│   ├── head-and-neck/
│   └── ...
│
├── images/                          (Source images for cards)
│   ├── abdomen/
│   │   ├── vessels/
│   │   │   ├── celiac_anterior.jpg
│   │   │   └── celiac_posterior.jpg
│   │   ├── nerves/
│   │   └── organs/
│   ├── upper-limb/
│   └── ...
│
├── deck.json                        (Generated by build pipeline)
├── media/                           (Generated media files for Anki)
│
└── build_deck.py                    (Build pipeline script)
```

---

## Key Concepts

### Cards vs. Decks

- **Card**: One anatomical structure from one view (e.g., "Celiac Trunk - Anterior")
  - Front: Question image + multilingual question text
  - Back: Answer image + multilingual answer + annotations
  
- **Deck**: Hierarchical organization (Deck → Subdeck → Cards)
  - Reflects study structure (Abdomen → Vessels → [Celiac, SMA, ...])
  - Defined once in `decks.json`, referenced by cards

### Annotations

Three types of visual markings on the answer image:

1. **Label**: Text with bounding box (auto-scales to fit)
2. **Arrow**: Line from origin to target, with optional label
3. **Overlay**: Polygon region highlighting, with color/opacity

All support multilingual text.

### Translations

Each text field can have up to 5 languages:
- **EN** — English
- **DE** — German
- **FR** — French
- **PL** — Polish
- **LA** — Latin (anatomical nomenclature)

Translation completeness is tracked per card:
- **Complete**: All languages present
- **Partial**: Some languages present
- **Missing**: No translation for language

### Views

16 anatomical view axes (must pick exactly one per card):

**Directional (6):**
- Anterior, Posterior, Superior, Inferior, Left, Right

**Anatomical (10):**
- Medial, Lateral, Axial, Sagittal, Coronal, Transverse, Dorsal, Ventral, Deep, Superficial

### Tags

Flexible labels for filtering cards. Suggested taxonomy:

**Type:** artery, vein, nerve, muscle, bone, organ, ...
**System:** cardiovascular, nervous, musculoskeletal, ...
**Region:** abdominal, thoracic, cervical, ...
**Relationship:** major-vessel, innervation, vascularization, ...

---

## Data Formats

### Card JSON Structure (Simplified)

```json
{
  "id": "AbdomenCeliac_Anterior",
  "title": "Celiac Trunk",
  "deck": "abdomen",
  "subdeck": "abdomen-vessels",
  "tags": ["artery", "major-vessel"],
  "image": {
    "path": "images/abdomen/celiac_anterior.jpg",
    "width": 800,
    "height": 600
  },
  "view": "Anterior",
  "cards": [
    {
      "side": "front",
      "text": {
        "EN": "Identify the vessel highlighted...",
        "DE": "Identifizieren Sie das Gefäß..."
      },
      "annotations": []
    },
    {
      "side": "back",
      "text": {
        "EN": "Celiac Trunk - branches into...",
        "DE": "Zöliakalstamm - verzweigt sich..."
      },
      "annotations": [
        {
          "id": "ann_1",
          "type": "label",
          "text": {"EN": "Celiac Trunk", "DE": "Zöliakalstamm"},
          "bounds": {"topLeft": {"x": 320, "y": 140}, "bottomRight": {"x": 480, "y": 180}}
        }
      ]
    }
  ]
}
```

### Deck Hierarchy (Simplified)

```json
{
  "decks": [
    {
      "id": "abdomen",
      "name": "Abdomen",
      "subdecks": [
        {
          "id": "abdomen-vessels",
          "name": "Vessels",
          "cardIds": ["AbdomenCeliac_Anterior", "AbdomenSMA_Anterior"]
        }
      ]
    }
  ]
}
```

---

## Common Tasks

### Adding a New Card

1. **Create structure:**
   ```
   cards/abdomen/vessels/AbdomenNewVessel_Anterior.json
   images/abdomen/vessels/new_vessel_anterior.jpg
   ```

2. **Create card JSON** (copy card_example_v3.json as template)

3. **Update decks.json:**
   ```json
   "cardIds": [..., "AbdomenNewVessel_Anterior"]
   ```

4. **Run build:**
   ```bash
   python build_deck.py
   ```

### Adding a Translation

1. Open card in web UI
2. Click "Add Language" (e.g., German)
3. Type translated text
4. Save (web UI writes updated JSON)
5. Run build pipeline
6. Re-import to Anki

### Creating a New Subdeck

1. **Update decks.json:**
   ```json
   {
     "id": "abdomen-organs",
     "name": "Organs",
     "cardIds": []
   }
   ```

2. **Create directory:**
   ```bash
   mkdir -p cards/abdomen/organs
   mkdir -p images/abdomen/organs
   ```

3. Add cards to the subdeck

4. Run build pipeline

---

## Validation

### Build-time Checks (by build_deck.py)

- Card files have all required fields
- Image files exist and are referenced correctly
- Card IDs are unique
- All cardIds in decks.json match actual cards
- No orphaned cards
- Annotation bounds within image dimensions

### Runtime Checks (by web UI)

- Text fields have at least one language
- Card ID is unique
- View axis is valid
- Annotation coordinates valid
- Deck/subdeck references valid

---

## Troubleshooting

### Card not appearing in web UI?

- Check `decks.json` includes card ID in appropriate subdeck
- Verify JSON file is valid (`python -m json.tool` to validate)
- Verify file path matches: `cards/{deck}/{subdeck}/{id}.json`

### Image not loading?

- Check image path in card JSON: `images/{deck}/{subdeck}/{filename}`
- Verify image file exists and is readable
- Check image format (JPEG or PNG supported)

### Build pipeline fails?

- Run with verbose output: `python build_deck.py --verbose`
- Check card JSON syntax: `python -m json.tool cards/*/*/}`
- Verify all image references point to existing files
- Check deck.json has valid structure

### Anki import fails?

- Ensure deck.json is valid JSON (CrowdAnki strict format)
- Clear Anki cache before re-importing
- Check card GUIDs are unique
- Verify media files are in `media/` folder (flat structure)

---

## Glossary

| Term | Definition |
|------|-----------|
| **Card** | Single anatomical learning unit (front question + back answer) |
| **Deck** | Top-level collection (e.g., "Abdomen", "Upper Limb") |
| **Subdeck** | Second-level organization within deck (e.g., "Vessels", "Nerves") |
| **Annotation** | Visual mark on image (label, arrow, overlay) |
| **View** | Anatomical direction (Anterior, Posterior, Axial, etc.) |
| **Translation** | Text in alternate language (EN, DE, FR, PL, LA) |
| **Tag** | Searchable keyword (e.g., "artery", "nerve") |
| **GUID** | Globally unique identifier for Anki note |
| **CrowdAnki** | Anki add-on for importing JSON decks |

---

## Support

For questions about:
- **Data structure**: See DATA_MODEL.md
- **Web UI features**: See UI_REQUIREMENTS.md
- **Build process**: See BUILD_PIPELINE.md
- **System design**: See ARCHITECTURE.md
- **JSON schema**: See card_schema_v3.json

---

## Version History

- **v3.0** (Oct 2024)
  - Removed complex variants system (simplified)
  - Added view axis (single per card)
  - Added tags for filtering
  - Added deck/subdeck organization
  - Analyzed PPT files for common view axes

---

## Next Steps

1. **Build the web UI** (React app) following UI_REQUIREMENTS.md
2. **Implement build pipeline** (Python script) following BUILD_PIPELINE.md
3. **Create initial cards** (using web UI or manual JSON)
4. **Generate deck.json** (run build script)
5. **Import to Anki** (via CrowdAnki)
6. **Iterate and expand** (add more cards, translations)

---

**Last updated:** 2024-10-04
