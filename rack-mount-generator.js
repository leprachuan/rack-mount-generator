// THREE.JS Scene Setup
let scene, camera, renderer, controls, mountMesh, supportMesh;

function initScene() {
    const container = document.getElementById('preview-container');

    scene = new THREE.Scene();
    scene.background = new THREE.Color(0xf5f5f5);
    scene.add(new THREE.GridHelper(400, 40, 0xe0e0e0, 0xf0f0f0));

    camera = new THREE.PerspectiveCamera(75, container.clientWidth / container.clientHeight, 0.1, 1000);
    camera.position.set(150, 100, 150);

    renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(container.clientWidth, container.clientHeight);
    renderer.setPixelRatio(window.devicePixelRatio);
    container.appendChild(renderer.domElement);

    controls = new THREE.OrbitControls(camera, renderer.domElement);
    controls.enableDamping = true;
    controls.dampingFactor = 0.05;
    controls.autoRotate = true;
    controls.autoRotateSpeed = 2;

    // Lighting
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.7);
    scene.add(ambientLight);

    const directionalLight = new THREE.DirectionalLight(0xffffff, 0.8);
    directionalLight.position.set(100, 100, 100);
    directionalLight.castShadow = true;
    scene.add(directionalLight);

    animate();
}

function animate() {
    requestAnimationFrame(animate);
    controls.update();
    renderer.render(scene, camera);
}

// Check if device requires full-width (two-bracket) mode
function isWideDeviceMode(width, tolerance) {
    const RACK_HALF_WIDTH = 225.0;
    const openingWidth = width + 2 * tolerance;
    // If opening is wider than 200mm, use wide mode (two brackets)
    return openingWidth > 200;
}

