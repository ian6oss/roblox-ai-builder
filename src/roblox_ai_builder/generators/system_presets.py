"""Game system presets - pre-built game templates for each genre."""

from __future__ import annotations

from pathlib import Path

from roblox_ai_builder.core.models import GeneratedFile, Genre, SystemType


# Embedded preset templates (no external file dependency for Alpha)
PRESET_TEMPLATES: dict[str, dict[str, str]] = {
    "obby": {
        "CheckpointService.server.lua": '''-- CheckpointService: Manages player checkpoints and respawning
local Players = game:GetService("Players")
local ServerStorage = game:GetService("ServerStorage")

local CheckpointService = {}
CheckpointService.__index = CheckpointService

local playerCheckpoints: {[Player]: number} = {}

function CheckpointService.init()
    Players.PlayerAdded:Connect(function(player)
        playerCheckpoints[player] = 1
        player.CharacterAdded:Connect(function(character)
            task.wait(0.5)
            local checkpoint = workspace:FindFirstChild("Checkpoint_" .. playerCheckpoints[player])
            if checkpoint then
                character:SetPrimaryPartCFrame(checkpoint.CFrame + Vector3.new(0, 5, 0))
            end
        end)
    end)

    Players.PlayerRemoving:Connect(function(player)
        playerCheckpoints[player] = nil
    end)
end

function CheckpointService.setCheckpoint(player: Player, checkpointNumber: number)
    if checkpointNumber > (playerCheckpoints[player] or 0) then
        playerCheckpoints[player] = checkpointNumber
    end
end

function CheckpointService.getCheckpoint(player: Player): number
    return playerCheckpoints[player] or 1
end

return CheckpointService
''',
        "LeaderboardService.server.lua": '''-- LeaderboardService: Manages player stats and leaderboard
local Players = game:GetService("Players")
local DataStoreService = game:GetService("DataStoreService")

local LeaderboardService = {}
LeaderboardService.__index = LeaderboardService

local DATASTORE_KEY = "PlayerStats_v1"

function LeaderboardService.init()
    Players.PlayerAdded:Connect(function(player)
        local leaderstats = Instance.new("Folder")
        leaderstats.Name = "leaderstats"
        leaderstats.Parent = player

        local stage = Instance.new("IntValue")
        stage.Name = "Stage"
        stage.Value = 1
        stage.Parent = leaderstats

        local time = Instance.new("NumberValue")
        time.Name = "Time"
        time.Value = 0
        time.Parent = leaderstats

        -- Load saved data
        local success, data = pcall(function()
            local store = DataStoreService:GetDataStore(DATASTORE_KEY)
            return store:GetAsync("player_" .. player.UserId)
        end)

        if success and data then
            stage.Value = data.stage or 1
        end
    end)

    Players.PlayerRemoving:Connect(function(player)
        LeaderboardService.saveData(player)
    end)
end

function LeaderboardService.saveData(player: Player)
    local leaderstats = player:FindFirstChild("leaderstats")
    if not leaderstats then return end

    pcall(function()
        local store = DataStoreService:GetDataStore(DATASTORE_KEY)
        store:SetAsync("player_" .. player.UserId, {
            stage = leaderstats.Stage.Value,
        })
    end)
end

function LeaderboardService.setStat(player: Player, statName: string, value: number)
    local leaderstats = player:FindFirstChild("leaderstats")
    if leaderstats then
        local stat = leaderstats:FindFirstChild(statName)
        if stat then
            stat.Value = value
        end
    end
end

return LeaderboardService
''',
    },
    "tycoon": {
        "TycoonService.server.lua": '''-- TycoonService: Core tycoon mechanics (buttons, droppers, upgraders)
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local TycoonService = {}
TycoonService.__index = TycoonService

local playerTycoons: {[Player]: any} = {}

function TycoonService.init()
    Players.PlayerAdded:Connect(function(player)
        TycoonService.assignTycoon(player)
    end)

    Players.PlayerRemoving:Connect(function(player)
        TycoonService.releaseTycoon(player)
    end)
end

function TycoonService.assignTycoon(player: Player)
    local tycoons = workspace:FindFirstChild("Tycoons")
    if not tycoons then return end

    for _, tycoon in tycoons:GetChildren() do
        if not tycoon:GetAttribute("Owner") then
            tycoon:SetAttribute("Owner", player.UserId)
            playerTycoons[player] = tycoon
            TycoonService.setupButtons(player, tycoon)
            break
        end
    end
end

function TycoonService.releaseTycoon(player: Player)
    local tycoon = playerTycoons[player]
    if tycoon then
        tycoon:SetAttribute("Owner", nil)
        playerTycoons[player] = nil
    end
end

function TycoonService.setupButtons(player: Player, tycoon: any)
    local buttons = tycoon:FindFirstChild("Buttons")
    if not buttons then return end

    for _, button in buttons:GetChildren() do
        if button:IsA("BasePart") then
            button.Touched:Connect(function(hit)
                local hitPlayer = Players:GetPlayerFromCharacter(hit.Parent)
                if hitPlayer == player then
                    TycoonService.onButtonPressed(player, tycoon, button)
                end
            end)
        end
    end
end

function TycoonService.onButtonPressed(player: Player, tycoon: any, button: any)
    local cost = button:GetAttribute("Cost") or 0
    local leaderstats = player:FindFirstChild("leaderstats")
    if not leaderstats then return end

    local cash = leaderstats:FindFirstChild("Cash")
    if cash and cash.Value >= cost then
        cash.Value = cash.Value - cost
        local itemName = button:GetAttribute("Unlocks")
        if itemName then
            local item = tycoon:FindFirstChild(itemName)
            if item then
                item.Transparency = 0
                item.CanCollide = true
            end
        end
        button:Destroy()
    end
end

return TycoonService
''',
        "EconomyService.server.lua": '''-- EconomyService: Manages in-game currency
local Players = game:GetService("Players")
local DataStoreService = game:GetService("DataStoreService")

local EconomyService = {}
EconomyService.__index = EconomyService

local DATASTORE_KEY = "Economy_v1"

function EconomyService.init()
    Players.PlayerAdded:Connect(function(player)
        local leaderstats = player:FindFirstChild("leaderstats")
        if not leaderstats then
            leaderstats = Instance.new("Folder")
            leaderstats.Name = "leaderstats"
            leaderstats.Parent = player
        end

        local cash = Instance.new("IntValue")
        cash.Name = "Cash"
        cash.Value = 0
        cash.Parent = leaderstats

        -- Load saved data
        local success, data = pcall(function()
            local store = DataStoreService:GetDataStore(DATASTORE_KEY)
            return store:GetAsync("player_" .. player.UserId)
        end)

        if success and data then
            cash.Value = data.cash or 0
        end
    end)

    Players.PlayerRemoving:Connect(function(player)
        EconomyService.saveData(player)
    end)
end

function EconomyService.addCash(player: Player, amount: number)
    local leaderstats = player:FindFirstChild("leaderstats")
    if leaderstats then
        local cash = leaderstats:FindFirstChild("Cash")
        if cash then
            cash.Value = cash.Value + amount
        end
    end
end

function EconomyService.removeCash(player: Player, amount: number): boolean
    local leaderstats = player:FindFirstChild("leaderstats")
    if leaderstats then
        local cash = leaderstats:FindFirstChild("Cash")
        if cash and cash.Value >= amount then
            cash.Value = cash.Value - amount
            return true
        end
    end
    return false
end

function EconomyService.getCash(player: Player): number
    local leaderstats = player:FindFirstChild("leaderstats")
    if leaderstats then
        local cash = leaderstats:FindFirstChild("Cash")
        if cash then
            return cash.Value
        end
    end
    return 0
end

function EconomyService.saveData(player: Player)
    local leaderstats = player:FindFirstChild("leaderstats")
    if not leaderstats then return end
    local cash = leaderstats:FindFirstChild("Cash")
    if not cash then return end

    pcall(function()
        local store = DataStoreService:GetDataStore(DATASTORE_KEY)
        store:SetAsync("player_" .. player.UserId, {
            cash = cash.Value,
        })
    end)
end

return EconomyService
''',
    },
}

