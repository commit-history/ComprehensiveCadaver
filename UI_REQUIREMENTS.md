# Web UI Requirements

Web-based editor and viewer for anatomical card definitions. Allows users to:
- Browse decks and cards
- Filter and search cards
- View and edit card content (front/back, translations, annotations)
- Replace images and overlay annotations

---

## 1. Layout Overview

```
┌─────────────────────────────────────────────────────┐
│           Header: Card Editor / Viewer              │
├──────────────┬──────────────────────────────────────┤
│              │                                      │
│  Left Panel  │        Center Panel (Main)           │
│  (Sidebar)   │  - Deck & Card Selector              │
│              │  - Card Preview/Editor               │
│  • Decks     │                                      │
│  • Cards     │                                      │
│  • Filters   │                                      │
│              │                                      │
│              │                                      │
└──────────────┴──────────────────────────────────────┘
```

---

## 2. Left Sidebar

### 2.1 Deck Navigation

**Component: Hierarchical Deck List**

```
Decks (collapsible tree)
├─ Abdomen [5 cards]
│  ├─ Vessels [3 cards]
│  ├─ Nerves [2 cards]
│  └─ Organs [3 cards]
├─ Upper Limb [8 cards]
│  ├─ Osteology [4 cards]
│  ├─ Nerves [3 cards]
│  └─ Vessels [1 card]
└─ Head and Neck [6 cards]
   ├─ Brain [4 cards]
   └─ Cranial Nerves [2 cards]
```

**Features:**
- Click deck to expand/collapse
- Click subdeck to show cards in center panel
- Badge showing card count
- Color-coded by category (optional)
- Drag-to-reorder (future)

### 2.2 Card List

**Component: Searchable Card List**

Shows all cards in selected subdeck (or filtered results).

```
Cards: Vessels (3 found)
┌─────────────────────────┐
│ 🔍 Search cards...      │
└─────────────────────────┘

┌─────────────────────────┐
│ Celiac Trunk            │
│ Anterior | #artery      │
│ EN ✓ DE ✗ LA ✓          │
└─────────────────────────┘

┌─────────────────────────┐
│ SMA Trunk               │
│ Anterior | #artery      │
│ EN ✓ DE ✓ LA ✓          │
└─────────────────────────┘
```

**Features:**
- Live search by title or tag
- Each card shows:
  - Title
  - View orientation
  - Tags (clickable to filter)
  - Translation status per language (checkmarks)
- Click card to load in center panel
- Highlight currently selected card

### 2.3 Filters

**Component: Filter Panel**

```
Filters (collapsible)

  Decks
  ☑ Abdomen
  ☑ Upper Limb
  ☐ Head and Neck

  Translation Status
  ☑ Complete (all 5 languages)
  ☑ Partial (some languages)
  ☑ Missing (no translations)

  Tags
  (shows top 10 tags from cards in view)
  ☑ artery
  ☑ nerve
  ☑ muscle
  ☐ bone

  View Axis
  ☑ Anterior
  ☑ Posterior
  ☐ Axial
  (etc.)
```

**Features:**
- Multi-select checkboxes
- Dynamically shows available options
- "Clear all" / "Select all" buttons
- Apply filters instantly (updates card list)
- Shows filter count badge

---

## 3. Center Panel: Card Editor

### 3.1 Header

```
┌──────────────────────────────────────────────┐
│ Celiac Trunk                                 │
│ Abdomen > Vessels | Anterior View            │
│ ID: AbdomenCeliac_Anterior                   │
│ Tags: #artery #major-vessel #abdominal       │
├──────────────────────────────────────────────┤
│  [Edit] [Save] [Delete] [Duplicate] [Export] │
└──────────────────────────────────────────────┘
```

**Features:**
- Display card title, location, view
- Editable tags (click to add/remove)
- Action buttons (save, delete, duplicate, export)

### 3.2 Tabs

Two main tabs: **Front** and **Back**

```
  [Front]  [Back]  [Metadata]
```

### 3.3 Front Tab

**Shows question side only**

```
┌─────────────────────────────────────────┐
│ FRONT SIDE                              │
├─────────────────────────────────────────┤
│ Image:                                  │
│ ┌─────────────────────────────────────┐ │
│ │                                     │ │
│ │   [Image preview / upload area]     │ │
│ │                                     │ │
│ │  Current: celiac_anterior.jpg       │ │
│ │  [Replace Image]  [Upload from PPT] │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ Question Text (multi-language):         │
│ ┌─────────────────────────────────────┐ │
│ │ Language [EN ▼]                     │ │
│ │                                     │ │
│ │ [Text editor area]                  │ │
│ │ "Identify the vessel highlighted... │ │
│ │                                     │ │
│ │ [+ Add Language] [Translation mode] │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ Available Languages:                    │
│ EN ✓ | DE ✗ | FR ✗ | PL ✗ | LA ✓      │
└─────────────────────────────────────────┘
```