// Generate a single bracket for wide-device mode
// bracketSide: 'left' or 'right' determines which half we're generating
function generateWideBracket(width, height, depth, tolerance, wallThickness, addSupport, shelfThickness, flangeThickness, gussetSize, shelfGussetWidth, bracketSide) {
    const group = new THREE.Group();
    
    const RACK_HALF_WIDTH = 225.0;
    const RACK_UNIT_HEIGHT = 44.45;
    const DEVICE_HEIGHT_PER_U = 25.0;  // Tighter fit for wide mode (25mm vs 35mm standard)
    const EAR_WIDTH = 15.875;
    const FULL_RACK_WIDTH = RACK_HALF_WIDTH * 2;  // 450mm
    
    const isBlank = document.getElementById('isBlank').checked;
    const addRackHoles = document.getElementById('addRackHoles').checked;
    
    // Calculate dimensions
    const rackUnits = Math.ceil(height / DEVICE_HEIGHT_PER_U);
    const faceplateHeight = rackUnits * RACK_UNIT_HEIGHT;
    const faceplateWidth = RACK_HALF_WIDTH;
    const faceplateThickness = wallThickness;
    
    // Device opening spans both brackets, centered in full rack
    const openingWidth = width + 2 * tolerance;
    const openingHeight = height + 2 * tolerance;
    const openingY = (faceplateHeight - openingHeight) / 2;
    
    // Calculate where opening starts in full-width coordinate system
    const fullOpeningX = (FULL_RACK_WIDTH - openingWidth) / 2;
    
    // Materials
    const bracketMat = new THREE.MeshPhongMaterial({ color: 0x667eea });
    const shelfMat = new THREE.MeshPhongMaterial({ color: 0x764ba2 });
    const earMat = new THREE.MeshPhongMaterial({ color: 0x4CAF50 });
    const flangeMat = new THREE.MeshPhongMaterial({ color: 0x9C27B0 });
    
    // Calculate this bracket's portion of the opening
    let localOpeningStart, localOpeningEnd;
    if (bracketSide === 'left') {
        // Left bracket covers X: 0 to RACK_HALF_WIDTH
        localOpeningStart = Math.max(0, fullOpeningX);
        localOpeningEnd = Math.min(RACK_HALF_WIDTH, fullOpeningX + openingWidth);
    } else {
        // Right bracket covers X: RACK_HALF_WIDTH to FULL_RACK_WIDTH
        // Convert to local coordinates (0 to RACK_HALF_WIDTH)
        localOpeningStart = Math.max(0, fullOpeningX - RACK_HALF_WIDTH);
        localOpeningEnd = Math.min(RACK_HALF_WIDTH, fullOpeningX + openingWidth - RACK_HALF_WIDTH);
    }
    const localOpeningWidth = localOpeningEnd - localOpeningStart;
    
    // BLANK PANEL - solid faceplate
    if (isBlank) {
        const blankGeom = new THREE.BoxGeometry(faceplateWidth, faceplateHeight, faceplateThickness);
        const blankMesh = new THREE.Mesh(blankGeom, bracketMat);
        blankMesh.position.set(faceplateWidth/2, faceplateHeight/2, -faceplateThickness/2);
        group.add(blankMesh);
    } else {
        // Create faceplate with partial opening
        
        // Bottom section (below opening)
        if (openingY > 0) {
            const bottomGeom = new THREE.BoxGeometry(faceplateWidth, openingY, faceplateThickness);
            const bottomMesh = new THREE.Mesh(bottomGeom, bracketMat);
            bottomMesh.position.set(faceplateWidth/2, openingY/2, -faceplateThickness/2);
            group.add(bottomMesh);
        }
        
        // Top section (above opening)
        const topHeight = faceplateHeight - openingY - openingHeight;
        if (topHeight > 0) {
            const topGeom = new THREE.BoxGeometry(faceplateWidth, topHeight, faceplateThickness);
            const topMesh = new THREE.Mesh(topGeom, bracketMat);
            topMesh.position.set(faceplateWidth/2, openingY + openingHeight + topHeight/2, -faceplateThickness/2);
            group.add(topMesh);
        }
        
        // Left section (beside opening in local coords)
        if (localOpeningStart > 0) {
            const leftGeom = new THREE.BoxGeometry(localOpeningStart, openingHeight, faceplateThickness);
            const leftMesh = new THREE.Mesh(leftGeom, bracketMat);
            leftMesh.position.set(localOpeningStart/2, openingY + openingHeight/2, -faceplateThickness/2);
            group.add(leftMesh);
        }
        
        // Right section (beside opening in local coords)
        const rightStart = localOpeningEnd;
        const rightWidth = faceplateWidth - rightStart;
        if (rightWidth > 0) {
            const rightGeom = new THREE.BoxGeometry(rightWidth, openingHeight, faceplateThickness);
            const rightMesh = new THREE.Mesh(rightGeom, bracketMat);
            rightMesh.position.set(rightStart + rightWidth/2, openingY + openingHeight/2, -faceplateThickness/2);
            group.add(rightMesh);
        }
    }
    
    // Support shelf - only on the side with opening, with OUTER gusset only
    if (addSupport && !isBlank && localOpeningWidth > 0) {
        const shelfDepth = depth + 10;
        const gussetWidth = shelfGussetWidth;
        
        // Shelf extends from the opening edge to the outer edge of bracket
        let shelfStart, shelfWidth, hasOuterGusset;
        
        if (bracketSide === 'left') {
            // Left bracket: shelf goes from opening start to left edge
            // Outer gusset is on the LEFT side (towards rack ear)
            shelfStart = localOpeningStart - gussetWidth;
            shelfWidth = localOpeningWidth + gussetWidth;  // Only outer gusset
            hasOuterGusset = localOpeningStart > gussetWidth;  // Has room for outer gusset
        } else {
            // Right bracket: shelf goes from opening end plus gusset
            // Outer gusset is on the RIGHT side (towards rack ear)
            shelfStart = localOpeningStart;
            shelfWidth = localOpeningWidth + gussetWidth;  // Only outer gusset
            hasOuterGusset = (faceplateWidth - localOpeningEnd) > gussetWidth;
        }
        
        if (shelfWidth > 0) {
            const shelfGeom = new THREE.BoxGeometry(shelfWidth, shelfThickness, shelfDepth);
            const shelfMesh = new THREE.Mesh(shelfGeom, shelfMat);
            shelfMesh.position.set(
                shelfStart + shelfWidth/2,
                openingY - shelfThickness/2,
                -faceplateThickness - shelfDepth/2
            );
            group.add(shelfMesh);
            
            // Only add the OUTER gusset (towards the rack ear, away from center)
            if (hasOuterGusset) {
                const gussetHeight = height;
                const gussetShape = new THREE.Shape();
                gussetShape.moveTo(0, 0);
                gussetShape.lineTo(shelfDepth, 0);
                gussetShape.lineTo(0, gussetHeight);
                gussetShape.lineTo(0, 0);
                
                const extrudeSettings = {
                    steps: 1,
                    depth: gussetWidth,
                    bevelEnabled: false
                };
                
                const gussetGeom = new THREE.ExtrudeGeometry(gussetShape, extrudeSettings);
                const outerGusset = new THREE.Mesh(gussetGeom, shelfMat);
                outerGusset.rotation.y = Math.PI / 2;
                
                if (bracketSide === 'left') {
                    // Outer gusset on left side of opening
                    outerGusset.position.set(
                        localOpeningStart - gussetWidth,
                        openingY,
                        -faceplateThickness
                    );
                } else {
                    // Outer gusset on right side of opening  
                    outerGusset.position.set(
                        localOpeningEnd,
                        openingY,
                        -faceplateThickness
                    );
                }
                group.add(outerGusset);
            }
        }
    }
    
    // Rack ear - on the outer edge
    const earSide = bracketSide;  // Left bracket gets left ear, right bracket gets right ear
    
    if (addRackHoles) {
        const holeRadius = 3.175;
        
        let holeX, earXStart, earXEnd;
        if (earSide === 'left') {
            holeX = -EAR_WIDTH / 2;
            earXStart = -EAR_WIDTH;
            earXEnd = 0;
        } else {
            holeX = faceplateWidth + EAR_WIDTH / 2;
            earXStart = faceplateWidth;
            earXEnd = faceplateWidth + EAR_WIDTH;
        }
        
        const holePositions = [];
        for (let u = 0; u < rackUnits; u++) {
            const baseY = u * RACK_UNIT_HEIGHT;
            holePositions.push(baseY + 6.35);
            holePositions.push(baseY + 22.225);
            holePositions.push(baseY + 38.1);
        }
        
        const earShape = new THREE.Shape();
        earShape.moveTo(earXStart, 0);
        earShape.lineTo(earXEnd, 0);
        earShape.lineTo(earXEnd, faceplateHeight);
        earShape.lineTo(earXStart, faceplateHeight);
        earShape.lineTo(earXStart, 0);
        
        holePositions.forEach(holeY => {
            const holePath = new THREE.Path();
            holePath.absarc(holeX, holeY, holeRadius, 0, Math.PI * 2, true);
            earShape.holes.push(holePath);
        });
        
        const extrudeSettings = {
            steps: 1,
            depth: faceplateThickness,
            bevelEnabled: false
        };
        
        const earGeom = new THREE.ExtrudeGeometry(earShape, extrudeSettings);
        const earMesh = new THREE.Mesh(earGeom, earMat);
        earMesh.position.set(0, 0, -faceplateThickness);
        group.add(earMesh);
    } else {
        const earGeom = new THREE.BoxGeometry(EAR_WIDTH, faceplateHeight, faceplateThickness);
        const earMesh = new THREE.Mesh(earGeom, earMat);
        if (earSide === 'left') {
            earMesh.position.set(-EAR_WIDTH/2, faceplateHeight/2, -faceplateThickness/2);
        } else {
            earMesh.position.set(faceplateWidth + EAR_WIDTH/2, faceplateHeight/2, -faceplateThickness/2);
        }
        group.add(earMesh);
    }
    
    // Joining flanges - TOP and BOTTOM (to connect to the other bracket)
    // Using ExtrudeGeometry with Shape.holes to create actual holes through the flange
    const flangeWidth = flangeThickness;
    const flangeDepth = 50.8;  // 2 inches
    const m3HoleRadius = 1.6;
    
    // Helper to create flange with real holes
    // Shape is drawn in depth(X) × height(Y) plane, extruded along flangeWidth
    // Then rotated so extrusion (holes) go along world X axis
    // Front hole offset: gussetSize + 5mm clearance to avoid gusset conflict
    const frontHoleOffset = gussetSize + 5;
    const backHoleOffset = 15;  // Back holes stay at 15mm from back edge
    
    function createFlangeWithHoles(fHeight, holeYPositions) {
        const flangeShape = new THREE.Shape();
        // Shape: X = depth (0 to flangeDepth), Y = height (0 to fHeight)
        flangeShape.moveTo(0, 0);
        flangeShape.lineTo(flangeDepth, 0);
        flangeShape.lineTo(flangeDepth, fHeight);
        flangeShape.lineTo(0, fHeight);
        flangeShape.lineTo(0, 0);
        
        // Add holes - two per Y position (front and back of flange)
        // Front hole offset by gussetSize + 5mm to clear gussets
        holeYPositions.forEach(holeY => {
            const hole1 = new THREE.Path();
            hole1.absarc(frontHoleOffset, holeY, m3HoleRadius, 0, Math.PI * 2, true);
            flangeShape.holes.push(hole1);
            
            const hole2 = new THREE.Path();
            hole2.absarc(flangeDepth - backHoleOffset, holeY, m3HoleRadius, 0, Math.PI * 2, true);
            flangeShape.holes.push(hole2);
        });
        
        const extrudeSettings = {
            steps: 1,
            depth: flangeWidth,
            bevelEnabled: false
        };
        
        return new THREE.ExtrudeGeometry(flangeShape, extrudeSettings);
    }
    
    // Bottom flange (below opening, at bottom of faceplate)
    const bottomFlangeHeight = openingY;
    if (bottomFlangeHeight > 5) {
        // Calculate hole Y positions
        let bottomHoleYPositions = [];
        if (bottomFlangeHeight >= 6) {
            if (bottomFlangeHeight >= 20) {
                const numHoles = Math.max(1, Math.floor(bottomFlangeHeight / 20));
                const edgeMargin = 5;
                const usableHeight = bottomFlangeHeight - 2 * edgeMargin;
                const spacing = numHoles > 1 ? usableHeight / (numHoles - 1) : 0;
                for (let i = 0; i < numHoles; i++) {
                    bottomHoleYPositions.push(edgeMargin + (numHoles > 1 ? i * spacing : usableHeight / 2));
                }
            } else {
                bottomHoleYPositions.push(bottomFlangeHeight / 2);
            }
        }
        
        const bottomFlangeGeom = createFlangeWithHoles(bottomFlangeHeight, bottomHoleYPositions);
        const bottomFlangeMesh = new THREE.Mesh(bottomFlangeGeom, flangeMat);
        
        // Rotate so extrusion (local Z) becomes world X (hole direction)
        // After rotation.y = PI/2: local Z → world X, local X → world -Z, local Y → world Y
        bottomFlangeMesh.rotation.y = Math.PI / 2;
        
        // Position: after rotation, mesh spans X: 0 to flangeWidth, Y: 0 to height, Z: 0 to -flangeDepth
        // We want it at Z = -faceplateThickness (front edge)
        if (bracketSide === 'left') {
            bottomFlangeMesh.position.set(faceplateWidth - flangeWidth, 0, -faceplateThickness);
        } else {
            bottomFlangeMesh.position.set(0, 0, -faceplateThickness);
        }
        group.add(bottomFlangeMesh);
    }
    
    // Top flange (above opening, at top of faceplate)
    const topFlangeHeight = faceplateHeight - openingY - openingHeight;
    if (topFlangeHeight > 5) {
        // Calculate hole Y positions (relative to flange, not faceplate)
        let topHoleYPositions = [];
        if (topFlangeHeight >= 6) {
            if (topFlangeHeight >= 20) {
                const numHoles = Math.max(1, Math.floor(topFlangeHeight / 20));
                const edgeMargin = 5;
                const usableHeight = topFlangeHeight - 2 * edgeMargin;
                const spacing = numHoles > 1 ? usableHeight / (numHoles - 1) : 0;
                for (let i = 0; i < numHoles; i++) {
                    topHoleYPositions.push(edgeMargin + (numHoles > 1 ? i * spacing : usableHeight / 2));
                }
            } else {
                topHoleYPositions.push(topFlangeHeight / 2);
            }
        }
        
        const topFlangeGeom = createFlangeWithHoles(topFlangeHeight, topHoleYPositions);
        const topFlangeMesh = new THREE.Mesh(topFlangeGeom, flangeMat);
        topFlangeMesh.rotation.y = Math.PI / 2;
        
        // Position at top of opening
        if (bracketSide === 'left') {
            topFlangeMesh.position.set(faceplateWidth - flangeWidth, openingY + openingHeight, -faceplateThickness);
        } else {
            topFlangeMesh.position.set(0, openingY + openingHeight, -faceplateThickness);
        }
        group.add(topFlangeMesh);
    }
    
    // Flange gussets - at corners connecting faceplate to flanges
    // Calculate gusset dimensions - may need to shrink to fit available space
    const gussetDepth = gussetSize;
    const gussetMat = new THREE.MeshPhongMaterial({ color: 0x9C27B0 });
    
    // Bottom gusset: top should align with shelf (openingY), bottom at faceplate bottom (0)
    // So max height is openingY
    const bottomGussetHeight = Math.min(gussetSize, openingY);
    
    // Top gusset: bottom at top of opening, top should not exceed faceplate top
    const topGussetHeight = Math.min(gussetSize, faceplateHeight - openingY - openingHeight);
    
    const gussetExtrudeSettings = {
        steps: 1,
        depth: flangeWidth,
        bevelEnabled: false
    };
    
    // Bottom corner gusset (only if there's room)
    if (bottomGussetHeight > 5) {
        // Create gusset shape - direction depends on bracket side
        const bottomGussetShape = new THREE.Shape();
        if (bracketSide === 'left') {
            // Triangle pointing left (into the faceplate from right edge)
            bottomGussetShape.moveTo(0, 0);
            bottomGussetShape.lineTo(0, bottomGussetHeight);
            bottomGussetShape.lineTo(-gussetDepth, 0);
            bottomGussetShape.lineTo(0, 0);
        } else {
            // Triangle pointing right (into the faceplate from left edge)
            bottomGussetShape.moveTo(0, 0);
            bottomGussetShape.lineTo(0, bottomGussetHeight);
            bottomGussetShape.lineTo(gussetDepth, 0);
            bottomGussetShape.lineTo(0, 0);
        }
        
        const bottomGussetGeom = new THREE.ExtrudeGeometry(bottomGussetShape, gussetExtrudeSettings);
        const bottomGusset = new THREE.Mesh(bottomGussetGeom, gussetMat);
        bottomGusset.rotation.x = -Math.PI / 2;
        
        // Position so top of gusset aligns with shelf (openingY), bottom at 0
        const bottomGussetY = openingY - bottomGussetHeight;
        if (bracketSide === 'left') {
            bottomGusset.position.set(faceplateWidth - flangeWidth, bottomGussetY, -faceplateThickness);
        } else {
            bottomGusset.position.set(flangeWidth, bottomGussetY, -faceplateThickness);
        }
        group.add(bottomGusset);
    }
    
    // Top corner gusset (only if there's room)
    if (topGussetHeight > 5) {
        const topGussetShape = new THREE.Shape();
        if (bracketSide === 'left') {
            topGussetShape.moveTo(0, 0);
            topGussetShape.lineTo(0, topGussetHeight);
            topGussetShape.lineTo(-gussetDepth, 0);
            topGussetShape.lineTo(0, 0);
        } else {
            topGussetShape.moveTo(0, 0);
            topGussetShape.lineTo(0, topGussetHeight);
            topGussetShape.lineTo(gussetDepth, 0);
            topGussetShape.lineTo(0, 0);
        }
        
        const topGussetGeom = new THREE.ExtrudeGeometry(topGussetShape, gussetExtrudeSettings);
        const topGusset = new THREE.Mesh(topGussetGeom, gussetMat);
        topGusset.rotation.x = -Math.PI / 2;
        
        // Position at top of opening
        if (bracketSide === 'left') {
            topGusset.position.set(faceplateWidth - flangeWidth, openingY + openingHeight, -faceplateThickness);
        } else {
            topGusset.position.set(flangeWidth, openingY + openingHeight, -faceplateThickness);
        }
        group.add(topGusset);
    }
    
    return group;
}

