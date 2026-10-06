# Card Editor — Quick Start

A local, browser-based editor for creating and editing anatomical flashcards without any setup beyond running a simple Python server.

## Setup & Usage

### 1. Start the Server

```bash
python3 server.py
```

The server will start at `http://localhost:8000` and print a message when ready.

### 2. Open the Editor

Open your browser and go to:
```
http://localhost:8000/editor.html
```

### 3. Start Editing

- **Left sidebar:** Browse decks and cards
- **Center form:** Edit card content
- **Save:** Click "Save Card" to write changes to `cards/{deck}/{subdeck}/{id}.json`

## What You Can Edit

### Card Metadata
- **Title** — The structure name (e.g., "Celiac Trunk")
- **View** — Anatomical orientation (Anterior, Posterior, Axial, etc.)
- **Tags** — Searchable keywords (add by typing and pressing Enter)

### Card Content
- **Front/Back sides** — Each with 5 languages (EN, DE, FR, PL, LA)
- Click language tabs to switch languages
- Leave blank for untranslated languages

### Image
- Displays the associated image
- Path is read-only (set in the JSON file)

## File Structure

Cards are automatically saved to the correct location based on their deck/subdeck:

```
cards/
├── abdomen/
│   ├── vessels/
│   │   ├── AbdomenCeliac_Anterior.json
│   │   └── ...
│   ├── nerves/
│   └── organs/
├── upper-limb/
│   └── ...
└── head-neck/
    └── ...
```

## Creating New Cards

1. Create a new JSON file in the appropriate `cards/{deck}/{subdeck}/` directory
2. Use `card_example_v3.json` as a template
3. Update `decks.json` to add the card ID to the appropriate subdeck:
   ```json
   "cardIds": ["ExistingCard_Anterior", "NewCard_Anterior"]
   ```
4. Reload the editor to see the new card in the sidebar

## Features

✅ Browse deck hierarchy  
✅ Search cards by name  
✅ Edit multilingual text  
✅ Manage tags  
✅ View associated image  
✅ Auto-save to JSON  
✅ No database needed (pure file-based)  

## Notes

- **No network required** — Everything runs locally
- **Auto-save on click** — Changes save immediately when you click "Save Card"
- **Reset button** — Undoes all unsaved changes in the form
- **Status messages** — Green for success, red for errors (fade after 3 seconds)

## Troubleshooting

### Cards not appearing?
- Check `decks.json` includes the card ID in the correct subdeck
- Make sure the card JSON file exists at `cards/{deck}/{subdeck}/{id}.json`

### Image not loading?
- Verify the image path in the card JSON is correct
- Check the image file exists at that path

### Server won't start?
- Make sure port 8000 is available
- Try a different port: modify the `HTTPServer(('localhost', 8000), ...)` line in `server.py`

### Changes not saving?
- Check browser console (F12) for errors
- Verify the `cards/` directory is writable

---

**Keyboard Shortcuts:**
- Add tag: Type and press Enter
- Save card: Click "Save Card" button (or implement Ctrl+S if needed)

---

*For detailed card structure info, see [CARD_SYSTEM_README.md](CARD_SYSTEM_README.md)*
