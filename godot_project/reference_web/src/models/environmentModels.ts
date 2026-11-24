import * as THREE from 'three';

export interface ArenaEnvironment {
  group: THREE.Group;
  updateEnvironment: (time: number, swordAuraColor: string) => void;
}

export function buildArenaEnvironment(): ArenaEnvironment {
  const group = new THREE.Group();
  group.name = 'SoulForge_Arena_Environment';

  const darkStoneMat = new THREE.MeshStandardMaterial({
    color: 0x1e2430,
    roughness: 0.88,
    metalness: 0.12,
  });
  const tileStoneMat = new THREE.MeshStandardMaterial({
    color: 0x2a3242,
    roughness: 0.82,
    metalness: 0.16,
  });
  const pillarStoneMat = new THREE.MeshStandardMaterial({
    color: 0x374151,
    roughness: 0.75,
    metalness: 0.2,
  });
  const anvilIronMat = new THREE.MeshStandardMaterial({
    color: 0x1f2937,
    roughness: 0.32,
    metalness: 0.88,
  });
  const runeRingMat = new THREE.MeshStandardMaterial({
    color: 0x38bdf8,
    emissive: 0x0284c7,
    emissiveIntensity: 0.65,
    roughness: 0.2,
  });
  const fireMat = new THREE.MeshStandardMaterial({
    color: 0xf97316,
    emissive: 0xff4500,
    emissiveIntensity: 1.4,
    roughness: 0.1,
  });

  // Main Arena Floor Disc (Radius 38)
  const floorDisc = new THREE.Mesh(new THREE.CylinderGeometry(38, 40, 1.2, 48), darkStoneMat);
  floorDisc.position.y = -0.6;
  floorDisc.receiveShadow = true;
  group.add(floorDisc);

  // Inner Elevated Combat Ring & Radial Stone Slabs
  const innerRing = new THREE.Mesh(new THREE.CylinderGeometry(28, 28.5, 0.16, 36), tileStoneMat);
  innerRing.position.y = -0.05;
  innerRing.receiveShadow = true;
  group.add(innerRing);

  // Concentric Glowing Rune Circles on the Arena Floor
  const runeCircleInner = new THREE.Mesh(new THREE.RingGeometry(5.6, 5.9, 48), runeRingMat);
  runeCircleInner.rotation.x = -Math.PI / 2;
  runeCircleInner.position.y = 0.04;
  group.add(runeCircleInner);

  const runeCircleOuter = new THREE.Mesh(new THREE.RingGeometry(16.5, 16.85, 64), runeRingMat);
  runeCircleOuter.rotation.x = -Math.PI / 2;
  runeCircleOuter.position.y = 0.04;
  group.add(runeCircleOuter);

  // Radial Flagstone Spokes
  for (let i = 0; i < 12; i++) {
    const angle = (i / 12) * Math.PI * 2;
    const spoke = new THREE.Mesh(new THREE.BoxGeometry(1.1, 0.08, 22), darkStoneMat);
    spoke.position.set(Math.sin(angle) * 17, 0.01, Math.cos(angle) * 17);
    spoke.rotation.y = angle;
    spoke.receiveShadow = true;
    group.add(spoke);
  }

  // Central Sacred Anvil Pedestal (At origin 0, 0, -19 so combat center stays open!)
  const forgeAltar = new THREE.Group();
  forgeAltar.position.set(0, 0, -21.5);
  group.add(forgeAltar);

  const dais1 = new THREE.Mesh(new THREE.CylinderGeometry(3.4, 3.9, 0.45, 8), pillarStoneMat);
  dais1.position.y = 0.22;
  dais1.receiveShadow = true;
  forgeAltar.add(dais1);

  const dais2 = new THREE.Mesh(new THREE.CylinderGeometry(2.3, 2.7, 0.45, 8), tileStoneMat);
  dais2.position.y = 0.65;
  dais2.receiveShadow = true;
  forgeAltar.add(dais2);

  // 3D Blacksmith Anvil on the Altar
  const anvilBase = new THREE.Mesh(new THREE.BoxGeometry(1.3, 0.55, 0.85), anvilIronMat);
  anvilBase.position.y = 1.15;
  anvilBase.castShadow = true;
  forgeAltar.add(anvilBase);

  const anvilTop = new THREE.Mesh(new THREE.BoxGeometry(1.75, 0.45, 0.78), anvilIronMat);
  anvilTop.position.y = 1.62;
  anvilTop.castShadow = true;
  forgeAltar.add(anvilTop);

  const anvilHorn = new THREE.Mesh(new THREE.ConeGeometry(0.36, 1.05, 8), anvilIronMat);
  anvilHorn.rotation.z = Math.PI / 2;
  anvilHorn.position.set(-1.32, 1.64, 0);
  anvilHorn.castShadow = true;
  forgeAltar.add(anvilHorn);

  // 8 Ancient Stone Pillars + Flickering Fire Braziers around the Arena Perimeter
  const flames: THREE.Mesh[] = [];
  const floatingCrystals: THREE.Mesh[] = [];

  for (let i = 0; i < 8; i++) {
    const angle = (i / 8) * Math.PI * 2 + Math.PI / 8;
    const radius = 27.5;
    const px = Math.sin(angle) * radius;
    const pz = Math.cos(angle) * radius;

    const pillarGroup = new THREE.Group();
    pillarGroup.position.set(px, 0, pz);
    pillarGroup.rotation.y = angle;
    group.add(pillarGroup);

    const base = new THREE.Mesh(new THREE.BoxGeometry(2.1, 0.8, 2.1), pillarStoneMat);
    base.position.y = 0.4;
    base.castShadow = true;
    base.receiveShadow = true;
    pillarGroup.add(base);

    const shaft = new THREE.Mesh(new THREE.CylinderGeometry(0.72, 0.85, 5.2, 8), pillarStoneMat);
    shaft.position.y = 3.4;
    shaft.castShadow = true;
    shaft.receiveShadow = true;
    pillarGroup.add(shaft);

    const runeBand = new THREE.Mesh(new THREE.CylinderGeometry(0.8, 0.8, 0.35, 8), runeRingMat);
    runeBand.position.y = 2.8;
    pillarGroup.add(runeBand);

    const capital = new THREE.Mesh(new THREE.BoxGeometry(1.9, 0.55, 1.9), pillarStoneMat);
    capital.position.y = 6.2;
    capital.castShadow = true;
    pillarGroup.add(capital);

    // Fire Brazier Bowl + 3D Flame
    const bowl = new THREE.Mesh(new THREE.CylinderGeometry(0.85, 0.45, 0.45, 10), anvilIronMat);
    bowl.position.y = 6.65;
    pillarGroup.add(bowl);

    const flame = new THREE.Mesh(new THREE.OctahedronGeometry(0.62, 0), fireMat);
    flame.position.y = 7.25;
    flame.scale.set(0.85, 1.55, 0.85);
    pillarGroup.add(flame);
    flames.push(flame);
  }

  // Outer Scenic Pine Trees, Boulders & Floating Crystal Monoliths (Radius 31..36)
  const foliageMat = new THREE.MeshStandardMaterial({ color: 0x14532d, roughness: 0.85 });
  const trunkMat = new THREE.MeshStandardMaterial({ color: 0x451a03, roughness: 0.9 });

  for (let i = 0; i < 16; i++) {
    const angle = (i / 16) * Math.PI * 2;
    const dist = 32.5 + (i % 3) * 1.6;
    const tx = Math.sin(angle) * dist;
    const tz = Math.cos(angle) * dist;

    if (i % 4 === 0) {
      // Floating Arcane Monolith Crystal
      const monolith = new THREE.Mesh(new THREE.OctahedronGeometry(1.15, 0), runeRingMat);
      monolith.position.set(tx, 3.5, tz);
      monolith.scale.set(0.7, 2.3, 0.7);
      group.add(monolith);
      floatingCrystals.push(monolith);
    } else {
      // Handcrafted 3-Tier Pine Tree + Rock Cluster
      const tree = new THREE.Group();
      tree.position.set(tx, 0, tz);
      const scale = 0.85 + (i % 3) * 0.22;
      tree.scale.setScalar(scale);

      const trunk = new THREE.Mesh(new THREE.CylinderGeometry(0.28, 0.42, 1.8, 7), trunkMat);
      trunk.position.y = 0.9;
      trunk.castShadow = true;
      tree.add(trunk);

      for (let tier = 0; tier < 3; tier++) {
        const cone = new THREE.Mesh(
          new THREE.ConeGeometry(1.65 - tier * 0.35, 2.1 - tier * 0.2, 7),
          foliageMat
        );
        cone.position.y = 2.1 + tier * 1.15;
        cone.castShadow = true;
        tree.add(cone);
      }
      group.add(tree);
    }
  }

  const updateEnvironment = (time: number, swordAuraColor: string) => {
    runeRingMat.color.set(swordAuraColor);
    runeRingMat.emissive.set(swordAuraColor);

    flames.forEach((flame, idx) => {
      const pulse = 1 + Math.sin(time * 9 + idx * 1.7) * 0.18;
      flame.scale.set(0.82 * pulse, 1.5 * pulse, 0.82 * pulse);
      flame.rotation.y = time * 2.5 + idx;
    });

    floatingCrystals.forEach((crystal, idx) => {
      crystal.position.y = 3.5 + Math.sin(time * 2.2 + idx) * 0.45;
      crystal.rotation.y = time * 0.8 + idx;
    });
  };

  return { group, updateEnvironment };
}