// Generate Mount Bracket Geometry
// This creates a preview that matches the STL generator output
function generateMountGeometry(width, height, depth, tolerance, wallThickness, addSupport, shelfThickness, flangeThickness, gussetSize, shelfGussetWidth) {
    const group = new THREE.Group();
    
    // Check if wide device mode is needed
    if (isWideDeviceMode(width, tolerance)) {
        // Generate BOTH brackets for wide device
        const RACK_HALF_WIDTH = 225.0;
        
        // Left bracket - geometry goes from 0 to RACK_HALF_WIDTH internally
        // Position so it spans -RACK_HALF_WIDTH to 0 in world coords
        const leftBracket = generateWideBracket(width, height, depth, tolerance, wallThickness, addSupport, shelfThickness, flangeThickness, gussetSize, shelfGussetWidth, 'left');
        leftBracket.position.set(-RACK_HALF_WIDTH, 0, 0);
        group.add(leftBracket);
        
        // Right bracket - geometry goes from 0 to RACK_HALF_WIDTH internally
        // Position so it spans 0 to RACK_HALF_WIDTH in world coords
        const rightBracket = generateWideBracket(width, height, depth, tolerance, wallThickness, addSupport, shelfThickness, flangeThickness, gussetSize, shelfGussetWidth, 'right');
        rightBracket.position.set(0, 0, 0);
        group.add(rightBracket);
        
        // Calculate centering offset - must use same DEVICE_HEIGHT_PER_U as generateWideBracket
        const RACK_UNIT_HEIGHT = 44.45;
        const DEVICE_HEIGHT_PER_U = 25.0;  // Wide mode uses 25mm
        const rackUnits = Math.ceil(height / DEVICE_HEIGHT_PER_U);
        const faceplateHeight = rackUnits * RACK_UNIT_HEIGHT;
        
        // Center the combined group
        group.position.set(0, -faceplateHeight/2, 0);
        
        return group;
    }
    
    // Standard single-bracket mode (original code)
    // Constants matching STL generator
    const RACK_HALF_WIDTH = 225.0;  // Half of 19" rack inside width
    const RACK_UNIT_HEIGHT = 44.45; // 1U in mm
    const DEVICE_HEIGHT_PER_U = 35.0; // Max device height per rack unit (leaves room for tolerance)
    const EAR_WIDTH = 15.875; // Standard rack ear width
    
    // Get settings from form
    const earSide = document.getElementById('earSide').value;
    const isBlank = document.getElementById('isBlank').checked;
    
    // Calculate dimensions
    const rackUnits = Math.ceil(height / DEVICE_HEIGHT_PER_U);
    const faceplateHeight = rackUnits * RACK_UNIT_HEIGHT;
    const faceplateWidth = RACK_HALF_WIDTH;
    const faceplateThickness = wallThickness; // This is now the plate thickness (default 10mm)
    
    // Opening dimensions (with tolerance)
    const openingWidth = width + 2 * tolerance;
    const openingHeight = height + 2 * tolerance;
    
    // Center the opening
    const openingX = (faceplateWidth - openingWidth) / 2;
    const openingY = (faceplateHeight - openingHeight) / 2;
    
    // Material for the bracket
    const bracketMat = new THREE.MeshPhongMaterial({ color: 0x667eea });
    const shelfMat = new THREE.MeshPhongMaterial({ color: 0x764ba2 });
    const earMat = new THREE.MeshPhongMaterial({ color: 0x4CAF50 });
    
    // BLANK PANEL - solid faceplate
    if (isBlank) {
        const blankGeom = new THREE.BoxGeometry(faceplateWidth, faceplateHeight, faceplateThickness);
        const blankMesh = new THREE.Mesh(blankGeom, bracketMat);
        blankMesh.position.set(faceplateWidth/2, faceplateHeight/2, -faceplateThickness/2);
        group.add(blankMesh);
    } else {
        // Create faceplate with hole using CSG-like approach with BoxGeometry pieces
        // Since Three.js doesn't have native CSG, we'll build it from pieces
        
        // Bottom section (below opening)
        if (openingY > 0) {
            const bottomGeom = new THREE.BoxGeometry(faceplateWidth, openingY, faceplateThickness);
            const bottomMesh = new THREE.Mesh(bottomGeom, bracketMat);
            bottomMesh.position.set(faceplateWidth/2, openingY/2, -faceplateThickness/2);
            group.add(bottomMesh);
        }
        
        // Top section (above opening)
        const topHeight = faceplateHeight - openingY - openingHeight;
        if (topHeight > 0) {
            const topGeom = new THREE.BoxGeometry(faceplateWidth, topHeight, faceplateThickness);
            const topMesh = new THREE.Mesh(topGeom, bracketMat);
            topMesh.position.set(faceplateWidth/2, openingY + openingHeight + topHeight/2, -faceplateThickness/2);
            group.add(topMesh);
        }
        
        // Left section (beside opening)
        if (openingX > 0) {
            const leftGeom = new THREE.BoxGeometry(openingX, openingHeight, faceplateThickness);
            const leftMesh = new THREE.Mesh(leftGeom, bracketMat);
            leftMesh.position.set(openingX/2, openingY + openingHeight/2, -faceplateThickness/2);
            group.add(leftMesh);
        }
        
        // Right section (beside opening)
        const rightWidth = faceplateWidth - openingX - openingWidth;
        if (rightWidth > 0) {
            const rightGeom = new THREE.BoxGeometry(rightWidth, openingHeight, faceplateThickness);
            const rightMesh = new THREE.Mesh(rightGeom, bracketMat);
            rightMesh.position.set(openingX + openingWidth + rightWidth/2, openingY + openingHeight/2, -faceplateThickness/2);
            group.add(rightMesh);
        }
    }
    
    // Support shelf (extends back from bottom of opening)
    // Shelf is wider than opening with triangular gussets for strength
    // Only add support if not a blank panel
    if (addSupport && !isBlank) {
        const shelfDepth = depth + 10; // Extends 10mm past device
        // Limit shelf gusset width to 5mm when width > 180mm but not in wide mode
        let gussetWidth = shelfGussetWidth;
        if (width > 180 && width <= 200) {
            gussetWidth = Math.min(gussetWidth, 5);
        }
        
        // Wider shelf
        const shelfWidth = openingWidth + (gussetWidth * 2);
        const shelfGeom = new THREE.BoxGeometry(shelfWidth, shelfThickness, shelfDepth);
        const shelfMesh = new THREE.Mesh(shelfGeom, shelfMat);
        // Position: centered under opening, extending back
        shelfMesh.position.set(
            openingX + openingWidth/2,
            openingY - shelfThickness/2,
            -faceplateThickness - shelfDepth/2
        );
        group.add(shelfMesh);
        
        // Left triangular gusset (right triangle for support)
        // Gusset height matches device height
        const gussetHeight = height; // Device height
        const gussetShape = new THREE.Shape();
        gussetShape.moveTo(0, 0);  // Front bottom
        gussetShape.lineTo(shelfDepth, 0);  // Back bottom
        gussetShape.lineTo(0, gussetHeight);  // Front top (height = device height)
        gussetShape.lineTo(0, 0);  // Close
        
        const extrudeSettings = {
            steps: 1,
            depth: gussetWidth,
            bevelEnabled: false
        };
        
        const gussetGeom = new THREE.ExtrudeGeometry(gussetShape, extrudeSettings);
        
        // Left gusset
        const leftGusset = new THREE.Mesh(gussetGeom, shelfMat);
        leftGusset.rotation.y = Math.PI / 2;
        leftGusset.position.set(
            openingX - gussetWidth,
            openingY,
            -faceplateThickness
        );
        group.add(leftGusset);
        
        // Right gusset
        const rightGusset = new THREE.Mesh(gussetGeom, shelfMat);
        rightGusset.rotation.y = Math.PI / 2;
        rightGusset.position.set(
            openingX + openingWidth,
            openingY,
            -faceplateThickness
        );
        group.add(rightGusset);
    }
    
    // Rack ear (mounting flange) - built with holes if needed
    const addRackHoles = document.getElementById('addRackHoles').checked;
    
    if (addRackHoles) {
        // Build ear with holes using BufferGeometry
        // We'll create the ear as a series of segments between holes
        const holeRadius = 3.175; // M6 hole radius (6.35mm / 2)
        const holeSegments = 24;
        
        // Calculate hole X position (center of ear)
        let holeX;
        let earXStart, earXEnd;
        if (earSide === 'left') {
            holeX = -EAR_WIDTH / 2;
            earXStart = -EAR_WIDTH;
            earXEnd = 0;
        } else {
            holeX = faceplateWidth + EAR_WIDTH / 2;
            earXStart = faceplateWidth;
            earXEnd = faceplateWidth + EAR_WIDTH;
        }
        
        // Collect all hole Y positions
        const holePositions = [];
        for (let u = 0; u < rackUnits; u++) {
            const baseY = u * RACK_UNIT_HEIGHT;
            holePositions.push(baseY + 6.35);
            holePositions.push(baseY + 22.225);
            holePositions.push(baseY + 38.1);
        }
        
        // Create ear geometry with holes using shape extrusion
        const earShape = new THREE.Shape();
        
        // Outer rectangle of ear
        earShape.moveTo(earXStart, 0);
        earShape.lineTo(earXEnd, 0);
        earShape.lineTo(earXEnd, faceplateHeight);
        earShape.lineTo(earXStart, faceplateHeight);
        earShape.lineTo(earXStart, 0);
        
        // Add circular holes
        holePositions.forEach(holeY => {
            const holePath = new THREE.Path();
            holePath.absarc(holeX, holeY, holeRadius, 0, Math.PI * 2, true);
            earShape.holes.push(holePath);
        });
        
        const extrudeSettings = {
            steps: 1,
            depth: faceplateThickness,
            bevelEnabled: false
        };
        
        const earGeom = new THREE.ExtrudeGeometry(earShape, extrudeSettings);
        const earMesh = new THREE.Mesh(earGeom, earMat);
        earMesh.position.set(0, 0, -faceplateThickness);
        group.add(earMesh);
    } else {
        // Simple ear without holes
        const earGeom = new THREE.BoxGeometry(EAR_WIDTH, faceplateHeight, faceplateThickness);
        const earMesh = new THREE.Mesh(earGeom, earMat);
        if (earSide === 'left') {
            earMesh.position.set(-EAR_WIDTH/2, faceplateHeight/2, -faceplateThickness/2);
        } else {
            earMesh.position.set(faceplateWidth + EAR_WIDTH/2, faceplateHeight/2, -faceplateThickness/2);
        }
        group.add(earMesh);
    }
    
    // Joining flange (on inner edge, opposite from ear)
    // This flange extends back into the rack and has M3 holes for connecting brackets
    // Using ExtrudeGeometry with Shape.holes to create actual holes through the flange
    const flangeWidth = flangeThickness;  // mm (thin for short M3 screws)
    const flangeDepth = 50.8;  // 2 inches
    const flangeMat = new THREE.MeshPhongMaterial({ color: 0x9C27B0 }); // Purple
    const m3HoleRadius = 1.6; // M3 clearance hole
    
    // Calculate hole Y positions
    const numJoiningHoles = Math.max(2, Math.floor(faceplateHeight / 30));
    const joiningSpacing = faceplateHeight / (numJoiningHoles + 1);
    const holeYPositions = [];
    for (let i = 1; i <= numJoiningHoles; i++) {
        holeYPositions.push(i * joiningSpacing);
    }
    
    // Create flange shape with holes
    // Shape: X = depth (0 to flangeDepth), Y = height (0 to faceplateHeight)
    const flangeShape = new THREE.Shape();
    flangeShape.moveTo(0, 0);
    flangeShape.lineTo(flangeDepth, 0);
    flangeShape.lineTo(flangeDepth, faceplateHeight);
    flangeShape.lineTo(0, faceplateHeight);
    flangeShape.lineTo(0, 0);
    
    // Add holes at front (gussetSize + 5mm to clear gussets) and back (15mm from back edge)
    const frontHoleOffset = gussetSize + 5;
    const backHoleOffset = 15;
    holeYPositions.forEach(holeY => {
        const hole1 = new THREE.Path();
        hole1.absarc(frontHoleOffset, holeY, m3HoleRadius, 0, Math.PI * 2, true);
        flangeShape.holes.push(hole1);
        
        const hole2 = new THREE.Path();
        hole2.absarc(flangeDepth - backHoleOffset, holeY, m3HoleRadius, 0, Math.PI * 2, true);
        flangeShape.holes.push(hole2);
    });
    
    const flangeExtrudeSettings = {
        steps: 1,
        depth: flangeWidth,
        bevelEnabled: false
    };
    
    const flangeGeom = new THREE.ExtrudeGeometry(flangeShape, flangeExtrudeSettings);
    const flangeMesh = new THREE.Mesh(flangeGeom, flangeMat);
    
    // Rotate so extrusion (local Z) becomes world X (hole direction)
    flangeMesh.rotation.y = Math.PI / 2;
    
    if (earSide === 'left') {
        // Flange on right edge (inner)
        flangeMesh.position.set(faceplateWidth - flangeWidth, 0, -faceplateThickness);
    } else {
        // Flange on left edge (inner)
        flangeMesh.position.set(0, 0, -faceplateThickness);
    }
    group.add(flangeMesh);
    
    // Flange gussets (right-angle triangular supports connecting faceplate back to flange)
    const gussetHeight = gussetSize;  // Height up the faceplate back (Y)
    const gussetDepth = gussetSize;   // Depth along the flange (Z)
    const gussetMat = new THREE.MeshPhongMaterial({ color: 0x9C27B0 }); // Same purple as flange
    
    // Create gusset shape - direction depends on ear side
    // When ear is left, flange is right (inner), gusset points left (into faceplate)
    // When ear is right, flange is left (inner), gusset points right (into faceplate)
    const gussetShape = new THREE.Shape();
    gussetShape.moveTo(0, 0);  // Corner (at faceplate back / flange front)
    gussetShape.lineTo(0, gussetHeight);  // Up the faceplate back
    if (earSide === 'left') {
        gussetShape.lineTo(-gussetDepth, 0);  // Along the flange (into rack, pointing left)
    } else {
        gussetShape.lineTo(gussetDepth, 0);  // Along the flange (into rack, pointing right)
    }
    gussetShape.lineTo(0, 0);
    
    const gussetExtrudeSettings = {
        steps: 1,
        depth: flangeWidth,
        bevelEnabled: false
    };
    
    const gussetGeom = new THREE.ExtrudeGeometry(gussetShape, gussetExtrudeSettings);
    
    // Bottom gusset (lifted 10mm from bottom)
    const bottomGusset = new THREE.Mesh(gussetGeom, gussetMat);
    bottomGusset.rotation.x = -Math.PI / 2;  // Rotate to Y-Z plane
    if (earSide === 'left') {
        bottomGusset.position.set(faceplateWidth - flangeWidth, 10, -faceplateThickness);
    } else {
        bottomGusset.position.set(0, 10, -faceplateThickness);
    }
    group.add(bottomGusset);
    
    // Top gusset - copy of bottom, shifted up
    const topGusset = new THREE.Mesh(gussetGeom.clone(), gussetMat);
    topGusset.rotation.x = -Math.PI / 2;  // Same rotation as bottom
    if (earSide === 'left') {
        topGusset.position.set(faceplateWidth - flangeWidth, faceplateHeight - gussetHeight, -faceplateThickness);
    } else {
        topGusset.position.set(0, faceplateHeight - gussetHeight, -faceplateThickness);
    }
    group.add(topGusset);
    
    // Center the group
    group.position.set(-faceplateWidth/2, -faceplateHeight/2, 0);
    
    return group;
}