**Features:**
- Image preview (read-only on front)
- Multi-language text editor
  - Dropdown to select language
  - Rich text editor (or plain text with formatting helpers)
- Translation status indicators
- Add missing language button
- Side-by-side translation comparison (toggle)

### 3.4 Back Tab

**Shows answer side with annotations**

```
┌─────────────────────────────────────────────────┐
│ BACK SIDE                                       │
├─────────────────────────────────────────────────┤
│ Image (editable):                               │
│ ┌─────────────────────────────────────────────┐ │
│ │                                             │ │
│ │  [Interactive image canvas]                 │ │
│ │  - Overlays visible                         │ │
│ │  - Click to edit annotations                │ │
│ │  - Drag image to pan (if zoomed)            │ │
│ │                                             │ │
│ │  [Replace Image] [Zoom controls] [Reset]    │ │
│ └─────────────────────────────────────────────┘ │
│                                                 │
│ Annotations Panel:                              │
│ ┌──────────────────┬──────────────────────────┐ │
│ │ Annotations (3)  │ Annotation Details       │ │
│ │ [+ New Label]    │ ┌────────────────────┐   │ │
│ │ [+ New Arrow]    │ │ Label: Celiac T.   │   │ │
│ │ [+ New Overlay]  │ │ ID: ann_1          │   │ │
│ │                  │ │                    │   │ │
│ │ ☑ ann_1: Label   │ │ Languages:         │   │ │
│ │   "Celiac T."    │ │ EN: Celiac Trunk   │   │ │
│ │                  │ │ DE: Zöliakalstamm  │   │ │
│ │ ☑ ann_2: Arrow   │ │ FR: [empty]        │   │ │
│ │   "Branches"     │ │                    │   │ │
│ │                  │ │ Position:          │   │ │
│ │ ☑ ann_3: Overlay│ │ TopLeft: (320,140) │   │ │
│ │   (4 nodes)     │ │ BottomRight: ...   │   │ │
│ │                  │ │                    │   │ │
│ │ [Delete selected]│ │ Color: [picker]    │   │ │
│ │ [Duplicate]     │ │ FontSize: 14 px    │   │ │
│ │                  │ │                    │   │ │
│ │                  │ │ [Save] [Revert]    │   │ │
│ │                  │ └────────────────────┘   │ │
│ └──────────────────┴──────────────────────────┘ │
│                                                 │
│ Answer Text (multi-language):                   │
│ ┌──────────────────────────────────────────────┐ │
│ │ Language [EN ▼]                              │ │
│ │ [Text editor area]                           │ │
│ │ "Celiac Trunk - branches into..."            │ │
│ │                                              │ │
│ │ EN ✓ | DE ✓ | FR ✗ | PL ✗ | LA ✓           │ │
│ └──────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────┘
```

**Features:**

**Image Canvas:**
- Display image with overlays rendered
- Click on annotation to select it (highlight in list)
- Hover over annotation to preview label/details
- Toggle annotation visibility (eye icon)
- Zoom controls (fit, 100%, custom)
- Pan/scroll when zoomed

**Annotations List:**
- Numbered list of all annotations
- Checkboxes to toggle visibility
- Click to select annotation (shows details)
- Drag to reorder (z-index)
- Delete/duplicate buttons

**Annotation Details Editor:**
- Shows selected annotation properties
- Edit type-specific fields:
  - **Label**: text (multilang), bounds (topLeft/bottomRight), color, fontSize, fontWeight, align
  - **Arrow**: origin, target, text (multilang), color, strokeWidth
  - **Overlay**: nodes (polygon vertices), color, opacity, strokeColor, strokeWidth
- Multi-language text editor for annotation labels
- Live preview on image
- Click image to place/adjust points (for arrows, overlays)

**Answer Text:**
- Multi-language text editor
- Same as front (but with translations often more complete)

### 3.5 Metadata Tab

