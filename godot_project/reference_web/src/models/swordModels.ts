import * as THREE from 'three';
import { SwordTierId } from '../types/game';
import {
  createDiamondBladeGeometry,
  createSculptedWingBladeGeometry,
  createSerratedBladeGeometry,
} from './customGeometry';

export interface SwordModelInstance {
  group: THREE.Group;
  bladePivot: THREE.Group;
  orbitGroup: THREE.Group;
  tipPositionLocal: THREE.Vector3;
  updateAnimation: (time: number) => void;
}

/**
 * Builds the handcrafted 3D model for any of the 8 Sword Evolution Tiers.
 * Also applies sub-level visual progression (e.g., Level 1..4 within Wood, 5..9 within Copper, etc.)
 */
export function buildSword3DModel(tierId: SwordTierId, currentLevel = 1): SwordModelInstance {
  const root = new THREE.Group();
  root.name = `Sword_${tierId}_Lv${currentLevel}`;

  const bladePivot = new THREE.Group();
  bladePivot.name = 'BladePivot';
  root.add(bladePivot);

  const orbitGroup = new THREE.Group();
  orbitGroup.name = 'OrbitingParts';
  bladePivot.add(orbitGroup);

  // Sub-level within current 5-level bracket (0 to 4)
  const subLevel = Math.max(0, (currentLevel - 1) % 5);
  const subLevelGlowBoost = subLevel * 0.18;

  let tipY = 2.4;

  switch (tierId) {
    case 'wood': {
      tipY = 2.15;
      const oakMat = new THREE.MeshStandardMaterial({
        color: 0x9c6635,
        roughness: 0.78,
        metalness: 0.05,
      });
      const darkOakMat = new THREE.MeshStandardMaterial({
        color: 0x5c3a1e,
        roughness: 0.85,
        metalness: 0.05,
      });
      const bevelWoodMat = new THREE.MeshStandardMaterial({
        color: 0xc48f5a,
        roughness: 0.65,
        metalness: 0.08,
        emissive: 0x4ade80,
        emissiveIntensity: subLevel * 0.06,
      });
      const ropeMat = new THREE.MeshStandardMaterial({
        color: 0xd9b98b,
        roughness: 0.9,
        metalness: 0.0,
      });
      const leafMat = new THREE.MeshStandardMaterial({
        color: 0x22c55e,
        emissive: 0x16a34a,
        emissiveIntensity: 0.35 + subLevelGlowBoost,
        roughness: 0.4,
      });

      // Handle / Grip
      const grip = new THREE.Mesh(new THREE.CylinderGeometry(0.065, 0.08, 0.56, 10), darkOakMat);
      grip.position.y = -0.28;
      grip.name = 'Wood_Grip';
      bladePivot.add(grip);

      // Hemp rope bindings around handle
      for (let i = 0; i < 5; i++) {
        const ropeRing = new THREE.Mesh(new THREE.TorusGeometry(0.074, 0.018, 8, 14), ropeMat);
        ropeRing.rotation.x = Math.PI / 2 + (i % 2 === 0 ? 0.12 : -0.12);
        ropeRing.position.y = -0.46 + i * 0.09;
        ropeRing.name = `Rope_Wrap_${i}`;
        bladePivot.add(ropeRing);
      }

      // Pommel: Acorn-like carved oak cap + glowing forest seed core
      const pommel = new THREE.Mesh(new THREE.DodecahedronGeometry(0.12, 0), darkOakMat);
      pommel.position.y = -0.6;
      pommel.name = 'Wood_Pommel';
      bladePivot.add(pommel);

      const seedCore = new THREE.Mesh(new THREE.OctahedronGeometry(0.065, 0), leafMat);
      seedCore.position.set(0, -0.6, 0.09);
      seedCore.name = 'Living_Seed_Gem';
      bladePivot.add(seedCore);

      // Sprout leaves on pommel
      const leafGeo = createSculptedWingBladeGeometry(0.18, 0.22, 0.025);
      const leafL = new THREE.Mesh(leafGeo, leafMat);
      leafL.position.set(0.05, -0.64, 0);
      leafL.rotation.z = -0.5;
      bladePivot.add(leafL);

      // Crossguard: Carved oak beam with rope cross-lashing & iron pins
      const guardMain = new THREE.Mesh(new THREE.BoxGeometry(0.76, 0.13, 0.16), darkOakMat);
      guardMain.position.y = 0.02;
      guardMain.name = 'Wood_Crossguard';
      bladePivot.add(guardMain);

      const guardCapL = new THREE.Mesh(new THREE.BoxGeometry(0.12, 0.17, 0.18), oakMat);
      guardCapL.position.set(-0.38, 0.03, 0);
      guardCapL.rotation.z = 0.2;
      bladePivot.add(guardCapL);

      const guardCapR = new THREE.Mesh(new THREE.BoxGeometry(0.12, 0.17, 0.18), oakMat);
      guardCapR.position.set(0.38, 0.03, 0);
      guardCapR.rotation.z = -0.2;
      bladePivot.add(guardCapR);

      // Rope X-binding on guard center
      const crossRope1 = new THREE.Mesh(new THREE.TorusGeometry(0.11, 0.022, 8, 16), ropeMat);
      crossRope1.position.y = 0.02;
      crossRope1.rotation.y = Math.PI / 4;
      bladePivot.add(crossRope1);
      const crossRope2 = crossRope1.clone();
      crossRope2.rotation.y = -Math.PI / 4;
      bladePivot.add(crossRope2);

      // Handcrafted Diamond Wooden Blade
      const bladeGeo = createDiamondBladeGeometry(2.05, 0.28, 0.25, 0.42, 0.11);
      const bladeMesh = new THREE.Mesh(bladeGeo, bevelWoodMat);
      bladeMesh.position.y = 0.08;
      bladeMesh.name = 'Wood_Diamond_Blade';
      bladePivot.add(bladeMesh);

      // Central darker wood ridge / fuller plank
      const coreRidge = new THREE.Mesh(new THREE.BoxGeometry(0.08, 1.5, 0.118), oakMat);
      coreRidge.position.y = 0.85;
      coreRidge.name = 'Wood_Core_Grain';
      bladePivot.add(coreRidge);

      // Sub-level awakening emerald runes on the wood (preparing to evolve into Copper at Lv 5!)
      for (let i = 0; i < subLevel; i++) {
        const rune = new THREE.Mesh(new THREE.OctahedronGeometry(0.042, 0), leafMat);
        rune.position.set(0, 0.4 + i * 0.32, 0.065);
        const runeBack = rune.clone();
        runeBack.position.z = -0.065;
        bladePivot.add(rune, runeBack);
      }
      break;
    }

    case 'copper': {
      tipY = 2.48;
      const copperBladeMat = new THREE.MeshStandardMaterial({
        color: 0xe07a45,
        roughness: 0.26,
        metalness: 0.86,
        emissive: 0x9a3412,
        emissiveIntensity: 0.14 + subLevelGlowBoost * 0.5,
      });
      const darkBronzeMat = new THREE.MeshStandardMaterial({
        color: 0x7c3f23,
        roughness: 0.42,
        metalness: 0.8,
      });
      const patinaMat = new THREE.MeshStandardMaterial({
        color: 0x2dd4bf,
        emissive: 0x0d9488,
        emissiveIntensity: 0.45 + subLevelGlowBoost,
        roughness: 0.35,
        metalness: 0.5,
      });
      const leatherMat = new THREE.MeshStandardMaterial({
        color: 0x3b1f14,
        roughness: 0.75,
        metalness: 0.1,
      });

      // Leather-bound Grip with Copper Wire Rings
      const grip = new THREE.Mesh(new THREE.CylinderGeometry(0.065, 0.075, 0.62, 12), leatherMat);
      grip.position.y = -0.31;
      bladePivot.add(grip);

      for (let i = 0; i < 4; i++) {
        const ring = new THREE.Mesh(new THREE.TorusGeometry(0.074, 0.014, 8, 18), copperBladeMat);
        ring.rotation.x = Math.PI / 2;
        ring.position.y = -0.52 + i * 0.14;
        bladePivot.add(ring);
      }

      // Octagonal Copper Pommel with Verdigris Turquoise Core
      const pommel = new THREE.Mesh(new THREE.CylinderGeometry(0.13, 0.09, 0.16, 8), darkBronzeMat);
      pommel.position.y = -0.68;
      pommel.rotation.x = Math.PI / 2;
      bladePivot.add(pommel);

      const pommelGem = new THREE.Mesh(new THREE.OctahedronGeometry(0.075, 0), patinaMat);
      pommelGem.position.y = -0.68;
      pommelGem.scale.set(1, 1, 1.4);
      bladePivot.add(pommelGem);

      // Curved Horned Copper Crossguard + Riveted Center Block
      const guardBlock = new THREE.Mesh(new THREE.BoxGeometry(0.34, 0.18, 0.18), darkBronzeMat);
      guardBlock.position.y = 0.04;
      bladePivot.add(guardBlock);

      // Center Turquoise Gem in Crossguard
      const guardGem = new THREE.Mesh(new THREE.OctahedronGeometry(0.085, 0), patinaMat);
      guardGem.position.set(0, 0.04, 0.1);
      const guardGemBack = guardGem.clone();
      guardGemBack.position.z = -0.1;
      bladePivot.add(guardGem, guardGemBack);

      // Swept Copper Horns on Left & Right of Guard
      for (const side of [-1, 1]) {
        const horn1 = new THREE.Mesh(new THREE.ConeGeometry(0.085, 0.45, 8), copperBladeMat);
        horn1.position.set(side * 0.34, 0.09, 0);
        horn1.rotation.z = -side * 1.15;
        bladePivot.add(horn1);

        const rivet = new THREE.Mesh(new THREE.SphereGeometry(0.035, 8, 8), patinaMat);
        rivet.position.set(side * 0.22, 0.04, 0.095);
        bladePivot.add(rivet);
      }

      // Ricasso Copper Collar with Verdigris Inlay
      const ricasso = new THREE.Mesh(new THREE.BoxGeometry(0.32, 0.28, 0.13), darkBronzeMat);
      ricasso.position.y = 0.22;
      bladePivot.add(ricasso);

      // Forged Copper Diamond Blade
      const bladeGeo = createDiamondBladeGeometry(2.32, 0.33, 0.29, 0.48, 0.115);
      const bladeMesh = new THREE.Mesh(bladeGeo, copperBladeMat);
      bladeMesh.position.y = 0.12;
      bladeMesh.name = 'Copper_Forged_Blade';
      bladePivot.add(bladeMesh);

      // Central Fuller Groove (Bronze + Patina energy vein)
      const fuller = new THREE.Mesh(new THREE.BoxGeometry(0.065, 1.65, 0.122), darkBronzeMat);
      fuller.position.y = 1.02;
      bladePivot.add(fuller);

      const energyVein = new THREE.Mesh(new THREE.BoxGeometry(0.025, 1.45, 0.128), patinaMat);
      energyVein.position.y = 0.98;
      bladePivot.add(energyVein);
      break;
    }

    case 'iron': {
      tipY = 2.75;
      const steelMat = new THREE.MeshStandardMaterial({
        color: 0xcbd5e1,
        roughness: 0.2,
        metalness: 0.92,
      });
      const darkIronMat = new THREE.MeshStandardMaterial({
        color: 0x334155,
        roughness: 0.38,
        metalness: 0.85,
      });
      const crimsonGripMat = new THREE.MeshStandardMaterial({
        color: 0x7f1d1d,
        roughness: 0.65,
        metalness: 0.15,
      });
      const bloodGemMat = new THREE.MeshStandardMaterial({
        color: 0xef4444,
        emissive: 0xdc2626,
        emissiveIntensity: 0.55 + subLevelGlowBoost,
        roughness: 0.2,
      });

      // Two-handed Greatsword Grip
      const grip = new THREE.Mesh(new THREE.CylinderGeometry(0.068, 0.078, 0.74, 12), crimsonGripMat);
      grip.position.y = -0.37;
      bladePivot.add(grip);

      const gripWaistRing = new THREE.Mesh(new THREE.TorusGeometry(0.082, 0.018, 8, 16), darkIronMat);
      gripWaistRing.rotation.x = Math.PI / 2;
      gripWaistRing.position.y = -0.37;
      bladePivot.add(gripWaistRing);

      // Heavy Wolf-Crest Iron Pommel
      const pommel = new THREE.Mesh(new THREE.OctahedronGeometry(0.145, 1), darkIronMat);
      pommel.position.y = -0.8;
      bladePivot.add(pommel);

      const pommelSpike = new THREE.Mesh(new THREE.ConeGeometry(0.07, 0.16, 6), steelMat);
      pommelSpike.position.y = -0.94;
      pommelSpike.rotation.x = Math.PI;
      bladePivot.add(pommelSpike);

      // Crusader Flanged Crossguard
      const guardBar = new THREE.Mesh(new THREE.BoxGeometry(0.96, 0.12, 0.16), darkIronMat);
      guardBar.position.y = 0.03;
      bladePivot.add(guardBar);

      for (const side of [-1, 1]) {
        const flange = new THREE.Mesh(new THREE.OctahedronGeometry(0.13, 0), steelMat);
        flange.position.set(side * 0.52, 0.03, 0);
        flange.scale.set(1.3, 0.8, 0.7);
        bladePivot.add(flange);
      }

      // Guard Center Shield & Blood Ruby
      const shieldCrest = new THREE.Mesh(new THREE.CylinderGeometry(0.14, 0.08, 0.24, 6), darkIronMat);
      shieldCrest.position.y = 0.05;
      bladePivot.add(shieldCrest);

      const ruby = new THREE.Mesh(new THREE.OctahedronGeometry(0.09, 0), bloodGemMat);
      ruby.position.set(0, 0.05, 0.13);
      const rubyBack = ruby.clone();
      rubyBack.position.z = -0.13;
      bladePivot.add(ruby, rubyBack);

      // Tempered Broad Diamond Blade + Ricasso Lugs
      const bladeGeo = createDiamondBladeGeometry(2.58, 0.37, 0.33, 0.52, 0.125);
      const bladeMesh = new THREE.Mesh(bladeGeo, steelMat);
      bladeMesh.position.y = 0.1;
      bladePivot.add(bladeMesh);

      // Flamberge Parrying Hooks above Ricasso
      for (const side of [-1, 1]) {
        const hook = new THREE.Mesh(new THREE.ConeGeometry(0.06, 0.24, 5), darkIronMat);
        hook.position.set(side * 0.24, 0.45, 0);
        hook.rotation.z = -side * 0.9;
        bladePivot.add(hook);
      }

      const darkFuller = new THREE.Mesh(new THREE.BoxGeometry(0.09, 1.9, 0.132), darkIronMat);
      darkFuller.position.y = 1.12;
      bladePivot.add(darkFuller);
      break;
    }

    case 'silver': {
      tipY = 2.95;
      const silverMat = new THREE.MeshStandardMaterial({
        color: 0xf1f5f9,
        roughness: 0.14,
        metalness: 0.96,
        emissive: 0x1e40af,
        emissiveIntensity: 0.15,
      });
      const royalBlueMat = new THREE.MeshStandardMaterial({
        color: 0x1e3a8a,
        roughness: 0.3,
        metalness: 0.75,
      });
      const runeCyanMat = new THREE.MeshStandardMaterial({
        color: 0x38bdf8,
        emissive: 0x00f2fe,
        emissiveIntensity: 0.95 + subLevelGlowBoost,
        roughness: 0.1,
      });

      // Grip
      const grip = new THREE.Mesh(new THREE.CylinderGeometry(0.062, 0.072, 0.76, 14), royalBlueMat);
      grip.position.y = -0.38;
      bladePivot.add(grip);

      // Crescent Moon Pommel
      const moonOuter = new THREE.Mesh(new THREE.TorusGeometry(0.13, 0.036, 10, 24, Math.PI * 1.35), silverMat);
      moonOuter.position.y = -0.84;
      moonOuter.rotation.z = Math.PI * 0.82;
      bladePivot.add(moonOuter);

      const moonCore = new THREE.Mesh(new THREE.OctahedronGeometry(0.075, 0), runeCyanMat);
      moonCore.position.y = -0.84;
      bladePivot.add(moonCore);

      // Valkyrie Winged Crossguard using custom sculpted wing geometry
      const wingGeo = createSculptedWingBladeGeometry(0.62, 0.38, 0.065);
      const wingR = new THREE.Mesh(wingGeo, silverMat);
      wingR.position.set(0.08, -0.02, 0);
      bladePivot.add(wingR);

      const wingL = new THREE.Mesh(wingGeo, silverMat);
      wingL.scale.x = -1;
      wingL.position.set(-0.08, -0.02, 0);
      bladePivot.add(wingL);

      const guardHub = new THREE.Mesh(new THREE.OctahedronGeometry(0.16, 1), royalBlueMat);
      guardHub.position.y = 0.06;
      guardHub.scale.set(1.2, 1.0, 0.8);
      bladePivot.add(guardHub);

      const hubSapphire = new THREE.Mesh(new THREE.OctahedronGeometry(0.095, 0), runeCyanMat);
      hubSapphire.position.set(0, 0.06, 0.12);
      const hubSapphireBack = hubSapphire.clone();
      hubSapphireBack.position.z = -0.12;
      bladePivot.add(hubSapphire, hubSapphireBack);

      // Moon-Silver Blade
      const bladeGeo = createDiamondBladeGeometry(2.75, 0.36, 0.31, 0.58, 0.12);
      const bladeMesh = new THREE.Mesh(bladeGeo, silverMat);
      bladeMesh.position.y = 0.12;
      bladePivot.add(bladeMesh);

      // 7 Glowing Nordic Runes inlaid along the blade
      for (let i = 0; i < 7; i++) {
        const rune = new THREE.Mesh(new THREE.OctahedronGeometry(0.048, 0), runeCyanMat);
        rune.position.set(0, 0.38 + i * 0.28, 0.062);
        rune.scale.set(0.8, 1.4, 0.5);
        const runeB = rune.clone();
        runeB.position.z = -0.062;
        bladePivot.add(rune, runeB);
      }
      break;
    }

    case 'gold': {
      tipY = 3.15;
      const goldMat = new THREE.MeshStandardMaterial({
        color: 0xfacc15,
        roughness: 0.16,
        metalness: 0.94,
        emissive: 0xd97706,
        emissiveIntensity: 0.22 + subLevelGlowBoost * 0.4,
      });
      const bronzeGoldMat = new THREE.MeshStandardMaterial({
        color: 0xb45309,
        roughness: 0.28,
        metalness: 0.88,
      });
      const solarGemMat = new THREE.MeshStandardMaterial({
        color: 0xf43f5e,
        emissive: 0xff2a00,
        emissiveIntensity: 0.95 + subLevelGlowBoost,
        roughness: 0.12,
      });
      const sunHaloMat = new THREE.MeshStandardMaterial({
        color: 0xfef08a,
        emissive: 0xf59e0b,
        emissiveIntensity: 1.1,
        roughness: 0.1,
      });

      // Imperial Grip
      const grip = new THREE.Mesh(new THREE.CylinderGeometry(0.068, 0.082, 0.8, 12), bronzeGoldMat);
      grip.position.y = -0.4;
      bladePivot.add(grip);

      // Sunburst Pommel
      const pommelSun = new THREE.Mesh(new THREE.DodecahedronGeometry(0.15, 1), goldMat);
      pommelSun.position.y = -0.86;
      bladePivot.add(pommelSun);

      // Phoenix Feather Guard + Solar Halo Ring
      const sunHalo = new THREE.Mesh(new THREE.TorusGeometry(0.32, 0.026, 12, 32), sunHaloMat);
      sunHalo.position.y = 0.12;
      orbitGroup.add(sunHalo);

      for (const side of [-1, 1]) {
        for (let f = 0; f < 3; f++) {
          const featherGeo = createSculptedWingBladeGeometry(0.55 - f * 0.08, 0.26, 0.05);
          const feather = new THREE.Mesh(featherGeo, f % 2 === 0 ? goldMat : sunHaloMat);
          feather.scale.x = side;
          feather.position.set(side * 0.1, 0.02 + f * 0.08, 0);
          feather.rotation.z = side * (0.25 - f * 0.22);
          bladePivot.add(feather);
        }
      }

      const sunCore = new THREE.Mesh(new THREE.SphereGeometry(0.12, 16, 16), solarGemMat);
      sunCore.position.y = 0.08;
      bladePivot.add(sunCore);

      // Royal Gold Blade with Serrated Solar Ricasso
      const bladeGeo = createDiamondBladeGeometry(2.92, 0.42, 0.36, 0.62, 0.13);
      const bladeMesh = new THREE.Mesh(bladeGeo, goldMat);
      bladeMesh.position.y = 0.14;
      bladePivot.add(bladeMesh);

      const solarFlameCore = new THREE.Mesh(new THREE.BoxGeometry(0.08, 2.2, 0.14), sunHaloMat);
      solarFlameCore.position.y = 1.3;
      bladePivot.add(solarFlameCore);
      break;
    }

    case 'crystal': {
      tipY = 3.35;
      const crystalMat = new THREE.MeshStandardMaterial({
        color: 0xd8b4fe,
        emissive: 0x9333ea,
        emissiveIntensity: 0.48 + subLevelGlowBoost * 0.5,
        roughness: 0.08,
        metalness: 0.35,
        transparent: true,
        opacity: 0.92,
      });
      const arcaneCoreMat = new THREE.MeshStandardMaterial({
        color: 0xf5d0fe,
        emissive: 0xe879f9,
        emissiveIntensity: 1.15,
        roughness: 0.05,
      });
      const platinumMat = new THREE.MeshStandardMaterial({
        color: 0xe2e8f0,
        roughness: 0.18,
        metalness: 0.92,
      });

      const grip = new THREE.Mesh(new THREE.CylinderGeometry(0.06, 0.07, 0.78, 8), platinumMat);
      grip.position.y = -0.39;
      bladePivot.add(grip);

      // Levitating Mana Crystal Pommel
      const pommelPrism = new THREE.Mesh(new THREE.OctahedronGeometry(0.15, 0), arcaneCoreMat);
      pommelPrism.position.y = -0.9;
      pommelPrism.scale.set(0.8, 1.4, 0.8);
      orbitGroup.add(pommelPrism);

      // Arcane Crystal Guard
      for (const side of [-1, 1]) {
        const crystalHorn = new THREE.Mesh(new THREE.OctahedronGeometry(0.18, 0), crystalMat);
        crystalHorn.position.set(side * 0.36, 0.08, 0);
        crystalHorn.scale.set(2.1, 0.65, 0.65);
        crystalHorn.rotation.z = side * 0.35;
        bladePivot.add(crystalHorn);
      }

      const centerPrism = new THREE.Mesh(new THREE.OctahedronGeometry(0.15, 0), arcaneCoreMat);
      centerPrism.position.y = 0.08;
      bladePivot.add(centerPrism);

      // Arcane Filigree Halo Rings around Crystal Guard
      const arcaneRing1 = new THREE.Mesh(new THREE.TorusGeometry(0.28, 0.02, 12, 32), platinumMat);
      arcaneRing1.position.y = 0.12;
      orbitGroup.add(arcaneRing1);

      const arcaneRing2 = new THREE.Mesh(new THREE.TorusGeometry(0.22, 0.018, 12, 28), arcaneCoreMat);
      arcaneRing2.position.y = 0.12;
      arcaneRing2.rotation.x = Math.PI / 3;
      orbitGroup.add(arcaneRing2);

      // Main Prism Blade + Inner Mana Spine
      const bladeGeo = createDiamondBladeGeometry(3.1, 0.44, 0.38, 0.7, 0.145);
      const bladeMesh = new THREE.Mesh(bladeGeo, crystalMat);
      bladeMesh.position.y = 0.15;
      bladePivot.add(bladeMesh);

      const manaSpineGeo = createDiamondBladeGeometry(2.85, 0.18, 0.14, 0.5, 0.16);
      const manaSpine = new THREE.Mesh(manaSpineGeo, arcaneCoreMat);
      manaSpine.position.y = 0.2;
      bladePivot.add(manaSpine);

      // 8 Floating Orbiting Crystal Shards alongside the blade!
      for (let i = 0; i < 8; i++) {
        const side = i % 2 === 0 ? 1 : -1;
        const row = Math.floor(i / 2);
        const shard = new THREE.Mesh(new THREE.OctahedronGeometry(0.095, 1), arcaneCoreMat);
        shard.scale.set(0.55, 2.2, 0.55);
        shard.position.set(side * 0.36, 0.55 + row * 0.55, 0);
        shard.rotation.z = -side * 0.15;
        shard.name = `FloatingShard_${i}`;
        orbitGroup.add(shard);
      }
      break;
    }

    case 'obsidian': {
      tipY = 3.55;
      const obsidianMat = new THREE.MeshStandardMaterial({
        color: 0x18181b,
        roughness: 0.22,
        metalness: 0.88,
      });
      const magmaMat = new THREE.MeshStandardMaterial({
        color: 0xff4500,
        emissive: 0xff2200,
        emissiveIntensity: 1.2 + subLevelGlowBoost,
        roughness: 0.15,
      });
      const boneHornMat = new THREE.MeshStandardMaterial({
        color: 0xd6d3d1,
        roughness: 0.55,
        metalness: 0.2,
      });

      const grip = new THREE.Mesh(new THREE.CylinderGeometry(0.072, 0.086, 0.84, 10), obsidianMat);
      grip.position.y = -0.42;
      bladePivot.add(grip);

      // Demon-Heart Pommel
      const heartPommel = new THREE.Mesh(new THREE.DodecahedronGeometry(0.16, 0), magmaMat);
      heartPommel.position.y = -0.92;
      bladePivot.add(heartPommel);

      // Dragon Skull Crossguard with Horned Tusks & Glowing Eyes
      const skullBlock = new THREE.Mesh(new THREE.DodecahedronGeometry(0.22, 0), obsidianMat);
      skullBlock.position.y = 0.08;
      skullBlock.scale.set(1.3, 1.0, 1.1);
      bladePivot.add(skullBlock);

      for (const side of [-1, 1]) {
        const eye = new THREE.Mesh(new THREE.SphereGeometry(0.045, 8, 8), magmaMat);
        eye.position.set(side * 0.1, 0.12, 0.19);
        bladePivot.add(eye);

        const dragonHorn = new THREE.Mesh(new THREE.ConeGeometry(0.11, 0.68, 8), boneHornMat);
        dragonHorn.position.set(side * 0.44, 0.22, 0);
        dragonHorn.rotation.z = -side * 1.05;
        bladePivot.add(dragonHorn);
      }

      // Serrated Saw-Toothed Obsidian Blade + Molten Magma Core
      const serratedGeo = createSerratedBladeGeometry(3.25, 0.48, 0.15, 7);
      const bladeMesh = new THREE.Mesh(serratedGeo, obsidianMat);
      bladeMesh.position.y = 0.14;
      bladePivot.add(bladeMesh);

      const magmaCoreGeo = createDiamondBladeGeometry(2.95, 0.22, 0.18, 0.45, 0.165);
      const magmaCoreMesh = new THREE.Mesh(magmaCoreGeo, magmaMat);
      magmaCoreMesh.position.y = 0.18;
      bladePivot.add(magmaCoreMesh);
      break;
    }

    case 'celestial': {
      tipY = 3.85;
      const astralBladeMat = new THREE.MeshStandardMaterial({
        color: 0x38bdf8,
        emissive: 0x0284c7,
        emissiveIntensity: 0.75,
        roughness: 0.08,
        metalness: 0.9,
      });
      const starGoldMat = new THREE.MeshStandardMaterial({
        color: 0xfef08a,
        emissive: 0xf59e0b,
        emissiveIntensity: 0.85,
        roughness: 0.12,
        metalness: 0.95,
      });
      const voidCoreMat = new THREE.MeshStandardMaterial({
        color: 0x090514,
        emissive: 0x7e22ce,
        emissiveIntensity: 0.5,
        roughness: 0.05,
      });
      const plasmaMat = new THREE.MeshStandardMaterial({
        color: 0x67e8f9,
        emissive: 0x22d3ee,
        emissiveIntensity: 1.4,
        roughness: 0.05,
      });

      const grip = new THREE.Mesh(new THREE.CylinderGeometry(0.068, 0.08, 0.88, 16), starGoldMat);
      grip.position.y = -0.44;
      bladePivot.add(grip);

      // Singularity Black Hole Core at Crossguard Center
      const blackHole = new THREE.Mesh(new THREE.SphereGeometry(0.16, 20, 20), voidCoreMat);
      blackHole.position.y = 0.14;
      bladePivot.add(blackHole);

      // Accretion Disk Rings around Singularity
      const ring1 = new THREE.Mesh(new THREE.TorusGeometry(0.32, 0.022, 12, 36), plasmaMat);
      ring1.position.y = 0.14;
      ring1.rotation.x = 0.8;
      orbitGroup.add(ring1);

      const ring2 = new THREE.Mesh(new THREE.TorusGeometry(0.42, 0.018, 12, 36), starGoldMat);
      ring2.position.y = 0.14;
      ring2.rotation.y = 0.8;
      orbitGroup.add(ring2);

      // 4 Seraphim Cosmic Wings around the Hilt
      for (const side of [-1, 1]) {
        const upperWingGeo = createSculptedWingBladeGeometry(0.85, 0.52, 0.055);
        const upperWing = new THREE.Mesh(upperWingGeo, starGoldMat);
        upperWing.scale.x = side;
        upperWing.position.set(side * 0.16, 0.12, 0);
        upperWing.rotation.z = side * 0.25;
        bladePivot.add(upperWing);

        const lowerWingGeo = createSculptedWingBladeGeometry(0.65, 0.38, 0.045);
        const lowerWing = new THREE.Mesh(lowerWingGeo, plasmaMat);
        lowerWing.scale.x = side;
        lowerWing.position.set(side * 0.14, -0.08, 0);
        lowerWing.rotation.z = -side * 0.35;
        bladePivot.add(lowerWing);
      }

      // Twin-Split Cosmic Blade (Left & Right Astral Prongs + Central Plasma Beam)
      for (const side of [-1, 1]) {
        const prongGeo = createDiamondBladeGeometry(3.45, 0.22, 0.19, 0.65, 0.12);
        const prong = new THREE.Mesh(prongGeo, astralBladeMat);
        prong.position.set(side * 0.13, 0.22, 0);
        prong.rotation.z = -side * 0.018;
        bladePivot.add(prong);
      }

      const centralBeamGeo = createDiamondBladeGeometry(3.65, 0.16, 0.14, 0.55, 0.15);
      const centralBeam = new THREE.Mesh(centralBeamGeo, plasmaMat);
      centralBeam.position.y = 0.22;
      bladePivot.add(centralBeam);

      // Orbiting Starlight Satellites
      for (let s = 0; s < 4; s++) {
        const star = new THREE.Mesh(new THREE.OctahedronGeometry(0.085, 0), starGoldMat);
        const angle = (s / 4) * Math.PI * 2;
        star.position.set(Math.cos(angle) * 0.48, 1.4 + (s % 2) * 0.7, Math.sin(angle) * 0.48);
        orbitGroup.add(star);
      }
      break;
    }
  }

  // Enable castShadow on all sword meshes
  root.traverse((obj) => {
    if (obj instanceof THREE.Mesh) {
      obj.castShadow = true;
      obj.receiveShadow = true;
    }
  });

  const updateAnimation = (time: number) => {
    orbitGroup.children.forEach((child, idx) => {
      if (child.name.startsWith('FloatingShard_')) {
        child.position.y += Math.sin(time * 3.5 + idx) * 0.0018;
        child.rotation.y = time * 2.2 + idx;
      } else {
        child.rotation.z = time * (idx % 2 === 0 ? 1.8 : -1.4);
      }
    });
  };

  return {
    group: root,
    bladePivot,
    orbitGroup,
    tipPositionLocal: new THREE.Vector3(0, tipY, 0),
    updateAnimation,
  };
}
