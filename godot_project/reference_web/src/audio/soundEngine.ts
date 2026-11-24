import { SwordTierId } from '../types/game';

class SoundEngine {
  private ctx: AudioContext | null = null;
  public muted = false;

  private getContext(): AudioContext | null {
    if (this.muted) return null;
    if (!this.ctx && typeof window !== 'undefined') {
      const AudioCtx = window.AudioContext || (window as unknown as { webkitAudioContext: typeof AudioContext }).webkitAudioContext;
      if (AudioCtx) {
        this.ctx = new AudioCtx();
      }
    }
    if (this.ctx && this.ctx.state === 'suspended') {
      this.ctx.resume().catch(() => {});
    }
    return this.ctx;
  }

  public playSlash(tier: SwordTierId, comboStep = 0) {
    const ctx = this.getContext();
    if (!ctx) return;

    const now = ctx.currentTime;
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();

    // Wooden sword sounds deeper/hollow, metallic/crystal swords have a higher resonant ring
    const baseFreq = tier === 'wood' ? 160 : tier === 'copper' ? 260 : 340;
    const pitchBoost = comboStep * 45;

    osc.type = tier === 'wood' ? 'triangle' : 'sawtooth';
    osc.frequency.setValueAtTime(baseFreq + pitchBoost, now);
    osc.frequency.exponentialRampToValueAtTime(65, now + 0.16);

    gain.gain.setValueAtTime(0.16, now);
    gain.gain.exponentialRampToValueAtTime(0.001, now + 0.17);

    osc.connect(gain);
    gain.connect(ctx.destination);
    osc.start(now);
    osc.stop(now + 0.18);
  }

  public playHit(tier: SwordTierId, isCrit: boolean) {
    const ctx = this.getContext();
    if (!ctx) return;

    const now = ctx.currentTime;
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();

    if (tier === 'wood') {
      // Wooden thwack
      osc.type = 'square';
      osc.frequency.setValueAtTime(isCrit ? 220 : 145, now);
      osc.frequency.exponentialRampToValueAtTime(48, now + 0.11);
    } else {
      // Metallic / Arcane ring
      osc.type = isCrit ? 'sawtooth' : 'triangle';
      osc.frequency.setValueAtTime(isCrit ? 620 : 410, now);
      osc.frequency.exponentialRampToValueAtTime(110, now + 0.15);
    }

    gain.gain.setValueAtTime(isCrit ? 0.24 : 0.15, now);
    gain.gain.exponentialRampToValueAtTime(0.001, now + 0.16);

    osc.connect(gain);
    gain.connect(ctx.destination);
    osc.start(now);
    osc.stop(now + 0.17);
  }

  public playSkill(type: 'whirlwind' | 'wave' | 'ultimate' | 'dash') {
    const ctx = this.getContext();
    if (!ctx) return;

    const now = ctx.currentTime;
    const osc = ctx.createOscillator();
    const gain = ctx.createGain();

    if (type === 'whirlwind') {
      osc.type = 'sawtooth';
      osc.frequency.setValueAtTime(190, now);
      osc.frequency.linearRampToValueAtTime(460, now + 0.22);
      osc.frequency.linearRampToValueAtTime(150, now + 0.42);
      gain.gain.setValueAtTime(0.2, now);
      gain.gain.exponentialRampToValueAtTime(0.001, now + 0.44);
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.start(now);
      osc.stop(now + 0.45);
    } else if (type === 'wave') {
      osc.type = 'sine';
      osc.frequency.setValueAtTime(520, now);
      osc.frequency.exponentialRampToValueAtTime(180, now + 0.32);
      gain.gain.setValueAtTime(0.22, now);
      gain.gain.exponentialRampToValueAtTime(0.001, now + 0.34);
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.start(now);
      osc.stop(now + 0.35);
    } else if (type === 'ultimate') {
      [220, 330, 440, 660].forEach((freq, idx) => {
        const o = ctx.createOscillator();
        const g = ctx.createGain();
        o.type = 'triangle';
        o.frequency.setValueAtTime(freq, now + idx * 0.06);
        o.frequency.exponentialRampToValueAtTime(freq * 1.5, now + idx * 0.06 + 0.35);
        g.gain.setValueAtTime(0.15, now + idx * 0.06);
        g.gain.exponentialRampToValueAtTime(0.001, now + idx * 0.06 + 0.38);
        o.connect(g);
        g.connect(ctx.destination);
        o.start(now + idx * 0.06);
        o.stop(now + idx * 0.06 + 0.4);
      });
    } else {
      osc.type = 'triangle';
      osc.frequency.setValueAtTime(310, now);
      osc.frequency.exponentialRampToValueAtTime(90, now + 0.14);
      gain.gain.setValueAtTime(0.14, now);
      gain.gain.exponentialRampToValueAtTime(0.001, now + 0.15);
      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.start(now);
      osc.stop(now + 0.16);
    }
  }

  public playLevelUp(isEvolution: boolean) {
    const ctx = this.getContext();
    if (!ctx) return;

    const now = ctx.currentTime;
    const notes = isEvolution
      ? [261.63, 329.63, 392.0, 523.25, 659.25, 783.99, 1046.5]
      : [329.63, 440.0, 554.37, 659.25];

    notes.forEach((freq, idx) => {
      const osc = ctx.createOscillator();
      const gain = ctx.createGain();
      osc.type = isEvolution ? 'sawtooth' : 'triangle';
      const startTime = now + idx * (isEvolution ? 0.08 : 0.06);
      const duration = isEvolution ? 0.38 : 0.22;

      osc.frequency.setValueAtTime(freq, startTime);
      gain.gain.setValueAtTime(isEvolution ? 0.18 : 0.14, startTime);
      gain.gain.exponentialRampToValueAtTime(0.001, startTime + duration);

      osc.connect(gain);
      gain.connect(ctx.destination);
      osc.start(startTime);
      osc.stop(startTime + duration + 0.02);
    });
  }
}

export const soundEngine = new SoundEngine();
