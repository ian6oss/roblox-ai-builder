"""Asset guide generator - creates placement guides for game assets."""

from __future__ import annotations

from roblox_ai_builder.core.models import Genre


GENRE_ASSET_GUIDES: dict[Genre, str] = {
    Genre.OBBY: """## Asset Placement Guide - Obstacle Course

### Required Assets
| Asset | Count | Placement | Toolbox Search |
|-------|-------|-----------|----------------|
| Start Platform | 1 | Beginning of course | "obby start" |
| Checkpoints | 8-15 | Every 3-5 obstacles | "checkpoint flag" |
| Kill Bricks | 10-20 | Between platforms | "kill brick red" |
| Moving Platforms | 5-10 | Mid-course sections | "moving platform" |
| Finish Platform | 1 | End of course | "finish line obby" |
| Decorations | 15-30 | Around the course | "obby decoration" |

### Layout Tips
1. Start easy, increase difficulty gradually
2. Place checkpoints BEFORE hard sections (not after)
3. Use different colors for kill bricks (red) vs safe platforms (green/blue)
4. Add visual indicators for moving platforms (arrows, glow)
5. Keep the course visible - players should see the next checkpoint
""",
    Genre.TYCOON: """## Asset Placement Guide - Tycoon

### Required Assets
| Asset | Count | Placement | Toolbox Search |
|-------|-------|-----------|----------------|
| Tycoon Plot | 1+ per player | Evenly spaced in map | "tycoon plot base" |
| Purchase Buttons | 10-20 | On tycoon plot floor | "tycoon button" |
| Droppers | 3-5 | Top of tycoon | "dropper tycoon" |
| Conveyors | 3-5 | Connect dropper to collector | "conveyor belt" |
| Collector/Furnace | 1-2 | End of conveyor | "tycoon collector" |
| Upgrades | 5-10 | Unlock progressively | "upgrade station" |

### Folder Structure in Workspace
```
Workspace/
├── Tycoons/
│   ├── Tycoon1/
│   │   ├── Buttons/ (Parts with "Cost" and "Unlocks" attributes)
│   │   ├── Droppers/
│   │   └── Conveyors/
│   └── Tycoon2/
```

### Setup Instructions
1. Each button needs attributes: `Cost` (number) and `Unlocks` (string = item name)
2. Unlockable items start with Transparency=1, CanCollide=false
3. Place a "CashCollector" part where dropped items are converted to cash
""",
    Genre.SURVIVAL: """## Asset Placement Guide - Survival Game

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
""",
    Genre.RPG: """## Asset Placement Guide - RPG

### Required Assets
| Asset | Count | Placement | Toolbox Search |
|-------|-------|-----------|----------------|
| Town/Hub | 1 | Center of map | "rpg town medieval" |
| NPCs | 5-10 | In town for quests/shops | "npc character" |
| Dungeon Entrance | 1-3 | Map edges | "dungeon gate" |
| Monsters | 5+ types | In wilderness/dungeons | "monster enemy rpg" |
| Treasure Chests | 10-20 | Hidden locations | "treasure chest" |
| Weapon Models | 5-10 | As Tools in ServerStorage | "sword rpg weapon" |

### Setup Instructions
1. Place NPCs as Models with a "DialogId" attribute
2. Set monster spawn zones with "SpawnZone" parts
3. Chests need "LootTable" attribute (JSON string)
""",
    Genre.FPS: """## Asset Placement Guide - FPS/Shooter

### Required Assets
| Asset | Count | Placement | Toolbox Search |
|-------|-------|-----------|----------------|
| Map/Arena | 1 | Game world | "fps arena map" |
| Spawn Points | 8-16 | Spread across map (per team) | "spawn point" |
| Cover Objects | 20-40 | Throughout map | "cover wall crate" |
| Weapon Pickups | 5-10 | Strategic locations | "weapon pickup fps" |
| Ammo Boxes | 10-15 | Near combat areas | "ammo box" |

### Setup Instructions
1. Create Team spawn groups in Workspace/SpawnPoints/TeamA and TeamB
2. Place cover objects at strategic positions for gameplay flow
3. Weapons as Tools in ReplicatedStorage
""",
}

DEFAULT_GUIDE = """## Asset Placement Guide

### General Setup
1. Create your game map in Workspace
2. Add spawn points as Parts in Workspace/SpawnPoints/
3. Place any interactive objects with appropriate attributes
4. Check the generated scripts for expected Workspace structure

### Tips
- Use Roblox Toolbox to find free models matching your theme
- Keep the poly count reasonable for performance
- Test with multiple players to ensure proper spawning
"""


class AssetGuide:
    """Generates asset placement guides for different game genres."""

    async def generate(self, asset_hints: list[str], genre: Genre) -> str:
        """Generate an asset placement guide."""
        guide = f"# Asset Placement Guide\n\n"
        guide += f"**Genre**: {genre.value}\n"
        guide += f"**Suggested Assets**: {', '.join(asset_hints)}\n\n"
        guide += "---\n\n"
        guide += GENRE_ASSET_GUIDES.get(genre, DEFAULT_GUIDE)
        guide += "\n\n---\n\n"
        guide += "### Toolbox Quick Search Keywords\n\n"
        for hint in asset_hints:
            guide += f"- `{hint}`: Search in Roblox Toolbox for relevant models\n"
        return guide
