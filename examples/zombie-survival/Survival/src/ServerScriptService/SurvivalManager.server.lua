-- SurvivalManager: Day/night cycle, hunger, and survival mechanics
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
