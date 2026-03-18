-- CombatService: Combat mechanics (damage, health, death)
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
