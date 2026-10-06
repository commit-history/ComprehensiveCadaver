# Anki Image Annotation Editor — Design & Handoff

## Goal

Create Anki cards whose front and back show an image with **non-destructive overlays**:

- arrows, lines, text annotations
- freeform polygons and curves (Bézier paths) as highlights
- different overlay sets per card side (front / back)

The source of truth is a plain `deck.json`. A browser editor (Fabric.js) edits it. A build step turns it into an `.apkg`.

```
deck.json  ──load──▶  editor (Fabric.js)  ──save──▶  deck.json  ──build.py──▶  deck.apkg
```

## Decisions so far

| Topic | Decision | Reason |
|---|---|---|
| Existing Anki tools | Not sufficient | Native Image Occlusion: rect/ellipse/polygon/text only, no arrows or lines, and its shapes are masks rather than highlights. Method-Draw-based Image Editor add-ons bake annotations into the image and have a weak arrow tool. |
| Filerobot Image Editor | Rejected | Only regular polygons, no freeform polygons. |
| Excalidraw / tldraw | Rejected | Too awkward to use for this task. |
| Canvas library | **Fabric.js v6** | Built-in selection and transforms, editable polygon vertices (`controlsUtils.createPolyControls`), SVG-path Béziers, freehand brush, `IText`. Konva would need custom text editing and vertex editing, and has no SVG export. |
| Storage format | **Own tool-neutral schema** in deck.json | Fabric JSON is not stored, so the editor library can be swapped later. |
| Rendering in Anki | **Static inline SVG** over `<img>` | No JavaScript at review time, so it works on desktop, AnkiDroid and AnkiMobile. |
| Build | Python + `genanki` | Stable GUIDs and model IDs, and the media files get bundled into the package. |

## Suggested repo layout

```
anki-annotator/
├─ deck.json
├─ media/                 # source images
├─ editor/
│  ├─ index.html
│  ├─ main.js             # canvas setup, toolbar, load/save
│  ├─ adapter.js          # schema <-> Fabric conversion
│  ├─ arrow.js            # custom Arrow class
│  └─ tools/              # polygon, path, arrow, text drawing tools
├─ build/
│  ├─ build.py            # deck.json -> .apkg
│  └─ svg.py              # schema -> SVG (one function per kind)
└─ README.md
```

Serve the editor with any local static server, e.g. `npx vite` or `python -m http.server`. For saving, either:

- use the File System Access API (`showOpenFilePicker` / `createWritable`) in Chromium, or
- run a tiny local server, e.g. Python or Node, with `GET /deck` and `PUT /deck` endpoints.

## Schema (deck.json)

All coordinates are **natural image pixels**: origin top-left, x to the right, y down.

```json
{
  "version": 1,
  "deck": { "name": "Anatomy::Heart", "id": 1712345678 },
  "cards": [
    {
      "id": "c001",
      "image": "media/heart.png",
      "size": [1600, 1200],
      "front": { "prompt": "Name the highlighted vessel" },
      "back":  { "answer": "Aorta", "extra": "" },
      "tags": ["cardio"],
      "annotations": [
        { "id": "a1", "kind": "arrow",   "sides": ["back"],          "points": [[400,300],[620,410]], "stroke": "#e00000", "width": 6, "head": "end" },
        { "id": "a2", "kind": "line",    "sides": ["back"],          "points": [[100,900],[500,900]], "stroke": "#000000", "width": 3 },
        { "id": "a3", "kind": "polygon", "sides": ["front","back"],  "points": [[610,380],[700,360],[740,450],[650,500]], "fill": "#ffff0055", "stroke": "#ff8800", "width": 3 },
        { "id": "a4", "kind": "path",    "sides": ["back"],          "d": "M 100 100 C 150 50 250 50 300 100", "fill": "none", "stroke": "#0000ff", "width": 4 },
        { "id": "a5", "kind": "text",    "sides": ["back"],          "at": [700,120], "text": "Aorta", "size": 40, "color": "#e00000" }
      ]
    }
  ]
}
```

Rules for the schema:

- `kind` is one of `arrow | line | polygon | path | text`. Freehand strokes from the brush are saved as `path`.
- `sides` is a subset of `["front","back"]`.
- `path.d` uses absolute commands only (`M L C Q Z`), with transforms already baked in.
- Colors are `#rrggbb` or `#rrggbbaa`.
- `id` is stable and never reused. The build uses the card `id` to derive the Anki GUID.

