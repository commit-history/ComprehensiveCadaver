/**
 * Adapter between annotation schema and Fabric objects
 * Converts between tool-neutral JSON schema and Fabric.js objects
 */

// Custom Arrow class extending Line
class Arrow extends fabric.Line {
    static type = 'Arrow';

    _render(ctx) {
        super._render(ctx);
        const { x1, y1, x2, y2 } = this.calcLinePoints();
        const ang = Math.atan2(y2 - y1, x2 - x1);
        const len = Math.max(12, this.strokeWidth * 4);
        ctx.save();
        ctx.translate(x2, y2);
        ctx.rotate(ang);
        ctx.beginPath();
        ctx.moveTo(0, 0);
        ctx.lineTo(-len, len / 2);
        ctx.lineTo(-len, -len / 2);
        ctx.closePath();
        ctx.fillStyle = this.stroke;
        ctx.fill();
        ctx.restore();
    }
}

fabric.classRegistry.setClass(Arrow);

// Helper: transform point through matrix
function transformPoint(x, y, matrix) {
    const p = new fabric.Point(x, y);
    return fabric.util.transformPoint(p, matrix);
}

// Helper: round number
function round(n, decimals = 1) {
    return Math.round(n * Math.pow(10, decimals)) / Math.pow(10, decimals);
}

// Helper: get absolute coordinates for polygon/path
function getAbsPoint(obj, x, y) {
    const m = obj.calcTransformMatrix();
    const localPoint = new fabric.Point(x - obj.pathOffset.x, y - obj.pathOffset.y);
    return fabric.util.transformPoint(localPoint, m);
}

/**
 * Convert annotation schema to Fabric object
 */
function toFabric(ann) {
    let obj;

    switch (ann.kind) {
        case 'polygon':
            obj = new fabric.Polygon(ann.points, {
                fill: ann.fill || 'rgba(255,255,0,0.3)',
                stroke: ann.stroke || '#ff0000',
                strokeWidth: ann.width || 2,
                left: 0,
                top: 0,
                originX: 'left',
                originY: 'top',
            });
            break;

        case 'arrow': {
            const [x1, y1] = ann.points[0];
            const [x2, y2] = ann.points[1];
            obj = new Arrow(x1, y1, x2, y2, {
                stroke: ann.stroke || '#ff0000',
                strokeWidth: ann.width || 2,
                left: 0,
                top: 0,
                originX: 'left',
                originY: 'top',
            });
            break;
        }

        case 'line': {
            const [x1, y1] = ann.points[0];
            const [x2, y2] = ann.points[1];
            obj = new fabric.Line(x1, y1, x2, y2, {
                stroke: ann.stroke || '#000000',
                strokeWidth: ann.width || 2,
                left: 0,
                top: 0,
                originX: 'left',
                originY: 'top',
            });
            break;
        }

        case 'path':
            obj = new fabric.Path(ann.d, {
                fill: ann.fill || 'none',
                stroke: ann.stroke || '#0000ff',
                strokeWidth: ann.width || 2,
                left: 0,
                top: 0,
                originX: 'left',
                originY: 'top',
            });
            break;

        case 'text':
            const [x, y] = ann.at;
            obj = new fabric.IText(ann.text, {
                fontSize: ann.size || 20,
                fill: ann.color || '#000000',
                left: x,
                top: y,
                originX: 'left',
                originY: 'top',
            });
            break;
    }

    // Store custom properties
    obj.annId = ann.id;
    obj.kind = ann.kind;
    obj.sides = ann.sides || ['back'];

    return obj;
}

/**
 * Convert Fabric object to annotation schema
 */
function fromFabric(obj) {
    const ann = {
        id: obj.annId,
        kind: obj.kind,
        sides: obj.sides || ['back'],
    };

    switch (obj.kind) {
        case 'polygon': {
            // Get absolute coordinates
            const pts = obj.points.map(p => {
                const a = getAbsPoint(obj, p.x, p.y);
                return [round(a.x), round(a.y)];
            });
            ann.points = pts;
            ann.fill = obj.fill;
            ann.stroke = obj.stroke;
            ann.width = obj.strokeWidth;
            break;
        }

        case 'arrow':
        case 'line': {
            const { x1, y1, x2, y2 } = obj.calcLinePoints();
            ann.points = [[round(x1), round(y1)], [round(x2), round(y2)]];
            ann.stroke = obj.stroke;
            ann.width = obj.strokeWidth;
            break;
        }

        case 'path': {
            // Bake transforms into path
            const pathData = obj.path.map(([cmd, ...nums]) => {
                if (nums.length === 0) return [cmd].join(' ');
                const out = [];
                for (let i = 0; i < nums.length; i += 2) {
                    const a = getAbsPoint(obj, nums[i], nums[i + 1]);
                    out.push(round(a.x), round(a.y));
                }
                return [cmd, ...out].join(' ');
            }).join(' ');
            ann.d = pathData;
            ann.fill = obj.fill;
            ann.stroke = obj.stroke;
            ann.width = obj.strokeWidth;
            break;
        }

        case 'text':
            ann.at = [round(obj.left), round(obj.top)];
            ann.text = obj.text;
            ann.size = round(obj.fontSize * obj.scaleY);
            ann.color = obj.fill;
            break;
    }

    return ann;
}

/**
 * Load card annotations onto canvas
 */
function loadCardAnnotations(canvas, card) {
    canvas.clear();
    if (!card.annotations) return;

    card.annotations.forEach(ann => {
        const obj = toFabric(ann);
        canvas.add(obj);
    });
    canvas.renderAll();
}

/**
 * Save canvas annotations to card
 */
function saveCardAnnotations(canvas, card) {
    const objs = canvas.getObjects();
    card.annotations = objs.map(obj => fromFabric(obj));
}

/**
 * Set object visibility based on current side
 */
function setObjectSideVisibility(obj, currentSide) {
    const visible = (obj.sides || ['back']).includes(currentSide);
    obj.opacity = visible ? 1 : 0.3;
    obj.selectable = visible;
    obj.evented = visible;
}

/**
 * Update all objects for current side
 */
function updateCanvasForSide(canvas, currentSide) {
    canvas.getObjects().forEach(obj => {
        setObjectSideVisibility(obj, currentSide);
    });
    canvas.renderAll();
}
