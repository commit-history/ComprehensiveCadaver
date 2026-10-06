/**
 * Fabric.js annotation editor
 */

const API_BASE = 'http://localhost:8000/api';
let canvas = null;
let deckData = null;
let currentCard = null;
let currentSide = 'back';
let activeTool = 'select';
let drawingPolygon = false;
let polygonPoints = [];

// Initialize on page load
async function initEditor() {
    console.log('Initializing editor...');

    // Setup canvas
    const canvasEl = document.getElementById('canvas');
    if (!canvasEl) {
        console.error('Canvas element not found!');
        return;
    }

    const container = canvasEl.parentElement;
    const width = container.clientWidth;
    const height = container.clientHeight;

    console.log('Container size:', width, 'x', height);

    canvas = new fabric.Canvas('canvas', {
        width: Math.max(width - 32, 600),
        height: Math.max(height - 32, 400),
        selection: true,
        preserveObjectStacking: true,
        backgroundColor: '#ffffff',
    });

    console.log('Canvas initialized:', canvas, 'Size:', canvas.width, 'x', canvas.height);

    // Load decks
    await loadDecks();

    // Setup event listeners
    setupToolButtons();
    setupSideToggle();
    setupCanvasEvents();

    console.log('Editor ready');
}

/**
 * Load decks from server
 */
async function loadDecks() {
    try {
        const response = await fetch(`${API_BASE}/decks`);
        deckData = await response.json();
        renderCardSelector();

        // Load first card
        if (deckData.decks[0]?.subdecks[0]?.cardIds[0]) {
            const cardId = deckData.decks[0].subdecks[0].cardIds[0];
            await loadCard(cardId);
        }
    } catch (error) {
        showStatus(`Error loading decks: ${error.message}`, 'error');
    }
}

/**
 * Render card list in sidebar
 */
function renderCardSelector() {
    const selector = document.getElementById('cardSelector');
    selector.innerHTML = '';

    deckData.decks.forEach(deck => {
        deck.subdecks.forEach(subdeck => {
            subdeck.cardIds.forEach(cardId => {
                const item = document.createElement('div');
                item.className = 'card-item';
                item.textContent = cardId;
                item.onclick = () => loadCard(cardId);
                selector.appendChild(item);
            });
        });
    });
}

/**
 * Load card by ID
 */
async function loadCard(cardId) {
    try {
        const response = await fetch(`${API_BASE}/card?id=${cardId}`);
        currentCard = await response.json();

        // Setup canvas
        setupCanvasImage();

        // Load annotations
        loadCardAnnotations(canvas, currentCard);

        // Update sidebar
        document.querySelectorAll('.card-item').forEach(el => {
            el.classList.toggle('active', el.textContent === cardId);
        });

        updateCanvasForSide(canvas, currentSide);
        showStatus(`Loaded: ${currentCard.title}`, 'success');
    } catch (error) {
        showStatus(`Error loading card: ${error.message}`, 'error');
    }
}

/**
 * Setup canvas with background image
 */
async function setupCanvasImage() {
    if (!currentCard) return;

    try {
        const img = await fabric.FabricImage.fromURL(`/${currentCard.image.path}`);
        img.set({
            selectable: false,
            evented: false,
            left: 0,
            top: 0,
            originX: 'left',
            originY: 'top',
        });

        // Resize canvas to fit image and container
        fitCanvas(currentCard.image.width, currentCard.image.height);
        canvas.backgroundImage = img;
        canvas.renderAll();
    } catch (error) {
        showStatus(`Error loading image: ${error.message}`, 'error');
    }
}

/**
 * Fit canvas to image and container
 */
function fitCanvas(imageWidth, imageHeight) {
    const container = canvas.getElement().parentElement;
    const scale = Math.min(
        container.clientWidth / imageWidth,
        container.clientHeight / imageHeight
    );

    canvas.setDimensions({
        width: imageWidth * scale,
        height: imageHeight * scale,
    });
    canvas.setZoom(scale);
}

/**
 * Setup tool button handlers
 */
