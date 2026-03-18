# Pet Simulator — Example

Generated with:

```bash
rab generate "Make a pet simulator game. Players click to earn coins, hatch eggs to get pets, and can rebirth for multipliers. Add a shop and leaderboard." --no-ai
```

## Detected Configuration

- **Language**: English
- **Genre**: Simulator
- **Systems**: economy, pet, leaderboard, shop, inventory
- **UI**: HUD, shop GUI, leaderboard GUI, inventory GUI
- **Files generated**: 16

## What's Included

### Server Scripts
- `SimulatorCore` — Click-to-earn loop, zones, rebirth system
- `PetService` — Egg hatching (gacha), pet equipping, multipliers
- `EconomyService` — Coin tracking and persistence
- `ShopService` — Buy items with coins
- `InventoryService` — Player inventory management
- `LeaderboardService` — Player stats display
- `GameManager` — Main initialization script

### Client Scripts
- `InputHandler` — Player input (click events)
- `UIController` — UI state management

### UI
- `HUD` — Health bar + currency display
- `ShopGui` — In-game shop (toggle with B)
- `InventoryGui` — Player inventory (toggle with I)
- `LeaderboardGui` — Player rankings

### Shared Modules
- `Constants`, `Types`, `Utils`

## How to Use

```bash
cd Simulator/
rojo serve
# Connect from Roblox Studio
```

Then follow `ASSET_GUIDE.md` to place click zones, egg models, and pet display areas.
