-- ShopService: In-game shop for buying items
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
