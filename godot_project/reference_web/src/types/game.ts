export type SwordTierId =
  | 'wood'
  | 'copper'
  | 'iron'
  | 'silver'
  | 'gold'
  | 'crystal'
  | 'obsidian'
  | 'celestial';

export interface SwordEvolutionTier {
  id: SwordTierId;
  tierIndex: number;
  minLevel: number;
  nextEvolutionLevel: number | null;
  name: string;
  subtitle: string;
  materialName: string;
  description: string;
  passiveName: string;
  passiveDescription: string;
  baseDamage: number;
  attackSpeed: number;
  range: number;
  critChance: number;
  bladeColor: string;
  edgeColor: string;
  guardColor: string;
  gripColor: string;
  gemColor: string;
  auraColor: string;
  slashTrailColor: string;
  specialEffect: 'none' | 'sparks' | 'bleed' | 'lightning' | 'solar_burn' | 'arcane_shards' | 'lifesteal_magma' | 'cosmic_nova';
  modelStats: {
    partsCount: number;
    triangles: number;
    lengthMeters: number;
    weightKg: number;
  };
}

export type MonsterSpeciesId =
  | 'slime'
  | 'goblin'
  | 'skeleton'
  | 'copper_golem'
  | 'orc_berserker'
  | 'crimson_drake'
  | 'demon_lord';

export interface MonsterDefinition {
  id: MonsterSpeciesId;
  name: string;
  title: string;
  minWave: number;
  isBoss: boolean;
  baseHp: number;
  baseDamage: number;
  speed: number;
  attackRange: number;
  attackCooldown: number;
  xpReward: number;
  goldReward: number;
  scale: number;
  primaryColor: string;
  accentColor: string;
  description: string;
}

export interface ForgeUpgrades {
  sharpness: number;     // +Damage %
  swiftness: number;     // +Attack Speed & Cooldown Reduction
  vampirism: number;     // HP regen on hit / kill
  criticalMastery: number; // +Crit chance & crit damage
  soulMagnet: number;    // +XP & Gold gain %
  bladeSize: number;     // +Sword physical scale & reach
}

export type WielderMode = 'living_sword' | 'knight_wielder';

export interface CombatLogEntry {
  id: string;
  text: string;
  type: 'evolution' | 'levelup' | 'boss' | 'kill' | 'upgrade';
  timestamp: number;
}

export interface ActiveSkillCooldowns {
  whirlwind: number; // Q / Right Click (max 4s)
  swordWave: number; // E (max 5s)
  ultimate: number;  // R (max 12s)
  dash: number;      // Shift (max 2s)
}
