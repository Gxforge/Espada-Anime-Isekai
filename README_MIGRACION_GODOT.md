# Forja de Almas 3D - Migración a Godot 4.4

Este repositorio contiene la migración del juego web **3D Sword Evolution Game / Forja de Almas 3D** (Three.js + React) a **Godot 4.4**.

## Estructura

- `godot_project/` - Proyecto Godot 4.4 completo
  - `project.godot` - Configuración del proyecto (Godot 4.4, Forward+)
  - `scenes/Main.tscn` - Escena principal (arena, jugador, cámara, HUD)
  - `scenes/Monster.tscn` - Escena de monstruo
  - `scripts/` - Lógica GDScript (Player, Monster, Main, HUD, GameData, habilidades)
  - `assets/models/` - **16 modelos 3D OBJ** migrados (8 espadas + 7 monstruos + caballero)
  - `export_presets.cfg` - Preset de exportación Linux
  - `reference_web/` - Código fuente web original para referencia
- `.github/workflows/godot-ci.yml` - CI en GitHub Actions: import headless + export Linux

## Modelos 3D migrados

Espadas: wood, copper, iron, silver, gold, crystal, obsidian, celestial  
Monstruos: slime, goblin, skeleton, copper_golem, orc_berserker, crimson_drake, demon_lord  
Jugador: hero_knight_wielder

## Cómo ejecutar

1. Abrir `godot_project/` con **Godot 4.4**.
2. Ejecutar la escena principal `scenes/Main.tscn` (F5).

## Controles

- **WASD / Flechas**: mover
- **Click Izq / Espacio**: atacar
- **Q**: Torbellino
- **E**: Onda Cortante
- **R**: Lluvia de Espadas (Ultimate)
- **Shift**: Dash

## GitHub Actions

El workflow `.github/workflows/godot-ci.yml` valida el proyecto con Godot 4.4 en modo headless e intenta exportar un build Linux.