## Editor: key implementation notes

### 1. Coordinate system: zoom the viewport, never scale objects

```js
import { Canvas, FabricImage } from 'fabric';

const canvas = new Canvas('c', { selection: true, preserveObjectStacking: true });
const img = await FabricImage.fromURL(card.image);
img.set({ selectable: false, evented: false, left: 0, top: 0, originX: 'left', originY: 'top' });
canvas.backgroundImage = img;

function fit() {
  const [w, h] = card.size;
  const scale = Math.min(container.clientWidth / w, container.clientHeight / h);
  canvas.setDimensions({ width: w * scale, height: h * scale });
  canvas.setZoom(scale);          // object coords stay in image pixels
}
```

### 2. Custom properties must be serialized explicitly

```js
import { FabricObject } from 'fabric';
FabricObject.customProperties = ['annId', 'kind', 'sides'];
// or per call: obj.toObject(['annId', 'kind', 'sides'])
```

### 3. Bake transforms on save (main pitfall)

Fabric stores polygon/polyline/path coordinates **relative to the object**, offset by `pathOffset`. After the user moves, rotates or scales a shape, the raw `points` are stale. Convert them to absolute coordinates on save:

```js
import { Point, util } from 'fabric';

function absPoint(obj, x, y) {
  const m = obj.calcTransformMatrix();
  return util.transformPoint(new Point(x - obj.pathOffset.x, y - obj.pathOffset.y), m);
}

// polygon
const pts = obj.points.map(p => { const a = absPoint(obj, p.x, p.y); return [a.x, a.y]; });

// path: obj.path is an array like ['M', x, y], ['C', x1, y1, x2, y2, x, y], ...
const d = obj.path.map(([cmd, ...nums]) => {
  const out = [];
  for (let i = 0; i < nums.length; i += 2) {
    const a = absPoint(obj, nums[i], nums[i + 1]);
    out.push(round(a.x), round(a.y));
  }
  return [cmd, ...out].join(' ');
}).join(' ');
```

Notes:

- Fabric normalizes parsed paths to absolute commands. Verify that brush output also contains only `M/L/Q/C/Z`; if it doesn't, run it through `util.makePathSimpler`.
- For `line` and `arrow`, get the endpoints with `obj.calcLinePoints()` and pass them through the same matrix.
- `text`: save `left/top` as `at` and `fontSize * scaleY` as `size`. Ignore rotation in v1, or add an `angle` field.
- Round coordinates to one decimal place to keep diffs readable.

### 4. Polygon vertex editing

```js
import { Polygon, controlsUtils } from 'fabric';

poly.controls = controlsUtils.createPolyControls(poly);
poly.hasBorders = false;
poly.objectCaching = false;
```

Add a toggle (e.g. double-click) to switch between "transform mode", which uses the default controls, and "vertex mode", which uses the poly controls. For adding and deleting points, insert or remove an entry in `poly.points`, then call `poly.setBoundingBox(true)` and rebuild the controls.

### 5. Arrow

Fabric has no arrow primitive. Subclass `Line` and draw the head in `_render`:

```js
import { Line, classRegistry } from 'fabric';

export class Arrow extends Line {
  static type = 'Arrow';
  _render(ctx) {
    super._render(ctx);
    const { x1, y1, x2, y2 } = this.calcLinePoints();
    const ang = Math.atan2(y2 - y1, x2 - x1);
    const len = Math.max(12, this.strokeWidth * 4);
    ctx.save();
    ctx.translate(x2, y2); ctx.rotate(ang);
    ctx.beginPath(); ctx.moveTo(0, 0);
    ctx.lineTo(-len, len / 2); ctx.lineTo(-len, -len / 2); ctx.closePath();
    ctx.fillStyle = this.stroke; ctx.fill();
    ctx.restore();
  }
}
classRegistry.setClass(Arrow);
```

Optional: register endpoint controls so the user can drag the tail and the head directly instead of using the bounding box.

### 6. Curves (Bézier tool)

The simplest workable version for v1:

- Click to add anchor points; drag while clicking to pull out a control handle.
- Build the `d` string as `M` followed by `C` segments, and recreate the `Path` on each change while drawing.
- After drawing, edit the curve via custom controls on the anchor and handle coordinates, or just redraw it.

A cheaper alternative is to draw a polyline and smooth it into a Catmull-Rom spline, converted to `C` segments on save.

