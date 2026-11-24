import * as THREE from 'three';
import { MonsterSpeciesId } from '../types/game';
import { createDiamondBladeGeometry, createSculptedWingBladeGeometry } from './customGeometry';

export interface ArticulatedMonsterModel {
  group: THREE.Group;
  body: THREE.Group;
  head: THREE.Group;
  leftArm: THREE.Group;
  rightArm: THREE.Group;
  leftLeg: THREE.Group;
  rightLeg: THREE.Group;
  leftWing?: THREE.Group;
  rightWing?: THREE.Group;
  tail?: THREE.Group;
  hitMaterials: THREE.MeshStandardMaterial[];
  animate: (time: number, isMoving: boolean, attackPhase: number) => void;
  setHitFlash: (active: boolean) => void;
}

export function buildMonster3DModel(species: MonsterSpeciesId): ArticulatedMonsterModel {
  const group = new THREE.Group();
  group.name = `Monster_${species}`;

  const body = new THREE.Group();
  const head = new THREE.Group();
  const leftArm = new THREE.Group();
  const rightArm = new THREE.Group();
  const leftLeg = new THREE.Group();
  const rightLeg = new THREE.Group();
  let leftWing: THREE.Group | undefined;
  let rightWing: THREE.Group | undefined;
  let tail: THREE.Group | undefined;

  group.add(body);
  body.add(head, leftArm, rightArm, leftLeg, rightLeg);

  const hitMaterials: THREE.MeshStandardMaterial[] = [];
  const registerMat = (mat: THREE.MeshStandardMaterial) => {
    mat.userData.origEmissive = mat.emissive.getHex();
    mat.userData.origIntensity = mat.emissiveIntensity;
    hitMaterials.push(mat);
    return mat;
  };

  const eyeWhiteMat = new THREE.MeshStandardMaterial({ color: 0xffffff, roughness: 0.2 });
  const eyeEvilMat = new THREE.MeshStandardMaterial({
    color: 0xff2a00,
    emissive: 0xff1100,
    emissiveIntensity: 0.9,
  });

  switch (species) {
    case 'slime': {
      const gelMat = registerMat(
        new THREE.MeshStandardMaterial({
          color: 0x22c55e,
          emissive: 0x15803d,
          emissiveIntensity: 0.2,
          roughness: 0.15,
          metalness: 0.1,
          transparent: true,
          opacity: 0.84,
        })
      );
      const coreMat = registerMat(
        new THREE.MeshStandardMaterial({
          color: 0x86efac,
          emissive: 0x4ade80,
          emissiveIntensity: 0.85,
          roughness: 0.2,
        })
      );
      const mossMat = registerMat(
        new THREE.MeshStandardMaterial({ color: 0x166534, roughness: 0.85 })
      );

      // Outer Gel Dome
      const outerGel = new THREE.Mesh(new THREE.SphereGeometry(0.85, 20, 16), gelMat);
      outerGel.scale.set(1.12, 0.88, 1.12);
      outerGel.position.y = 0.72;
      body.add(outerGel);

      // Base puddle skirt
      const skirt = new THREE.Mesh(new THREE.CylinderGeometry(0.82, 1.02, 0.28, 16), gelMat);
      skirt.position.y = 0.16;
      body.add(skirt);

      // Floating Inner Crystal Core
      const innerCore = new THREE.Mesh(new THREE.OctahedronGeometry(0.34, 0), coreMat);
      innerCore.position.y = 0.72;
      head.add(innerCore);

      // Bubbles inside slime
      for (let b = 0; b < 5; b++) {
        const bubble = new THREE.Mesh(new THREE.SphereGeometry(0.09 + (b % 2) * 0.04, 8, 8), coreMat);
        const ang = (b / 5) * Math.PI * 2;
        bubble.position.set(Math.cos(ang) * 0.42, 0.55 + (b % 3) * 0.18, Math.sin(ang) * 0.42);
        body.add(bubble);
      }

      // Expressive Angry Eyes & Brows on Front (+Z)
      for (const side of [-1, 1]) {
        const eye = new THREE.Mesh(new THREE.SphereGeometry(0.13, 12, 12), eyeWhiteMat);
        eye.position.set(side * 0.28, 0.82, 0.76);
        body.add(eye);

        const pupil = new THREE.Mesh(new THREE.SphereGeometry(0.07, 8, 8), eyeEvilMat);
        pupil.position.set(side * 0.28, 0.82, 0.86);
        body.add(pupil);

        const brow = new THREE.Mesh(new THREE.BoxGeometry(0.24, 0.06, 0.08), mossMat);
        brow.position.set(side * 0.28, 0.96, 0.82);
        brow.rotation.z = -side * 0.35;
        body.add(brow);
      }

      // Leaf Crown on top
      const crownLeaf = new THREE.Mesh(new THREE.ConeGeometry(0.28, 0.36, 6), mossMat);
      crownLeaf.position.y = 1.48;
      body.add(crownLeaf);
      break;
    }

    case 'goblin': {
      const skinMat = registerMat(
        new THREE.MeshStandardMaterial({ color: 0x65a30d, roughness: 0.65 })
      );
      const leatherMat = registerMat(
        new THREE.MeshStandardMaterial({ color: 0x78350f, roughness: 0.8 })
      );
      const ironMat = registerMat(
        new THREE.MeshStandardMaterial({ color: 0x52525b, roughness: 0.4, metalness: 0.8 })
      );

      // Torso + Leather Harness
      const torso = new THREE.Mesh(new THREE.BoxGeometry(0.72, 0.82, 0.46), skinMat);
      torso.position.y = 1.15;
      body.add(torso);

      const belt = new THREE.Mesh(new THREE.BoxGeometry(0.78, 0.26, 0.52), leatherMat);
      belt.position.y = 0.82;
      body.add(belt);

      // Head + Pointed Goblin Ears + Nose + Fangs
      head.position.set(0, 1.65, 0);
      const skull = new THREE.Mesh(new THREE.BoxGeometry(0.58, 0.54, 0.56), skinMat);
      skull.position.y = 0.25;
      head.add(skull);

      const nose = new THREE.Mesh(new THREE.ConeGeometry(0.1, 0.28, 6), skinMat);
      nose.rotation.x = Math.PI / 2;
      nose.position.set(0, 0.22, 0.36);
      head.add(nose);

      for (const side of [-1, 1]) {
        const ear = new THREE.Mesh(new THREE.ConeGeometry(0.12, 0.52, 5), skinMat);
        ear.position.set(side * 0.48, 0.28, 0);
        ear.rotation.z = -side * 1.15;
        head.add(ear);

        const eye = new THREE.Mesh(new THREE.SphereGeometry(0.075, 8, 8), eyeEvilMat);
        eye.position.set(side * 0.15, 0.3, 0.28);
        head.add(eye);

        const fang = new THREE.Mesh(new THREE.ConeGeometry(0.035, 0.1, 5), eyeWhiteMat);
        fang.position.set(side * 0.12, 0.06, 0.29);
        head.add(fang);
      }

      // Left Arm + Wooden Buckler Shield
      leftArm.position.set(-0.5, 1.45, 0);
      const lArmMesh = new THREE.Mesh(new THREE.CylinderGeometry(0.11, 0.09, 0.65, 8), skinMat);
      lArmMesh.position.y = -0.28;
      leftArm.add(lArmMesh);

      const shield = new THREE.Mesh(new THREE.CylinderGeometry(0.42, 0.42, 0.08, 12), leatherMat);
      shield.rotation.z = Math.PI / 2;
      shield.position.set(-0.18, -0.45, 0.15);
      leftArm.add(shield);

      const shieldBoss = new THREE.Mesh(new THREE.SphereGeometry(0.12, 8, 8), ironMat);
      shieldBoss.position.set(-0.23, -0.45, 0.15);
      leftArm.add(shieldBoss);

      // Right Arm + Spiked War Club
      rightArm.position.set(0.5, 1.45, 0);
      const rArmMesh = new THREE.Mesh(new THREE.CylinderGeometry(0.11, 0.09, 0.65, 8), skinMat);
      rArmMesh.position.y = -0.28;
      rightArm.add(rArmMesh);

      const club = new THREE.Mesh(new THREE.CylinderGeometry(0.16, 0.06, 0.95, 8), leatherMat);
      club.rotation.x = Math.PI / 2;
      club.position.set(0, -0.55, 0.42);
      rightArm.add(club);

      for (let s = 0; s < 4; s++) {
        const spike = new THREE.Mesh(new THREE.ConeGeometry(0.05, 0.18, 5), ironMat);
        spike.position.set(0, -0.42, 0.68 + (s % 2) * 0.12);
        spike.rotation.z = (s * Math.PI) / 2;
        rightArm.add(spike);
      }

      // Legs
      leftLeg.position.set(-0.22, 0.72, 0);
      const lLegMesh = new THREE.Mesh(new THREE.CylinderGeometry(0.13, 0.1, 0.72, 8), skinMat);
      lLegMesh.position.y = -0.36;
      leftLeg.add(lLegMesh);

      rightLeg.position.set(0.22, 0.72, 0);
      const rLegMesh = lLegMesh.clone();
      rightLeg.add(rLegMesh);
      break;
    }

    case 'skeleton': {
      const boneMat = registerMat(
        new THREE.MeshStandardMaterial({ color: 0xe2e8f0, roughness: 0.45, metalness: 0.1 })
      );
      const darkSteelMat = registerMat(
        new THREE.MeshStandardMaterial({ color: 0x334155, roughness: 0.35, metalness: 0.85 })
      );
      const soulCyanMat = new THREE.MeshStandardMaterial({
        color: 0x38bdf8,
        emissive: 0x00f2fe,
        emissiveIntensity: 1.2,
      });

      // Spine & Ribcage
      const spine = new THREE.Mesh(new THREE.CylinderGeometry(0.09, 0.09, 0.95, 8), boneMat);
      spine.position.y = 1.25;
      body.add(spine);

      for (let r = 0; r < 4; r++) {
        const rib = new THREE.Mesh(new THREE.TorusGeometry(0.32 - r * 0.02, 0.045, 6, 14), boneMat);
        rib.rotation.x = Math.PI / 2;
        rib.position.y = 1.55 - r * 0.14;
        body.add(rib);
      }

      const pelvis = new THREE.Mesh(new THREE.CylinderGeometry(0.32, 0.24, 0.22, 8), boneMat);
      pelvis.position.y = 0.82;
      body.add(pelvis);

      // Skull + Horned Iron Helmet + Glowing Cyan Eyes
      head.position.set(0, 1.78, 0);
      const cranium = new THREE.Mesh(new THREE.SphereGeometry(0.32, 12, 12), boneMat);
      cranium.position.y = 0.28;
      head.add(cranium);

      const jaw = new THREE.Mesh(new THREE.BoxGeometry(0.34, 0.18, 0.34), boneMat);
      jaw.position.set(0, 0.08, 0.08);
      head.add(jaw);

      const helm = new THREE.Mesh(new THREE.ConeGeometry(0.36, 0.35, 8), darkSteelMat);
      helm.position.y = 0.48;
      head.add(helm);

      for (const side of [-1, 1]) {
        const eye = new THREE.Mesh(new THREE.SphereGeometry(0.075, 8, 8), soulCyanMat);
        eye.position.set(side * 0.12, 0.26, 0.27);
        head.add(eye);

        const horn = new THREE.Mesh(new THREE.ConeGeometry(0.07, 0.42, 6), boneMat);
        horn.position.set(side * 0.36, 0.52, 0);
        horn.rotation.z = -side * 0.85;
        head.add(horn);
      }

      // Left Arm + Kite Shield
      leftArm.position.set(-0.48, 1.62, 0);
      const lBone = new THREE.Mesh(new THREE.CylinderGeometry(0.07, 0.06, 0.75, 6), boneMat);
      lBone.position.y = -0.35;
      leftArm.add(lBone);

      const kiteShield = new THREE.Mesh(new THREE.BoxGeometry(0.1, 0.85, 0.58), darkSteelMat);
      kiteShield.position.set(-0.16, -0.45, 0.18);
      leftArm.add(kiteShield);

      // Right Arm + Ancient Broadsword
      rightArm.position.set(0.48, 1.62, 0);
      const rBone = lBone.clone();
      rightArm.add(rBone);

      const skelBladeGeo = createDiamondBladeGeometry(1.25, 0.22, 0.18, 0.3, 0.08);
      const skelSword = new THREE.Mesh(skelBladeGeo, darkSteelMat);
      skelSword.rotation.x = Math.PI / 2;
      skelSword.position.set(0, -0.65, 0.15);
      rightArm.add(skelSword);

      // Bone Legs
      leftLeg.position.set(-0.2, 0.75, 0);
      const legBone = new THREE.Mesh(new THREE.CylinderGeometry(0.08, 0.07, 0.78, 6), boneMat);
      legBone.position.y = -0.38;
      leftLeg.add(legBone);

      rightLeg.position.set(0.2, 0.75, 0);
      rightLeg.add(legBone.clone());
      break;
    }

    case 'copper_golem': {
      const rockMat = registerMat(
        new THREE.MeshStandardMaterial({ color: 0x57534e, roughness: 0.88, metalness: 0.15 })
      );
      const copperOreMat = registerMat(
        new THREE.MeshStandardMaterial({
          color: 0xea580c,
          emissive: 0xc2410c,
          emissiveIntensity: 0.65,
          roughness: 0.25,
          metalness: 0.85,
        })
      );

      // Massive Boulder Chest + Glowing Copper Core
      const chest = new THREE.Mesh(new THREE.DodecahedronGeometry(0.82, 0), rockMat);
      chest.position.y = 1.55;
      chest.scale.set(1.25, 1.05, 0.9);
      body.add(chest);

      const coreFurnace = new THREE.Mesh(new THREE.OctahedronGeometry(0.35, 0), copperOreMat);
      coreFurnace.position.set(0, 1.55, 0.62);
      body.add(coreFurnace);

      // Copper Ore Crystals jutting from shoulders
      for (const side of [-1, 1]) {
        const crystal = new THREE.Mesh(new THREE.OctahedronGeometry(0.26, 0), copperOreMat);
        crystal.position.set(side * 0.75, 2.15, 0);
        crystal.scale.set(0.7, 1.7, 0.7);
        crystal.rotation.z = -side * 0.4;
        body.add(crystal);
      }

      // Monolith Head + Cyclops Visor
      head.position.set(0, 2.25, 0);
      const headStone = new THREE.Mesh(new THREE.BoxGeometry(0.62, 0.56, 0.58), rockMat);
      headStone.position.y = 0.22;
      head.add(headStone);

      const visor = new THREE.Mesh(new THREE.BoxGeometry(0.44, 0.14, 0.12), copperOreMat);
      visor.position.set(0, 0.24, 0.28);
      head.add(visor);

      // Giant Articulated Boulder Gauntlets
      leftArm.position.set(-1.05, 1.9, 0);
      const armBoulder = new THREE.Mesh(new THREE.DodecahedronGeometry(0.44, 0), rockMat);
      armBoulder.position.y = -0.58;
      armBoulder.scale.set(0.85, 1.55, 0.85);
      leftArm.add(armBoulder);

      const cuff = new THREE.Mesh(new THREE.TorusGeometry(0.34, 0.07, 8, 14), copperOreMat);
      cuff.rotation.x = Math.PI / 2;
      cuff.position.y = -0.85;
      leftArm.add(cuff);

      rightArm.position.set(1.05, 1.9, 0);
      rightArm.add(armBoulder.clone(), cuff.clone());

      // Heavy Pillar Legs
      leftLeg.position.set(-0.42, 0.88, 0);
      const legPillar = new THREE.Mesh(new THREE.CylinderGeometry(0.3, 0.36, 0.88, 7), rockMat);
      legPillar.position.y = -0.44;
      leftLeg.add(legPillar);

      rightLeg.position.set(0.42, 0.88, 0);
      rightLeg.add(legPillar.clone());
      break;
    }

    case 'orc_berserker': {
      const orcSkinMat = registerMat(
        new THREE.MeshStandardMaterial({ color: 0x15803d, roughness: 0.6 })
      );
      const armorMat = registerMat(
        new THREE.MeshStandardMaterial({ color: 0x27272a, roughness: 0.35, metalness: 0.82 })
      );
      const crimsonSteelMat = registerMat(
        new THREE.MeshStandardMaterial({
          color: 0xdc2626,
          emissive: 0x7f1d1d,
          emissiveIntensity: 0.35,
          roughness: 0.25,
          metalness: 0.85,
        })
      );

      // Muscular Torso + Spiked Pauldrons
      const torso = new THREE.Mesh(new THREE.BoxGeometry(1.05, 1.05, 0.65), orcSkinMat);
      torso.position.y = 1.45;
      body.add(torso);

      const chestHarnesses = new THREE.Mesh(new THREE.BoxGeometry(1.1, 0.55, 0.7), armorMat);
      chestHarnesses.position.y = 1.42;
      body.add(chestHarnesses);

      for (const side of [-1, 1]) {
        const pauldron = new THREE.Mesh(new THREE.SphereGeometry(0.36, 10, 10), armorMat);
        pauldron.position.set(side * 0.72, 1.88, 0);
        body.add(pauldron);

        const spike = new THREE.Mesh(new THREE.ConeGeometry(0.1, 0.36, 6), crimsonSteelMat);
        spike.position.set(side * 0.9, 2.15, 0);
        spike.rotation.z = -side * 0.5;
        body.add(spike);
      }

      // Orc Head + Tusks + Horned War-Helm
      head.position.set(0, 2.02, 0);
      const orcHead = new THREE.Mesh(new THREE.BoxGeometry(0.64, 0.62, 0.64), orcSkinMat);
      orcHead.position.y = 0.28;
      head.add(orcHead);

      for (const side of [-1, 1]) {
        const tusk = new THREE.Mesh(new THREE.ConeGeometry(0.06, 0.26, 6), eyeWhiteMat);
        tusk.position.set(side * 0.18, 0.16, 0.36);
        tusk.rotation.x = 0.35;
        head.add(tusk);

        const eye = new THREE.Mesh(new THREE.SphereGeometry(0.08, 8, 8), eyeEvilMat);
        eye.position.set(side * 0.16, 0.34, 0.33);
        head.add(eye);
      }

      // Dual Battle Axes in Left & Right Hands!
      const buildBattleAxe = () => {
        const axeGroup = new THREE.Group();
        const shaft = new THREE.Mesh(new THREE.CylinderGeometry(0.05, 0.05, 1.25, 8), armorMat);
        shaft.rotation.x = Math.PI / 2;
        shaft.position.set(0, -0.65, 0.35);
        axeGroup.add(shaft);

        const blade = new THREE.Mesh(new THREE.CylinderGeometry(0.38, 0.38, 0.08, 12, 1, false, 0, Math.PI), crimsonSteelMat);
        blade.rotation.z = Math.PI / 2;
        blade.position.set(0, -0.65, 0.82);
        axeGroup.add(blade);
        return axeGroup;
      };

      leftArm.position.set(-0.75, 1.75, 0);
      const armMesh = new THREE.Mesh(new THREE.CylinderGeometry(0.18, 0.15, 0.78, 8), orcSkinMat);
      armMesh.position.y = -0.35;
      leftArm.add(armMesh, buildBattleAxe());

      rightArm.position.set(0.75, 1.75, 0);
      rightArm.add(armMesh.clone(), buildBattleAxe());

      leftLeg.position.set(-0.3, 0.85, 0);
      const legMesh = new THREE.Mesh(new THREE.CylinderGeometry(0.2, 0.16, 0.85, 8), armorMat);
      legMesh.position.y = -0.42;
      leftLeg.add(legMesh);

      rightLeg.position.set(0.3, 0.85, 0);
      rightLeg.add(legMesh.clone());
      break;
    }

    case 'crimson_drake': {
      const scaleMat = registerMat(
        new THREE.MeshStandardMaterial({ color: 0xb91c1c, roughness: 0.4, metalness: 0.3 })
      );
      const bellyMat = registerMat(
        new THREE.MeshStandardMaterial({
          color: 0xf59e0b,
          emissive: 0xd97706,
          emissiveIntensity: 0.3,
          roughness: 0.45,
        })
      );
      const hornMat = registerMat(
        new THREE.MeshStandardMaterial({ color: 0x1c1917, roughness: 0.3, metalness: 0.5 })
      );

      // Hovering Dragon Body
      const torso = new THREE.Mesh(new THREE.ConeGeometry(0.68, 1.55, 8), scaleMat);
      torso.rotation.x = Math.PI * 0.35;
      torso.position.set(0, 1.85, 0);
      body.add(torso);

      const chestPlate = new THREE.Mesh(new THREE.BoxGeometry(0.65, 0.85, 0.45), bellyMat);
      chestPlate.position.set(0, 1.85, 0.28);
      body.add(chestPlate);

      // Dragon Head + Snout + Swept Horns
      head.position.set(0, 2.45, 0.45);
      const snout = new THREE.Mesh(new THREE.ConeGeometry(0.36, 0.82, 6), scaleMat);
      snout.rotation.x = Math.PI / 2;
      snout.position.z = 0.25;
      head.add(snout);

      for (const side of [-1, 1]) {
        const horn = new THREE.Mesh(new THREE.ConeGeometry(0.1, 0.68, 6), hornMat);
        horn.position.set(side * 0.24, 0.28, -0.15);
        horn.rotation.x = -0.65;
        horn.rotation.z = -side * 0.35;
        head.add(horn);

        const eye = new THREE.Mesh(new THREE.SphereGeometry(0.08, 8, 8), bellyMat);
        eye.position.set(side * 0.2, 0.14, 0.22);
        head.add(eye);
      }

      // Dorsal Dragon Spines along back
      for (let sp = 0; sp < 5; sp++) {
        const spineSpike = new THREE.Mesh(new THREE.ConeGeometry(0.09, 0.34, 6), hornMat);
        spineSpike.position.set(0, 2.35 - sp * 0.22, -0.25 - sp * 0.12);
        spineSpike.rotation.x = -0.8;
        body.add(spineSpike);
      }

      // Foreclaws (Left & Right Arms)
      leftArm.position.set(-0.45, 1.9, 0.35);
      const foreClaw = new THREE.Mesh(new THREE.ConeGeometry(0.12, 0.55, 8), hornMat);
      foreClaw.rotation.x = Math.PI * 0.75;
      foreClaw.position.set(0, -0.2, 0.2);
      leftArm.add(foreClaw);

      rightArm.position.set(0.45, 1.9, 0.35);
      rightArm.add(foreClaw.clone());

      // Articulated Dragon Wings (Left & Right) with Bone Struts
      leftWing = new THREE.Group();
      leftWing.position.set(-0.45, 2.15, 0);
      const wingGeo = createSculptedWingBladeGeometry(1.75, 1.1, 0.06);
      const lWingMesh = new THREE.Mesh(wingGeo, scaleMat);
      lWingMesh.scale.x = -1;
      const wingBoneL = new THREE.Mesh(new THREE.CylinderGeometry(0.05, 0.03, 1.65, 8), hornMat);
      wingBoneL.rotation.z = Math.PI * 0.38;
      wingBoneL.position.set(-0.75, 0.38, 0);
      leftWing.add(lWingMesh, wingBoneL);
      body.add(leftWing);

      rightWing = new THREE.Group();
      rightWing.position.set(0.45, 2.15, 0);
      const rWingMesh = new THREE.Mesh(wingGeo, scaleMat);
      const wingBoneR = new THREE.Mesh(new THREE.CylinderGeometry(0.05, 0.03, 1.65, 8), hornMat);
      wingBoneR.rotation.z = -Math.PI * 0.38;
      wingBoneR.position.set(0.75, 0.38, 0);
      rightWing.add(rWingMesh, wingBoneR);
      body.add(rightWing);

      // Spiked Whip Tail
      tail = new THREE.Group();
      tail.position.set(0, 1.35, -0.55);
      const tailCone = new THREE.Mesh(new THREE.ConeGeometry(0.26, 1.35, 6), scaleMat);
      tailCone.rotation.x = -Math.PI * 0.42;
      tailCone.position.set(0, -0.25, -0.55);
      tail.add(tailCone);
      body.add(tail);

      // Clawed Hind Legs
      leftLeg.position.set(-0.38, 1.25, 0.1);
      const clawLeg = new THREE.Mesh(new THREE.ConeGeometry(0.16, 0.72, 6), hornMat);
      clawLeg.rotation.x = Math.PI;
      clawLeg.position.y = -0.36;
      leftLeg.add(clawLeg);

      rightLeg.position.set(0.38, 1.25, 0.1);
      rightLeg.add(clawLeg.clone());
      break;
    }

    case 'demon_lord': {
      const obsidianArmorMat = registerMat(
        new THREE.MeshStandardMaterial({ color: 0x18181b, roughness: 0.2, metalness: 0.9 })
      );
      const demonFleshMat = registerMat(
        new THREE.MeshStandardMaterial({ color: 0x7f1d1d, roughness: 0.45, metalness: 0.25 })
      );
      const hellfireMat = registerMat(
        new THREE.MeshStandardMaterial({
          color: 0xff4500,
          emissive: 0xff1100,
          emissiveIntensity: 1.15,
          roughness: 0.15,
        })
      );

      // Towering Armored Torso + Molten Chest Core
      const torso = new THREE.Mesh(new THREE.BoxGeometry(1.25, 1.35, 0.78), obsidianArmorMat);
      torso.position.y = 1.75;
      body.add(torso);

      const magmaRunes = new THREE.Mesh(new THREE.OctahedronGeometry(0.42, 0), hellfireMat);
      magmaRunes.position.set(0, 1.82, 0.4);
      body.add(magmaRunes);

      // Giant Spiked Shoulder Pauldrons
      for (const side of [-1, 1]) {
        const pauldron = new THREE.Mesh(new THREE.DodecahedronGeometry(0.46, 0), obsidianArmorMat);
        pauldron.position.set(side * 0.9, 2.28, 0);
        body.add(pauldron);

        const horn = new THREE.Mesh(new THREE.ConeGeometry(0.14, 0.58, 6), hellfireMat);
        horn.position.set(side * 1.15, 2.65, 0);
        horn.rotation.z = -side * 0.55;
        body.add(horn);
      }

      // Demon Lord Crowned Head + Great Curved Horns
      head.position.set(0, 2.5, 0);
      const skull = new THREE.Mesh(new THREE.BoxGeometry(0.68, 0.68, 0.68), demonFleshMat);
      skull.position.y = 0.32;
      head.add(skull);

      const crown = new THREE.Mesh(new THREE.TorusGeometry(0.38, 0.06, 8, 16), hellfireMat);
      crown.rotation.x = Math.PI / 2;
      crown.position.y = 0.68;
      head.add(crown);

      for (const side of [-1, 1]) {
        const greatHorn = new THREE.Mesh(new THREE.ConeGeometry(0.14, 0.85, 8), obsidianArmorMat);
        greatHorn.position.set(side * 0.48, 0.68, 0);
        greatHorn.rotation.z = -side * 0.75;
        head.add(greatHorn);

        const eye = new THREE.Mesh(new THREE.SphereGeometry(0.1, 8, 8), hellfireMat);
        eye.position.set(side * 0.18, 0.36, 0.35);
        head.add(eye);
      }

      // Abyssal Demon Wings
      leftWing = new THREE.Group();
      leftWing.position.set(-0.5, 2.2, -0.35);
      const wingGeo = createSculptedWingBladeGeometry(1.9, 1.4, 0.08);
      const lWingMesh = new THREE.Mesh(wingGeo, obsidianArmorMat);
      lWingMesh.scale.x = -1;
      leftWing.add(lWingMesh);
      body.add(leftWing);

      rightWing = new THREE.Group();
      rightWing.position.set(0.5, 2.2, -0.35);
      const rWingMesh = new THREE.Mesh(wingGeo, obsidianArmorMat);
      rightWing.add(rWingMesh);
      body.add(rightWing);

      // Left Arm + Claw Gauntlet
      leftArm.position.set(-0.95, 2.1, 0);
      const arm = new THREE.Mesh(new THREE.CylinderGeometry(0.22, 0.18, 0.95, 8), demonFleshMat);
      arm.position.y = -0.45;
      leftArm.add(arm);

      // Right Arm + Colossal Hellfire Doom-Cleaver Sword
      rightArm.position.set(0.95, 2.1, 0);
      rightArm.add(arm.clone());

      const bossBladeGeo = createDiamondBladeGeometry(2.3, 0.46, 0.4, 0.55, 0.15);
      const bossSword = new THREE.Mesh(bossBladeGeo, hellfireMat);
      bossSword.rotation.x = Math.PI / 2;
      bossSword.position.set(0, -0.85, 0.25);
      rightArm.add(bossSword);

      // Armored Greaves Legs
      leftLeg.position.set(-0.38, 1.05, 0);
      const leg = new THREE.Mesh(new THREE.CylinderGeometry(0.24, 0.2, 1.05, 8), obsidianArmorMat);
      leg.position.y = -0.52;
      leftLeg.add(leg);

      rightLeg.position.set(0.38, 1.05, 0);
      rightLeg.add(leg.clone());
      break;
    }
  }

  group.traverse((obj) => {
    if (obj instanceof THREE.Mesh) {
      obj.castShadow = true;
      obj.receiveShadow = true;
    }
  });

  const animate = (time: number, isMoving: boolean, attackPhase: number) => {
    if (species === 'slime') {
      const bounce = isMoving ? Math.abs(Math.sin(time * 7)) * 0.35 : Math.sin(time * 3) * 0.06;
      const squash = isMoving ? 1 - Math.sin(time * 7) * 0.16 : 1 + Math.sin(time * 3) * 0.05;
      body.position.y = bounce;
      body.scale.set(1 / Math.sqrt(squash), squash, 1 / Math.sqrt(squash));
      head.rotation.y = time * 2.5;
      if (attackPhase > 0) {
        body.position.z = Math.sin(attackPhase * Math.PI) * 0.55;
      } else {
        body.position.z = 0;
      }
      return;
    }

    const walkCycle = isMoving ? Math.sin(time * 8) : Math.sin(time * 2) * 0.1;
    leftLeg.rotation.x = walkCycle * 0.55;
    rightLeg.rotation.x = -walkCycle * 0.55;
    body.position.y = isMoving ? Math.abs(Math.sin(time * 8)) * 0.08 : Math.sin(time * 2.5) * 0.04;

    if (leftWing && rightWing) {
      const flap = Math.sin(time * (species === 'crimson_drake' ? 9 : 4.5)) * 0.45;
      leftWing.rotation.y = flap;
      rightWing.rotation.y = -flap;
    }
    if (tail) {
      tail.rotation.y = Math.sin(time * 5) * 0.35;
    }

    if (attackPhase > 0) {
      // Wind-up and overhead strike animation
      const swing = Math.sin(attackPhase * Math.PI);
      rightArm.rotation.x = -1.6 * swing + 0.5;
      leftArm.rotation.x = -0.8 * swing;
      body.rotation.x = 0.25 * swing;
    } else {
      rightArm.rotation.x = -walkCycle * 0.45;
      leftArm.rotation.x = walkCycle * 0.45;
      body.rotation.x = 0;
    }
  };

  const setHitFlash = (active: boolean) => {
    for (const mat of hitMaterials) {
      if (active) {
        mat.emissive.setHex(0xffffff);
        mat.emissiveIntensity = 1.1;
      } else {
        mat.emissive.setHex(mat.userData.origEmissive ?? 0x000000);
        mat.emissiveIntensity = mat.userData.origIntensity ?? 0;
      }
    }
  };

  return {
    group,
    body,
    head,
    leftArm,
    rightArm,
    leftLeg,
    rightLeg,
    leftWing,
    rightWing,
    tail,
    hitMaterials,
    animate,
    setHitFlash,
  };
}