function setupToolButtons() {
    document.getElementById('toolPolygon').onclick = () => selectTool('polygon');
    document.getElementById('toolArrow').onclick = () => selectTool('arrow');
    document.getElementById('toolLine').onclick = () => selectTool('line');
    document.getElementById('toolText').onclick = () => selectTool('text');
    document.getElementById('toolSelect').onclick = () => selectTool('select');
}

/**
 * Select tool
 */
function selectTool(tool) {
    activeTool = tool;

    // Update button states
    document.querySelectorAll('.tool-btn').forEach(btn => {
        btn.classList.remove('active');
    });

    // Find and activate the button for this tool
    const btnId = `tool${tool.charAt(0).toUpperCase()}${tool.slice(1)}`;
    const btn = document.getElementById(btnId);
    if (btn) btn.classList.add('active');

    // Update canvas mode
    if (tool === 'select') {
        canvas.isDrawingMode = false;
        canvas.selection = true;
        drawingPolygon = false;
        polygonPoints = [];
        showStatus('Select mode', 'success');
    } else if (tool === 'polygon') {
        canvas.isDrawingMode = false;
        canvas.selection = false;
        drawingPolygon = true;
        polygonPoints = [];
        showStatus('Polygon mode: click to add points, right-click to finish', 'success');
        console.log('Polygon tool activated');
    } else {
        canvas.isDrawingMode = false;
        canvas.selection = true;
    }
}

/**
 * Setup side toggle
 */
function setupSideToggle() {
    document.getElementById('sideFront').onclick = (e) => {
        currentSide = 'front';
        updateSideButtons();
        updateCanvasForSide(canvas, currentSide);
    };
    document.getElementById('sideBack').onclick = (e) => {
        currentSide = 'back';
        updateSideButtons();
        updateCanvasForSide(canvas, currentSide);
    };
}

/**
 * Update side button states
 */
function updateSideButtons() {
    document.getElementById('sideFront').classList.toggle('active', currentSide === 'front');
    document.getElementById('sideBack').classList.toggle('active', currentSide === 'back');
}

/**
 * Setup canvas events
 */
function setupCanvasEvents() {
    console.log('Setting up canvas events');
    canvas.on('mouse:down', (e) => {
        console.log('Mouse down on canvas, tool:', activeTool, 'drawing:', drawingPolygon);
        handleCanvasMouseDown(e);
    });
    canvas.on('mouse:move', handleCanvasMouseMove);
    canvas.on('mouse:up', handleCanvasMouseUp);
}

/**
 * Canvas mouse handlers for polygon drawing
 */
function handleCanvasMouseDown(e) {
    if (activeTool !== 'polygon' || !drawingPolygon) return;

    const pointer = canvas.getPointer(e.e);
    const x = pointer.x;
    const y = pointer.y;

    console.log(`Polygon point: (${x}, ${y}), total: ${polygonPoints.length + 1}`);
    polygonPoints.push([x, y]);

    // Draw larger, more visible point
    const circle = new fabric.Circle({
        left: x,
        top: y,
        radius: 8,
        fill: '#ff0000',
        stroke: '#ffffff',
        strokeWidth: 2,
        selectable: false,
        evented: false,
        originX: 'center',
        originY: 'center',
    });
    canvas.add(circle);

    // Draw connecting line if we have multiple points (simplified for v6)
    if (polygonPoints.length > 1) {
        const prev = polygonPoints[polygonPoints.length - 2];
        const line = new fabric.Line([prev[0], prev[1], x, y], {
            stroke: '#ff0000',
            strokeWidth: 3,
            selectable: false,
            evented: false,
        });
        canvas.add(line);
    }

    canvas.renderAll();
    showStatus(`Polygon points: ${polygonPoints.length}. Right-click to finish.`, 'success');
}

function handleCanvasMouseMove(e) {
    if (activeTool !== 'polygon' || !drawingPolygon || polygonPoints.length === 0) return;

    // Preview line to cursor
    const pointer = canvas.getPointer(e.e);
    canvas.renderAll();
}