// Update preview
function updatePreview() {
    const width = parseFloat(document.getElementById('deviceWidth').value);
    const height = parseFloat(document.getElementById('deviceHeight').value);
    const depth = parseFloat(document.getElementById('deviceDepth').value);
    const tolerance = parseFloat(document.getElementById('tolerance').value);
    const wallThickness = parseFloat(document.getElementById('wallThickness').value);
    const shelfThickness = parseFloat(document.getElementById('shelfThickness').value);
    const flangeThickness = parseFloat(document.getElementById('flangeThickness').value);
    const gussetSize = parseFloat(document.getElementById('gussetSize').value);
    const shelfGussetWidth = parseFloat(document.getElementById('shelfGussetWidth').value);
    const addSupport = document.getElementById('addSupport').checked;

    // Remove old mesh
    if (mountMesh) scene.remove(mountMesh);
    if (supportMesh) scene.remove(supportMesh);

    // Generate geometry (returns a group)
    mountMesh = generateMountGeometry(width, height, depth, tolerance, wallThickness, addSupport, shelfThickness, flangeThickness, gussetSize, shelfGussetWidth);
    scene.add(mountMesh);

    // Remove old device mesh if exists
    const oldDevice = scene.getObjectByName('deviceMesh');
    if (oldDevice) scene.remove(oldDevice);

    // Constants
    const RACK_HALF_WIDTH = 225.0;
    const FULL_RACK_WIDTH = RACK_HALF_WIDTH * 2;
    const RACK_UNIT_HEIGHT = 44.45;
    // Use different DEVICE_HEIGHT_PER_U for wide vs standard mode
    const isWide = isWideDeviceMode(width, tolerance);
    const DEVICE_HEIGHT_PER_U = isWide ? 25.0 : 35.0;
    const rackUnits = Math.ceil(height / DEVICE_HEIGHT_PER_U);
    const faceplateHeight = rackUnits * RACK_UNIT_HEIGHT;
    const openingWidth = width + 2 * tolerance;
    const openingHeight = height + 2 * tolerance;
    const openingY = (faceplateHeight - openingHeight) / 2;
    
    // Add device representation (semi-transparent)
    const deviceGeometry = new THREE.BoxGeometry(width, height, depth);
    const deviceMaterial = new THREE.MeshPhongMaterial({
        color: 0xff6b6b,
        transparent: true,
        opacity: 0.4,
        wireframe: false
    });
    const deviceMesh = new THREE.Mesh(deviceGeometry, deviceMaterial);
    deviceMesh.name = 'deviceMesh';
    
    // Position device based on mode
    if (isWide) {
        // Wide mode: device is centered in full-width rack
        deviceMesh.position.set(
            0,  // Centered in full-width
            openingY + tolerance + height/2 - faceplateHeight/2,
            -(wallThickness + depth/2)
        );
    } else {
        // Standard mode: device centered in half-width
        const openingX = (RACK_HALF_WIDTH - openingWidth) / 2;
        deviceMesh.position.set(
            openingX + openingWidth/2 - RACK_HALF_WIDTH/2,
            openingY + tolerance + height/2 - faceplateHeight/2,
            -(wallThickness + depth/2)
        );
    }
    scene.add(deviceMesh);

    // Calculate stats
    calculateStats(width, height, depth, tolerance, wallThickness, shelfThickness);
    
    // Update wide mode indicator
    updateWideModeIndicator(width, tolerance);
}

