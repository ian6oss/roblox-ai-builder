-- SimulatorCore: Core simulator loop (click/tap to earn, zones, rebirths)
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
