# Data Model Documentation

This document defines the structure for storing and managing anatomical card definitions. The system consists of two main layers:
1. **Deck Model** — organizational hierarchy
2. **Card Model** — individual card definitions with annotations

---

## 1. Deck Model

### Purpose
Organizes cards into a hierarchical structure (Deck → Subdeck → Cards).

### Structure

```json
{
  "decks": [
    {
      "id": "abdomen",
      "name": "Abdomen",
      "description": "Abdominal anatomy including organs, vessels, and nerves",
      "order": 1,
      "subdecks": [
        {
          "id": "abdomen-vessels",
          "name": "Vessels",
          "description": "Arterial and venous supply to abdominal organs",
          "order": 1,
          "cardIds": [
            "AbdomenCeliac_Anterior",
            "AbdomenCeliac_Posterior",
            "AbdomenSMA_Anterior"
          ]
        },
        {
          "id": "abdomen-nerves",
          "name": "Nerves",
          "description": "Autonomic and somatic innervation",
          "order": 2,
          "cardIds": [
            "AbdomenVagus_Anterior",
            "AbdomenPelvicPlexus_Inferior"
          ]
        },
        {
          "id": "abdomen-organs",
          "name": "Organs",
          "description": "Abdominal viscera and their relationships",
          "order": 3,
          "cardIds": [
            "AbdomenLiver_Anterior",
            "AbdomenStomach_Anterior"
          ]
        }
      ]
    },
    {
      "id": "upper-limb",
      "name": "Upper Limb",
      "description": "Anatomy of the shoulder, arm, and hand",
      "order": 2,
      "subdecks": [
        {
          "id": "upper-limb-osteology",
          "name": "Osteology",
          "order": 1,
          "cardIds": [
            "UpperLimbHumerus_Anterior",
            "UpperLimbRadius_Anterior"
          ]
        },
        {
          "id": "upper-limb-nerves",
          "name": "Nerves",
          "order": 2,
          "cardIds": [
            "UpperLimbBrachialPlexus_Anterior",
            "UpperLimbRadialNerve_Lateral"
          ]
        }
      ]
    }
  ]
}
```

### Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `id` | string | ✓ | Unique deck identifier (kebab-case) |
| `name` | string | ✓ | Human-readable deck name |
| `description` | string | ✗ | Optional description of deck contents |
| `order` | number | ✓ | Display order (lower = first) |
| `subdecks` | array | ✓ | Array of subdeck objects |

### Subdeck Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `id` | string | ✓ | Unique subdeck identifier (kebab-case) |
| `name` | string | ✓ | Human-readable name (e.g., "Vessels", "Nerves") |
| `description` | string | ✗ | Optional description |
| `order` | number | ✓ | Display order within deck |
| `cardIds` | array | ✓ | Array of card IDs belonging to this subdeck |

---

## 2. Card Model

### Purpose
Defines a single anatomical card with front/back content, annotations, translations, and metadata.

### Structure