# Common system templates available for all genres
COMMON_SYSTEM_TEMPLATES: dict[str, str] = {
    "InventoryService.server.lua": '''-- InventoryService: Player inventory management
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local InventoryService = {}
InventoryService.__index = InventoryService

local playerInventories: {[Player]: {[string]: number}} = {}
local MAX_SLOTS = 20

function InventoryService.init()
    local remotes = Instance.new("Folder")
    remotes.Name = "InventoryRemotes"
    remotes.Parent = ReplicatedStorage

    local getInventory = Instance.new("RemoteFunction")
    getInventory.Name = "GetInventory"
    getInventory.Parent = remotes

    getInventory.OnServerInvoke = function(player)
        return playerInventories[player] or {}
    end

    Players.PlayerAdded:Connect(function(player)
        playerInventories[player] = {}
    end)

    Players.PlayerRemoving:Connect(function(player)
        playerInventories[player] = nil
    end)
end

function InventoryService.addItem(player: Player, itemId: string, amount: number?): boolean
    local inv = playerInventories[player]
    if not inv then return false end

    local count = amount or 1
    local totalItems = 0
    for _, v in inv do
        totalItems = totalItems + 1
    end

    if totalItems >= MAX_SLOTS and not inv[itemId] then
        return false
    end

    inv[itemId] = (inv[itemId] or 0) + count
    return true
end

function InventoryService.removeItem(player: Player, itemId: string, amount: number?): boolean
    local inv = playerInventories[player]
    if not inv or not inv[itemId] then return false end

    local count = amount or 1
    if inv[itemId] < count then return false end

    inv[itemId] = inv[itemId] - count
    if inv[itemId] <= 0 then
        inv[itemId] = nil
    end
    return true
end

function InventoryService.hasItem(player: Player, itemId: string, amount: number?): boolean
    local inv = playerInventories[player]
    if not inv then return false end
    return (inv[itemId] or 0) >= (amount or 1)
end

function InventoryService.getInventory(player: Player): {[string]: number}
    return playerInventories[player] or {}
end

return InventoryService
''',
    "CombatService.server.lua": '''-- CombatService: Combat mechanics (damage, health, death)
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local CombatService = {}
CombatService.__index = CombatService

local DEFAULT_MAX_HEALTH = 100

function CombatService.init()
    local remotes = Instance.new("Folder")
    remotes.Name = "CombatRemotes"
    remotes.Parent = ReplicatedStorage

    local attackRemote = Instance.new("RemoteEvent")
    attackRemote.Name = "Attack"
    attackRemote.Parent = remotes

    attackRemote.OnServerEvent:Connect(function(player, targetId)
        CombatService.handleAttack(player, targetId)
    end)

    Players.PlayerAdded:Connect(function(player)
        player.CharacterAdded:Connect(function(character)
            local humanoid = character:WaitForChild("Humanoid")
            humanoid.MaxHealth = DEFAULT_MAX_HEALTH
            humanoid.Health = DEFAULT_MAX_HEALTH
        end)
    end)
end

function CombatService.dealDamage(target: Model, amount: number, source: Player?)
    local humanoid = target:FindFirstChildOfClass("Humanoid")
    if not humanoid then return end
    if humanoid.Health <= 0 then return end

    humanoid:TakeDamage(amount)
end

function CombatService.handleAttack(player: Player, targetId: number?)
    local character = player.Character
    if not character then return end

    -- Basic melee attack: damage nearby enemies
    local hrp = character:FindFirstChild("HumanoidRootPart")
    if not hrp then return end

    local range = 8
    for _, model in workspace:GetChildren() do
        if model:IsA("Model") and model ~= character then
            local targetHRP = model:FindFirstChild("HumanoidRootPart")
            if targetHRP then
                local distance = (hrp.Position - targetHRP.Position).Magnitude
                if distance <= range then
                    CombatService.dealDamage(model, 25, player)
                end
            end
        end
    end
end

return CombatService
''',
    "ShopService.server.lua": '''-- ShopService: In-game shop for buying items
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local ShopService = {}
ShopService.__index = ShopService

-- Shop items configuration
local SHOP_ITEMS = {
    {id = "sword", name = "Iron Sword", price = 100, category = "weapon"},
    {id = "shield", name = "Wooden Shield", price = 75, category = "armor"},
    {id = "potion_hp", name = "Health Potion", price = 25, category = "consumable"},
    {id = "potion_speed", name = "Speed Potion", price = 50, category = "consumable"},
}

function ShopService.init()
    local remotes = Instance.new("Folder")
    remotes.Name = "ShopRemotes"
    remotes.Parent = ReplicatedStorage

    local buyItem = Instance.new("RemoteFunction")
    buyItem.Name = "BuyItem"
    buyItem.Parent = remotes

    local getShopItems = Instance.new("RemoteFunction")
    getShopItems.Name = "GetShopItems"
    getShopItems.Parent = remotes

    buyItem.OnServerInvoke = function(player, itemId)
        return ShopService.purchase(player, itemId)
    end

    getShopItems.OnServerInvoke = function(_player)
        return SHOP_ITEMS
    end
end

function ShopService.purchase(player: Player, itemId: string): (boolean, string)
    local item = nil
    for _, shopItem in SHOP_ITEMS do
        if shopItem.id == itemId then
            item = shopItem
            break
        end
    end

    if not item then
        return false, "Item not found"
    end

    local leaderstats = player:FindFirstChild("leaderstats")
    if not leaderstats then return false, "No stats" end

    local cash = leaderstats:FindFirstChild("Cash")
    if not cash or cash.Value < item.price then
        return false, "Not enough cash"
    end

    cash.Value = cash.Value - item.price
    -- Add to inventory (requires InventoryService)
    return true, "Purchase successful"
end

function ShopService.getItems(): {}
    return SHOP_ITEMS
end

return ShopService
''',
    "WaveManager.server.lua": '''-- WaveManager: Wave-based enemy spawning system
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local WaveManager = {}
WaveManager.__index = WaveManager

local currentWave = 0
local enemiesAlive = 0
local isWaveActive = false

local WAVE_CONFIG = {
    baseEnemies = 5,
    enemiesPerWave = 3,
    spawnDelay = 1.5,
    waveDelay = 10,
    maxWaves = 0, -- 0 = infinite
}

function WaveManager.init()
    local waveValue = Instance.new("IntValue")
    waveValue.Name = "CurrentWave"
    waveValue.Value = 0
    waveValue.Parent = ReplicatedStorage

    local enemyCount = Instance.new("IntValue")
    enemyCount.Name = "EnemiesAlive"
    enemyCount.Value = 0
    enemyCount.Parent = ReplicatedStorage

    -- Auto-start when players join
    Players.PlayerAdded:Connect(function(_player)
        if not isWaveActive and #Players:GetPlayers() > 0 then
            task.wait(5)
            WaveManager.startNextWave()
        end
    end)
end

function WaveManager.startNextWave()
    if isWaveActive then return end

    currentWave = currentWave + 1
    isWaveActive = true

    local waveValue = ReplicatedStorage:FindFirstChild("CurrentWave")
    if waveValue then
        waveValue.Value = currentWave
    end

    local enemyCount = WAVE_CONFIG.baseEnemies + (currentWave - 1) * WAVE_CONFIG.enemiesPerWave
    enemiesAlive = enemyCount

    local enemyCountValue = ReplicatedStorage:FindFirstChild("EnemiesAlive")
    if enemyCountValue then
        enemyCountValue.Value = enemiesAlive
    end

    -- Spawn enemies
    for i = 1, enemyCount do
        task.wait(WAVE_CONFIG.spawnDelay)
        WaveManager.spawnEnemy()
    end
end

function WaveManager.spawnEnemy()
    local spawnPoints = workspace:FindFirstChild("EnemySpawns")
    if not spawnPoints then return end

    local spawns = spawnPoints:GetChildren()
    if #spawns == 0 then return end

    local spawn = spawns[math.random(1, #spawns)]

    -- Create basic enemy
    local enemy = Instance.new("Model")
    enemy.Name = "Enemy_Wave" .. currentWave

    local part = Instance.new("Part")
    part.Name = "HumanoidRootPart"
    part.Size = Vector3.new(2, 5, 2)
    part.Position = spawn.Position + Vector3.new(0, 3, 0)
    part.Anchored = false
    part.BrickColor = BrickColor.new("Bright red")
    part.Parent = enemy

    local humanoid = Instance.new("Humanoid")
    humanoid.MaxHealth = 50 + currentWave * 10
    humanoid.Health = humanoid.MaxHealth
    humanoid.WalkSpeed = 12 + currentWave
    humanoid.Parent = enemy

    humanoid.Died:Connect(function()
        WaveManager.onEnemyDied(enemy)
    end)

    enemy.PrimaryPart = part
    enemy.Parent = workspace
end

function WaveManager.onEnemyDied(enemy: Model)
    enemiesAlive = enemiesAlive - 1

    local enemyCountValue = ReplicatedStorage:FindFirstChild("EnemiesAlive")
    if enemyCountValue then
        enemyCountValue.Value = enemiesAlive
    end

    task.wait(1)
    enemy:Destroy()

    if enemiesAlive <= 0 then
        isWaveActive = false
        task.wait(WAVE_CONFIG.waveDelay)
        WaveManager.startNextWave()
    end
end

function WaveManager.getCurrentWave(): number
    return currentWave
end

return WaveManager
''',
}