function updateWideModeIndicator(width, tolerance) {
    const indicator = document.getElementById('wideModeIndicator');
    if (isWideDeviceMode(width, tolerance)) {
        indicator.style.display = 'block';
        indicator.innerHTML = '⚠️ <strong>Wide Device Mode:</strong> Device spans full rack width. Two brackets will be generated (left + right) with joining flanges above and below the device.';
    } else {
        indicator.style.display = 'none';
    }
}

function calculateStats(width, height, depth, tolerance, wallThickness, shelfThickness) {
    // Constants
    const RACK_HALF_WIDTH = 225.0;
    const RACK_UNIT_HEIGHT = 44.45;
    
    // Check if wide mode
    const wideMode = isWideDeviceMode(width, tolerance);
    
    // Use different DEVICE_HEIGHT_PER_U for wide vs standard mode
    const DEVICE_HEIGHT_PER_U = wideMode ? 25.0 : 35.0;
    
    // Calculate dimensions
    const rackUnits = Math.ceil(height / DEVICE_HEIGHT_PER_U);
    const faceplateHeight = rackUnits * RACK_UNIT_HEIGHT;
    const openingWidth = width + 2 * tolerance;
    const openingHeight = height + 2 * tolerance;
    
    let totalVolume;
    let numParts;
    
    if (wideMode) {
        // Two brackets, each half-width
        // Each faceplate has partial opening
        const faceplateVolume = (RACK_HALF_WIDTH * faceplateHeight * wallThickness) * 2;
        const openingVolume = openingWidth * openingHeight * wallThickness;
        const netFaceplateVolume = faceplateVolume - openingVolume;
        
        // Shelf spans opening (roughly)
        const shelfDepth = depth + 10;
        const shelfVolume = openingWidth * shelfThickness * shelfDepth;
        
        totalVolume = (netFaceplateVolume + shelfVolume) / 1000;
        numParts = 2;
    } else {
        // Single bracket
        const faceplateVolume = (RACK_HALF_WIDTH * faceplateHeight * wallThickness) - 
                                (openingWidth * openingHeight * wallThickness);
        const shelfDepth = depth + 10;
        const shelfVolume = openingWidth * shelfThickness * shelfDepth;
        
        totalVolume = (faceplateVolume + shelfVolume) / 1000;
        numParts = 1;
    }

    const infill = parseInt(document.getElementById('infill').value) / 100;
    const estimatedVolume = totalVolume * infill;
    const estimatedWeight = estimatedVolume * 1.24; // PLA density

    document.getElementById('volumeValue').textContent = totalVolume.toFixed(1);
    document.getElementById('weightValue').textContent = estimatedWeight.toFixed(1);
    document.getElementById('partsValue').textContent = numParts.toString();

    // Rough estimate: 0.5 hours per 10cm³ at 20% infill
    const printHours = (estimatedVolume / 10) * 0.5;
    document.getElementById('timeValue').textContent = printHours.toFixed(1) + 'h';
}