```
┌──────────────────────────────────────────┐
│ METADATA                                 │
├──────────────────────────────────────────┤
│ Card ID: AbdomenCeliac_Anterior          │
│ Title: Celiac Trunk                      │
│                                          │
│ Organization:                            │
│ Deck: [Abdomen ▼]                        │
│ Subdeck: [Vessels ▼]                     │
│                                          │
│ Anatomical Properties:                   │
│ View Axis: [Anterior ▼]                  │
│ Tags: #artery #major-vessel #abdominal   │
│ [+ Add tag]                              │
│                                          │
│ Image Properties:                        │
│ Path: images/abdomen/celiac_anterior.jpg │
│ Dimensions: 800 × 600 px                 │
│ [Edit path]                              │
│                                          │
│ Credits:                                 │
│ Source: [Comprehensive Cadaver         ]│
│ Authors: [Cadaveric specimen           ]│
│ Copyright: [Educational use            ]│
│ URL: [https://...                      ]│
│                                          │
│ Translation Status:                      │
│ Complete: LA, EN                         │
│ Partial: DE, FR                          │
│ Missing: PL                              │
│                                          │
│ Created: 2024-10-04 14:23                │
│ Last modified: 2024-10-05 09:15          │
│                                          │
│ [Save Changes]  [Revert]                 │
└──────────────────────────────────────────┘
```

---

## 4. Interaction Patterns

### 4.1 Creating a New Card

1. Click "+ New Card" in sidebar
2. Select deck/subdeck from dropdowns
3. Fill in title, ID, view axis
4. Upload image
5. Add question text (EN required)
6. Switch to back tab, add answer text + annotations
7. Add translations
8. Save

### 4.2 Editing Annotations

**Label:**
- Click annotation in list → shows bounds on image
- Click bounding box corners to resize
- Edit text in details panel
- Real-time preview

**Arrow:**
- Click annotation → shows origin/target points
- Click point to move (crosshair cursor)
- Or type coordinates in details panel
- Drag to new position

**Overlay:**
- Click annotation → shows polygon vertices
- Click vertex to move
- Right-click to delete vertex
- Click edge to add vertex
- Or edit node coordinates in details panel

### 4.3 Adding Translations

1. Click "+ Add Language" in text editor
2. Select language (e.g., German)
3. Type translated text
4. System marks card as "partial" until all languages complete
5. Show side-by-side comparison with original

### 4.4 Translation Mode

When enabled:
- Shows original language (left) alongside target language (right)
- Highlights missing translations
- Shows context (e.g., which annotation this text belongs to)

---

## 5. Search & Filter Features

### 5.1 Search Box

```
🔍 Search cards... [X]
```

- Real-time search as user types
- Searches: title, tags, ID
- Shows matching count
- Keyboard shortcut: Cmd+K (or Ctrl+K)

### 5.2 Filter Combinations

Examples:
- "Show all artery cards in Abdomen"
- "Show all nerve cards missing Spanish translation"
- "Show all cards from Upper Limb with incomplete translations"

**UI:**
```
Results: 7 cards found
[Clear filters]

Filters applied:
✕ deck:abdomen  ✕ tags:artery  ✕ translationStatus:partial
```

---

## 6. Data Export/Import

### 6.1 Export Card

```
[Export] 
  → Download JSON
  → Copy to clipboard
  → Email
```

### 6.2 Export Entire Subdeck

```
[Export Subdeck]
  → ZIP file with all cards + images
```

### 6.3 Import from PPT

```
[Import from PPT]
  → Select .pptx file
  → Extract slide images
  → Auto-generate card skeleton
  → User fills in annotations
```

---

## 7. Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Cmd+S` | Save current card |
| `Cmd+K` | Focus search box |
| `Cmd+N` | New card |
| `Cmd+E` | Export card |
| `←` / `→` | Switch between Front/Back tabs |
| `Del` | Delete selected annotation |
| `Esc` | Deselect annotation |

---

## 8. Mobile Responsiveness

**Breakpoints:**
- Desktop (1200px+): Full 3-column layout
- Tablet (768px-1199px): Collapsible sidebar + full center panel
- Mobile (< 768px): Modal sidebar + full-screen card editor

**Mobile Optimizations:**
- Stack panels vertically
- Simplify annotation editing (touch-friendly)
- Hide some panels (e.g., translation comparison)
- Larger touch targets (44px minimum)

---

## 9. Performance Requirements

- Load 1000+ cards without lag
- Virtualized card list (render only visible)
- Lazy-load images (thumbnails first)
- Debounce search/filter (~300ms)
- Cache images locally (IndexedDB)

---

## 10. Validation & Error Handling

**Card-level validation:**
- At least one language per text field (required)
- Annotation bounds must be within image dimensions
- Card ID must be unique
- Deck/subdeck must exist

**User feedback:**
- Toast notifications (success/error)
- Inline field validation (red border on error)
- Confirmation dialogs for destructive actions
- Auto-save with indicator ("Saving..." → "Saved")

---

## 11. Browser Requirements

- Chrome/Firefox/Safari (latest 2 versions)
- Canvas API for image rendering
- localStorage or IndexedDB for caching
- File API for image upload

---

## Notes

- All interactions are non-destructive (undo/redo optional for future)
- Translation status calculated on-the-fly from card data
- Filters apply client-side (for small datasets) or server-side (for 10k+ cards)
