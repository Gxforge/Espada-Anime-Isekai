import * as THREE from 'three';

/**
 * Handcrafted Diamond-Cross-Section Sword Blade Geometry
 * Constructs explicit vertices and triangle indices for a realistic multi-section
 * double-edged blade with central fuller/ridge, beveled cutting edges, ricasso, and sharp tip.
 */
export function createDiamondBladeGeometry(
  length: number,
  baseWidth: number,
  midWidth: number,
  tipLength: number,
  thickness: number
): THREE.BufferGeometry {
  const geometry = new THREE.BufferGeometry();

  const y0 = 0; // Base at crossguard
  const y1 = length * 0.18; // Ricasso / lower fuller
  const y2 = length * 0.55; // Mid blade
  const y3 = length - tipLength; // Upper blade before point
  const yTip = length; // Sharp point

  const w0 = baseWidth * 0.5;
  const w1 = (baseWidth * 1.04) * 0.5;
  const w2 = midWidth * 0.5;
  const w3 = (midWidth * 0.78) * 0.5;

  const t0 = thickness * 0.5;
  const t1 = thickness * 0.52;
  const t2 = thickness * 0.44;
  const t3 = thickness * 0.32;

  // Each cross-section ring has 4 vertices:
  // 0: Left sharp edge (-x, y, 0)
  // 1: Front central ridge (0, y, +z)
  // 2: Right sharp edge (+x, y, 0)
  // 3: Back central ridge (0, y, -z)
  const rings = [
    { y: y0, w: w0, t: t0 },
    { y: y1, w: w1, t: t1 },
    { y: y2, w: w2, t: t2 },
    { y: y3, w: w3, t: t3 },
  ];

  const positions: number[] = [];

  const pushTri = (
    ax: number, ay: number, az: number,
    bx: number, by: number, bz: number,
    cx: number, cy: number, cz: number
  ) => {
    positions.push(ax, ay, az, bx, by, bz, cx, cy, cz);
  };

  for (let i = 0; i < rings.length - 1; i++) {
    const rA = rings[i];
    const rB = rings[i + 1];

    // Front-Left bevel face
    pushTri(-rA.w, rA.y, 0, 0, rA.y, rA.t, -rB.w, rB.y, 0);
    pushTri(0, rA.y, rA.t, 0, rB.y, rB.t, -rB.w, rB.y, 0);

    // Front-Right bevel face
    pushTri(0, rA.y, rA.t, rA.w, rA.y, 0, 0, rB.y, rB.t);
    pushTri(rA.w, rA.y, 0, rB.w, rB.y, 0, 0, rB.y, rB.t);

    // Back-Right bevel face
    pushTri(rA.w, rA.y, 0, 0, rA.y, -rA.t, rB.w, rB.y, 0);
    pushTri(0, rA.y, -rA.t, 0, rB.y, -rB.t, rB.w, rB.y, 0);

    // Back-Left bevel face
    pushTri(0, rA.y, -rA.t, -rA.w, rA.y, 0, 0, rB.y, -rB.t);
    pushTri(-rA.w, rA.y, 0, -rB.w, rB.y, 0, 0, rB.y, -rB.t);
  }

  // Tip pyramid connecting last ring to sharp point (0, yTip, 0)
  const last = rings[rings.length - 1];
  // Front-Left tip
  pushTri(-last.w, last.y, 0, 0, last.y, last.t, 0, yTip, 0);
  // Front-Right tip
  pushTri(0, last.y, last.t, last.w, last.y, 0, 0, yTip, 0);
  // Back-Right tip
  pushTri(last.w, last.y, 0, 0, last.y, -last.t, 0, yTip, 0);
  // Back-Left tip
  pushTri(0, last.y, -last.t, -last.w, last.y, 0, 0, yTip, 0);

  // Bottom cap
  const first = rings[0];
  pushTri(-first.w, first.y, 0, first.w, first.y, 0, 0, first.y, first.t);
  pushTri(first.w, first.y, 0, -first.w, first.y, 0, 0, first.y, -first.t);

  geometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
  geometry.computeVertexNormals();
  return geometry;
}

/**
 * Handcrafted Serrated / Saw-Toothed Blade Geometry (for Obsidian & Gold Ricasso blades)
 */
