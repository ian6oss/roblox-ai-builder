-- PetService: Pet collection, equipping, and following
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