// Export STL from Three.js scene
function exportSTL() {
    if (!mountMesh) {
        alert('No geometry to export. Please configure your mount first.');
        return null;
    }
    
    const exporter = new THREE.STLExporter();
    
    // Create a temporary group with the geometry in the correct position
    const exportGroup = new THREE.Group();
    
    // Clone the mount mesh and reset its position for export
    // The preview centers the model, but we want origin at corner for printing
    mountMesh.traverse((child) => {
        if (child.isMesh) {
            const clonedMesh = child.clone();
            // Apply the parent's transformations
            clonedMesh.applyMatrix4(mountMesh.matrixWorld);
            exportGroup.add(clonedMesh);
        }
    });
    
    // Generate binary STL
    const stlBinary = exporter.parse(exportGroup, { binary: true });
    return stlBinary;
}

// Export a specific bracket (for wide mode)
function exportBracketSTL(bracketSide) {
    const width = parseFloat(document.getElementById('deviceWidth').value);
    const height = parseFloat(document.getElementById('deviceHeight').value);
    const depth = parseFloat(document.getElementById('deviceDepth').value);
    const tolerance = parseFloat(document.getElementById('tolerance').value);
    const wallThickness = parseFloat(document.getElementById('wallThickness').value);
    const shelfThickness = parseFloat(document.getElementById('shelfThickness').value);
    const flangeThickness = parseFloat(document.getElementById('flangeThickness').value);
    const gussetSize = parseFloat(document.getElementById('gussetSize').value);
    const shelfGussetWidth = parseFloat(document.getElementById('shelfGussetWidth').value);
    const addSupport = document.getElementById('addSupport').checked;
    
    // Generate fresh bracket geometry - it's already in correct local coords (0 to RACK_HALF_WIDTH)
    const bracket = generateWideBracket(width, height, depth, tolerance, wallThickness, addSupport, shelfThickness, flangeThickness, gussetSize, shelfGussetWidth, bracketSide);
    
    // Update all matrices in the hierarchy
    bracket.updateMatrixWorld(true);
    
    const exporter = new THREE.STLExporter();
    const exportGroup = new THREE.Group();
    
    // Clone meshes and bake their transforms into geometry
    bracket.traverse((child) => {
        if (child.isMesh) {
            // Clone geometry to avoid modifying original
            const clonedGeom = child.geometry.clone();
            // Bake the child's world matrix into geometry vertices
            clonedGeom.applyMatrix4(child.matrixWorld);
            
            const clonedMesh = new THREE.Mesh(clonedGeom, child.material);
            exportGroup.add(clonedMesh);
        }
    });
    
    return exporter.parse(exportGroup, { binary: true });
}

