-- InventoryService: Player inventory management
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