class SystemPresets:
    """Manages genre-specific game system presets."""

    def __init__(self, presets_dir: Path | None = None):
        self.presets_dir = presets_dir

    def load(
        self,
        preset_id: str,
        systems: list[SystemType],
    ) -> list[GeneratedFile]:
        """Load preset files for given genre and systems."""
        files: list[GeneratedFile] = []

        # Load genre-specific presets
        genre_presets = PRESET_TEMPLATES.get(preset_id, {})
        for filename, code in genre_presets.items():
            rojo_path = self._filename_to_rojo_path(filename)
            files.append(GeneratedFile(path=rojo_path, content=code, source="preset"))

        # Load common system templates for requested systems
        system_file_map: dict[SystemType, str] = {
            SystemType.INVENTORY: "InventoryService.server.lua",
            SystemType.COMBAT: "CombatService.server.lua",
            SystemType.SHOP: "ShopService.server.lua",
            SystemType.WAVE_SPAWNER: "WaveManager.server.lua",
        }

        for system in systems:
            filename = system_file_map.get(system)
            if filename and filename in COMMON_SYSTEM_TEMPLATES:
                # Skip if already provided by genre preset
                if filename not in genre_presets:
                    rojo_path = self._filename_to_rojo_path(filename)
                    files.append(
                        GeneratedFile(
                            path=rojo_path,
                            content=COMMON_SYSTEM_TEMPLATES[filename],
                            source="preset",
                        )
                    )

        return files

    def list_presets(self) -> list[str]:
        """List available preset IDs."""
        return list(PRESET_TEMPLATES.keys())

    @staticmethod
    def _filename_to_rojo_path(filename: str) -> str:
        """Convert filename to Rojo-compatible path."""
        if ".server.lua" in filename:
            return f"src/ServerScriptService/{filename}"
        elif ".client.lua" in filename:
            return f"src/StarterPlayerScripts/{filename}"
        else:
            return f"src/ReplicatedStorage/{filename}"