function downloadSTLFromPreview() {
    const width = parseFloat(document.getElementById('deviceWidth').value);
    const tolerance = parseFloat(document.getElementById('tolerance').value);
    
    if (isWideDeviceMode(width, tolerance)) {
        // Wide mode: download two files
        downloadBracket('left');
        // Small delay between downloads
        setTimeout(() => downloadBracket('right'), 500);
    } else {
        // Standard mode: single file
        const stlData = exportSTL();
        if (!stlData) return;
        
        const blob = new Blob([stlData], { type: 'application/octet-stream' });
        const url = URL.createObjectURL(blob);
        const link = document.createElement('a');
        link.href = url;
        link.download = 'rack_mount_bracket.stl';
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
    }
}

function downloadBracket(side) {
    const stlData = exportBracketSTL(side);
    if (!stlData) return;
    
    const blob = new Blob([stlData], { type: 'application/octet-stream' });
    const url = URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `rack_mount_bracket_${side}.stl`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
    URL.revokeObjectURL(url);
}

// Form Handling
document.getElementById('mountForm').addEventListener('submit', async (e) => {
    e.preventDefault();

    const statusDiv = document.getElementById('statusMessage');
    
    try {
        // Show loading state
        statusDiv.innerHTML = '<p style="color: #667eea;">⏳ Generating STL from preview...</p>';
        
        // Short delay to show the message
        await new Promise(resolve => setTimeout(resolve, 100));
        
        const width = parseFloat(document.getElementById('deviceWidth').value);
        const tolerance = parseFloat(document.getElementById('tolerance').value);
        const wideMode = isWideDeviceMode(width, tolerance);
        
        // Export directly from Three.js
        downloadSTLFromPreview();
        
        // Display success message
        statusDiv.innerHTML = `<p class="success">✓ STL exported successfully!</p>`;
        
        // Show file info display based on mode
        const fileList = document.getElementById('fileList');
        
        if (wideMode) {
            fileList.innerHTML = `
                <div class="file-item">
                    <div>
                        <div class="file-name">📄 rack_mount_bracket_left.stl</div>
                        <div class="file-size">Left bracket (with left rack ear)</div>
                    </div>
                    <button class="btn-download" onclick="downloadBracket('left')">⬇ Download</button>
                </div>
                <div class="file-item">
                    <div>
                        <div class="file-name">📄 rack_mount_bracket_right.stl</div>
                        <div class="file-size">Right bracket (with right rack ear)</div>
                    </div>
                    <button class="btn-download" onclick="downloadBracket('right')">⬇ Download</button>
                </div>
            `;
        } else {
            fileList.innerHTML = `
                <div class="file-item">
                    <div>
                        <div class="file-name">📄 rack_mount_bracket.stl</div>
                        <div class="file-size">Exported from preview</div>
                    </div>
                    <button class="btn-download" onclick="downloadSTLFromPreview()">⬇ Download Again</button>
                </div>
            `;
        }
        document.getElementById('filesContainer').style.display = 'block';
        
    } catch (error) {
        statusDiv.innerHTML = `<p class="error">✗ Error: ${error.message}</p>`;
        console.error('Export error:', error);
    }
});