function handleCanvasMouseUp(e) {
    // Polygon completion on right-click or double-click
    if (e.e.button === 2 || (e.e.detail && e.e.detail >= 2)) {
        finishPolygon();
    }
}

/**
 * Finish drawing polygon
 */
function finishPolygon() {
    if (polygonPoints.length < 3) {
        showStatus('Polygon needs at least 3 points', 'error');
        return;
    }

    // Remove preview points and lines
    canvas.getObjects().forEach(obj => {
        if (obj instanceof fabric.Circle ||
            (obj instanceof fabric.Line && !obj.annId)) {
            canvas.remove(obj);
        }
    });

    // Create polygon with visible colors
    console.log('Creating polygon from points:', polygonPoints);

    // Normalize coordinates so they start from 0,0
    const minX = Math.min(...polygonPoints.map(p => p[0]));
    const minY = Math.min(...polygonPoints.map(p => p[1]));
    const normalizedPoints = polygonPoints.map(([x, y]) => ({
        x: x - minX,
        y: y - minY
    }));

    console.log('Normalized points, minX:', minX, 'minY:', minY);

    const polygon = new fabric.Polygon(
        normalizedPoints,
        {
            fill: 'rgba(255, 255, 0, 0.7)',
            stroke: '#ff0000',
            strokeWidth: 4,
            selectable: true,
            left: minX,
            top: minY,
        }
    );

    console.log('Polygon created:', polygon);

    // Add custom properties
    polygon.annId = `ann_${Date.now()}`;
    polygon.kind = 'polygon';
    polygon.sides = [currentSide];

    // Simplified - skip poly controls for now
    // polygon.controls = fabric.controlsUtils.createPolyControls(polygon);
    polygon.hasBorders = true;
    polygon.objectCaching = false;

    console.log('Adding polygon to canvas, total objects before:', canvas.getObjects().length);
    canvas.add(polygon);
    console.log('Polygon added, total objects after:', canvas.getObjects().length);

    // Test with a simple blue circle to see if anything renders
    const testCircle = new fabric.Circle({
        left: 100,
        top: 100,
        radius: 50,
        fill: 'blue',
        stroke: 'green',
        strokeWidth: 5,
    });
    canvas.add(testCircle);
    console.log('Test circle added, total objects now:', canvas.getObjects().length);

    canvas.renderAll();
    console.log('Canvas rendered, zoom:', canvas.getZoom());

    // Reset
    drawingPolygon = false;
    polygonPoints = [];
    selectTool('select');

    showStatus('Polygon created (test mode)', 'success');
}

/**
 * Save card
 */
async function saveCard() {
    if (!currentCard) {
        showStatus('No card loaded', 'error');
        return;
    }

    try {
        // Save annotations from canvas
        saveCardAnnotations(canvas, currentCard);

        // Send to server
        const response = await fetch(`${API_BASE}/card`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(currentCard),
        });

        if (response.ok) {
            showStatus('Card saved!', 'success');
        } else {
            showStatus('Error saving card', 'error');
        }
    } catch (error) {
        showStatus(`Error: ${error.message}`, 'error');
    }
}

/**
 * Show status message
 */
function showStatus(message, type) {
    const el = document.getElementById('status');
    el.className = `status ${type}`;
    el.textContent = message;
    if (type === 'success') {
        setTimeout(() => el.textContent = '', 3000);
    }
}

// Initialize when page loads
document.addEventListener('DOMContentLoaded', initEditor);

// Handle right-click or double-click to finish polygon
document.addEventListener('contextmenu', (e) => {
    if (activeTool === 'polygon' && drawingPolygon && polygonPoints.length >= 3) {
        e.preventDefault();
        console.log('Right-click to finish polygon');
        finishPolygon();
    }
});

// Also finish on Escape key
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape' && activeTool === 'polygon' && drawingPolygon && polygonPoints.length >= 3) {
        console.log('Escape key to finish polygon');
        finishPolygon();
    }
});