/**
 * Builds the 3D Hero Knight Wielder body (for when the player toggles between
 * "Modo Espada Viviente" and "Modo Caballero Portador 3D").
 */
export function buildHeroKnightWielder(): {
  group: THREE.Group;
  leftLeg: THREE.Group;
  rightLeg: THREE.Group;
  cape: THREE.Mesh;
} {
  const group = new THREE.Group();
  group.name = 'HeroKnightWielder';

  const steelMat = new THREE.MeshStandardMaterial({
    color: 0xcbd5e1,
    roughness: 0.22,
    metalness: 0.88,
  });
  const darkArmorMat = new THREE.MeshStandardMaterial({
    color: 0x1e293b,
    roughness: 0.35,
    metalness: 0.8,
  });
  const goldTrimMat = new THREE.MeshStandardMaterial({
    color: 0xfacc15,
    roughness: 0.2,
    metalness: 0.9,
  });
  const capeMat = new THREE.MeshStandardMaterial({
    color: 0x991b1b,
    roughness: 0.75,
    side: THREE.DoubleSide,
  });
  const visorGlowMat = new THREE.MeshStandardMaterial({
    color: 0x38bdf8,
    emissive: 0x00f2fe,
    emissiveIntensity: 1.2,
  });

  // Cuirass Torso
  const torso = new THREE.Mesh(new THREE.CylinderGeometry(0.38, 0.3, 0.85, 8), darkArmorMat);
  torso.position.y = 1.18;
  group.add(torso);

  const chestPlate = new THREE.Mesh(new THREE.BoxGeometry(0.68, 0.56, 0.48), steelMat);
  chestPlate.position.y = 1.28;
  group.add(chestPlate);

  // Pauldrons
  for (const side of [-1, 1]) {
    const pauldron = new THREE.Mesh(new THREE.SphereGeometry(0.24, 10, 10), steelMat);
    pauldron.position.set(side * 0.48, 1.48, 0);
    group.add(pauldron);

    const trim = new THREE.Mesh(new THREE.TorusGeometry(0.22, 0.03, 6, 14), goldTrimMat);
    trim.position.set(side * 0.48, 1.42, 0);
    trim.rotation.x = Math.PI / 2;
    group.add(trim);
  }

  // Knight Helmet + Visor + Plume
  const helm = new THREE.Mesh(new THREE.CylinderGeometry(0.24, 0.26, 0.46, 10), steelMat);
  helm.position.y = 1.85;
  group.add(helm);

  const visor = new THREE.Mesh(new THREE.BoxGeometry(0.34, 0.08, 0.16), visorGlowMat);
  visor.position.set(0, 1.86, 0.2);
  group.add(visor);

  const crest = new THREE.Mesh(new THREE.ConeGeometry(0.14, 0.42, 6), capeMat);
  crest.rotation.x = -Math.PI * 0.35;
  crest.position.set(0, 2.15, -0.1);
  group.add(crest);

  // Flowing Cape
  const cape = new THREE.Mesh(new THREE.PlaneGeometry(0.82, 1.28, 4, 6), capeMat);
  cape.position.set(0, 0.96, -0.28);
  cape.rotation.x = 0.18;
  group.add(cape);

  // Legs
  const leftLeg = new THREE.Group();
  leftLeg.position.set(-0.18, 0.75, 0);
  const legMesh = new THREE.Mesh(new THREE.CylinderGeometry(0.13, 0.11, 0.75, 8), darkArmorMat);
  legMesh.position.y = -0.37;
  leftLeg.add(legMesh);
  group.add(leftLeg);

  const rightLeg = new THREE.Group();
  rightLeg.position.set(0.18, 0.75, 0);
  rightLeg.add(legMesh.clone());
  group.add(rightLeg);

  group.traverse((obj) => {
    if (obj instanceof THREE.Mesh) {
      obj.castShadow = true;
      obj.receiveShadow = true;
    }
  });

  return { group, leftLeg, rightLeg, cape };
}