```json
{
  "id": "AbdomenCeliac_Anterior",
  "title": "Celiac Trunk",
  "deck": "abdomen",
  "subdeck": "abdomen-vessels",
  "tags": [
    "artery",
    "vessel",
    "abdominal",
    "major-vessel"
  ],
  "image": {
    "path": "images/abdomen/celiac_anterior.jpg",
    "width": 800,
    "height": 600
  },
  "view": "Anterior",
  "credits": {
    "source": "Comprehensive Cadaver",
    "authors": ["Cadaveric specimen"],
    "copyright": "Educational use",
    "url": "https://example.com"
  },
  "cards": [
    {
      "side": "front",
      "text": {
        "EN": "Identify the vessel highlighted on the anterior view of the abdomen",
        "DE": "Identifizieren Sie das hervorgehobene Blutgefäß auf der vorderen Ansicht des Abdomens",
        "FR": "Identifier le vaisseau mis en évidence sur la vue antérieure de l'abdomen",
        "PL": "Zidentyfikuj naczynia podświetlone na widoku przedniego brzucha",
        "LA": "Identifica vas luminis in prospectiva anteriore abdominis"
      },
      "annotations": []
    },
    {
      "side": "back",
      "text": {
        "EN": "Celiac Trunk (Truncus coeliacus) - branches into left gastric, splenic, and common hepatic arteries",
        "DE": "Zöliakalstamm - verzweigt sich in linke Magengefäße, Milzgefäße und gemeinsame Lebergefäße",
        "FR": "Tronc coeliaque - se divise en artères gastrique gauche, splénique et hépatique commune",
        "PL": "Pień trzewny - rozgałęzia się na arteria żołądkowa lewa, splenic i hepatica",
        "LA": "Truncus coeliacus - rami in arteria gastrica sinistra, lienalis, et hepatica communis"
      },
      "annotations": [
        {
          "id": "ann_1",
          "type": "label",
          "text": {
            "EN": "Celiac Trunk",
            "DE": "Zöliakalstamm",
            "FR": "Tronc coeliaque",
            "LA": "Truncus coeliacus"
          },
          "bounds": {
            "topLeft": { "x": 320, "y": 140 },
            "bottomRight": { "x": 480, "y": 180 }
          },
          "color": "FF0000",
          "fontSize": 14,
          "fontWeight": "bold",
          "align": "center"
        },
        {
          "id": "ann_2",
          "type": "arrow",
          "origin": { "x": 400, "y": 160 },
          "target": { "x": 400, "y": 300 },
          "text": {
            "EN": "Branches",
            "DE": "Äste"
          },
          "color": "FF6666",
          "strokeWidth": 2
        },
        {
          "id": "ann_3",
          "type": "overlay",
          "nodes": [
            { "x": 300, "y": 130 },
            { "x": 500, "y": 140 },
            { "x": 520, "y": 320 },
            { "x": 280, "y": 310 }
          ],
          "color": "FF0000",
          "opacity": 0.15,
          "strokeColor": "FF0000",
          "strokeWidth": 2
        }
      ]
    }
  ],
  "translations": {
    "complete": ["LA", "EN"],
    "partial": ["DE", "FR"],
    "missing": ["PL"]
  }
}
```

### Top-Level Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `id` | string | ✓ | Unique card ID (e.g., `AbdomenCeliac_Anterior`) |
| `title` | string | ✓ | Structure name (e.g., "Celiac Trunk") |
| `deck` | string | ✓ | Deck ID (foreign key to decks array) |
| `subdeck` | string | ✓ | Subdeck ID (foreign key) |
| `tags` | array | ✓ | Searchable tags (e.g., ["artery", "vessel"]) |
| `image` | object | ✓ | Image metadata (see Image Properties below) |
| `view` | enum | ✓ | Anatomical view axis (Anterior, Posterior, Axial, etc.) |
| `credits` | object | ✗ | Attribution information |
| `cards` | array | ✓ | Exactly 2 elements: [front, back] |
| `translations` | object | ✓ | Translation completeness status |

### Image Properties

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `path` | string | ✓ | File path relative to images root |
| `width` | number | ✓ | Image width in pixels |
| `height` | number | ✓ | Image height in pixels |

### Card Side Properties

Each card (front or back) has:

| Property | Type | Required | Description |
|----------|------|----------|-------------|
| `side` | enum | ✓ | "front" or "back" |
| `text` | object | ✓ | Translated text (keys: EN, DE, FR, PL, LA) |
| `annotations` | array | ✓ | Annotation objects (empty for front side) |

### Annotation Types

#### Label Annotation
```json
{
  "id": "ann_1",
  "type": "label",
  "text": {
    "EN": "Celiac Trunk",
    "DE": "Zöliakalstamm",
    "LA": "Truncus coeliacus"
  },
  "bounds": {
    "topLeft": { "x": 320, "y": 140 },
    "bottomRight": { "x": 480, "y": 180 }
  },
  "color": "FF0000",
  "fontSize": 14,
  "fontWeight": "bold",
  "align": "center"
}
```

**Properties:**
- `id`: Unique annotation ID
- `type`: "label"
- `text`: Multi-language text (at least one required)
- `bounds`: Bounding box with topLeft and bottomRight points
- `color`: Text color (hex, 6 digits)
- `fontSize`: Base font size (pixels)
- `fontWeight`: "normal" or "bold"
- `align`: "left", "center", or "right"

#### Arrow Annotation
```json
{
  "id": "ann_2",
  "type": "arrow",
  "origin": { "x": 400, "y": 160 },
  "target": { "x": 400, "y": 300 },
  "text": {
    "EN": "Branches",
    "DE": "Äste"
  },
  "color": "FF6666",
  "strokeWidth": 2
}
```

**Properties:**
- `id`: Unique annotation ID
- `type`: "arrow"
- `origin`: Start point {x, y}
- `target`: End point {x, y}
- `text`: Optional label (multi-language)
- `color`: Arrow color (hex)
- `strokeWidth`: Line width (pixels)