export function createSerratedBladeGeometry(
  length: number,
  baseWidth: number,
  thickness: number,
  teethCount: number
): THREE.BufferGeometry {
  const geometry = new THREE.BufferGeometry();
  const positions: number[] = [];

  const pushTri = (
    ax: number, ay: number, az: number,
    bx: number, by: number, bz: number,
    cx: number, cy: number, cz: number
  ) => {
    positions.push(ax, ay, az, bx, by, bz, cx, cy, cz);
  };

  const segments = teethCount * 2;
  const bladeBodyLen = length * 0.82;

  for (let i = 0; i < segments; i++) {
    const tA = i / segments;
    const tB = (i + 1) / segments;
    const yA = tA * bladeBodyLen;
    const yB = tB * bladeBodyLen;

    const flareA = i % 2 === 1 ? 1.24 : 0.88;
    const flareB = (i + 1) % 2 === 1 ? 1.24 : 0.88;

    const wA = baseWidth * 0.5 * (1 - tA * 0.22) * flareA;
    const wB = baseWidth * 0.5 * (1 - tB * 0.22) * flareB;
    const zA = thickness * 0.5 * (1 - tA * 0.25);
    const zB = thickness * 0.5 * (1 - tB * 0.25);

    // Front Left
    pushTri(-wA, yA, 0, 0, yA, zA, -wB, yB, 0);
    pushTri(0, yA, zA, 0, yB, zB, -wB, yB, 0);
    // Front Right
    pushTri(0, yA, zA, wA, yA, 0, 0, yB, zB);
    pushTri(wA, yA, 0, wB, yB, 0, 0, yB, zB);
    // Back Right
    pushTri(wA, yA, 0, 0, yA, -zA, wB, yB, 0);
    pushTri(0, yA, -zA, 0, yB, -zB, wB, yB, 0);
    // Back Left
    pushTri(0, yA, -zA, -wA, yA, 0, 0, yB, -zB);
    pushTri(-wA, yA, 0, -wB, yB, 0, 0, yB, -zB);
  }

  // Tip
  const wEnd = baseWidth * 0.5 * 0.78 * 0.88;
  const zEnd = thickness * 0.5 * 0.75;
  pushTri(-wEnd, bladeBodyLen, 0, 0, bladeBodyLen, zEnd, 0, length, 0);
  pushTri(0, bladeBodyLen, zEnd, wEnd, bladeBodyLen, 0, 0, length, 0);
  pushTri(wEnd, bladeBodyLen, 0, 0, bladeBodyLen, -zEnd, 0, length, 0);
  pushTri(0, bladeBodyLen, -zEnd, -wEnd, bladeBodyLen, 0, 0, length, 0);

  geometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
  geometry.computeVertexNormals();
  return geometry;
}

/**
 * Handcrafted Wing / Feather / Crystal Shard Geometry
 */
export function createSculptedWingBladeGeometry(
  span: number,
  height: number,
  thickness: number
): THREE.BufferGeometry {
  const geometry = new THREE.BufferGeometry();
  const positions = new Float32Array([
    // Front upper facet
    0, 0, thickness,
    span * 0.6, height * 0.45, thickness * 0.4,
    span * 0.15, height * 0.85, 0,

    // Front outer facet
    span * 0.6, height * 0.45, thickness * 0.4,
    span, height, 0,
    span * 0.15, height * 0.85, 0,

    // Front lower facet
    0, 0, thickness,
    span * 0.85, height * 0.15, 0,
    span * 0.6, height * 0.45, thickness * 0.4,

    // Back upper facet
    0, 0, -thickness,
    span * 0.15, height * 0.85, 0,
    span * 0.6, height * 0.45, -thickness * 0.4,

    // Back outer facet
    span * 0.6, height * 0.45, -thickness * 0.4,
    span * 0.15, height * 0.85, 0,
    span, height, 0,

    // Back lower facet
    0, 0, -thickness,
    span * 0.6, height * 0.45, -thickness * 0.4,
    span * 0.85, height * 0.15, 0,
  ]);
  geometry.setAttribute('position', new THREE.BufferAttribute(positions, 3));
  geometry.computeVertexNormals();
  return geometry;
}

/**
 * Handcrafted Crescent Slash Wave Geometry for 3D Sword Beam Projectiles & Slash Trails
 */
