import React, { useEffect, useRef, useState } from 'react';
import * as THREE from 'three';
import {
  Download,
  Eye,
  Flame,
  Layers,
  Play,
  RotateCcw,
  ShieldAlert,
  Sparkles,
  Sword,
  X,
} from 'lucide-react';
import { MONSTER_DEFINITIONS, SWORD_EVOLUTIONS } from '../data/evolutions';
import { buildSword3DModel } from '../models/swordModels';
import { buildMonster3DModel } from '../models/monsterModels';
import { exportModelToOBJ } from '../models/customGeometry';
import { MonsterSpeciesId, SwordTierId } from '../types/game';

interface ModelViewerModalProps {
  isOpen: boolean;
  onClose: () => void;
  currentSwordLevel: number;
  onSelectLevelForTesting: (targetLevel: number) => void;
}

export const ModelViewerModal: React.FC<ModelViewerModalProps> = ({
  isOpen,
  onClose,
  currentSwordLevel,
  onSelectLevelForTesting,
}) => {
  const [tab, setTab] = useState<'swords' | 'monsters'>('swords');
  const [selectedSwordId, setSelectedSwordId] = useState<SwordTierId>('wood');
  const [selectedMonsterId, setSelectedMonsterId] = useState<MonsterSpeciesId>('slime');
  const [wireframe, setWireframe] = useState(false);
  const [testAttackAnim, setTestAttackAnim] = useState(false);
  const [meshSummary, setMeshSummary] = useState({ vertices: 0, triangles: 0, parts: 0 });

  const mountRef = useRef<HTMLDivElement | null>(null);
  const currentGroupRef = useRef<THREE.Group | null>(null);
  const dragRef = useRef({ isDown: false, lastX: 0, rotY: 0.5, rotX: 0.15 });

  const selectedSword =
    SWORD_EVOLUTIONS.find((s) => s.id === selectedSwordId) || SWORD_EVOLUTIONS[0];
  const selectedMonster =
    MONSTER_DEFINITIONS.find((m) => m.id === selectedMonsterId) || MONSTER_DEFINITIONS[0];

  useEffect(() => {
    if (!isOpen || !mountRef.current) return;

    const container = mountRef.current;
    const width = container.clientWidth || 540;
    const height = container.clientHeight || 420;

    const scene = new THREE.Scene();
    scene.background = new THREE.Color(0x0b0f19);

    const camera = new THREE.PerspectiveCamera(42, width / height, 0.1, 100);
    camera.position.set(0, 1.35, 4.5);
    camera.lookAt(0, 0.95, 0);

    const renderer = new THREE.WebGLRenderer({ antialias: true });
    renderer.setSize(width, height);
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.shadowMap.enabled = true;
    container.innerHTML = '';
    container.appendChild(renderer.domElement);

    // Lighting
    const ambient = new THREE.AmbientLight(0xffffff, 0.85);
    scene.add(ambient);

    const keyLight = new THREE.DirectionalLight(0xfff7ed, 2.2);
    keyLight.position.set(4, 7, 5);
    scene.add(keyLight);

    const rimLight = new THREE.PointLight(0x38bdf8, 2.5, 14);
    rimLight.position.set(-3.5, 2.5, -3);
    scene.add(rimLight);

    // Turntable Pedestal
    const pedestalGeo = new THREE.CylinderGeometry(1.35, 1.55, 0.22, 32);
    const pedestalMat = new THREE.MeshStandardMaterial({
      color: 0x1e293b,
      roughness: 0.4,
      metalness: 0.7,
    });
    const pedestal = new THREE.Mesh(pedestalGeo, pedestalMat);
    pedestal.position.y = -0.25;
    scene.add(pedestal);

    const ringGeo = new THREE.RingGeometry(1.18, 1.25, 48);
    const ringMat = new THREE.MeshBasicMaterial({
      color: tab === 'swords' ? selectedSword.auraColor : selectedMonster.accentColor,
      side: THREE.DoubleSide,
    });
    const ring = new THREE.Mesh(ringGeo, ringMat);
    ring.rotation.x = -Math.PI / 2;
    ring.position.y = -0.13;
    scene.add(ring);

    const pivot = new THREE.Group();
    scene.add(pivot);

    let swordInstance: ReturnType<typeof buildSword3DModel> | null = null;
    let monsterInstance: ReturnType<typeof buildMonster3DModel> | null = null;

    if (tab === 'swords') {
      swordInstance = buildSword3DModel(selectedSwordId, selectedSword.minLevel + 2);
      swordInstance.group.position.set(0, 0.55, 0);
      swordInstance.group.scale.setScalar(0.72);
      pivot.add(swordInstance.group);
      currentGroupRef.current = swordInstance.group;
    } else {
      monsterInstance = buildMonster3DModel(selectedMonsterId);
      const scale = selectedMonster.isBoss ? 0.68 : 0.85;
      monsterInstance.group.scale.setScalar(scale);
      monsterInstance.group.position.set(0, -0.14, 0);
      pivot.add(monsterInstance.group);
      currentGroupRef.current = monsterInstance.group;
    }

    // Count actual vertices, triangles, and mesh parts
    let verts = 0;
    let tris = 0;
    let parts = 0;
    pivot.traverse((child) => {
      if (child instanceof THREE.Mesh) {
        parts++;
        const pos = child.geometry.getAttribute('position');
        if (pos) {
          verts += pos.count;
          const idx = child.geometry.getIndex();
          tris += idx ? idx.count / 3 : Math.floor(pos.count / 3);
        }
        if (child.material instanceof THREE.MeshStandardMaterial) {
          child.material.wireframe = wireframe;
        }
      }
    });
    setMeshSummary({ vertices: verts, triangles: Math.round(tris), parts });

    let frameId = 0;
    const startTime = performance.now();

    const animate = () => {
      frameId = requestAnimationFrame(animate);
      const elapsed = (performance.now() - startTime) * 0.001;

      if (!dragRef.current.isDown) {
        dragRef.current.rotY += 0.008;
      }
      pivot.rotation.y = dragRef.current.rotY;
      pivot.rotation.x = dragRef.current.rotX;

      if (swordInstance) {
        swordInstance.updateAnimation(elapsed);
        if (testAttackAnim) {
          swordInstance.bladePivot.rotation.z = Math.sin(elapsed * 8) * 0.85;
        } else {
          swordInstance.bladePivot.rotation.z = 0.22;
        }
      }

      if (monsterInstance) {
        const atk = testAttackAnim ? (elapsed * 1.8) % 1 : 0;
        monsterInstance.animate(elapsed, true, atk);
      }

      renderer.render(scene, camera);
    };
    animate();

    const handleResize = () => {
      if (!mountRef.current) return;
      const w = mountRef.current.clientWidth;
      const h = mountRef.current.clientHeight;
      camera.aspect = w / h;
      camera.updateProjectionMatrix();
      renderer.setSize(w, h);
    };
    window.addEventListener('resize', handleResize);

    return () => {
      cancelAnimationFrame(frameId);
      window.removeEventListener('resize', handleResize);
      renderer.dispose();
    };
  }, [isOpen, tab, selectedSwordId, selectedMonsterId, wireframe, testAttackAnim, selectedSword, selectedMonster]);

  if (!isOpen) return null;

  const handleDownloadOBJ = () => {
    if (!currentGroupRef.current) return;
    const name = tab === 'swords' ? selectedSword.name : selectedMonster.name;
    const objContent = exportModelToOBJ(currentGroupRef.current, name);
    const blob = new Blob([objContent], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${name.toLowerCase().replace(/\s+/g, '_')}.obj`;
    a.click();
    URL.revokeObjectURL(url);
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-md p-3 md:p-6">
      <div className="relative w-full max-w-6xl bg-slate-950 border border-amber-500/40 rounded-2xl shadow-2xl overflow-hidden flex flex-col max-h-[92vh]">
        {/* Header */}
        <div className="flex flex-wrap items-center justify-between gap-3 px-6 py-4 bg-gradient-to-r from-slate-900 via-slate-900 to-amber-950/40 border-b border-slate-800">
          <div className="flex items-center gap-3">
            <div className="p-2.5 rounded-xl bg-amber-500/20 border border-amber-400/40 text-amber-300">
              <Sword className="w-6 h-6" />
            </div>
            <div>
              <h2 className="text-lg md:text-xl font-black tracking-wide text-white uppercase">
                Armería 3D y Bestiario • Modelos Esculpidos a Mano
              </h2>
              <p className="text-xs text-slate-400">
                Inspecciona en 360° cada evolución de la espada (Madera → Cobre Nv.5 → Hierro Nv.10 → Celestial Nv.35) y todos los monstruos 3D
              </p>
            </div>
          </div>

          <div className="flex items-center gap-2">
            <button
              onClick={() => setTab('swords')}
              className={`px-4 py-2 rounded-lg text-xs font-bold uppercase tracking-wider transition flex items-center gap-1.5 ${
                tab === 'swords'
                  ? 'bg-amber-500 text-slate-950 shadow-lg shadow-amber-500/30'
                  : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
              }`}
            >
              <Sword className="w-4 h-4" />8 Espadas Evolutivas
            </button>
            <button
              onClick={() => setTab('monsters')}
              className={`px-4 py-2 rounded-lg text-xs font-bold uppercase tracking-wider transition flex items-center gap-1.5 ${
                tab === 'monsters'
                  ? 'bg-rose-500 text-white shadow-lg shadow-rose-500/30'
                  : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
              }`}
            >
              <ShieldAlert className="w-4 h-4" />7 Monstruos 3D
            </button>
            <button
              onClick={onClose}
              className="p-2 rounded-lg bg-slate-800 hover:bg-rose-600 text-slate-300 hover:text-white transition"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {/* Main Content Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-12 flex-1 overflow-y-auto">
          {/* Left Selector List */}
          <div className="lg:col-span-4 border-r border-slate-800 bg-slate-900/60 p-4 overflow-y-auto max-h-[38vh] lg:max-h-none space-y-2">
            {tab === 'swords' ? (
              <>
                <div className="text-xs font-bold uppercase tracking-wider text-amber-400 mb-2 px-1">
                  Árbol de Evolución de la Espada
                </div>
                {SWORD_EVOLUTIONS.map((tier) => {
                  const isUnlocked = currentSwordLevel >= tier.minLevel;
                  const isSelected = selectedSwordId === tier.id;
                  return (
                    <button
                      key={tier.id}
                      onClick={() => setSelectedSwordId(tier.id)}
                      className={`w-full text-left p-3 rounded-xl border transition flex items-center justify-between ${
                        isSelected
                          ? 'bg-amber-500/15 border-amber-400 text-white shadow-md'
                          : 'bg-slate-900/90 border-slate-800 text-slate-300 hover:border-slate-700'
                      }`}
                    >
                      <div className="flex items-center gap-3">
                        <span
                          className="w-4 h-10 rounded-full border border-white/20 shrink-0"
                          style={{
                            background: `linear-gradient(to bottom, ${tier.edgeColor}, ${tier.bladeColor})`,
                          }}
                        />
                        <div>
                          <div className="text-xs font-bold text-amber-300">
                            Nivel {tier.minLevel}+ • Fase {tier.tierIndex + 1}
                          </div>
                          <div className="font-bold text-sm text-white">{tier.name}</div>
                        </div>
                      </div>
                      <span
                        className={`text-[10px] px-2 py-0.5 rounded-full font-bold ${
                          isUnlocked
                            ? 'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                            : 'bg-slate-800 text-slate-400'
                        }`}
                      >
                        {isUnlocked ? 'ACTIVA' : `NV. ${tier.minLevel}`}
                      </span>
                    </button>
                  );
                })}
              </>
            ) : (
              <>
                <div className="text-xs font-bold uppercase tracking-wider text-rose-400 mb-2 px-1">
                  Bestiario 3D de la Arena
                </div>
                {MONSTER_DEFINITIONS.map((monster) => {
                  const isSelected = selectedMonsterId === monster.id;
                  return (
                    <button
                      key={monster.id}
                      onClick={() => setSelectedMonsterId(monster.id)}
                      className={`w-full text-left p-3 rounded-xl border transition flex items-center justify-between ${
                        isSelected
                          ? 'bg-rose-500/15 border-rose-400 text-white shadow-md'
                          : 'bg-slate-900/90 border-slate-800 text-slate-300 hover:border-slate-700'
                      }`}
                    >
                      <div className="flex items-center gap-3">
                        <span
                          className="w-4 h-10 rounded-full border border-white/20 shrink-0"
                          style={{
                            background: `linear-gradient(to bottom, ${monster.primaryColor}, ${monster.accentColor})`,
                          }}
                        />
                        <div>
                          <div className="text-xs font-bold text-rose-300">{monster.title}</div>
                          <div className="font-bold text-sm text-white">{monster.name}</div>
                        </div>
                      </div>
                      {monster.isBoss && (
                        <span className="text-[10px] px-2 py-0.5 rounded-full font-bold bg-rose-600 text-white">
                          JEFE
                        </span>
                      )}
                    </button>
                  );
                })}
              </>
            )}
          </div>

          {/* Center 3D Interactive Viewport */}
          <div className="lg:col-span-5 relative bg-slate-950 flex flex-col min-h-[340px]">
            <div
              ref={mountRef}
              onMouseDown={(e) => {
                dragRef.current.isDown = true;
                dragRef.current.lastX = e.clientX;
              }}
              onMouseMove={(e) => {
                if (!dragRef.current.isDown) return;
                const dx = e.clientX - dragRef.current.lastX;
                dragRef.current.lastX = e.clientX;
                dragRef.current.rotY += dx * 0.012;
              }}
              onMouseUp={() => {
                dragRef.current.isDown = false;
              }}
              onMouseLeave={() => {
                dragRef.current.isDown = false;
              }}
              className="w-full flex-1 cursor-grab active:cursor-grabbing min-h-[340px]"
            />

            {/* Viewport Controls Overlay */}
            <div className="absolute top-3 left-3 right-3 flex flex-wrap items-center justify-between gap-2 pointer-events-none">
              <div className="px-3 py-1.5 rounded-lg bg-slate-900/85 border border-slate-700 text-xs text-slate-200 flex items-center gap-2">
                <Layers className="w-3.5 h-3.5 text-amber-400" />
                <span>
                  Piezas 3D: <b>{meshSummary.parts}</b> • Vértices: <b>{meshSummary.vertices}</b> • Triángulos:{' '}
                  <b>{meshSummary.triangles}</b>
                </span>
              </div>

              <div className="flex items-center gap-1.5 pointer-events-auto">
                <button
                  onClick={() => setWireframe(!wireframe)}
                  className={`px-2.5 py-1.5 rounded-lg text-xs font-bold border transition flex items-center gap-1 ${
                    wireframe
                      ? 'bg-cyan-500 text-slate-950 border-cyan-300'
                      : 'bg-slate-900/90 text-slate-200 border-slate-700 hover:bg-slate-800'
                  }`}
                >
                  <Eye className="w-3.5 h-3.5" /> Malla 3D
                </button>
                <button
                  onClick={() => setTestAttackAnim(!testAttackAnim)}
                  className={`px-2.5 py-1.5 rounded-lg text-xs font-bold border transition flex items-center gap-1 ${
                    testAttackAnim
                      ? 'bg-amber-500 text-slate-950 border-amber-300'
                      : 'bg-slate-900/90 text-slate-200 border-slate-700 hover:bg-slate-800'
                  }`}
                >
                  <Play className="w-3.5 h-3.5" /> Animar Ataque
                </button>
                <button
                  onClick={() => {
                    dragRef.current.rotY = 0.5;
                    dragRef.current.rotX = 0.15;
                  }}
                  className="p-1.5 rounded-lg bg-slate-900/90 text-slate-300 border border-slate-700 hover:bg-slate-800"
                  title="Reiniciar cámara"
                >
                  <RotateCcw className="w-3.5 h-3.5" />
                </button>
              </div>
            </div>

            <div className="absolute bottom-3 left-3 right-3 flex items-center justify-between text-[11px] text-slate-400 px-3 py-1.5 rounded-lg bg-slate-900/80 border border-slate-800">
              <span>Arrastra con el ratón para rotar el modelo 3D en 360°</span>
              <button
                onClick={handleDownloadOBJ}
                className="text-amber-300 hover:text-amber-200 font-bold flex items-center gap-1"
              >
                <Download className="w-3.5 h-3.5" /> Descargar .OBJ 3D
              </button>
            </div>
          </div>

          {/* Right Inspector Details */}
          <div className="lg:col-span-3 p-5 bg-slate-900/80 border-l border-slate-800 flex flex-col justify-between space-y-4">
            {tab === 'swords' ? (
              <div className="space-y-4">
                <div>
                  <span className="text-xs font-black uppercase tracking-widest text-amber-400">
                    {selectedSword.subtitle}
                  </span>
                  <h3 className="text-xl font-black text-white mt-0.5">{selectedSword.name}</h3>
                  <p className="text-xs text-amber-200/80 mt-1 font-medium">
                    Material: {selectedSword.materialName}
                  </p>
                </div>

                <p className="text-xs text-slate-300 leading-relaxed bg-slate-950/60 p-3 rounded-xl border border-slate-800">
                  {selectedSword.description}
                </p>

                <div className="p-3 rounded-xl bg-amber-500/10 border border-amber-500/30">
                  <div className="text-xs font-bold text-amber-300 flex items-center gap-1.5">
                    <Sparkles className="w-4 h-4" /> Poder Pasivo: {selectedSword.passiveName}
                  </div>
                  <p className="text-xs text-slate-300 mt-1">{selectedSword.passiveDescription}</p>
                </div>

                <div className="grid grid-cols-2 gap-2 text-xs">
                  <div className="p-2.5 rounded-lg bg-slate-950 border border-slate-800">
                    <div className="text-slate-400">Daño Base</div>
                    <div className="text-base font-black text-amber-400">{selectedSword.baseDamage}</div>
                  </div>
                  <div className="p-2.5 rounded-lg bg-slate-950 border border-slate-800">
                    <div className="text-slate-400">Velocidad</div>
                    <div className="text-base font-black text-cyan-400">{selectedSword.attackSpeed}x</div>
                  </div>
                  <div className="p-2.5 rounded-lg bg-slate-950 border border-slate-800">
                    <div className="text-slate-400">Alcance 3D</div>
                    <div className="text-base font-black text-emerald-400">{selectedSword.range}m</div>
                  </div>
                  <div className="p-2.5 rounded-lg bg-slate-950 border border-slate-800">
                    <div className="text-slate-400">Prob. Crítico</div>
                    <div className="text-base font-black text-rose-400">
                      {Math.round(selectedSword.critChance * 100)}%
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              <div className="space-y-4">
                <div>
                  <span className="text-xs font-black uppercase tracking-widest text-rose-400">
                    {selectedMonster.title}
                  </span>
                  <h3 className="text-xl font-black text-white mt-0.5">{selectedMonster.name}</h3>
                </div>

                <p className="text-xs text-slate-300 leading-relaxed bg-slate-950/60 p-3 rounded-xl border border-slate-800">
                  {selectedMonster.description}
                </p>

                <div className="grid grid-cols-2 gap-2 text-xs">
                  <div className="p-2.5 rounded-lg bg-slate-950 border border-slate-800">
                    <div className="text-slate-400">Vida Base</div>
                    <div className="text-base font-black text-rose-400">{selectedMonster.baseHp} HP</div>
                  </div>
                  <div className="p-2.5 rounded-lg bg-slate-950 border border-slate-800">
                    <div className="text-slate-400">Ataque</div>
                    <div className="text-base font-black text-amber-400">{selectedMonster.baseDamage}</div>
                  </div>
                  <div className="p-2.5 rounded-lg bg-slate-950 border border-slate-800">
                    <div className="text-slate-400">Recompensa EXP</div>
                    <div className="text-base font-black text-cyan-400">+{selectedMonster.xpReward} EXP</div>
                  </div>
                  <div className="p-2.5 rounded-lg bg-slate-950 border border-slate-800">
                    <div className="text-slate-400">Esencia / Oro</div>
                    <div className="text-base font-black text-yellow-400">+{selectedMonster.goldReward}</div>
                  </div>
                </div>
              </div>
            )}

            {tab === 'swords' && (
              <button
                onClick={() => {
                  onSelectLevelForTesting(selectedSword.minLevel);
                  onClose();
                }}
                className="w-full py-3 px-4 rounded-xl bg-gradient-to-r from-amber-500 to-orange-500 hover:from-amber-400 hover:to-orange-400 text-slate-950 font-black text-xs uppercase tracking-wider shadow-lg shadow-amber-500/25 transition flex items-center justify-center gap-2"
              >
                <Flame className="w-4 h-4" />
                Equipar y Probar {selectedSword.name} (Nv. {selectedSword.minLevel})
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};