#### Overlay Annotation
```json
{
  "id": "ann_3",
  "type": "overlay",
  "nodes": [
    { "x": 300, "y": 130 },
    { "x": 500, "y": 140 },
    { "x": 520, "y": 320 },
    { "x": 280, "y": 310 }
  ],
  "color": "FF0000",
  "opacity": 0.15,
  "strokeColor": "FF0000",
  "strokeWidth": 2
}
```

**Properties:**
- `id`: Unique annotation ID
- `type`: "overlay"
- `nodes`: Array of polygon vertices (minimum 3)
- `color`: Fill color (hex)
- `opacity`: Fill opacity (0.0 to 1.0)
- `strokeColor`: Border color (hex)
- `strokeWidth`: Border width (pixels)

### Translation Tracking

The `translations` field tracks which languages are complete:

```json
"translations": {
  "complete": ["LA", "EN"],
  "partial": ["DE", "FR"],
  "missing": ["PL"]
}
```

**Rules:**
- `complete`: All text fields (cards + annotations) have this language
- `partial`: Some (but not all) text fields have this language
- `missing`: No text field has this language

---

## 3. File Storage Layout

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
    nerves/
      UpperLimbBrachialPlexus_Anterior.json

images/
  abdomen/
    celiac_anterior.jpg
    celiac_posterior.jpg
    sma_anterior.jpg
  upper-limb/
    humerus_anterior.jpg

decks.json  (master deck hierarchy file)
```

---

## 4. Available View Axes

Based on analysis of all PPT files, these view axes are supported:

| View | Description | Example |
|------|-------------|---------|
| Anterior | Front view of body part | Face, front of torso |
| Posterior | Back view | Back of torso, posterior leg |
| Superior | Looking down from above | Top of head, superior view of organ |
| Inferior | Looking up from below | Bottom of foot, inferior surface |
| Left | Lateral view from left side | Left side of head |
| Right | Lateral view from right side | Right side of body |
| Medial | Toward the midline | Inner arm, medial thigh |
| Lateral | Away from midline | Outer arm, lateral leg |
| Axial | Cross-section perpendicular to long axis | CT/MRI axial slice |
| Sagittal | Side-to-side section along midline | Midsagittal brain view |
| Coronal | Front-to-back section | Coronal MRI view |
| Transverse | Same as axial | Alternative term |
| Dorsal | Back surface (limbs) | Dorsum of hand/foot |
| Ventral | Front surface (limbs) | Ventral forearm |
| Deep | Deeper anatomical layer | Deep dissection |
| Superficial | Surface/superficial layer | Skin, fascia |

---

## 5. Tag Taxonomy

Suggested tags for filtering:

**Anatomical Type:**
- artery, vein, nerve, muscle, bone, organ, ligament, tendon, cartilage, fascia, vessel, lymph

**System:**
- cardiovascular, nervous, musculoskeletal, respiratory, digestive, genitourinary, endocrine, integumentary

**Region:**
- abdominal, thoracic, cervical, lumbar, cranial, upper-limb, lower-limb, dorsal, ventral

**Relationship:**
- major-vessel, major-nerve, superficial, deep, innervation, vascularization, attachment

Example tag combinations:
- `["artery", "major-vessel", "abdominal", "cardiovascular"]`
- `["nerve", "cervical", "nervous", "innervation"]`

---

## 6. Data Access Patterns

### Common Queries

1. **List all decks with hierarchy**
   ```json
   GET /api/decks
   Response: decks.json structure
   ```

2. **List cards in a subdeck**
   ```json
   GET /api/decks/:deckId/:subdeckId
   Response: Array of card previews
   ```

3. **Get full card definition**
   ```json
   GET /api/cards/:cardId
   Response: Complete card object
   ```

4. **Filter cards by criteria**
   ```json
   GET /api/cards?deck=abdomen&tags=artery,vessel&translationStatus=complete
   Response: Filtered card array
   ```

5. **Search cards by title or tag**
   ```json
   GET /api/cards/search?q=celiac
   Response: Matching cards
   ```

---

## Notes

- All point coordinates (x, y) are in pixels, with origin at top-left (0, 0)
- Colors are hex RGB without alpha (e.g., "FF0000" for red)
- Font sizes default to 12px if not specified
- The front card side should never have annotations
- At least one language must be present in the text object
- Card IDs should follow pattern: `{Deck}{Structure}_{View}` (e.g., `AbdomenCeliac_Anterior`)
