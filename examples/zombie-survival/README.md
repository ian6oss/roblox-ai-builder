# Zombie Survival — Example

Generated with:

```bash
rab generate "좀비 서바이벌 게임 만들어줘. 웨이브마다 좀비가 나오고 상점에서 무기를 사서 싸울 수 있게 해줘." --no-ai
```

## Detected Configuration

- **Language**: Korean
- **Genre**: Survival
- **Systems**: combat, inventory, wave_spawner, shop, economy
- **UI**: HUD, shop GUI, wave counter, inventory GUI
- **Files generated**: 16

## What's Included

### Server Scripts
- `SurvivalManager` — Day/night cycle, hunger/thirst mechanics
- `CombatService` — Damage, health, melee attacks
- `WaveManager` — Wave-based enemy spawning with scaling difficulty
- `ShopService` — Buy items with in-game currency
- `InventoryService` — Player inventory management
- `EconomyService` — Currency (Cash) tracking and persistence
- `GameManager` — Main initialization script

### Client Scripts
- `InputHandler` — Player input
- `UIController` — UI state management

### UI
- `HUD` — Health bar + currency display
- `ShopGui` — In-game shop (toggle with B)
- `InventoryGui` — Player inventory (toggle with I)
- `WaveCounter` — Current wave + enemies remaining

### Shared Modules
- `Constants`, `Types`, `Utils`

## How to Use

```bash
cd Survival/
rojo serve
# Connect from Roblox Studio
```

Then follow `ASSET_GUIDE.md` to place spawn points, weapons, and map objects.
