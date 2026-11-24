import React, { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import * as THREE from 'three';
import {
  Award,
  Bot,
  ChevronRight,
  Coins,
  Eye,
  Flame,
  Hammer,
  Heart,
  Shield,
  Skull,
  Sparkles,
  Sword,
  TrendingUp,
  User,
  Volume2,
  VolumeX,
  Zap,
} from 'lucide-react';
import {
  ActiveSkillCooldowns,
  CombatLogEntry,
  ForgeUpgrades,
  MonsterDefinition,
  SwordEvolutionTier,
  WielderMode,
} from './types/game';
import {
  getSwordEvolutionForLevel,
  getXpRequiredForLevel,
  MONSTER_DEFINITIONS,
  SWORD_EVOLUTIONS,
} from './data/evolutions';
import { buildSword3DModel, SwordModelInstance } from './models/swordModels';
import {
  ArticulatedMonsterModel,
  buildHeroKnightWielder,
  buildMonster3DModel,
} from './models/monsterModels';
import { buildArenaEnvironment } from './models/environmentModels';
import { createCrescentWaveGeometry } from './models/customGeometry';
import { soundEngine } from './audio/soundEngine';
import { ModelViewerModal } from './components/ModelViewerModal';

interface ActiveEnemy {
  id: string;
  def: MonsterDefinition;
  model: ArticulatedMonsterModel;
  hp: number;
  maxHp: number;
  damage: number;
  speed: number;
  attackCooldownTimer: number;
  attackAnimPhase: number;
  hitFlashTimer: number;
  knockbackVel: THREE.Vector3;
  bleedTimer: number;
}

interface ActiveProjectile {
  id: string;
  mesh: THREE.Group;
  velocity: THREE.Vector3;
  damage: number;
  radius: number;
  life: number;
  hitEnemyIds: Set<string>;
}

interface ActiveLootOrb {
  id: string;
  mesh: THREE.Mesh;
  type: 'xp' | 'gold' | 'heal';
  value: number;
  velocity: THREE.Vector3;
  age: number;
}

interface ActiveSkySword {
  mesh: THREE.Group;
  targetPos: THREE.Vector3;
  fallProgress: number;
  exploded: boolean;
  lingerTimer: number;
  damage: number;
}

interface FloatingDamageNumber {
  id: string;
  text: string;
  screenX: number;
  screenY: number;
  color: string;
  isCrit: boolean;
  createdAt: number;
}

interface EnemyScreenBar {
  id: string;
  name: string;
  hp: number;
  maxHp: number;
  isBoss: boolean;
  x: number;
  y: number;
  visible: boolean;
}

export function App() {
  // Core Progression State
  const [swordLevel, setSwordLevel] = useState<number>(1);
  const [currentXp, setCurrentXp] = useState<number>(0);
  const [gold, setGold] = useState<number>(60);
  const [kills, setKills] = useState<number>(0);
  const [wave, setWave] = useState<number>(1);
  const [waveKills, setWaveKills] = useState<number>(0);
  const [playerHp, setPlayerHp] = useState<number>(220);
  const [playerMaxHp, setPlayerMaxHp] = useState<number>(220);

  // Modes & UI Modals
  const [wielderMode, setWielderMode] = useState<WielderMode>('living_sword');
  const [autoHunt, setAutoHunt] = useState<boolean>(false);
  const [muted, setMuted] = useState<boolean>(false);
  const [isModelViewerOpen, setIsModelViewerOpen] = useState<boolean>(false);
  const [isForgeDrawerOpen, setIsForgeDrawerOpen] = useState<boolean>(true);
  const [evolutionBanner, setEvolutionBanner] = useState<SwordEvolutionTier | null>(null);

  // Forge Upgrades
  const [upgrades, setUpgrades] = useState<ForgeUpgrades>({
    sharpness: 0,
    swiftness: 0,
    vampirism: 0,
    criticalMastery: 0,
    soulMagnet: 0,
    bladeSize: 0,
  });

  // Cooldowns & HUD Overlays
  const [cooldowns, setCooldowns] = useState<ActiveSkillCooldowns>({
    whirlwind: 0,
    swordWave: 0,
    ultimate: 0,
    dash: 0,
  });
  const [floatingNumbers, setFloatingNumbers] = useState<FloatingDamageNumber[]>([]);
  const [enemyBars, setEnemyBars] = useState<EnemyScreenBar[]>([]);
  const [combatLog, setCombatLog] = useState<CombatLogEntry[]>([
    {
      id: 'init-1',
      text: '¡Has despertado como una Espada de Madera Ancestral (Nivel 1)! Derrota monstruos para evolucionar a Espada de Cobre al Nivel 5.',
      type: 'evolution',
      timestamp: Date.now(),
    },
  ]);

  const currentEvolution = useMemo(() => getSwordEvolutionForLevel(swordLevel), [swordLevel]);
  const xpRequired = useMemo(() => getXpRequiredForLevel(swordLevel), [swordLevel]);

  // Derived Combat Stats
  const computedStats = useMemo(() => {
    const levelBonus = 1 + (swordLevel - currentEvolution.minLevel) * 0.14;
    const sharpMult = 1 + upgrades.sharpness * 0.18;
    const damage = Math.round(currentEvolution.baseDamage * levelBonus * sharpMult);
    const attackSpeed = +(currentEvolution.attackSpeed * (1 + upgrades.swiftness * 0.08)).toFixed(2);
    const critChance = Math.min(0.95, currentEvolution.critChance + upgrades.criticalMastery * 0.04);
    const critDamageMult = 1.85 + upgrades.criticalMastery * 0.15 + (currentEvolution.id === 'celestial' ? 0.65 : 0);
    const range = +(currentEvolution.range * (1 + upgrades.bladeSize * 0.06)).toFixed(2);
    const lifeOnHit = upgrades.vampirism * 3 + (currentEvolution.id === 'obsidian' ? 14 : 0);
    const xpMult = 1 + upgrades.soulMagnet * 0.15 + (currentEvolution.id === 'wood' ? 0.15 : 0);

    return {
      damage,
      attackSpeed,
      critChance,
      critDamageMult,
      range,
      lifeOnHit,
      xpMult,
    };
  }, [currentEvolution, swordLevel, upgrades]);

  // Mutable Refs for 60FPS Three.js Game Loop access
  const stateRef = useRef({
    swordLevel,
    currentXp,
    xpRequired,
    gold,
    kills,
    wave,
    waveKills,
    playerHp,
    playerMaxHp,
    wielderMode,
    autoHunt,
    currentEvolution,
    computedStats,
    upgrades,
  });

  useEffect(() => {
    stateRef.current = {
      swordLevel,
      currentXp,
      xpRequired,
      gold,
      kills,
      wave,
      waveKills,
      playerHp,
      playerMaxHp,
      wielderMode,
      autoHunt,
      currentEvolution,
      computedStats,
      upgrades,
    };
  }, [
    swordLevel,
    currentXp,
    xpRequired,
    gold,
    kills,
    wave,
    waveKills,
    playerHp,
    playerMaxHp,
    wielderMode,
    autoHunt,
    currentEvolution,
    computedStats,
    upgrades,
  ]);

  const addCombatLog = useCallback((text: string, type: CombatLogEntry['type']) => {
    setCombatLog((prev) => [
      { id: `${Date.now()}-${Math.random()}`, text, type, timestamp: Date.now() },
      ...prev.slice(0, 7),
    ]);
  }, []);

  // Level Up & Evolution Handler
  const gainExperience = useCallback(
    (amount: number) => {
      setCurrentXp((prevXp) => {
        let newXp = prevXp + amount;
        let lvl = stateRef.current.swordLevel;
        let needed = getXpRequiredForLevel(lvl);
        let leveledUp = false;
        const oldTier = getSwordEvolutionForLevel(lvl);

        while (newXp >= needed) {
          newXp -= needed;
          lvl += 1;
          needed = getXpRequiredForLevel(lvl);
          leveledUp = true;
        }

        if (leveledUp) {
          const newTier = getSwordEvolutionForLevel(lvl);
          const didEvolve = newTier.id !== oldTier.id;
          setSwordLevel(lvl);
          const newMaxHp = 220 + (lvl - 1) * 28;
          setPlayerMaxHp(newMaxHp);
          setPlayerHp(newMaxHp);
          soundEngine.playLevelUp(didEvolve);

          if (didEvolve) {
            setEvolutionBanner(newTier);
            addCombatLog(
              `¡METAMORFOSIS AL NIVEL ${lvl}! Tu espada ha evolucionado a ${newTier.name.toUpperCase()}.`,
              'evolution'
            );
          } else {
            addCombatLog(
              `¡Tu espada subió al Nivel ${lvl}! El filo y poder aumentan.`,
              'levelup'
            );
          }
        }
        return newXp;
      });
    },
    [addCombatLog]
  );

  // Jump directly to a level (for testing or Forge direct level up)
  const jumpToLevel = useCallback(
    (targetLevel: number) => {
      const oldTier = getSwordEvolutionForLevel(stateRef.current.swordLevel);
      const newTier = getSwordEvolutionForLevel(targetLevel);
      setSwordLevel(targetLevel);
      setCurrentXp(0);
      const newMaxHp = 220 + (targetLevel - 1) * 28;
      setPlayerMaxHp(newMaxHp);
      setPlayerHp(newMaxHp);
      soundEngine.playLevelUp(newTier.id !== oldTier.id);

      if (newTier.id !== oldTier.id) {
        setEvolutionBanner(newTier);
        addCombatLog(
          `¡EVOLUCIÓN ACTIVADA (Nivel ${targetLevel}): ${newTier.name}!`,
          'evolution'
        );
      } else {
        addCombatLog(`Nivel de la espada ajustado a Nivel ${targetLevel}.`, 'levelup');
      }
    },
    [addCombatLog]
  );

  // Three.js Scene & Action Refs
  const canvasContainerRef = useRef<HTMLDivElement | null>(null);
  const triggerAttackRef = useRef<() => void>(() => {});
  const triggerSkillRef = useRef<(skill: 'whirlwind' | 'wave' | 'ultimate' | 'dash') => void>(
    () => {}
  );
  const rebuildPlayerSwordRef = useRef<(lvl: number, mode: WielderMode, sizeLvl: number) => void>(
    () => {}
  );

  // Rebuild 3D Sword Model whenever swordLevel, wielderMode, or bladeSize upgrade changes
  useEffect(() => {
    rebuildPlayerSwordRef.current(swordLevel, wielderMode, upgrades.bladeSize);
  }, [swordLevel, wielderMode, upgrades.bladeSize]);

  // Auto-dismiss Evolution Banner after 5.5 seconds
  useEffect(() => {
    if (!evolutionBanner) return;
    const timer = setTimeout(() => setEvolutionBanner(null), 5500);
    return () => clearTimeout(timer);
  }, [evolutionBanner]);

  // Main Three.js 3D Engine Setup
  useEffect(() => {
    const container = canvasContainerRef.current;
    if (!container) return;

    const width = container.clientWidth || window.innerWidth;
    const height = container.clientHeight || window.innerHeight;

    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x090d16);
    scene.fog = new THREE.FogExp2(0x090d16, 0.014);

    const camera = new THREE.PerspectiveCamera(48, width / height, 0.1, 140);
    camera.position.set(0, 13.5, 16.5);

    const renderer = new THREE.WebGLRenderer({ antialias: true, powerPreference: 'high-performance' });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.shadowMap.enabled = true;
    renderer.shadowMap.type = THREE.PCFSoftShadowMap;
    container.innerHTML = '';
    container.appendChild(renderer.domElement);

    // Lighting
    const hemiLight = new THREE.HemisphereLight(0xdbeafe, 0x1e1b4b, 0.9);
    scene.add(hemiLight);

    const dirLight = new THREE.DirectionalLight(0xfffbeb, 2.1);
    dirLight.position.set(16, 28, 18);
    dirLight.castShadow = true;
    dirLight.shadow.mapSize.width = 2048;
    dirLight.shadow.mapSize.height = 2048;
    dirLight.shadow.camera.near = 2;
    dirLight.shadow.camera.far = 75;
    const d = 28;
    dirLight.shadow.camera.left = -d;
    dirLight.shadow.camera.right = d;
    dirLight.shadow.camera.top = d;
    dirLight.shadow.camera.bottom = -d;
    scene.add(dirLight);

    // Build Handcrafted 3D Arena Environment
    const arena = buildArenaEnvironment();
    scene.add(arena.group);

    // Player Root Group
    const playerRoot = new THREE.Group();
    playerRoot.position.set(0, 0, 0);
    scene.add(playerRoot);

    // Player Aura Ring on Ground
    const playerRingGeo = new THREE.RingGeometry(1.15, 1.38, 36);
    const playerRingMat = new THREE.MeshBasicMaterial({
      color: 0x86efac,
      side: THREE.DoubleSide,
      transparent: true,
      opacity: 0.75,
    });
    const playerRing = new THREE.Mesh(playerRingGeo, playerRingMat);
    playerRing.rotation.x = -Math.PI / 2;
    playerRing.position.y = 0.05;
    playerRoot.add(playerRing);

    // Dynamic Point Light attached to the Living Sword
    const swordLight = new THREE.PointLight(0x86efac, 2.2, 9);
    swordLight.position.set(0, 2.2, 0);
    playerRoot.add(swordLight);

    // Holder for Sword & optional Knight Wielder
    const playerVisualHolder = new THREE.Group();
    playerRoot.add(playerVisualHolder);

    const swordSwingHolder = new THREE.Group();
    playerVisualHolder.add(swordSwingHolder);

    let activeSwordModel: SwordModelInstance | null = null;
    let activeKnightModel: ReturnType<typeof buildHeroKnightWielder> | null = null;

    // 3D Crescent Slash Arc Effect attached to Player during swings
    const slashArcGeo = createCrescentWaveGeometry(3.2, 1.15);
    const slashArcMat = new THREE.MeshBasicMaterial({
      color: 0xd4a373,
      side: THREE.DoubleSide,
      transparent: true,
      opacity: 0.0,
    });
    const slashArcMesh = new THREE.Mesh(slashArcGeo, slashArcMat);
    slashArcMesh.position.y = 1.25;
    playerRoot.add(slashArcMesh);

    const rebuildPlayerVisuals = (lvl: number, mode: WielderMode, sizeUpgrade: number) => {
      const tier = getSwordEvolutionForLevel(lvl);
      swordSwingHolder.clear();
      if (activeKnightModel) {
        playerVisualHolder.remove(activeKnightModel.group);
        activeKnightModel = null;
      }

      activeSwordModel = buildSword3DModel(tier.id, lvl);
      const scaleMult = 1 + sizeUpgrade * 0.06;

      if (mode === 'knight_wielder') {
        activeKnightModel = buildHeroKnightWielder();
        playerVisualHolder.add(activeKnightModel.group);
        swordSwingHolder.position.set(0.58, 1.25, 0.25);
        activeSwordModel.group.scale.setScalar(0.88 * scaleMult);
      } else {
        // Sentient Living Sword Mode: giant levitating 3D sword with mystic runic halo
        swordSwingHolder.position.set(0, 1.55, 0);
        activeSwordModel.group.scale.setScalar(1.12 * scaleMult);
      }

      swordSwingHolder.add(activeSwordModel.group);
      playerRingMat.color.set(tier.auraColor);
      swordLight.color.set(tier.auraColor);
      slashArcMat.color.set(tier.slashTrailColor);
    };

    rebuildPlayerSwordRef.current = rebuildPlayerVisuals;
    rebuildPlayerVisuals(
      stateRef.current.swordLevel,
      stateRef.current.wielderMode,
      stateRef.current.upgrades.bladeSize
    );

    // Collections for Enemies, Projectiles, Loot Orbs, Sky Swords, Shockwaves
    const enemies: ActiveEnemy[] = [];
    const projectiles: ActiveProjectile[] = [];
    const lootOrbs: ActiveLootOrb[] = [];
    const skySwords: ActiveSkySword[] = [];
    const shockwaves: { mesh: THREE.Mesh; mat: THREE.MeshBasicMaterial; age: number; maxRadius: number }[] = [];

    const spawnShockwave = (pos: THREE.Vector3, colorHex: string, maxRadius = 4.5) => {
      const geo = new THREE.RingGeometry(0.3, 0.65, 32);
      const mat = new THREE.MeshBasicMaterial({
        color: colorHex,
        side: THREE.DoubleSide,
        transparent: true,
        opacity: 0.85,
      });
      const mesh = new THREE.Mesh(geo, mat);
      mesh.rotation.x = -Math.PI / 2;
      mesh.position.set(pos.x, 0.08, pos.z);
      scene.add(mesh);
      shockwaves.push({ mesh, mat, age: 0, maxRadius });
    };

    const pushFloatingNumber = (
      worldPos: THREE.Vector3,
      text: string,
      color: string,
      isCrit = false
    ) => {
      const projected = worldPos.clone().project(camera);
      const sx = (projected.x * 0.5 + 0.5) * container.clientWidth;
      const sy = (-projected.y * 0.5 + 0.5) * container.clientHeight;
      setFloatingNumbers((prev) => [
        ...prev.slice(-18),
        {
          id: `${Date.now()}-${Math.random()}`,
          text,
          screenX: sx + (Math.random() - 0.5) * 28,
          screenY: sy - 20,
          color,
          isCrit,
          createdAt: performance.now(),
        },
      ]);
    };

    const spawnLootOrbs = (pos: THREE.Vector3, xpAmount: number, goldAmount: number) => {
      // XP Soul Orb
      const xpOrbMat = new THREE.MeshStandardMaterial({
        color: 0x38bdf8,
        emissive: 0x00f2fe,
        emissiveIntensity: 1.1,
      });
      const xpOrb = new THREE.Mesh(new THREE.OctahedronGeometry(0.28, 0), xpOrbMat);
      xpOrb.position.set(pos.x, 0.8, pos.z);
      scene.add(xpOrb);
      lootOrbs.push({
        id: `xp-${ Math.random() }`,
        mesh: xpOrb,
        type: 'xp',
        value: xpAmount,
        velocity: new THREE.Vector3((Math.random() - 0.5) * 4, 4.5, (Math.random() - 0.5) * 4),
        age: 0,
      });

      // Gold Essence Gem
      const goldOrbMat = new THREE.MeshStandardMaterial({
        color: 0xfacc15,
        emissive: 0xf59e0b,
        emissiveIntensity: 0.9,
      });
      const goldOrb = new THREE.Mesh(new THREE.DodecahedronGeometry(0.24, 0), goldOrbMat);
      goldOrb.position.set(pos.x, 0.8, pos.z);
      scene.add(goldOrb);
      lootOrbs.push({
        id: `gold-${ Math.random() }`,
        mesh: goldOrb,
        type: 'gold',
        value: goldAmount,
        velocity: new THREE.Vector3((Math.random() - 0.5) * 4, 4.0, (Math.random() - 0.5) * 4),
        age: 0,
      });
    };

    // Spawn a 3D Monster in the Arena
    const spawnMonster = (forceBoss = false) => {
      const currentWave = stateRef.current.wave;
      const eligible = MONSTER_DEFINITIONS.filter(
        (m) => m.minWave <= currentWave && (forceBoss ? m.isBoss : !m.isBoss)
      );
      const pool = eligible.length > 0 ? eligible : [MONSTER_DEFINITIONS[0]];
      const def = forceBoss
        ? MONSTER_DEFINITIONS.find((m) => m.isBoss) || pool[pool.length - 1]
        : pool[Math.floor(Math.random() * pool.length)];

      const model = buildMonster3DModel(def.id);
      model.group.scale.setScalar(def.scale);

      const angle = Math.random() * Math.PI * 2;
      const dist = 12 + Math.random() * 10;
      model.group.position.set(
        Math.max(-23, Math.min(23, playerRoot.position.x + Math.sin(angle) * dist)),
        0,
        Math.max(-23, Math.min(23, playerRoot.position.z + Math.cos(angle) * dist))
      );

      scene.add(model.group);

      const waveScale = 1 + (currentWave - 1) * 0.24;
      const maxHp = Math.round(def.baseHp * waveScale);
      const damage = Math.round(def.baseDamage * (1 + (currentWave - 1) * 0.16));

      enemies.push({
        id: `enemy-${Date.now()}-${Math.random()}`,
        def,
        model,
        hp: maxHp,
        maxHp,
        damage,
        speed: def.speed,
        attackCooldownTimer: 0.8,
        attackAnimPhase: 0,
        hitFlashTimer: 0,
        knockbackVel: new THREE.Vector3(),
        bleedTimer: 0,
      });
    };

    // Initial wave of monsters
    for (let i = 0; i < 6; i++) {
      spawnMonster(false);
    }

    // Damage an Enemy & Handle Death + Evolution XP
    const applyDamageToEnemy = (
      enemy: ActiveEnemy,
      rawDamage: number,
      knockbackForce = 5.5,
      allowSpecial = true
    ) => {
      const { computedStats: stats, currentEvolution: evo } = stateRef.current;
      const isCrit = Math.random() < stats.critChance;
      const finalDamage = Math.max(1, Math.round(rawDamage * (isCrit ? stats.critDamageMult : 1)));

      enemy.hp -= finalDamage;
      enemy.hitFlashTimer = 0.14;
      enemy.model.setHitFlash(true);

      const dir = enemy.model.group.position
        .clone()
        .sub(playerRoot.position)
        .setY(0)
        .normalize();
      enemy.knockbackVel.copy(dir.multiplyScalar(knockbackForce));

      soundEngine.playHit(evo.id, isCrit);

      pushFloatingNumber(
        enemy.model.group.position.clone().add(new THREE.Vector3(0, 2.2, 0)),
        isCrit ? `¡${finalDamage}!` : `${finalDamage}`,
        isCrit ? '#facc15' : evo.slashTrailColor,
        isCrit
      );

      // Lifesteal / Vampirism
      if (stats.lifeOnHit > 0) {
        setPlayerHp((hp) => Math.min(stateRef.current.playerMaxHp, hp + stats.lifeOnHit));
      }

      // Evolution Passive Effects
      if (allowSpecial) {
        if (evo.specialEffect === 'bleed' && isCrit) {
          enemy.bleedTimer = 3.0;
        } else if (evo.specialEffect === 'lightning') {
          // Chain lightning to another nearby monster
          const other = enemies.find(
            (e) =>
              e.id !== enemy.id &&
              e.hp > 0 &&
              e.model.group.position.distanceTo(enemy.model.group.position) < 6.5
          );
          if (other) {
            applyDamageToEnemy(other, Math.round(rawDamage * 0.45), 2.0, false);
            spawnShockwave(other.model.group.position, '#38bdf8', 2.2);
          }
        }
      }

      if (enemy.hp <= 0) {
        // Enemy defeated!
        spawnShockwave(enemy.model.group.position, evo.auraColor, enemy.def.isBoss ? 6.5 : 3.0);
        const xpGain = Math.round(enemy.def.xpReward * stats.xpMult);
        const goldGain = Math.round(
          enemy.def.goldReward * (1 + stateRef.current.upgrades.soulMagnet * 0.12)
        );
        spawnLootOrbs(enemy.model.group.position, xpGain, goldGain);
        scene.remove(enemy.model.group);

        setKills((k) => k + 1);
        setWaveKills((wk) => {
          const nextWk = wk + 1;
          if (nextWk >= 8) {
            const nextWave = stateRef.current.wave + 1;
            setWave(nextWave);
            if (nextWave % 3 === 0) {
              addCombatLog(
                `¡OLEADA ${nextWave}! ¡El Jefe Supremo Malakor ha entrado en la Arena!`,
                'boss'
              );
              setTimeout(() => spawnMonster(true), 300);
            } else {
              addCombatLog(
                `¡Oleada ${nextWave} iniciada! Monstruos más fuertes emergen.`,
                'kill'
              );
            }
            return 0;
          }
          return nextWk;
        });
      }
    };

    // Player Movement & Combat Animation State
    const keys: Record<string, boolean> = {};
    let playerFacingAngle = 0;
    let comboStep = 0;
    let attackAnimTimer = 0;
    let attackCooldownTimer = 0;
    let whirlwindTimer = 0;
    let dashTimer = 0;
    const dashDir = new THREE.Vector3();

    const skillCd = {
      whirlwind: 0,
      swordWave: 0,
      ultimate: 0,
      dash: 0,
    };

    const performBasicAttack = () => {
      if (attackCooldownTimer > 0) return;
      const { computedStats: stats, currentEvolution: evo } = stateRef.current;

      attackCooldownTimer = 0.42 / stats.attackSpeed;
      attackAnimTimer = 0.28;
      comboStep = (comboStep + 1) % 3;

      soundEngine.playSlash(evo.id, comboStep);

      // Show 3D Slash Arc
      slashArcMesh.rotation.y = playerFacingAngle;
      slashArcMesh.rotation.z = comboStep === 0 ? 0.15 : comboStep === 1 ? -0.25 : 0;
      slashArcMesh.scale.setScalar(stats.range / 3.0);
      slashArcMat.opacity = 0.92;

      if (comboStep === 2 || evo.specialEffect === 'sparks' || evo.specialEffect === 'cosmic_nova') {
        const forwardPos = playerRoot.position
          .clone()
          .add(new THREE.Vector3(Math.sin(playerFacingAngle) * 1.8, 0, Math.cos(playerFacingAngle) * 1.8));
        spawnShockwave(forwardPos, evo.slashTrailColor, stats.range * 1.05);
      }

      // Hit all enemies within sword reach and arc (generous cleave so combat feels awesome!)
      const forward = new THREE.Vector3(Math.sin(playerFacingAngle), 0, Math.cos(playerFacingAngle));
      const comboMult = comboStep === 2 ? 1.35 : 1.0;

      for (let i = enemies.length - 1; i >= 0; i--) {
        const enemy = enemies[i];
        if (enemy.hp <= 0) continue;
        const toEnemy = enemy.model.group.position.clone().sub(playerRoot.position);
        toEnemy.y = 0;
        const dist = toEnemy.length();
        const hitRadius = stats.range + (enemy.def.isBoss ? 1.3 : 0.75);

        if (dist <= hitRadius) {
          const dirNorm = toEnemy.clone().normalize();
          const dot = forward.dot(dirNorm);
          // 3rd combo hit is a 360 cleave; 1st and 2nd hit a wide 220-degree front arc
          if (comboStep === 2 || dist < 2.2 || dot > -0.35) {
            applyDamageToEnemy(enemy, stats.damage * comboMult, comboStep === 2 ? 8.0 : 5.2);
          }
        }
      }

      // Clean dead enemies
      for (let i = enemies.length - 1; i >= 0; i--) {
        if (enemies[i].hp <= 0) enemies.splice(i, 1);
      }
    };

    const performSkill = (skill: 'whirlwind' | 'wave' | 'ultimate' | 'dash') => {
      const { computedStats: stats, currentEvolution: evo } = stateRef.current;

      if (skill === 'whirlwind') {
        if (skillCd.whirlwind > 0) return;
        skillCd.whirlwind = 4.0;
        whirlwindTimer = 1.1;
        soundEngine.playSkill('whirlwind');
        spawnShockwave(playerRoot.position, evo.auraColor, stats.range * 1.45);
      } else if (skill === 'wave') {
        if (skillCd.swordWave > 0) return;
        skillCd.swordWave = 4.5;
        soundEngine.playSkill('wave');

        // Create 3D Crescent Energy Blade Projectile
        const waveGroup = new THREE.Group();
        const waveGeo = createCrescentWaveGeometry(2.3, 0.85);
        const waveMat = new THREE.MeshBasicMaterial({
          color: evo.slashTrailColor,
          side: THREE.DoubleSide,
        });
        const waveMesh = new THREE.Mesh(waveGeo, waveMat);
        waveGroup.add(waveMesh);
        waveGroup.position.copy(playerRoot.position).add(new THREE.Vector3(0, 1.3, 0));
        waveGroup.rotation.y = playerFacingAngle;
        scene.add(waveGroup);

        const vel = new THREE.Vector3(
          Math.sin(playerFacingAngle) * 20,
          0,
          Math.cos(playerFacingAngle) * 20
        );
        projectiles.push({
          id: `wave-${Date.now()}-${Math.random()}`,
          mesh: waveGroup,
          velocity: vel,
          damage: Math.round(stats.damage * 1.9),
          radius: 2.5,
          life: 1.6,
          hitEnemyIds: new Set(),
        });
      } else if (skill === 'ultimate') {
        if (skillCd.ultimate > 0) return;
        skillCd.ultimate = 10.0;
        soundEngine.playSkill('ultimate');

        // Summon 7 Giant 3D Swords of the current evolution tier falling from the sky!
        for (let s = 0; s < 7; s++) {
          const angle = (s / 7) * Math.PI * 2;
          const dist = s === 0 ? 2.5 : 5.2;
          const target = new THREE.Vector3(
            playerRoot.position.x + Math.sin(angle) * dist,
            0,
            playerRoot.position.z + Math.cos(angle) * dist
          );

          const skySwordInst = buildSword3DModel(evo.id, stateRef.current.swordLevel);
          skySwordInst.group.scale.setScalar(1.45);
          // Point blade downward!
          skySwordInst.bladePivot.rotation.z = Math.PI;
          skySwordInst.group.position.set(target.x, 18 + s * 2.2, target.z);
          scene.add(skySwordInst.group);

          skySwords.push({
            mesh: skySwordInst.group,
            targetPos: target,
            fallProgress: -s * 0.08,
            exploded: false,
            lingerTimer: 1.1,
            damage: Math.round(stats.damage * 2.5),
          });
        }
      } else if (skill === 'dash') {
        if (skillCd.dash > 0) return;
        skillCd.dash = 1.8;
        dashTimer = 0.22;
        dashDir.set(Math.sin(playerFacingAngle), 0, Math.cos(playerFacingAngle));
        soundEngine.playSkill('dash');
        spawnShockwave(playerRoot.position, '#38bdf8', 2.8);
      }
    };

    triggerAttackRef.current = performBasicAttack;
    triggerSkillRef.current = performSkill;

    // Input Listeners
    const handleKeyDown = (e: KeyboardEvent) => {
      const code = e.code;
      keys[code] = true;
      if (code === 'Space') {
        e.preventDefault();
        performBasicAttack();
      } else if (code === 'KeyQ') {
        performSkill('whirlwind');
      } else if (code === 'KeyE') {
        performSkill('wave');
      } else if (code === 'KeyR') {
        performSkill('ultimate');
      } else if (code === 'ShiftLeft' || code === 'ShiftRight') {
        performSkill('dash');
      }
    };

    const handleKeyUp = (e: KeyboardEvent) => {
      keys[e.code] = false;
    };

    const handleCanvasMouseDown = (e: MouseEvent) => {
      if (e.button === 0) {
        // Aim towards mouse ray on ground plane & attack
        const rect = renderer.domElement.getBoundingClientRect();
        const ndcX = ((e.clientX - rect.left) / rect.width) * 2 - 1;
        const ndcY = -((e.clientY - rect.top) / rect.height) * 2 + 1;
        const raycaster = new THREE.Raycaster();
        raycaster.setFromCamera(new THREE.Vector2(ndcX, ndcY), camera);
        const groundPlane = new THREE.Plane(new THREE.Vector3(0, 1, 0), 0);
        const hitPoint = new THREE.Vector3();
        if (raycaster.ray.intersectPlane(groundPlane, hitPoint)) {
          const dx = hitPoint.x - playerRoot.position.x;
          const dz = hitPoint.z - playerRoot.position.z;
          if (Math.hypot(dx, dz) > 0.2) {
            playerFacingAngle = Math.atan2(dx, dz);
          }
        }
        performBasicAttack();
      } else if (e.button === 2) {
        e.preventDefault();
        performSkill('whirlwind');
      }
    };

    const handleContextMenu = (e: MouseEvent) => e.preventDefault();

    window.addEventListener('keydown', handleKeyDown);
    window.addEventListener('keyup', handleKeyUp);
    renderer.domElement.addEventListener('mousedown', handleCanvasMouseDown);
    renderer.domElement.addEventListener('contextmenu', handleContextMenu);

    // Main 60FPS Game Loop
    let animationFrameId = 0;
    let lastTime = performance.now();
    let spawnTimer = 0;
    let whirlwindTickTimer = 0;
    let hudSyncTimer = 0;

    const animate = () => {
      animationFrameId = requestAnimationFrame(animate);
      const now = performance.now();
      const dt = Math.min(0.05, (now - lastTime) * 0.001);
      lastTime = now;
      const elapsed = now * 0.001;

      const { autoHunt: isAuto, currentEvolution: evo, computedStats: stats } = stateRef.current;

      // Update Environment
      arena.updateEnvironment(elapsed, evo.auraColor);

      // Update Cooldowns
      for (const k of ['whirlwind', 'swordWave', 'ultimate', 'dash'] as const) {
        if (skillCd[k] > 0) skillCd[k] = Math.max(0, skillCd[k] - dt);
      }

      // Maintain active monster population in arena
      spawnTimer += dt;
      if (enemies.length < 7 && spawnTimer > 1.35) {
        spawnTimer = 0;
        spawnMonster(false);
      }

      // Player Movement (Keyboard or Auto-Hunt AI)
      const moveVec = new THREE.Vector3();
      if (keys['KeyW'] || keys['ArrowUp']) moveVec.z -= 1;
      if (keys['KeyS'] || keys['ArrowDown']) moveVec.z += 1;
      if (keys['KeyA'] || keys['ArrowLeft']) moveVec.x -= 1;
      if (keys['KeyD'] || keys['ArrowRight']) moveVec.x += 1;

      let isPlayerMoving = false;

      if (dashTimer > 0) {
        dashTimer -= dt;
        playerRoot.position.addScaledVector(dashDir, 24 * dt);
        isPlayerMoving = true;
      } else if (moveVec.lengthSq() > 0) {
        moveVec.normalize();
        playerFacingAngle = Math.atan2(moveVec.x, moveVec.z);
        playerRoot.position.addScaledVector(moveVec, 8.2 * dt);
        isPlayerMoving = true;
      } else if (isAuto && enemies.length > 0) {
        // Intelligent Auto-Hunt AI: move toward nearest monster and unleash attacks & skills!
        let nearest = enemies[0];
        let minDist = playerRoot.position.distanceTo(nearest.model.group.position);
        for (const e of enemies) {
          const d = playerRoot.position.distanceTo(e.model.group.position);
          if (d < minDist) {
            minDist = d;
            nearest = e;
          }
        }
        const toTarget = nearest.model.group.position.clone().sub(playerRoot.position).setY(0);
        if (toTarget.length() > 0.05) {
          playerFacingAngle = Math.atan2(toTarget.x, toTarget.z);
        }
        if (minDist > stats.range * 0.72) {
          toTarget.normalize();
          playerRoot.position.addScaledVector(toTarget, 7.6 * dt);
          isPlayerMoving = true;
        } else {
          performBasicAttack();
          if (skillCd.whirlwind <= 0) performSkill('whirlwind');
          else if (skillCd.swordWave <= 0) performSkill('wave');
        }
      }

      // Clamp Player inside Arena
      const distFromCenter = Math.hypot(playerRoot.position.x, playerRoot.position.z);
      if (distFromCenter > 25.5) {
        const scaleBack = 25.5 / distFromCenter;
        playerRoot.position.x *= scaleBack;
        playerRoot.position.z *= scaleBack;
      }

      // Smoothly rotate Player Visual Holder
      playerVisualHolder.rotation.y = playerFacingAngle;

      // Animate Sword & Wielder
      if (attackCooldownTimer > 0) attackCooldownTimer -= dt;
      if (slashArcMat.opacity > 0) {
        slashArcMat.opacity = Math.max(0, slashArcMat.opacity - dt * 4.2);
      }

      if (whirlwindTimer > 0) {
        whirlwindTimer -= dt;
        whirlwindTickTimer += dt;
        playerVisualHolder.rotation.y = elapsed * 24;
        if (activeSwordModel) {
          activeSwordModel.bladePivot.rotation.x = Math.PI * 0.46;
        }
        if (whirlwindTickTimer >= 0.22) {
          whirlwindTickTimer = 0;
          spawnShockwave(playerRoot.position, evo.slashTrailColor, stats.range * 1.25);
          for (let i = enemies.length - 1; i >= 0; i--) {
            const e = enemies[i];
            if (
              e.hp > 0 &&
              e.model.group.position.distanceTo(playerRoot.position) <= stats.range * 1.25
            ) {
              applyDamageToEnemy(e, Math.round(stats.damage * 0.75), 4.0);
            }
          }
          for (let i = enemies.length - 1; i >= 0; i--) {
            if (enemies[i].hp <= 0) enemies.splice(i, 1);
          }
        }
      } else if (attackAnimTimer > 0) {
        attackAnimTimer -= dt;
        const progress = 1 - attackAnimTimer / 0.28;
        const swingAngle = Math.sin(progress * Math.PI);
        if (activeSwordModel) {
          if (comboStep === 0) {
            activeSwordModel.bladePivot.rotation.z = -1.35 + swingAngle * 2.5;
            activeSwordModel.bladePivot.rotation.x = 0.95;
          } else if (comboStep === 1) {
            activeSwordModel.bladePivot.rotation.z = 1.35 - swingAngle * 2.5;
            activeSwordModel.bladePivot.rotation.x = 0.85;
          } else {
            activeSwordModel.bladePivot.rotation.x = -0.7 + swingAngle * 2.1;
            activeSwordModel.bladePivot.rotation.z = 0;
          }
        }
      } else if (activeSwordModel) {
        // Idle levitation or knight carry pose
        activeSwordModel.bladePivot.rotation.x = THREE.MathUtils.lerp(
          activeSwordModel.bladePivot.rotation.x,
          stateRef.current.wielderMode === 'living_sword' ? 0.22 : 0.35,
          dt * 10
        );
        activeSwordModel.bladePivot.rotation.z = THREE.MathUtils.lerp(
          activeSwordModel.bladePivot.rotation.z,
          Math.sin(elapsed * 2.8) * 0.12,
          dt * 10
        );
        if (stateRef.current.wielderMode === 'living_sword') {
          swordSwingHolder.position.y = 1.55 + Math.sin(elapsed * 3.5) * 0.18;
        }
      }

      if (activeSwordModel) {
        activeSwordModel.updateAnimation(elapsed);
      }

      if (activeKnightModel) {
        const legSwing = isPlayerMoving ? Math.sin(elapsed * 10) * 0.55 : 0;
        activeKnightModel.leftLeg.rotation.x = legSwing;
        activeKnightModel.rightLeg.rotation.x = -legSwing;
        activeKnightModel.cape.rotation.x = 0.22 + (isPlayerMoving ? 0.35 : 0) + Math.sin(elapsed * 6) * 0.08;
      }

      // Update Projectiles (Sword Wave Beams)
      for (let i = projectiles.length - 1; i >= 0; i--) {
        const p = projectiles[i];
        p.life -= dt;
        p.mesh.position.addScaledVector(p.velocity, dt);

        for (let j = enemies.length - 1; j >= 0; j--) {
          const e = enemies[j];
          if (e.hp <= 0 || p.hitEnemyIds.has(e.id)) continue;
          const dist = p.mesh.position.distanceTo(e.model.group.position);
          if (dist <= p.radius + 0.8) {
            p.hitEnemyIds.add(e.id);
            applyDamageToEnemy(e, p.damage, 6.5);
          }
        }
        for (let j = enemies.length - 1; j >= 0; j--) {
          if (enemies[j].hp <= 0) enemies.splice(j, 1);
        }

        if (p.life <= 0) {
          scene.remove(p.mesh);
          projectiles.splice(i, 1);
        }
      }

      // Update Sky Swords (Ultimate Skill)
      for (let i = skySwords.length - 1; i >= 0; i--) {
        const sk = skySwords[i];
        if (!sk.exploded) {
          sk.fallProgress += dt * 3.4;
          if (sk.fallProgress >= 0) {
            sk.mesh.position.y = THREE.MathUtils.lerp(18, 2.2, Math.min(1, sk.fallProgress));
            if (sk.fallProgress >= 1) {
              sk.exploded = true;
              spawnShockwave(sk.targetPos, evo.auraColor, 5.2);
              for (let j = enemies.length - 1; j >= 0; j--) {
                const e = enemies[j];
                if (e.hp > 0 && e.model.group.position.distanceTo(sk.targetPos) <= 5.2) {
                  applyDamageToEnemy(e, sk.damage, 7.5);
                }
              }
              for (let j = enemies.length - 1; j >= 0; j--) {
                if (enemies[j].hp <= 0) enemies.splice(j, 1);
              }
            }
          }
        } else {
          sk.lingerTimer -= dt;
          if (sk.lingerTimer <= 0) {
            scene.remove(sk.mesh);
            skySwords.splice(i, 1);
          }
        }
      }

      // Update Loot Orbs (Magnetize into the Living Sword!)
      for (let i = lootOrbs.length - 1; i >= 0; i--) {
        const orb = lootOrbs[i];
        orb.age += dt;
        orb.mesh.rotation.y += dt * 4;

        const targetPos = playerRoot.position.clone().add(new THREE.Vector3(0, 1.3, 0));
        const toPlayer = targetPos.sub(orb.mesh.position);
        const dist = toPlayer.length();

        if (orb.age < 0.25) {
          orb.velocity.y -= 12 * dt;
          orb.mesh.position.addScaledVector(orb.velocity, dt);
          if (orb.mesh.position.y < 0.4) orb.mesh.position.y = 0.4;
        } else {
          toPlayer.normalize();
          orb.mesh.position.addScaledVector(toPlayer, 18 * dt);
        }

        if (dist < 1.15 || orb.age > 5) {
          if (orb.type === 'xp') {
            gainExperience(orb.value);
          } else if (orb.type === 'gold') {
            setGold((g) => g + orb.value);
          }
          scene.remove(orb.mesh);
          lootOrbs.splice(i, 1);
        }
      }

      // Update Shockwaves
      for (let i = shockwaves.length - 1; i >= 0; i--) {
        const sw = shockwaves[i];
        sw.age += dt;
        const progress = sw.age / 0.35;
        if (progress >= 1) {
          scene.remove(sw.mesh);
          shockwaves.splice(i, 1);
        } else {
          const s = 1 + progress * sw.maxRadius;
          sw.mesh.scale.setScalar(s);
          sw.mat.opacity = 0.85 * (1 - progress);
        }
      }

      // Update Enemies AI & Animations
      for (let i = enemies.length - 1; i >= 0; i--) {
        const enemy = enemies[i];
        if (enemy.hp <= 0) continue;

        if (enemy.hitFlashTimer > 0) {
          enemy.hitFlashTimer -= dt;
          if (enemy.hitFlashTimer <= 0) {
            enemy.model.setHitFlash(false);
          }
        }

        if (enemy.bleedTimer > 0) {
          enemy.bleedTimer -= dt;
          enemy.hp -= enemy.maxHp * 0.04 * dt;
          if (enemy.hp <= 0) {
            applyDamageToEnemy(enemy, 1, 2, false);
            if (enemies[i]?.hp <= 0) enemies.splice(i, 1);
            continue;
          }
        }

        // Apply Knockback Decay
        if (enemy.knockbackVel.lengthSq() > 0.1) {
          enemy.model.group.position.addScaledVector(enemy.knockbackVel, dt);
          enemy.knockbackVel.multiplyScalar(Math.pow(0.05, dt));
        }

        const toPlayer = playerRoot.position.clone().sub(enemy.model.group.position).setY(0);
        const dist = toPlayer.length();

        if (dist > 0.05) {
          enemy.model.group.rotation.y = Math.atan2(toPlayer.x, toPlayer.z);
        }

        let isMoving = false;
        if (dist > enemy.def.attackRange) {
          toPlayer.normalize();
          enemy.model.group.position.addScaledVector(toPlayer, enemy.speed * dt);
          isMoving = true;
          enemy.attackAnimPhase = 0;
        } else {
          enemy.attackCooldownTimer -= dt;
          if (enemy.attackCooldownTimer <= 0) {
            enemy.attackCooldownTimer = enemy.def.attackCooldown;
            enemy.attackAnimPhase = 0.01;
          }
        }

        if (enemy.attackAnimPhase > 0) {
          enemy.attackAnimPhase += dt * 2.6;
          if (enemy.attackAnimPhase >= 0.5 && enemy.attackAnimPhase - dt * 2.6 < 0.5) {
            // Monster hits player if still in range & not dashing
            if (dist <= enemy.def.attackRange + 0.7 && dashTimer <= 0) {
              setPlayerHp((hp) => {
                const nextHp = hp - enemy.damage;
                if (nextHp <= 0) {
                  // Respawn with full HP at center of forge!
                  addCombatLog(
                    '¡La Forja Ancestral ha restaurado tu energía vital!',
                    'upgrade'
                  );
                  return stateRef.current.playerMaxHp;
                }
                return nextHp;
              });
              pushFloatingNumber(
                playerRoot.position.clone().add(new THREE.Vector3(0, 2.5, 0)),
                `-${enemy.damage}`,
                '#f43f5e',
                false
              );
            }
          }
          if (enemy.attackAnimPhase >= 1) {
            enemy.attackAnimPhase = 0;
          }
        }

        enemy.model.animate(elapsed, isMoving, enemy.attackAnimPhase);
      }

      // Smooth Follow Camera
      const desiredCamPos = new THREE.Vector3(
        playerRoot.position.x,
        13.2,
        playerRoot.position.z + 15.8
      );
      camera.position.lerp(desiredCamPos, dt * 6.5);
      camera.lookAt(playerRoot.position.x, 1.0, playerRoot.position.z);

      // Sync HUD Cooldowns & Enemy Health Bars ~15 times per second
      hudSyncTimer += dt;
      if (hudSyncTimer >= 0.065) {
        hudSyncTimer = 0;
        setCooldowns({ ...skillCd });

        // Clean expired floating numbers
        setFloatingNumbers((prev) => prev.filter((fn) => now - fn.createdAt < 850));

        // Project Enemy Health Bars
        const bars: EnemyScreenBar[] = enemies.map((e) => {
          const headPos = e.model.group.position
            .clone()
            .add(new THREE.Vector3(0, e.def.isBoss ? 4.4 : 2.7, 0));
          headPos.project(camera);
          const x = (headPos.x * 0.5 + 0.5) * container.clientWidth;
          const y = (-headPos.y * 0.5 + 0.5) * container.clientHeight;
          return {
            id: e.id,
            name: e.def.name,
            hp: Math.max(0, Math.round(e.hp)),
            maxHp: e.maxHp,
            isBoss: e.def.isBoss,
            x,
            y,
            visible: headPos.z < 1 && x > 0 && x < container.clientWidth && y > 0 && y < container.clientHeight,
          };
        });
        setEnemyBars(bars);
      }

      renderer.render(scene, camera);
    };

    animate();

    const handleResize = () => {
      if (!container) return;
      const w = container.clientWidth;
      const h = container.clientHeight;
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
      renderer.setSize(w, h);
    };
    window.addEventListener('resize', handleResize);

    return () => {
      cancelAnimationFrame(animationFrameId);
      window.removeEventListener('keydown', handleKeyDown);
      window.removeEventListener('keyup', handleKeyUp);
      window.removeEventListener('resize', handleResize);
      renderer.domElement.removeEventListener('mousedown', handleCanvasMouseDown);
      renderer.domElement.removeEventListener('contextmenu', handleContextMenu);
      renderer.dispose();
    };
  }, [addCombatLog, gainExperience]);

  // Forge Upgrade Purchase Handler
  const buyUpgrade = (key: keyof ForgeUpgrades, baseCost: number) => {
    const currentLvl = upgrades[key];
    const cost = Math.round(baseCost * Math.pow(1.45, currentLvl));
    if (gold < cost) return;
    setGold((g) => g - cost);
    setUpgrades((prev) => ({ ...prev, [key]: prev[key] + 1 }));
    soundEngine.playLevelUp(false);
  };

  const xpPercent = Math.min(100, Math.round((currentXp / xpRequired) * 100));
  const hpPercent = Math.min(100, Math.round((playerHp / playerMaxHp) * 100));

  return (
    <div className="relative w-screen h-screen overflow-hidden bg-slate-950 select-none font-sans text-white">
      {/* 3D WebGL Game Viewport */}
      <div ref={canvasContainerRef} className="absolute inset-0 w-full h-full cursor-crosshair" />

      {/* 3D-Projected Enemy Health Bars */}
      <div className="absolute inset-0 pointer-events-none overflow-hidden">
        {enemyBars.map(
          (bar) =>
            bar.visible && (
              <div
                key={bar.id}
                style={{
                  transform: `translate3d(${bar.x - (bar.isBoss ? 85 : 52)}px, ${bar.y}px, 0)`,
                }}
                className={`absolute top-0 left-0 flex flex-col items-center ${
                  bar.isBoss ? 'w-[170px]' : 'w-[104px]'
                }`}
              >
                <span
                  className={`text-[10px] font-black tracking-wide drop-shadow px-1.5 py-0.2 rounded ${
                    bar.isBoss
                      ? 'bg-rose-950/90 text-amber-300 border border-amber-500/40 text-xs'
                      : 'text-slate-200 bg-slate-950/70'
                  }`}
                >
                  {bar.name}
                </span>
                <div className="w-full h-2 bg-slate-950/90 rounded-full border border-slate-700 overflow-hidden mt-0.5">
                  <div
                    className={`h-full transition-all duration-100 ${
                      bar.isBoss
                        ? 'bg-gradient-to-r from-rose-600 via-orange-500 to-amber-400'
                        : 'bg-gradient-to-r from-rose-600 to-red-400'
                    }`}
                    style={{ width: `${Math.max(0, (bar.hp / bar.maxHp) * 100)}%` }}
                  />
                </div>
              </div>
            )
        )}

        {/* Floating Damage Numbers */}
        {floatingNumbers.map((fn) => (
          <div
            key={fn.id}
            style={{
              left: `${fn.screenX}px`,
              top: `${fn.screenY}px`,
              color: fn.color,
            }}
            className={`absolute font-black pointer-events-none drop-shadow-[0_2px_4px_rgba(0,0,0,0.95)] animate-bounce ${
              fn.isCrit ? 'text-2xl scale-110' : 'text-base'
            }`}
          >
            {fn.text}
          </div>
        ))}
      </div>

      {/* TOP HUD: Sword Evolution Status, XP Bar & Quick Actions */}
      <header className="relative z-10 flex flex-wrap items-center justify-between gap-3 px-4 py-3 bg-gradient-to-b from-slate-950/95 via-slate-950/80 to-transparent">
        {/* Left: Current Sword Evolution Card & Level Progress */}
        <div className="flex items-center gap-3 bg-slate-900/90 border border-amber-500/40 rounded-2xl px-4 py-2.5 shadow-xl backdrop-blur-md">
          <div
            className="w-12 h-12 rounded-xl flex items-center justify-center border border-white/20 shadow-inner shrink-0"
            style={{
              background: `radial-gradient(circle, ${currentEvolution.auraColor}33, ${currentEvolution.bladeColor})`,
            }}
          >
            <Sword className="w-7 h-7 text-white drop-shadow" />
          </div>

          <div className="min-w-[230px] sm:min-w-[290px]">
            <div className="flex items-center justify-between gap-2">
              <span className="text-[11px] font-black uppercase tracking-wider text-amber-400">
                NIVEL {swordLevel} • {currentEvolution.subtitle}
              </span>
              {currentEvolution.nextEvolutionLevel ? (
                <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-amber-500/20 text-amber-300 border border-amber-400/30">
                  Próx. Evolución: Nv. {currentEvolution.nextEvolutionLevel}
                </span>
              ) : (
                <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-cyan-500/20 text-cyan-300 border border-cyan-400/30">
                  FORMA MÁXIMA DIVINA
                </span>
              )}
            </div>

            <div className="text-base sm:text-lg font-black text-white leading-tight">
              {currentEvolution.name}
            </div>

            {/* XP Bar */}
            <div className="mt-1.5">
              <div className="flex justify-between text-[10px] text-slate-300 font-bold mb-0.5">
                <span>
                  EXP DE ALMA: {currentXp} / {xpRequired}
                </span>
                <span className="text-amber-300">{xpPercent}%</span>
              </div>
              <div className="w-full h-2.5 bg-slate-950 rounded-full overflow-hidden border border-slate-700">
                <div
                  className="h-full bg-gradient-to-r from-amber-500 via-yellow-400 to-emerald-400 transition-all duration-200"
                  style={{ width: `${xpPercent}%` }}
                />
              </div>
            </div>
          </div>
        </div>

        {/* Center: Wave, Kills, Gold & HP */}
        <div className="flex flex-wrap items-center gap-2.5 bg-slate-900/90 border border-slate-800 rounded-2xl px-4 py-2 backdrop-blur-md">
          {/* HP Bar */}
          <div className="flex items-center gap-2 pr-3 border-r border-slate-800">
            <Heart className="w-5 h-5 text-rose-500 fill-rose-500" />
            <div className="w-28">
              <div className="flex justify-between text-[10px] font-bold">
                <span className="text-rose-300">VIDA</span>
                <span>
                  {Math.round(playerHp)}/{playerMaxHp}
                </span>
              </div>
              <div className="w-full h-2 bg-slate-950 rounded-full overflow-hidden border border-slate-800">
                <div
                  className="h-full bg-gradient-to-r from-rose-600 to-emerald-500 transition-all"
                  style={{ width: `${hpPercent}%` }}
                />
              </div>
            </div>
          </div>

          <div className="flex items-center gap-1.5 px-2">
            <Coins className="w-4 h-4 text-yellow-400" />
            <div>
              <div className="text-[10px] text-slate-400 font-bold">ESENCIA / ORO</div>
              <div className="text-sm font-black text-yellow-400">{gold}</div>
            </div>
          </div>

          <div className="flex items-center gap-1.5 px-2 border-l border-slate-800">
            <Skull className="w-4 h-4 text-rose-400" />
            <div>
              <div className="text-[10px] text-slate-400 font-bold">BAJAS</div>
              <div className="text-sm font-black text-white">{kills}</div>
            </div>
          </div>

          <div className="flex items-center gap-1.5 px-2 border-l border-slate-800">
            <Flame className="w-4 h-4 text-orange-400" />
            <div>
              <div className="text-[10px] text-slate-400 font-bold">OLEADA {wave}</div>
              <div className="text-xs font-bold text-orange-300">{waveKills}/8 para avanzar</div>
            </div>
          </div>
        </div>

        {/* Right: Action Buttons (3D Armory, Auto-Hunt, Wielder Toggle, Instant Level Up Test) */}
        <div className="flex flex-wrap items-center gap-2">
          <button
            onClick={() => jumpToLevel(swordLevel + 1)}
            className="px-3 py-2 rounded-xl bg-emerald-500/20 hover:bg-emerald-500/35 border border-emerald-400/50 text-emerald-300 text-xs font-black uppercase tracking-wider transition flex items-center gap-1.5 shadow-lg"
            title="Subir +1 Nivel inmediatamente para probar evoluciones (Nv.5 Cobre, Nv.10 Hierro, etc.)"
          >
            <TrendingUp className="w-4 h-4" /> +1 Nivel
          </button>

          <button
            onClick={() => setIsModelViewerOpen(true)}
            className="px-3.5 py-2 rounded-xl bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-400 hover:to-orange-400 text-slate-950 text-xs font-black uppercase tracking-wider shadow-lg shadow-amber-500/20 transition flex items-center gap-1.5"
          >
            <Eye className="w-4 h-4" /> Museo 3D (Espadas y Monstruos)
          </button>

          <button
            onClick={() => setAutoHunt(!autoHunt)}
            className={`px-3 py-2 rounded-xl text-xs font-black uppercase tracking-wider border transition flex items-center gap-1.5 ${
              autoHunt
                ? 'bg-cyan-500 text-slate-950 border-cyan-300 shadow-lg shadow-cyan-500/25'
                : 'bg-slate-900/90 text-slate-300 border-slate-700 hover:bg-slate-800'
            }`}
          >
            <Bot className="w-4 h-4" /> {autoHunt ? 'Auto-Caza: ON' : 'Auto-Caza: OFF'}
          </button>

          <button
            onClick={() =>
              setWielderMode((m) => (m === 'living_sword' ? 'knight_wielder' : 'living_sword'))
            }
            className="px-3 py-2 rounded-xl bg-slate-900/90 hover:bg-slate-800 text-slate-200 border border-slate-700 text-xs font-bold transition flex items-center gap-1.5"
            title="Alternar entre Espada Flotante Viviente o Caballero Portador 3D"
          >
            <User className="w-4 h-4 text-amber-400" />
            {wielderMode === 'living_sword' ? 'Modo: Espada Viva' : 'Modo: Caballero 3D'}
          </button>

          <button
            onClick={() => {
              const nextMuted = !muted;
              setMuted(nextMuted);
              soundEngine.muted = nextMuted;
            }}
            className="p-2 rounded-xl bg-slate-900/90 hover:bg-slate-800 border border-slate-700 text-slate-300"
          >
            {muted ? <VolumeX className="w-4 h-4 text-rose-400" /> : <Volume2 className="w-4 h-4 text-emerald-400" />}
          </button>
        </div>
      </header>

      {/* EVOLUTION ROADMAP BAR (Shows Madera Nv.1 -> Cobre Nv.5 -> Hierro Nv.10 -> ... clickable!) */}
      <div className="relative z-10 px-4 mt-1 flex items-center gap-1.5 overflow-x-auto pb-1 no-scrollbar">
        {SWORD_EVOLUTIONS.map((tier, idx) => {
          const isCurrent = currentEvolution.id === tier.id;
          const isUnlocked = swordLevel >= tier.minLevel;
          return (
            <React.Fragment key={tier.id}>
              <button
                onClick={() => jumpToLevel(tier.minLevel)}
                className={`px-2.5 py-1 rounded-lg text-[11px] font-bold whitespace-nowrap transition flex items-center gap-1.5 border ${
                  isCurrent
                    ? 'bg-amber-500 text-slate-950 border-amber-300 shadow-md shadow-amber-500/30 scale-105'
                    : isUnlocked
                    ? 'bg-slate-900/90 text-emerald-300 border-emerald-500/40 hover:bg-slate-800'
                    : 'bg-slate-950/80 text-slate-400 border-slate-800 hover:border-slate-700'
                }`}
                title={`Haz clic para equipar/probar ${tier.name} (Nivel ${tier.minLevel})`}
              >
                <span
                  className="w-2.5 h-2.5 rounded-full"
                  style={{ backgroundColor: tier.bladeColor }}
                />
                <span>
                  Nv.{tier.minLevel} {tier.name.replace('Espada de ', '').replace('Mandoble de ', '').replace('Hoja de ', '').replace('Claymore de ', '').replace('Devoradora de ', '').replace('Excalibur ', '')}
                </span>
              </button>
              {idx < SWORD_EVOLUTIONS.length - 1 && (
                <ChevronRight className="w-3.5 h-3.5 text-slate-600 shrink-0" />
              )}
            </React.Fragment>
          );
        })}
      </div>

      {/* DRAMATIC EVOLUTION METAMORPHOSIS BANNER */}
      {evolutionBanner && (
        <div className="fixed inset-x-0 top-28 z-40 flex justify-center pointer-events-none px-4 animate-bounce">
          <div className="pointer-events-auto max-w-xl w-full bg-gradient-to-r from-amber-950/95 via-slate-900/95 to-amber-950/95 border-2 border-amber-400 rounded-2xl p-4 shadow-2xl shadow-amber-500/30 flex items-center gap-4">
            <div
              className="w-14 h-14 rounded-2xl flex items-center justify-center shrink-0 border border-white/30"
              style={{ backgroundColor: evolutionBanner.bladeColor }}
            >
              <Sparkles className="w-8 h-8 text-white animate-spin" />
            </div>
            <div className="flex-1">
              <div className="text-xs font-black uppercase tracking-widest text-amber-300">
                ¡METAMORFOSIS DE ESPADA COMPLETADA!
              </div>
              <div className="text-xl font-black text-white">{evolutionBanner.name}</div>
              <div className="text-xs text-slate-300 mt-0.5">
                Nuevo Poder Pasivo: <b className="text-amber-300">{evolutionBanner.passiveName}</b> —{' '}
                {evolutionBanner.passiveDescription}
              </div>
            </div>
          </div>
        </div>
      )}

      {/* LEFT PANEL: Live Sword Stats & Combat Log */}
      <aside className="hidden md:flex fixed left-4 bottom-24 z-10 w-72 flex-col gap-2.5 pointer-events-none">
        <div className="bg-slate-950/85 border border-slate-800/90 rounded-2xl p-3.5 backdrop-blur-md pointer-events-auto">
          <div className="text-xs font-black uppercase tracking-wider text-amber-400 flex items-center gap-1.5 mb-2">
            <Award className="w-4 h-4" /> Atributos de la Espada
          </div>
          <div className="grid grid-cols-2 gap-2 text-xs">
            <div className="bg-slate-900/90 p-2 rounded-lg border border-slate-800">
              <span className="text-slate-400 block text-[10px]">DAÑO DE CORTE</span>
              <span className="font-black text-amber-400 text-sm">{computedStats.damage}</span>
            </div>
            <div className="bg-slate-900/90 p-2 rounded-lg border border-slate-800">
              <span className="text-slate-400 block text-[10px]">VEL. ATAQUE</span>
              <span className="font-black text-cyan-400 text-sm">{computedStats.attackSpeed}x</span>
            </div>
            <div className="bg-slate-900/90 p-2 rounded-lg border border-slate-800">
              <span className="text-slate-400 block text-[10px]">CRÍTICO</span>
              <span className="font-black text-rose-400 text-sm">
                {Math.round(computedStats.critChance * 100)}% ({computedStats.critDamageMult.toFixed(1)}x)
              </span>
            </div>
            <div className="bg-slate-900/90 p-2 rounded-lg border border-slate-800">
              <span className="text-slate-400 block text-[10px]">ALCANCE HOJA</span>
              <span className="font-black text-emerald-400 text-sm">{computedStats.range}m</span>
            </div>
          </div>
          <div className="mt-2 pt-2 border-t border-slate-800/80 text-[11px] text-slate-300">
            <span className="text-amber-300 font-bold">{currentEvolution.passiveName}:</span>{' '}
            {currentEvolution.passiveDescription}
          </div>
        </div>

        {/* Combat Log */}
        <div className="bg-slate-950/80 border border-slate-800/80 rounded-2xl p-3 backdrop-blur-md max-h-40 overflow-y-auto space-y-1.5">
          <div className="text-[10px] font-black uppercase tracking-wider text-slate-400">
            Crónicas de la Forja
          </div>
          {combatLog.map((entry) => (
            <div
              key={entry.id}
              className={`text-[11px] leading-snug ${
                entry.type === 'evolution'
                  ? 'text-amber-300 font-bold'
                  : entry.type === 'boss'
                  ? 'text-rose-400 font-bold'
                  : entry.type === 'levelup'
                  ? 'text-emerald-300 font-medium'
                  : 'text-slate-300'
              }`}
            >
              • {entry.text}
            </div>
          ))}
        </div>
      </aside>

      {/* RIGHT PANEL: La Forja de Almas (Upgrades) */}
      <aside className="fixed right-4 bottom-24 z-10 w-72 md:w-80">
        <div className="bg-slate-950/90 border border-amber-500/30 rounded-2xl overflow-hidden shadow-2xl backdrop-blur-md">
          <button
            onClick={() => setIsForgeDrawerOpen(!isForgeDrawerOpen)}
            className="w-full px-4 py-2.5 bg-gradient-to-r from-amber-500/20 to-slate-900 flex items-center justify-between text-xs font-black uppercase tracking-wider text-amber-300 border-b border-slate-800"
          >
            <span className="flex items-center gap-2">
              <Hammer className="w-4 h-4" /> Forja de Mejoras ({gold} Oro)
            </span>
            <span>{isForgeDrawerOpen ? '▼' : '▲'}</span>
          </button>

          {isForgeDrawerOpen && (
            <div className="p-3 space-y-2 max-h-[42vh] overflow-y-auto">
              {[
                {
                  key: 'sharpness' as const,
                  name: 'Afilar Hoja Letal',
                  desc: '+18% Daño total de la espada',
                  baseCost: 25,
                },
                {
                  key: 'swiftness' as const,
                  name: 'Equilibrio Ligero',
                  desc: '+8% Velocidad de corte',
                  baseCost: 30,
                },
                {
                  key: 'criticalMastery' as const,
                  name: 'Templado Crítico',
                  desc: '+4% Prob. Crítico y +15% Daño Crít.',
                  baseCost: 35,
                },
                {
                  key: 'vampirism' as const,
                  name: 'Runa Devoradora',
                  desc: '+3 Vida restaurada por cada golpe',
                  baseCost: 40,
                },
                {
                  key: 'soulMagnet' as const,
                  name: 'Núcleo de Almas',
                  desc: '+15% EXP y Oro para evolucionar rápido',
                  baseCost: 30,
                },
                {
                  key: 'bladeSize' as const,
                  name: 'Forja Colosal',
                  desc: '+6% Tamaño 3D y Alcance de la Espada',
                  baseCost: 45,
                },
              ].map((upg) => {
                const lvl = upgrades[upg.key];
                const cost = Math.round(upg.baseCost * Math.pow(1.45, lvl));
                const canAfford = gold >= cost;
                return (
                  <div
                    key={upg.key}
                    className="flex items-center justify-between gap-2 p-2 rounded-xl bg-slate-900/90 border border-slate-800"
                  >
                    <div>
                      <div className="text-xs font-bold text-white">
                        {upg.name} <span className="text-amber-400">Nv.{lvl}</span>
                      </div>
                      <div className="text-[10px] text-slate-400">{upg.desc}</div>
                    </div>
                    <button
                      onClick={() => buyUpgrade(upg.key, upg.baseCost)}
                      disabled={!canAfford}
                      className={`px-2.5 py-1.5 rounded-lg text-xs font-black transition shrink-0 ${
                        canAfford
                          ? 'bg-amber-500 hover:bg-amber-400 text-slate-950'
                          : 'bg-slate-800 text-slate-500 cursor-not-allowed'
                      }`}
                    >
                      {cost} Oro
                    </button>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </aside>

      {/* BOTTOM ACTION BAR: Combat Skills & Controls Guide */}
      <footer className="fixed inset-x-0 bottom-3 z-10 flex flex-col items-center pointer-events-none px-4">
        <div className="flex items-center gap-2.5 bg-slate-950/90 border border-slate-700/80 rounded-2xl p-2 shadow-2xl backdrop-blur-md pointer-events-auto">
          {/* Basic Slash */}
          <button
            onClick={() => triggerAttackRef.current()}
            className="group relative flex flex-col items-center justify-center w-20 h-16 rounded-xl bg-gradient-to-b from-amber-500/25 to-slate-900 border border-amber-400/50 hover:border-amber-300 active:scale-95 transition"
          >
            <Sword className="w-6 h-6 text-amber-300" />
            <span className="text-[10px] font-black text-white mt-1">TAJO COMBO</span>
            <span className="absolute top-1 right-1.5 text-[9px] font-bold text-amber-300">
              Click / Esp
            </span>
          </button>

          {/* Q: Whirlwind */}
          <button
            onClick={() => triggerSkillRef.current('whirlwind')}
            className="relative flex flex-col items-center justify-center w-20 h-16 rounded-xl bg-slate-900 border border-slate-700 hover:border-cyan-400 active:scale-95 transition overflow-hidden"
          >
            <Zap className="w-6 h-6 text-cyan-400" />
            <span className="text-[10px] font-black text-white mt-1">TORBELLINO</span>
            <span className="absolute top-1 right-1.5 text-[9px] font-bold text-cyan-300">[Q]</span>
            {cooldowns.whirlwind > 0 && (
              <div className="absolute inset-0 bg-slate-950/85 flex items-center justify-center text-xs font-black text-cyan-300">
                {cooldowns.whirlwind.toFixed(1)}s
              </div>
            )}
          </button>

          {/* E: Sword Wave */}
          <button
            onClick={() => triggerSkillRef.current('wave')}
            className="relative flex flex-col items-center justify-center w-20 h-16 rounded-xl bg-slate-900 border border-slate-700 hover:border-purple-400 active:scale-95 transition overflow-hidden"
          >
            <Sparkles className="w-6 h-6 text-purple-400" />
            <span className="text-[10px] font-black text-white mt-1">ONDA HOJA</span>
            <span className="absolute top-1 right-1.5 text-[9px] font-bold text-purple-300">[E]</span>
            {cooldowns.swordWave > 0 && (
              <div className="absolute inset-0 bg-slate-950/85 flex items-center justify-center text-xs font-black text-purple-300">
                {cooldowns.swordWave.toFixed(1)}s
              </div>
            )}
          </button>

          {/* R: Ultimate Sky Swords */}
          <button
            onClick={() => triggerSkillRef.current('ultimate')}
            className="relative flex flex-col items-center justify-center w-24 h-16 rounded-xl bg-gradient-to-b from-rose-500/25 to-slate-900 border border-rose-500/50 hover:border-rose-400 active:scale-95 transition overflow-hidden"
          >
            <Flame className="w-6 h-6 text-rose-400" />
            <span className="text-[10px] font-black text-white mt-1">LLUVIA ESPADAS</span>
            <span className="absolute top-1 right-1.5 text-[9px] font-bold text-rose-300">[R]</span>
            {cooldowns.ultimate > 0 && (
              <div className="absolute inset-0 bg-slate-950/85 flex items-center justify-center text-xs font-black text-rose-300">
                {cooldowns.ultimate.toFixed(1)}s
              </div>
            )}
          </button>

          {/* Shift: Dash */}
          <button
            onClick={() => triggerSkillRef.current('dash')}
            className="relative flex flex-col items-center justify-center w-20 h-16 rounded-xl bg-slate-900 border border-slate-700 hover:border-emerald-400 active:scale-95 transition overflow-hidden"
          >
            <Shield className="w-6 h-6 text-emerald-400" />
            <span className="text-[10px] font-black text-white mt-1">IMPULSO</span>
            <span className="absolute top-1 right-1.5 text-[9px] font-bold text-emerald-300">
              Shift
            </span>
            {cooldowns.dash > 0 && (
              <div className="absolute inset-0 bg-slate-950/85 flex items-center justify-center text-xs font-black text-emerald-300">
                {cooldowns.dash.toFixed(1)}s
              </div>
            )}
          </button>
        </div>

        <div className="mt-1 text-[11px] text-slate-400 bg-slate-950/80 px-3 py-0.5 rounded-full border border-slate-800">
          Mover: <b>WASD / Flechas</b> • Atacar: <b>Click Izq / Espacio</b> • Habilidades: <b>Q, E, R, Shift</b> • Evoluciona al <b>Nv. 5 (Cobre)</b>, <b>Nv. 10 (Hierro)</b>, <b>Nv. 15 (Plata)</b>...
        </div>
      </footer>

      {/* 3D ARMORY & BESTIARY VIEWER MODAL */}
      <ModelViewerModal
        isOpen={isModelViewerOpen}
        onClose={() => setIsModelViewerOpen(false)}
        currentSwordLevel={swordLevel}
        onSelectLevelForTesting={(lvl) => jumpToLevel(lvl)}
      />
    </div>
  );
}
export default App;
