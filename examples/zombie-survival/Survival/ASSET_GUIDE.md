# Asset Placement Guide

**Genre**: survival
**Suggested Assets**: weapons, zombies, barricades, supplies

---

## Asset Placement Guide - Survival Game

### Required Assets
| Asset | Count | Placement | Toolbox Search |
|-------|-------|-----------|----------------|
| Map/Terrain | 1 | Center of game world | "survival map" |
| Spawn Points | 4-8 | Spread across safe zone | "spawn point" |
| Enemy Spawn Points | 6-12 | Around map edges | "enemy spawn" |
| Weapons | 3-5 types | In weapon racks/chests | "sword weapon" |
| Barricades | 10-20 | Buildable positions | "barricade wall" |
| Supply Crates | 5-10 | Random positions | "supply crate loot" |
| Safe Zone | 1 | Center/start area | "safe zone barrier" |

### Folder Structure in Workspace
```
Workspace/
├── Map/
├── SpawnPoints/ (Parts named "Spawn_1", "Spawn_2", etc.)
├── EnemySpawns/ (Parts for enemy spawn locations)
├── Weapons/
└── Supplies/
```

### Setup Instructions
1. Name enemy spawn parts and place them in `Workspace/EnemySpawns/`
2. The WaveManager script spawns enemies at these locations
3. Place weapons as Tools in ServerStorage for distribution


---

### Toolbox Quick Search Keywords

- `weapons`: Search in Roblox Toolbox for relevant models
- `zombies`: Search in Roblox Toolbox for relevant models
- `barricades`: Search in Roblox Toolbox for relevant models
- `supplies`: Search in Roblox Toolbox for relevant models