### 7. Front/back layers

- Keep a `currentSide` toggle in the toolbar.
- Objects whose `sides` don't include `currentSide` are shown dimmed and unselectable, or hidden.
- New objects default to `sides = [currentSide]`. A small panel per object lets you set front, back or both.

### 8. Undo/redo

Snapshot the schema form (the output of `fromFabric`) on `object:modified`, `object:added` and `object:removed` into a stack. Restore by rebuilding the canvas from the snapshot. This reuses the adapter, so no extra code paths.

## Adapter contract (`adapter.js`)

```js
export function toFabric(ann) /* -> fabric.Object with annId/kind/sides set */ {}
export function fromFabric(obj) /* -> annotation (absolute coords, transforms baked) */ {}
export function loadCard(canvas, card) {}   // clear, set background, add toFabric(...) for each annotation
export function saveCard(canvas, card) {}   // card.annotations = canvas.getObjects().map(fromFabric)
```

Test: **round-trip identity**. `fromFabric(toFabric(a))` must equal `a` within rounding, both with and without a move/rotate/scale applied in between.

## Build step (`build/build.py`)

```python
import json, genanki, html
from svg import render_svg   # schema -> "<svg ...>...</svg>" for a given side

MODEL_ID = 1607392319   # fixed forever
MODEL = genanki.Model(
    MODEL_ID, "Annotated Image",
    fields=[{"name": "Front"}, {"name": "Back"}, {"name": "Extra"}],
    templates=[{
        "name": "Card 1",
        "qfmt": "{{Front}}",
        "afmt": "{{Back}}<hr id=answer>{{Extra}}",
    }],
    css=".ai{position:relative;display:inline-block;max-width:100%}"
        ".ai img{display:block;max-width:100%;height:auto}"
        ".ai svg{position:absolute;inset:0;width:100%;height:100%;pointer-events:none}",
)

def side_html(card, side, text):
    fname = card["image"].split("/")[-1]
    return (f'<div>{html.escape(text)}</div>'
            f'<div class="ai"><img src="{fname}">{render_svg(card, side)}</div>')

deck_json = json.load(open("deck.json"))
deck = genanki.Deck(deck_json["deck"]["id"], deck_json["deck"]["name"])
media = []
for c in deck_json["cards"]:
    deck.add_note(genanki.Note(
        model=MODEL,
        guid=genanki.guid_for(c["id"]),
        fields=[side_html(c, "front", c["front"].get("prompt", "")),
                side_html(c, "back",  c["back"].get("answer", "")),
                c["back"].get("extra", "")],
        tags=c.get("tags", []),
    ))
    media.append(c["image"])
genanki.Package(deck, media_files=sorted(set(media))).write_to_file("deck.apkg")
```

SVG rendering (`svg.py`): `viewBox="0 0 {w} {h}"` using the image's natural size. Write one small function per `kind`:

- `polygon` → `<polygon points=...>`
- `path` → `<path d=...>`
- `line` → `<line>`
- `arrow` → `<line marker-end="url(#ah-{id})">`, with a `<marker>` in `<defs>`. Use a per-arrow marker id so each arrowhead gets its own color.
- `text` → `<text>`, using `dominant-baseline="hanging"` to match Fabric's top-left origin.

Keep `vector-effect` off so stroke widths scale together with the image, which matches the editor.

## Open questions / later

- [ ] Should re-importing an `.apkg` update existing notes? Stable GUIDs and model ID handle this, but check how note updates behave on import in your Anki version.
- [ ] Multiple images per card, or one image per card with different overlays per side (the current design assumes the latter)?
- [ ] Rendering check on AnkiMobile / AnkiDroid: inline SVG and the `#rrggbbaa` fill format. If they cause problems, fall back to `fill` + `fill-opacity`.
- [ ] Optional: export to Anki's native Image Occlusion format for occlusion-style cards.
- [ ] Optional: live sync via AnkiConnect instead of `.apkg` re-import.

## v1 milestones

1. Load a single card from deck.json; background image with viewport zoom.
2. Polygon tool with vertex editing; save → deck.json, with the round-trip test passing.
3. Arrow, line and text tools.
4. Front/back toggle and per-object `sides`.
5. `build.py` + `svg.py` → import into Anki, then check on desktop and mobile.
6. Bézier/path tool and freehand brush.
7. Undo/redo and card navigation (previous/next/new card).
