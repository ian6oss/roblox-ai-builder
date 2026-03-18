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
    "simulator": {
        "SimulatorCore.server.lua": '''-- SimulatorCore: Core simulator loop (click/tap to earn, zones, rebirths)
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local DataStoreService = game:GetService("DataStoreService")

local SimulatorCore = {}
SimulatorCore.__index = SimulatorCore

local DATASTORE_KEY = "Simulator_v1"

local playerData: {[Player]: {coins: number, multiplier: number, rebirths: number, zone: number}} = {}

local ZONES = {
    {name = "Starter Field", minPower = 0, reward = 1},
    {name = "Forest", minPower = 50, reward = 3},
    {name = "Desert", minPower = 200, reward = 8},
    {name = "Volcano", minPower = 1000, reward = 25},
    {name = "Space", minPower = 5000, reward = 100},
}

function SimulatorCore.init()
    local remotes = Instance.new("Folder")
    remotes.Name = "SimulatorRemotes"
    remotes.Parent = ReplicatedStorage

    local clickRemote = Instance.new("RemoteEvent")
    clickRemote.Name = "Click"
    clickRemote.Parent = remotes

    local rebirthRemote = Instance.new("RemoteFunction")
    rebirthRemote.Name = "Rebirth"
    rebirthRemote.Parent = remotes

    clickRemote.OnServerEvent:Connect(function(player)
        SimulatorCore.onClickadd(player)
    end)

    rebirthRemote.OnServerInvoke = function(player)
        return SimulatorCore.rebirth(player)
    end

    Players.PlayerAdded:Connect(function(player)
        local data = SimulatorCore.loadData(player)
        playerData[player] = data

        local leaderstats = Instance.new("Folder")
        leaderstats.Name = "leaderstats"
        leaderstats.Parent = player

        local coins = Instance.new("IntValue")
        coins.Name = "Coins"
        coins.Value = data.coins
        coins.Parent = leaderstats

        local rebirths = Instance.new("IntValue")
        rebirths.Name = "Rebirths"
        rebirths.Value = data.rebirths
        rebirths.Parent = leaderstats
    end)

    Players.PlayerRemoving:Connect(function(player)
        SimulatorCore.saveData(player)
        playerData[player] = nil
    end)
end

function SimulatorCore.onClickadd(player: Player)
    local data = playerData[player]
    if not data then return end

    local zone = ZONES[data.zone] or ZONES[1]
    local earned = zone.reward * data.multiplier
    data.coins = data.coins + earned

    local leaderstats = player:FindFirstChild("leaderstats")
    if leaderstats then
        local coins = leaderstats:FindFirstChild("Coins")
        if coins then coins.Value = data.coins end
    end
end

function SimulatorCore.rebirth(player: Player): (boolean, string)
    local data = playerData[player]
    if not data then return false, "No data" end

    local rebirthCost = 10000 * (data.rebirths + 1)
    if data.coins < rebirthCost then
        return false, "Need " .. rebirthCost .. " coins"
    end

    data.coins = 0
    data.rebirths = data.rebirths + 1
    data.multiplier = 1 + data.rebirths * 0.5

    local leaderstats = player:FindFirstChild("leaderstats")
    if leaderstats then
        local coins = leaderstats:FindFirstChild("Coins")
        if coins then coins.Value = 0 end
        local rebirths = leaderstats:FindFirstChild("Rebirths")
        if rebirths then rebirths.Value = data.rebirths end
    end

    return true, "Rebirth successful! Multiplier: " .. data.multiplier .. "x"
end

function SimulatorCore.loadData(player: Player): {coins: number, multiplier: number, rebirths: number, zone: number}
    local default = {coins = 0, multiplier = 1, rebirths = 0, zone = 1}
    local success, data = pcall(function()
        local store = DataStoreService:GetDataStore(DATASTORE_KEY)
        return store:GetAsync("player_" .. player.UserId)
    end)
    if success and data then
        return {
            coins = data.coins or 0,
            multiplier = data.multiplier or 1,
            rebirths = data.rebirths or 0,
            zone = data.zone or 1,
        }
    end
    return default
end

function SimulatorCore.saveData(player: Player)
    local data = playerData[player]
    if not data then return end
    pcall(function()
        local store = DataStoreService:GetDataStore(DATASTORE_KEY)
        store:SetAsync("player_" .. player.UserId, data)
    end)
end

return SimulatorCore
''',
        "PetService.server.lua": '''-- PetService: Pet collection, equipping, and following
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local PetService = {}
PetService.__index = PetService

local playerPets: {[Player]: {owned: {[string]: boolean}, equipped: string?}} = {}

local PET_DATA = {
    {id = "dog", name = "Dog", rarity = "common", multiplier = 1.2},
    {id = "cat", name = "Cat", rarity = "common", multiplier = 1.3},
    {id = "dragon", name = "Dragon", rarity = "rare", multiplier = 2.0},
    {id = "unicorn", name = "Unicorn", rarity = "epic", multiplier = 3.5},
    {id = "phoenix", name = "Phoenix", rarity = "legendary", multiplier = 5.0},
}

local EGG_CHANCES = {
    common = 0.60,
    rare = 0.25,
    epic = 0.10,
    legendary = 0.05,
}

function PetService.init()
    local remotes = Instance.new("Folder")
    remotes.Name = "PetRemotes"
    remotes.Parent = ReplicatedStorage

    local hatchEgg = Instance.new("RemoteFunction")
    hatchEgg.Name = "HatchEgg"
    hatchEgg.Parent = remotes

    local equipPet = Instance.new("RemoteFunction")
    equipPet.Name = "EquipPet"
    equipPet.Parent = remotes

    hatchEgg.OnServerInvoke = function(player)
        return PetService.hatch(player)
    end

    equipPet.OnServerInvoke = function(player, petId)
        return PetService.equip(player, petId)
    end

    Players.PlayerAdded:Connect(function(player)
        playerPets[player] = {owned = {}, equipped = nil}
    end)

    Players.PlayerRemoving:Connect(function(player)
        playerPets[player] = nil
    end)
end

function PetService.hatch(player: Player): (boolean, string)
    local data = playerPets[player]
    if not data then return false, "No data" end

    -- Roll rarity
    local roll = math.random()
    local rarity = "common"
    local cumulative = 0
    for r, chance in EGG_CHANCES do
        cumulative = cumulative + chance
        if roll <= cumulative then
            rarity = r
            break
        end
    end

    -- Pick pet of that rarity
    local candidates = {}
    for _, pet in PET_DATA do
        if pet.rarity == rarity then
            table.insert(candidates, pet)
        end
    end

    if #candidates == 0 then return false, "No pets available" end
    local pet = candidates[math.random(1, #candidates)]
    data.owned[pet.id] = true

    return true, pet.name .. " (" .. pet.rarity .. ")"
end

function PetService.equip(player: Player, petId: string): (boolean, string)
    local data = playerPets[player]
    if not data then return false, "No data" end
    if not data.owned[petId] then return false, "Pet not owned" end

    data.equipped = petId
    return true, "Equipped " .. petId
end

function PetService.getEquippedMultiplier(player: Player): number
    local data = playerPets[player]
    if not data or not data.equipped then return 1 end

    for _, pet in PET_DATA do
        if pet.id == data.equipped then
            return pet.multiplier
        end
    end
    return 1
end

return PetService
''',
    },
    "rpg": {
        "QuestService.server.lua": '''-- QuestService: Quest tracking and completion
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local QuestService = {}
QuestService.__index = QuestService

local playerQuests: {[Player]: {active: {[string]: any}, completed: {[string]: boolean}}} = {}

local QUEST_DATABASE = {
    {
        id = "q_slime_hunt",
        name = "Slime Hunter",
        description = "Defeat 5 slimes",
        objective = {type = "kill", target = "Slime", count = 5},
        reward = {coins = 100, xp = 50},
    },
    {
        id = "q_gather_herbs",
        name = "Herb Gathering",
        description = "Collect 10 herbs",
        objective = {type = "collect", target = "Herb", count = 10},
        reward = {coins = 75, xp = 30},
    },
    {
        id = "q_boss_fight",
        name = "Boss Challenge",
        description = "Defeat the Forest Guardian",
        objective = {type = "kill", target = "ForestGuardian", count = 1},
        reward = {coins = 500, xp = 200},
    },
}

function QuestService.init()
    local remotes = Instance.new("Folder")
    remotes.Name = "QuestRemotes"
    remotes.Parent = ReplicatedStorage

    local acceptQuest = Instance.new("RemoteFunction")
    acceptQuest.Name = "AcceptQuest"
    acceptQuest.Parent = remotes

    local getQuests = Instance.new("RemoteFunction")
    getQuests.Name = "GetQuests"
    getQuests.Parent = remotes

    acceptQuest.OnServerInvoke = function(player, questId)
        return QuestService.accept(player, questId)
    end

    getQuests.OnServerInvoke = function(player)
        return QuestService.getAvailable(player)
    end

    Players.PlayerAdded:Connect(function(player)
        playerQuests[player] = {active = {}, completed = {}}
    end)

    Players.PlayerRemoving:Connect(function(player)
        playerQuests[player] = nil
    end)
end

function QuestService.accept(player: Player, questId: string): (boolean, string)
    local data = playerQuests[player]
    if not data then return false, "No data" end
    if data.completed[questId] then return false, "Already completed" end
    if data.active[questId] then return false, "Already active" end

    local quest = nil
    for _, q in QUEST_DATABASE do
        if q.id == questId then quest = q; break end
    end
    if not quest then return false, "Quest not found" end

    data.active[questId] = {progress = 0, required = quest.objective.count}
    return true, "Quest accepted: " .. quest.name
end

function QuestService.updateProgress(player: Player, objectiveType: string, target: string, amount: number?)
    local data = playerQuests[player]
    if not data then return end

    for questId, progress in data.active do
        local quest = nil
        for _, q in QUEST_DATABASE do
            if q.id == questId then quest = q; break end
        end
        if quest and quest.objective.type == objectiveType and quest.objective.target == target then
            progress.progress = progress.progress + (amount or 1)
            if progress.progress >= progress.required then
                QuestService.complete(player, questId, quest)
            end
        end
    end
end

function QuestService.complete(player: Player, questId: string, quest: any)
    local data = playerQuests[player]
    if not data then return end

    data.active[questId] = nil
    data.completed[questId] = true

    -- Grant rewards
    local leaderstats = player:FindFirstChild("leaderstats")
    if leaderstats then
        local coins = leaderstats:FindFirstChild("Coins") or leaderstats:FindFirstChild("Cash")
        if coins then coins.Value = coins.Value + (quest.reward.coins or 0) end
        local xp = leaderstats:FindFirstChild("XP")
        if xp then xp.Value = xp.Value + (quest.reward.xp or 0) end
    end
end

function QuestService.getAvailable(player: Player): {}
    local data = playerQuests[player]
    if not data then return {} end

    local available = {}
    for _, quest in QUEST_DATABASE do
        if not data.completed[quest.id] then
            local active = data.active[quest.id]
            table.insert(available, {
                id = quest.id,
                name = quest.name,
                description = quest.description,
                active = active ~= nil,
                progress = active and active.progress or 0,
                required = quest.objective.count,
            })
        end
    end
    return available
end

return QuestService
''',
        "DialogService.server.lua": '''-- DialogService: NPC dialog system with branching choices
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local DialogService = {}
DialogService.__index = DialogService

local DIALOGS = {
    npc_elder = {
        {text = "Welcome, adventurer! Our village needs your help.", choices = {
            {text = "What happened?", next = 2},
            {text = "Not interested.", next = nil},
        }},
        {text = "Monsters have been attacking from the forest. Can you help us?", choices = {
            {text = "I will help! (Accept Quest)", action = "accept_quest:q_slime_hunt", next = 3},
            {text = "Maybe later.", next = nil},
        }},
        {text = "Thank you, brave hero! Defeat the slimes in the forest.", choices = {}},
    },
    npc_merchant = {
        {text = "Welcome to my shop! Want to see what I have?", choices = {
            {text = "Show me your wares.", action = "open_shop", next = nil},
            {text = "No thanks.", next = nil},
        }},
    },
}

function DialogService.init()
    local remotes = Instance.new("Folder")
    remotes.Name = "DialogRemotes"
    remotes.Parent = ReplicatedStorage

    local startDialog = Instance.new("RemoteFunction")
    startDialog.Name = "StartDialog"
    startDialog.Parent = remotes

    local chooseOption = Instance.new("RemoteFunction")
    chooseOption.Name = "ChooseOption"
    chooseOption.Parent = remotes

    startDialog.OnServerInvoke = function(player, npcId)
        return DialogService.start(npcId)
    end

    chooseOption.OnServerInvoke = function(player, npcId, choiceIndex)
        return DialogService.choose(player, npcId, choiceIndex)
    end
end

function DialogService.start(npcId: string): any?
    local dialog = DIALOGS[npcId]
    if not dialog then return nil end
    return dialog[1]
end

function DialogService.choose(player: Player, npcId: string, stepIndex: number): any?
    local dialog = DIALOGS[npcId]
    if not dialog or not dialog[stepIndex] then return nil end

    local step = dialog[stepIndex]
    return step
end

function DialogService.getDialog(npcId: string): any?
    return DIALOGS[npcId]
end

return DialogService
''',
        "RPGStats.server.lua": '''-- RPGStats: Player stats, XP, and leveling system
local Players = game:GetService("Players")
local DataStoreService = game:GetService("DataStoreService")

local RPGStats = {}
RPGStats.__index = RPGStats

local DATASTORE_KEY = "RPGStats_v1"

local playerStats: {[Player]: {level: number, xp: number, str: number, def: number, spd: number}} = {}

local function xpForLevel(level: number): number
    return math.floor(100 * level ^ 1.5)
end

function RPGStats.init()
    Players.PlayerAdded:Connect(function(player)
        local stats = RPGStats.loadStats(player)
        playerStats[player] = stats

        local leaderstats = Instance.new("Folder")
        leaderstats.Name = "leaderstats"
        leaderstats.Parent = player

        local level = Instance.new("IntValue")
        level.Name = "Level"
        level.Value = stats.level
        level.Parent = leaderstats

        local xp = Instance.new("IntValue")
        xp.Name = "XP"
        xp.Value = stats.xp
        xp.Parent = leaderstats

        local coins = Instance.new("IntValue")
        coins.Name = "Coins"
        coins.Value = 0
        coins.Parent = leaderstats
    end)

    Players.PlayerRemoving:Connect(function(player)
        RPGStats.saveStats(player)
        playerStats[player] = nil
    end)
end

function RPGStats.addXP(player: Player, amount: number)
    local stats = playerStats[player]
    if not stats then return end

    stats.xp = stats.xp + amount
    while stats.xp >= xpForLevel(stats.level) do
        stats.xp = stats.xp - xpForLevel(stats.level)
        stats.level = stats.level + 1
        stats.str = stats.str + 2
        stats.def = stats.def + 1
        stats.spd = stats.spd + 1
    end

    local leaderstats = player:FindFirstChild("leaderstats")
    if leaderstats then
        local level = leaderstats:FindFirstChild("Level")
        if level then level.Value = stats.level end
        local xp = leaderstats:FindFirstChild("XP")
        if xp then xp.Value = stats.xp end
    end
end

function RPGStats.getStats(player: Player): any?
    return playerStats[player]
end

function RPGStats.loadStats(player: Player): {level: number, xp: number, str: number, def: number, spd: number}
    local default = {level = 1, xp = 0, str = 5, def = 3, spd = 3}
    local success, data = pcall(function()
        local store = DataStoreService:GetDataStore(DATASTORE_KEY)
        return store:GetAsync("player_" .. player.UserId)
    end)
    if success and data then
        return {
            level = data.level or 1, xp = data.xp or 0,
            str = data.str or 5, def = data.def or 3, spd = data.spd or 3,
        }
    end
    return default
end

function RPGStats.saveStats(player: Player)
    local stats = playerStats[player]
    if not stats then return end
    pcall(function()
        local store = DataStoreService:GetDataStore(DATASTORE_KEY)
        store:SetAsync("player_" .. player.UserId, stats)
    end)
end

return RPGStats
''',
    },
    "fps": {
        "WeaponService.server.lua": '''-- WeaponService: FPS weapon handling (equip, fire, reload, damage)
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local WeaponService = {}
WeaponService.__index = WeaponService

local WEAPONS = {
    {id = "pistol", name = "Pistol", damage = 15, fireRate = 0.3, magSize = 12, reloadTime = 1.5, range = 100},
    {id = "rifle", name = "Assault Rifle", damage = 20, fireRate = 0.1, magSize = 30, reloadTime = 2.0, range = 150},
    {id = "shotgun", name = "Shotgun", damage = 50, fireRate = 0.8, magSize = 6, reloadTime = 2.5, range = 30},
    {id = "sniper", name = "Sniper Rifle", damage = 80, fireRate = 1.5, magSize = 5, reloadTime = 3.0, range = 300},
}

local playerWeapons: {[Player]: {equipped: string, ammo: {[string]: number}}} = {}

function WeaponService.init()
    local remotes = Instance.new("Folder")
    remotes.Name = "WeaponRemotes"
    remotes.Parent = ReplicatedStorage

    local fireRemote = Instance.new("RemoteEvent")
    fireRemote.Name = "Fire"
    fireRemote.Parent = remotes

    local reloadRemote = Instance.new("RemoteEvent")
    reloadRemote.Name = "Reload"
    reloadRemote.Parent = remotes

    local equipRemote = Instance.new("RemoteEvent")
    equipRemote.Name = "Equip"
    equipRemote.Parent = remotes

    fireRemote.OnServerEvent:Connect(function(player, direction)
        WeaponService.fire(player, direction)
    end)

    reloadRemote.OnServerEvent:Connect(function(player)
        WeaponService.reload(player)
    end)

    equipRemote.OnServerEvent:Connect(function(player, weaponId)
        WeaponService.equip(player, weaponId)
    end)

    Players.PlayerAdded:Connect(function(player)
        local ammo = {}
        for _, w in WEAPONS do
            ammo[w.id] = w.magSize
        end
        playerWeapons[player] = {equipped = "pistol", ammo = ammo}
    end)

    Players.PlayerRemoving:Connect(function(player)
        playerWeapons[player] = nil
    end)
end

function WeaponService.fire(player: Player, direction: Vector3)
    local data = playerWeapons[player]
    if not data then return end

    local weapon = nil
    for _, w in WEAPONS do
        if w.id == data.equipped then weapon = w; break end
    end
    if not weapon then return end

    if (data.ammo[weapon.id] or 0) <= 0 then return end
    data.ammo[weapon.id] = data.ammo[weapon.id] - 1

    local character = player.Character
    if not character then return end
    local head = character:FindFirstChild("Head")
    if not head then return end

    -- Raycast for hit detection
    local rayParams = RaycastParams.new()
    rayParams.FilterType = Enum.RaycastFilterType.Exclude
    rayParams.FilterDescendantsInstances = {character}

    local result = workspace:Raycast(head.Position, direction.Unit * weapon.range, rayParams)
    if result and result.Instance then
        local hitModel = result.Instance:FindFirstAncestorOfClass("Model")
        if hitModel then
            local humanoid = hitModel:FindFirstChildOfClass("Humanoid")
            if humanoid and humanoid.Health > 0 then
                humanoid:TakeDamage(weapon.damage)

                -- Track kills
                if humanoid.Health <= 0 then
                    local leaderstats = player:FindFirstChild("leaderstats")
                    if leaderstats then
                        local kills = leaderstats:FindFirstChild("Kills")
                        if kills then kills.Value = kills.Value + 1 end
                    end
                end
            end
        end
    end
end

function WeaponService.reload(player: Player)
    local data = playerWeapons[player]
    if not data then return end

    local weapon = nil
    for _, w in WEAPONS do
        if w.id == data.equipped then weapon = w; break end
    end
    if not weapon then return end

    data.ammo[weapon.id] = weapon.magSize
end

function WeaponService.equip(player: Player, weaponId: string)
    local data = playerWeapons[player]
    if not data then return end
    data.equipped = weaponId
end

return WeaponService
''',
        "FPSLeaderboard.server.lua": '''-- FPSLeaderboard: Kill/death tracking and match scoring
local Players = game:GetService("Players")

local FPSLeaderboard = {}
FPSLeaderboard.__index = FPSLeaderboard

function FPSLeaderboard.init()
    Players.PlayerAdded:Connect(function(player)
        local leaderstats = Instance.new("Folder")
        leaderstats.Name = "leaderstats"
        leaderstats.Parent = player

        local kills = Instance.new("IntValue")
        kills.Name = "Kills"
        kills.Value = 0
        kills.Parent = leaderstats

        local deaths = Instance.new("IntValue")
        deaths.Name = "Deaths"
        deaths.Value = 0
        deaths.Parent = leaderstats

        player.CharacterAdded:Connect(function(character)
            local humanoid = character:WaitForChild("Humanoid")
            humanoid.Died:Connect(function()
                deaths.Value = deaths.Value + 1
            end)
        end)
    end)
end

function FPSLeaderboard.addKill(player: Player)
    local leaderstats = player:FindFirstChild("leaderstats")
    if leaderstats then
        local kills = leaderstats:FindFirstChild("Kills")
        if kills then kills.Value = kills.Value + 1 end
    end
end

function FPSLeaderboard.getKDR(player: Player): number
    local leaderstats = player:FindFirstChild("leaderstats")
    if not leaderstats then return 0 end
    local kills = leaderstats:FindFirstChild("Kills")
    local deaths = leaderstats:FindFirstChild("Deaths")
    if not kills or not deaths then return 0 end
    if deaths.Value == 0 then return kills.Value end
    return kills.Value / deaths.Value
end

return FPSLeaderboard
''',
    },
    "survival": {
        "SurvivalManager.server.lua": '''-- SurvivalManager: Day/night cycle, hunger, and survival mechanics
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Lighting = game:GetService("Lighting")

local SurvivalManager = {}
SurvivalManager.__index = SurvivalManager

local DAY_LENGTH = 300 -- seconds for full day/night cycle
local currentTime = 8 -- start at 8 AM (0-24 scale)

local playerSurvival: {[Player]: {hunger: number, thirst: number, health: number}} = {}

function SurvivalManager.init()
    local timeValue = Instance.new("NumberValue")
    timeValue.Name = "GameTime"
    timeValue.Value = currentTime
    timeValue.Parent = ReplicatedStorage

    Players.PlayerAdded:Connect(function(player)
        playerSurvival[player] = {hunger = 100, thirst = 100, health = 100}

        local leaderstats = Instance.new("Folder")
        leaderstats.Name = "leaderstats"
        leaderstats.Parent = player

        local kills = Instance.new("IntValue")
        kills.Name = "Kills"
        kills.Value = 0
        kills.Parent = leaderstats

        local survived = Instance.new("IntValue")
        survived.Name = "Waves"
        survived.Value = 0
        survived.Parent = leaderstats
    end)

    Players.PlayerRemoving:Connect(function(player)
        playerSurvival[player] = nil
    end)

    -- Day/night cycle
    task.spawn(function()
        while true do
            task.wait(1)
            currentTime = currentTime + (24 / DAY_LENGTH)
            if currentTime >= 24 then currentTime = 0 end

            Lighting.ClockTime = currentTime
            local tv = ReplicatedStorage:FindFirstChild("GameTime")
            if tv then tv.Value = currentTime end
        end
    end)

    -- Hunger/thirst drain
    task.spawn(function()
        while true do
            task.wait(10)
            for player, data in playerSurvival do
                data.hunger = math.max(0, data.hunger - 2)
                data.thirst = math.max(0, data.thirst - 3)

                if data.hunger <= 0 or data.thirst <= 0 then
                    local character = player.Character
                    if character then
                        local humanoid = character:FindFirstChildOfClass("Humanoid")
                        if humanoid and humanoid.Health > 0 then
                            humanoid:TakeDamage(5)
                        end
                    end
                end
            end
        end
    end)
end

function SurvivalManager.feed(player: Player, amount: number)
    local data = playerSurvival[player]
    if data then
        data.hunger = math.min(100, data.hunger + amount)
    end
end

function SurvivalManager.drink(player: Player, amount: number)
    local data = playerSurvival[player]
    if data then
        data.thirst = math.min(100, data.thirst + amount)
    end
end

function SurvivalManager.getStatus(player: Player): {hunger: number, thirst: number}?
    return playerSurvival[player]
end

function SurvivalManager.isNight(): boolean
    return currentTime >= 20 or currentTime < 6
end

return SurvivalManager
''',
    },
    "horror": {
        "HorrorManager.server.lua": '''-- HorrorManager: Horror game mechanics (darkness, jumpscares, monster AI)
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Lighting = game:GetService("Lighting")

local HorrorManager = {}
HorrorManager.__index = HorrorManager

local playerState: {[Player]: {sanity: number, hasFlashlight: boolean, keysFound: number}} = {}
local KEYS_TO_ESCAPE = 5

function HorrorManager.init()
    -- Dark ambient lighting
    Lighting.Brightness = 0.2
    Lighting.Ambient = Color3.fromRGB(10, 10, 15)
    Lighting.OutdoorAmbient = Color3.fromRGB(10, 10, 15)
    Lighting.ClockTime = 0
    Lighting.FogEnd = 80
    Lighting.FogColor = Color3.fromRGB(5, 5, 10)

    local remotes = Instance.new("Folder")
    remotes.Name = "HorrorRemotes"
    remotes.Parent = ReplicatedStorage

    local toggleFlashlight = Instance.new("RemoteEvent")
    toggleFlashlight.Name = "ToggleFlashlight"
    toggleFlashlight.Parent = remotes

    local collectKey = Instance.new("RemoteFunction")
    collectKey.Name = "CollectKey"
    collectKey.Parent = remotes

    toggleFlashlight.OnServerEvent:Connect(function(player)
        HorrorManager.toggleFlashlight(player)
    end)

    collectKey.OnServerInvoke = function(player)
        return HorrorManager.pickupKey(player)
    end

    Players.PlayerAdded:Connect(function(player)
        playerState[player] = {sanity = 100, hasFlashlight = true, keysFound = 0}

        player.CharacterAdded:Connect(function(character)
            -- Add flashlight
            local flashlight = Instance.new("SpotLight")
            flashlight.Name = "Flashlight"
            flashlight.Brightness = 2
            flashlight.Range = 40
            flashlight.Angle = 45
            flashlight.Enabled = false

            local head = character:WaitForChild("Head")
            flashlight.Parent = head
        end)
    end)

    Players.PlayerRemoving:Connect(function(player)
        playerState[player] = nil
    end)

    -- Sanity drain in darkness
    task.spawn(function()
        while true do
            task.wait(5)
            for player, state in playerState do
                local character = player.Character
                if character then
                    local head = character:FindFirstChild("Head")
                    if head then
                        local flashlight = head:FindFirstChild("Flashlight")
                        if not flashlight or not flashlight.Enabled then
                            state.sanity = math.max(0, state.sanity - 3)
                        else
                            state.sanity = math.min(100, state.sanity + 1)
                        end
                    end
                end
            end
        end
    end)
end

function HorrorManager.toggleFlashlight(player: Player)
    local state = playerState[player]
    if not state or not state.hasFlashlight then return end

    local character = player.Character
    if not character then return end
    local head = character:FindFirstChild("Head")
    if not head then return end
    local flashlight = head:FindFirstChild("Flashlight")
    if flashlight then
        flashlight.Enabled = not flashlight.Enabled
    end
end

function HorrorManager.pickupKey(player: Player): (boolean, string)
    local state = playerState[player]
    if not state then return false, "No state" end

    state.keysFound = state.keysFound + 1
    if state.keysFound >= KEYS_TO_ESCAPE then
        return true, "You found all keys! Run to the exit!"
    end
    return true, "Key " .. state.keysFound .. "/" .. KEYS_TO_ESCAPE .. " found"
end

function HorrorManager.getSanity(player: Player): number
    local state = playerState[player]
    return state and state.sanity or 0
end

return HorrorManager
''',
    },
    "racing": {
        "RacingService.server.lua": '''-- RacingService: Racing game with laps, checkpoints, and timing
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local RacingService = {}
RacingService.__index = RacingService

local TOTAL_LAPS = 3
local raceState: {[Player]: {lap: number, checkpoint: number, startTime: number, bestTime: number, finished: boolean}} = {}
local totalCheckpoints = 0

function RacingService.init()
    local remotes = Instance.new("Folder")
    remotes.Name = "RacingRemotes"
    remotes.Parent = ReplicatedStorage

    local hitCheckpoint = Instance.new("RemoteEvent")
    hitCheckpoint.Name = "HitCheckpoint"
    hitCheckpoint.Parent = remotes

    hitCheckpoint.OnServerEvent:Connect(function(player, checkpointNum)
        RacingService.onCheckpoint(player, checkpointNum)
    end)

    -- Count checkpoints in workspace
    local checkpoints = workspace:FindFirstChild("Checkpoints")
    if checkpoints then
        totalCheckpoints = #checkpoints:GetChildren()
    end

    Players.PlayerAdded:Connect(function(player)
        raceState[player] = {lap = 0, checkpoint = 0, startTime = 0, bestTime = 0, finished = false}

        local leaderstats = Instance.new("Folder")
        leaderstats.Name = "leaderstats"
        leaderstats.Parent = player

        local lap = Instance.new("IntValue")
        lap.Name = "Lap"
        lap.Value = 0
        lap.Parent = leaderstats

        local best = Instance.new("NumberValue")
        best.Name = "Best"
        best.Value = 0
        best.Parent = leaderstats
    end)

    Players.PlayerRemoving:Connect(function(player)
        raceState[player] = nil
    end)
end

function RacingService.startRace(player: Player)
    local state = raceState[player]
    if not state then return end

    state.lap = 1
    state.checkpoint = 0
    state.startTime = tick()
    state.finished = false

    local leaderstats = player:FindFirstChild("leaderstats")
    if leaderstats then
        local lap = leaderstats:FindFirstChild("Lap")
        if lap then lap.Value = 1 end
    end
end

function RacingService.onCheckpoint(player: Player, checkpointNum: number)
    local state = raceState[player]
    if not state or state.finished then return end

    -- Must hit checkpoints in order
    if checkpointNum ~= state.checkpoint + 1 then return end
    state.checkpoint = checkpointNum

    -- Completed a lap
    if state.checkpoint >= totalCheckpoints then
        state.checkpoint = 0
        state.lap = state.lap + 1

        local leaderstats = player:FindFirstChild("leaderstats")
        if leaderstats then
            local lap = leaderstats:FindFirstChild("Lap")
            if lap then lap.Value = state.lap end
        end

        if state.lap > TOTAL_LAPS then
            local elapsed = tick() - state.startTime
            state.finished = true

            if state.bestTime == 0 or elapsed < state.bestTime then
                state.bestTime = elapsed
                if leaderstats then
                    local best = leaderstats:FindFirstChild("Best")
                    if best then best.Value = math.floor(elapsed * 10) / 10 end
                end
            end
        end
    end
end

function RacingService.getRaceState(player: Player): any?
    return raceState[player]
end

return RacingService
''',
        "VehicleService.server.lua": '''-- VehicleService: Vehicle spawning and management
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local ServerStorage = game:GetService("ServerStorage")

local VehicleService = {}
VehicleService.__index = VehicleService

local playerVehicles: {[Player]: Model?} = {}

local VEHICLE_STATS = {
    {id = "kart", name = "Go-Kart", speed = 60, turnSpeed = 5},
    {id = "sports", name = "Sports Car", speed = 100, turnSpeed = 4},
    {id = "truck", name = "Monster Truck", speed = 45, turnSpeed = 3},
}

function VehicleService.init()
    local remotes = Instance.new("Folder")
    remotes.Name = "VehicleRemotes"
    remotes.Parent = ReplicatedStorage

    local spawnVehicle = Instance.new("RemoteFunction")
    spawnVehicle.Name = "SpawnVehicle"
    spawnVehicle.Parent = remotes

    spawnVehicle.OnServerInvoke = function(player, vehicleId)
        return VehicleService.spawn(player, vehicleId)
    end

    Players.PlayerRemoving:Connect(function(player)
        VehicleService.despawn(player)
        playerVehicles[player] = nil
    end)
end

function VehicleService.spawn(player: Player, vehicleId: string): (boolean, string)
    -- Despawn existing
    VehicleService.despawn(player)

    local vehicleData = nil
    for _, v in VEHICLE_STATS do
        if v.id == vehicleId then vehicleData = v; break end
    end
    if not vehicleData then return false, "Vehicle not found" end

    local character = player.Character
    if not character then return false, "No character" end
    local hrp = character:FindFirstChild("HumanoidRootPart")
    if not hrp then return false, "No root part" end

    -- Look for vehicle template in ServerStorage
    local templates = ServerStorage:FindFirstChild("Vehicles")
    if templates then
        local template = templates:FindFirstChild(vehicleId)
        if template then
            local vehicle = template:Clone()
            vehicle.Name = player.Name .. "_Vehicle"
            vehicle:PivotTo(hrp.CFrame + Vector3.new(0, 5, 10))
            vehicle.Parent = workspace
            playerVehicles[player] = vehicle
            return true, "Spawned " .. vehicleData.name
        end
    end

    return false, "Vehicle template not found in ServerStorage/Vehicles/"
end

function VehicleService.despawn(player: Player)
    local vehicle = playerVehicles[player]
    if vehicle then
        vehicle:Destroy()
        playerVehicles[player] = nil
    end
end

return VehicleService
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
        if cash then cash.Value = cash.Value + amount end
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
        if cash then return cash.Value end
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
        store:SetAsync("player_" .. player.UserId, { cash = cash.Value })
    end)
end

return EconomyService
''',
    "LeaderboardService.server.lua": '''-- LeaderboardService: Manages player stats and leaderboard
local Players = game:GetService("Players")
local DataStoreService = game:GetService("DataStoreService")

local LeaderboardService = {}
LeaderboardService.__index = LeaderboardService

local DATASTORE_KEY = "PlayerStats_v1"

function LeaderboardService.init()
    Players.PlayerAdded:Connect(function(player)
        local leaderstats = player:FindFirstChild("leaderstats")
        if not leaderstats then
            leaderstats = Instance.new("Folder")
            leaderstats.Name = "leaderstats"
            leaderstats.Parent = player
        end

        local stage = Instance.new("IntValue")
        stage.Name = "Stage"
        stage.Value = 1
        stage.Parent = leaderstats

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
            stage = (leaderstats:FindFirstChild("Stage") and leaderstats.Stage.Value) or 1,
        })
    end)
end

function LeaderboardService.setStat(player: Player, statName: string, value: number)
    local leaderstats = player:FindFirstChild("leaderstats")
    if leaderstats then
        local stat = leaderstats:FindFirstChild(statName)
        if stat then stat.Value = value end
    end
end

return LeaderboardService
''',
    "CheckpointService.server.lua": '''-- CheckpointService: Manages player checkpoints and respawning
local Players = game:GetService("Players")

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
    "CraftingService.server.lua": '''-- CraftingService: Item crafting system
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local CraftingService = {}
CraftingService.__index = CraftingService

local RECIPES = {
    {
        id = "iron_sword",
        name = "Iron Sword",
        ingredients = {iron_ore = 3, wood = 1},
        result = "iron_sword",
        resultCount = 1,
    },
    {
        id = "health_potion",
        name = "Health Potion",
        ingredients = {herb = 2, water = 1},
        result = "potion_hp",
        resultCount = 1,
    },
    {
        id = "iron_armor",
        name = "Iron Armor",
        ingredients = {iron_ore = 5, leather = 2},
        result = "iron_armor",
        resultCount = 1,
    },
}

function CraftingService.init()
    local remotes = Instance.new("Folder")
    remotes.Name = "CraftingRemotes"
    remotes.Parent = ReplicatedStorage

    local craftItem = Instance.new("RemoteFunction")
    craftItem.Name = "CraftItem"
    craftItem.Parent = remotes

    local getRecipes = Instance.new("RemoteFunction")
    getRecipes.Name = "GetRecipes"
    getRecipes.Parent = remotes

    craftItem.OnServerInvoke = function(player, recipeId)
        return CraftingService.craft(player, recipeId)
    end

    getRecipes.OnServerInvoke = function(_player)
        return RECIPES
    end
end

function CraftingService.craft(player: Player, recipeId: string): (boolean, string)
    local recipe = nil
    for _, r in RECIPES do
        if r.id == recipeId then recipe = r; break end
    end
    if not recipe then return false, "Recipe not found" end

    -- Check ingredients (requires InventoryService integration)
    -- For now, just return success placeholder
    return true, "Crafted " .. recipe.name
end

function CraftingService.getRecipes(): {}
    return RECIPES
end

return CraftingService
''',
    "GamePassService.server.lua": '''-- GamePassService: Roblox GamePass integration
local Players = game:GetService("Players")
local MarketplaceService = game:GetService("MarketplaceService")

local GamePassService = {}
GamePassService.__index = GamePassService

-- Configure your GamePass IDs here
local GAME_PASSES = {
    {id = 0, name = "VIP", perk = "2x_coins"},
    {id = 0, name = "Speed Boost", perk = "speed_boost"},
    {id = 0, name = "Extra Inventory", perk = "extra_slots"},
}

function GamePassService.init()
    Players.PlayerAdded:Connect(function(player)
        for _, pass in GAME_PASSES do
            if pass.id > 0 then
                local success, owns = pcall(function()
                    return MarketplaceService:UserOwnsGamePassAsync(player.UserId, pass.id)
                end)
                if success and owns then
                    GamePassService.applyPerk(player, pass.perk)
                end
            end
        end
    end)

    MarketplaceService.PromptGamePassPurchaseFinished:Connect(function(player, passId, purchased)
        if purchased then
            for _, pass in GAME_PASSES do
                if pass.id == passId then
                    GamePassService.applyPerk(player, pass.perk)
                    break
                end
            end
        end
    end)
end

function GamePassService.applyPerk(player: Player, perk: string)
    if perk == "2x_coins" then
        player:SetAttribute("CoinMultiplier", 2)
    elseif perk == "speed_boost" then
        local character = player.Character
        if character then
            local humanoid = character:FindFirstChildOfClass("Humanoid")
            if humanoid then humanoid.WalkSpeed = 24 end
        end
    elseif perk == "extra_slots" then
        player:SetAttribute("MaxInventorySlots", 40)
    end
end

function GamePassService.hasPass(player: Player, passId: number): boolean
    local success, owns = pcall(function()
        return MarketplaceService:UserOwnsGamePassAsync(player.UserId, passId)
    end)
    return success and owns or false
end

return GamePassService
''',
    "TradingService.server.lua": '''-- TradingService: Player-to-player item trading
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local TradingService = {}
TradingService.__index = TradingService

local activeTradeRequests: {[Player]: {target: Player, offeredItems: {[string]: number}}} = {}

function TradingService.init()
    local remotes = Instance.new("Folder")
    remotes.Name = "TradingRemotes"
    remotes.Parent = ReplicatedStorage

    local requestTrade = Instance.new("RemoteFunction")
    requestTrade.Name = "RequestTrade"
    requestTrade.Parent = remotes

    local acceptTrade = Instance.new("RemoteFunction")
    acceptTrade.Name = "AcceptTrade"
    acceptTrade.Parent = remotes

    local cancelTrade = Instance.new("RemoteEvent")
    cancelTrade.Name = "CancelTrade"
    cancelTrade.Parent = remotes

    requestTrade.OnServerInvoke = function(player, targetName, offeredItems)
        return TradingService.requestTrade(player, targetName, offeredItems)
    end

    acceptTrade.OnServerInvoke = function(player, requesterName)
        return TradingService.acceptTrade(player, requesterName)
    end

    cancelTrade.OnServerEvent:Connect(function(player)
        activeTradeRequests[player] = nil
    end)

    Players.PlayerRemoving:Connect(function(player)
        activeTradeRequests[player] = nil
    end)
end

function TradingService.requestTrade(player: Player, targetName: string, offeredItems: {[string]: number}): (boolean, string)
    local target = Players:FindFirstChild(targetName)
    if not target then return false, "Player not found" end
    if target == player then return false, "Cannot trade with yourself" end

    activeTradeRequests[player] = {target = target, offeredItems = offeredItems}
    return true, "Trade request sent to " .. targetName
end

function TradingService.acceptTrade(player: Player, requesterName: string): (boolean, string)
    local requester = Players:FindFirstChild(requesterName)
    if not requester then return false, "Requester not found" end

    local request = activeTradeRequests[requester]
    if not request or request.target ~= player then
        return false, "No pending trade request"
    end

    -- Execute trade (requires InventoryService integration)
    activeTradeRequests[requester] = nil
    return true, "Trade completed"
end

return TradingService
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
            SystemType.ECONOMY: "EconomyService.server.lua",
            SystemType.LEADERBOARD: "LeaderboardService.server.lua",
            SystemType.CHECKPOINT: "CheckpointService.server.lua",
            SystemType.CRAFTING: "CraftingService.server.lua",
            SystemType.GAMEPASS: "GamePassService.server.lua",
            SystemType.TRADING: "TradingService.server.lua",
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