function displayGeneratedFiles(jobId, files, stats) {
    const fileList = document.getElementById('fileList');
    fileList.innerHTML = '';

    files.forEach(file => {
        const item = document.createElement('div');
        item.className = 'file-item';
        
        let sizeInfo = '';
        if (file.size_mb) {
            sizeInfo += `${file.size_mb} MB`;
        }
        if (file.triangles) {
            sizeInfo += ` • ${file.triangles.toLocaleString()} triangles`;
        }
        
        item.innerHTML = `
            <div>
                <div class="file-name">📄 ${file.name}</div>
                <div class="file-size">${sizeInfo}</div>
            </div>
            <button class="btn-download" onclick="downloadFile('${jobId}', '${file.name}')">⬇ Download</button>
        `;
        fileList.appendChild(item);
    });
    
    // Add download all button
    const downloadAllItem = document.createElement('div');
    downloadAllItem.className = 'file-item';
    downloadAllItem.style.marginTop = '15px';
    downloadAllItem.innerHTML = `
        <div>
            <div class="file-name">📦 Download All as ZIP</div>
            <div class="file-size">All files packaged together</div>
        </div>
        <button class="btn-download" style="background: #2196F3;" onclick="downloadAllFiles('${jobId}')">⬇ Download ZIP</button>
    `;
    fileList.appendChild(downloadAllItem);

    document.getElementById('filesContainer').style.display = 'block';
}

function downloadFile(jobId, filename) {
    const link = document.createElement('a');
    link.href = `/api/download/${jobId}/${filename}`;
    link.download = filename;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

function downloadAllFiles(jobId) {
    const link = document.createElement('a');
    link.href = `/api/download-zip/${jobId}`;
    link.download = `rack_mount_${jobId}.zip`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

function resetForm() {
    document.getElementById('mountForm').reset();
    document.getElementById('deviceWidth').value = '100';
    document.getElementById('deviceHeight').value = '44';
    document.getElementById('deviceDepth').value = '200';
    document.getElementById('tolerance').value = '2';
    document.getElementById('wallThickness').value = '10';
    document.getElementById('infill').value = '20';
    document.getElementById('filesContainer').style.display = 'none';
    document.getElementById('statusMessage').innerHTML = '';
    updatePreview();
}

// Input listeners for live preview
['deviceWidth', 'deviceHeight', 'deviceDepth', 'tolerance', 'wallThickness', 'shelfThickness', 'flangeThickness', 'gussetSize', 'shelfGussetWidth', 'infill'].forEach(id => {
    document.getElementById(id).addEventListener('input', updatePreview);
});

document.getElementById('addSupport').addEventListener('change', updatePreview);
document.getElementById('earSide').addEventListener('change', updatePreview);
document.getElementById('addRackHoles').addEventListener('change', updatePreview);
document.getElementById('isBlank').addEventListener('change', updatePreview);

// Initialize
window.addEventListener('load', () => {
    initScene();
    updatePreview();
});

window.addEventListener('resize', () => {
    const container = document.getElementById('preview-container');
    camera.aspect = container.clientWidth / container.clientHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(container.clientWidth, container.clientHeight);
});
