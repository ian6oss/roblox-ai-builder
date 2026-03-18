# Roblox AI Builder

Generate complete Roblox game projects from a single prompt — in any language.

```
rab generate "좀비 서바이벌 게임 만들어줘"
```

RAB analyzes your prompt, picks the right genre and game systems, generates production-quality Luau scripts, UI code, and a Rojo-compatible project — all in one command.

## Features

- **9 Genres**: obby, tycoon, simulator, rpg, fps, survival, horror, racing, custom
- **15 Game Systems**: inventory, combat, shop, leaderboard, wave spawner, economy, crafting, quest, dialog, gamepass, dev products, checkpoint, tycoon core, pet, trading
- **Multi-language Prompts**: English, Korean, Japanese, Chinese — auto-detected
- **Smart Defaults**: genre detection auto-includes relevant systems and UI
- **Rojo Output**: ready to `rojo serve` into Roblox Studio
- **AI + Fallback**: uses Claude API for high-quality scripts, falls back to built-in presets when offline
- **Asset Guides**: per-genre placement guides with Toolbox search keywords

## Quick Start

### Install

```bash
# Requires Python 3.11+
pip install roblox-ai-builder

# Or with uv
uv pip install roblox-ai-builder
```

### Setup API Key (optional — enables AI generation)

```bash
rab login
# Opens browser → Anthropic Console → paste your key
```

Or set via environment variable:

```bash
export ANTHROPIC_API_KEY=sk-ant-...
```

### Generate a Game

```bash
# English
rab generate "zombie survival game with waves, shop, and inventory"

# Korean
rab generate "좀비 서바이벌 게임 만들어줘"

# Preview without generating files
rab preview "pet simulator with rebirths and trading"

# Specify output directory
rab generate "obby with 20 stages" --output ./my-games
```

## CLI Commands

| Command | Description |
|---------|-------------|
| `rab generate <prompt>` | Generate a complete game project |
| `rab preview <prompt>` | Preview game plan without generating files |
| `rab presets` | List available genre presets |
| `rab presets <name>` | Show details for a specific preset |
| `rab login` | Set up Anthropic API key |
| `rab config show` | Show current configuration |
| `rab config set <key> <value>` | Update configuration |
| `rab history` | View past generations |

## How It Works

```
Prompt → Parse → Plan → Generate → Write
  │        │       │        │         │
  │   Detect lang  │   AI + Presets   │
  │   + genre +    │   + UI builder   │
  │   systems      │   + asset guide  │
  │                │                  │
  └── "zombie      └── GamePlan       └── Rojo project/
      survival         with scripts       ├── src/
      game"            and UI specs       ├── ASSET_GUIDE.md
                                          └── README.md
```

1. **Parse**: Detects language, genre, game systems, and UI needs from natural language
2. **Plan**: Merges genre defaults with detected systems, resolves dependencies
3. **Generate**: Runs Luau generation (AI or preset), UI builder, and asset guide in parallel
4. **Write**: Outputs a Rojo-compatible file tree with all scripts organized

## Output Structure

```
MyGame/
├── default.project.json          # Rojo configuration
├── src/
│   ├── ServerScriptService/      # Server scripts
│   │   ├── GameManager.server.lua
│   │   ├── CombatService.server.lua
│   │   └── ...
│   ├── StarterPlayerScripts/     # Client scripts
│   │   ├── InputHandler.client.lua
│   │   └── UIController.client.lua
│   ├── ReplicatedStorage/        # Shared modules
│   │   ├── Constants.module.lua
│   │   └── Utils.module.lua
│   └── StarterGui/               # UI scripts
│       ├── HUD.client.lua
│       └── ShopGui.client.lua
├── ASSET_GUIDE.md                # What to place in Roblox Studio
└── README.md
```

## Genre Presets

Each genre comes with production-ready Luau scripts:

| Genre | Preset Scripts | Key Systems |
|-------|---------------|-------------|
| **Obby** | CheckpointService, LeaderboardService | Checkpoints, stage tracking, data save |
| **Tycoon** | TycoonService, EconomyService | Button unlocks, droppers, cash system |
| **Simulator** | SimulatorCore, PetService | Click-to-earn, zones, rebirths, pet gacha |
| **RPG** | QuestService, DialogService, RPGStats | Quests, NPC dialog, XP/leveling |
| **FPS** | WeaponService, FPSLeaderboard | Raycast shooting, reload, K/D tracking |
| **Survival** | SurvivalManager | Day/night, hunger/thirst, wave defense |
| **Horror** | HorrorManager | Flashlight, sanity, key collection |
| **Racing** | RacingService, VehicleService | Lap timing, checkpoints, vehicle spawns |

## Examples

See the [`examples/`](examples/) directory:

- [`examples/zombie-survival/`](examples/zombie-survival/) — Survival game with waves and combat
- [`examples/pet-simulator/`](examples/pet-simulator/) — Simulator with pets and rebirths

## Using the Output

### With Rojo (Recommended)

```bash
cd output/MyGame
rojo serve
# In Roblox Studio: Plugins → Rojo → Connect
```

### Manual Import

1. Open Roblox Studio
2. Copy `src/ServerScriptService/` files → ServerScriptService
3. Copy `src/StarterPlayerScripts/` files → StarterPlayer → StarterPlayerScripts
4. Copy `src/ReplicatedStorage/` files → ReplicatedStorage
5. Copy `src/StarterGui/` files → StarterGui
6. Follow `ASSET_GUIDE.md` to place maps, NPCs, and objects

## Default Controls

| Key | Action |
|-----|--------|
| **I** | Toggle Inventory |
| **B** | Toggle Shop |
| **F** | Toggle Flashlight (Horror) |

## Configuration

Config file: `~/.config/roblox-ai-builder/config.toml`

```toml
[ai]
api_key = "sk-ant-..."
model = "claude-sonnet-4-6-20250514"
max_tokens = 8192

[output]
dir = "./output"

[general]
language = "auto"
```

Environment variables override file config:
- `ANTHROPIC_API_KEY` — API key
- `ROBLOX_AI_BUILDER_OUTPUT` — output directory
- `ROBLOX_AI_BUILDER_CONFIG` — config file path

## Development

```bash
# Clone and install dev dependencies
git clone https://github.com/ian6oss/roblox-ai-builder.git
cd roblox-ai-builder
uv sync --dev

# Run tests
uv run pytest

# Lint
uv run ruff check src/

# Type check
uv run mypy src/
```

## License

MIT