export function createCrescentWaveGeometry(radius: number, width: number): THREE.BufferGeometry {
  const geometry = new THREE.BufferGeometry();
  const segments = 18;
  const positions: number[] = [];

  const pushTri = (
    ax: number, ay: number, az: number,
    bx: number, by: number, bz: number,
    cx: number, cy: number, cz: number
  ) => {
    positions.push(ax, ay, az, bx, by, bz, cx, cy, cz);
  };

  for (let i = 0; i < segments; i++) {
    const tA = (i / segments - 0.5) * Math.PI * 0.85;
    const tB = ((i + 1) / segments - 0.5) * Math.PI * 0.85;

    const taperA = Math.cos((i / segments - 0.5) * Math.PI);
    const taperB = Math.cos(((i + 1) / segments - 0.5) * Math.PI);

    const rOuterA = radius;
    const rInnerA = radius - width * Math.max(0.12, taperA);
    const rOuterB = radius;
    const rInnerB = radius - width * Math.max(0.12, taperB);

    const xOA = Math.sin(tA) * rOuterA;
    const zOA = Math.cos(tA) * rOuterA;
    const xIA = Math.sin(tA) * rInnerA;
    const zIA = Math.cos(tA) * rInnerA;

    const xOB = Math.sin(tB) * rOuterB;
    const zOB = Math.cos(tB) * rOuterB;
    const xIB = Math.sin(tB) * rInnerB;
    const zIB = Math.cos(tB) * rInnerB;

    // Top surface
    pushTri(xIA, 0.04 * taperA, zIA, xOA, 0, zOA, xOB, 0, zOB);
    pushTri(xIA, 0.04 * taperA, zIA, xOB, 0, zOB, xIB, 0.04 * taperB, zIB);
    // Bottom surface
    pushTri(xOA, 0, zOA, xIA, -0.04 * taperA, zIA, xOB, 0, zOB);
    pushTri(xOB, 0, zOB, xIA, -0.04 * taperA, zIA, xIB, -0.04 * taperB, zIB);
  }

  geometry.setAttribute('position', new THREE.Float32BufferAttribute(positions, 3));
  geometry.computeVertexNormals();
  return geometry;
}

/**
 * Exports any handcrafted THREE.Group into a standard Wavefront .OBJ or .GLTF-compatible JSON
 * so the user can download and inspect the 3D models created for the game!
 */
export function exportModelToOBJ(group: THREE.Group, modelName: string): string {
  let obj = `# Modelo 3D Creado a Mano - Forja de Almas: ${modelName}\n`;
  obj += `# Exportado directamente desde el Motor 3D del Juego\n`;
  obj += `o ${modelName.replace(/\s+/g, '_')}\n`;

  let vertexOffset = 1;
  group.updateMatrixWorld(true);

  group.traverse((child) => {
    const mesh = child as THREE.Mesh;
    if (mesh.isMesh && mesh.geometry) {
      const geom = mesh.geometry.clone();
      geom.applyMatrix4(child.matrixWorld);
      const posAttr = geom.getAttribute('position');
      if (!posAttr) return;

      obj += `g ${child.name || 'mesh_part'}\n`;
      for (let i = 0; i < posAttr.count; i++) {
        const vx = posAttr.getX(i).toFixed(4);
        const vy = posAttr.getY(i).toFixed(4);
        const vz = posAttr.getZ(i).toFixed(4);
        obj += `v ${vx} ${vy} ${vz}\n`;
      }

      const indexAttr = geom.getIndex();
      if (indexAttr) {
        for (let i = 0; i < indexAttr.count; i += 3) {
          const a = indexAttr.getX(i) + vertexOffset;
          const b = indexAttr.getX(i + 1) + vertexOffset;
          const c = indexAttr.getX(i + 2) + vertexOffset;
          obj += `f ${a} ${b} ${c}\n`;
        }
      } else {
        for (let i = 0; i < posAttr.count; i += 3) {
          const a = i + vertexOffset;
          const b = i + 1 + vertexOffset;
          const c = i + 2 + vertexOffset;
          obj += `f ${a} ${b} ${c}\n`;
        }
      }
      vertexOffset += posAttr.count;
    }
  });

  return obj;
}
