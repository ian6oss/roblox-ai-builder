-- HUD: Heads-up display showing player stats
local Players = game:GetService("Players")
local player = Players.LocalPlayer

local screenGui = Instance.new("ScreenGui")
screenGui.Name = "HUD"
screenGui.ResetOnSpawn = false
screenGui.Parent = player:WaitForChild("PlayerGui")

-- Health bar
local healthFrame = Instance.new("Frame")
healthFrame.Name = "HealthBar"
healthFrame.Size = UDim2.new(0.2, 0, 0.03, 0)
healthFrame.Position = UDim2.new(0.01, 0, 0.95, 0)
healthFrame.BackgroundColor3 = Color3.fromRGB(40, 40, 40)
healthFrame.BorderSizePixel = 0
healthFrame.Parent = screenGui

local healthCorner = Instance.new("UICorner")
healthCorner.CornerRadius = UDim.new(0, 4)
healthCorner.Parent = healthFrame

local healthFill = Instance.new("Frame")
healthFill.Name = "Fill"
healthFill.Size = UDim2.new(1, 0, 1, 0)
healthFill.BackgroundColor3 = Color3.fromRGB(0, 200, 0)
healthFill.BorderSizePixel = 0
healthFill.Parent = healthFrame

local fillCorner = Instance.new("UICorner")
fillCorner.CornerRadius = UDim.new(0, 4)
fillCorner.Parent = healthFill

-- Stats display
local statsFrame = Instance.new("Frame")
statsFrame.Name = "Stats"
statsFrame.Size = UDim2.new(0.15, 0, 0.05, 0)
statsFrame.Position = UDim2.new(0.85, 0, 0.01, 0)
statsFrame.BackgroundTransparency = 0.5
statsFrame.BackgroundColor3 = Color3.fromRGB(0, 0, 0)
statsFrame.BorderSizePixel = 0
statsFrame.Parent = screenGui

local statsCorner = Instance.new("UICorner")
statsCorner.CornerRadius = UDim.new(0, 8)
statsCorner.Parent = statsFrame

local statsLabel = Instance.new("TextLabel")
statsLabel.Name = "StatsText"
statsLabel.Size = UDim2.new(1, -10, 1, 0)
statsLabel.Position = UDim2.new(0, 5, 0, 0)
statsLabel.BackgroundTransparency = 1
statsLabel.TextColor3 = Color3.fromRGB(255, 255, 255)
statsLabel.TextScaled = true
statsLabel.Font = Enum.Font.GothamBold
statsLabel.Text = "$ 0"
statsLabel.TextXAlignment = Enum.TextXAlignment.Right
statsLabel.Parent = statsFrame

-- Update health bar
local function updateHealth()
    local character = player.Character
    if not character then return end
    local humanoid = character:FindFirstChildOfClass("Humanoid")
    if not humanoid then return end

    local ratio = humanoid.Health / humanoid.MaxHealth
    healthFill.Size = UDim2.new(ratio, 0, 1, 0)

    if ratio > 0.5 then
        healthFill.BackgroundColor3 = Color3.fromRGB(0, 200, 0)
    elseif ratio > 0.25 then
        healthFill.BackgroundColor3 = Color3.fromRGB(255, 165, 0)
    else
        healthFill.BackgroundColor3 = Color3.fromRGB(255, 0, 0)
    end
end

player.CharacterAdded:Connect(function(character)
    local humanoid = character:WaitForChild("Humanoid")
    humanoid.HealthChanged:Connect(updateHealth)
    updateHealth()
end)

-- Update stats from leaderstats
local function updateStats()
    local leaderstats = player:FindFirstChild("leaderstats")
    if not leaderstats then return end

    local cash = leaderstats:FindFirstChild("Cash")
    if cash then
        statsLabel.Text = "$ " .. tostring(cash.Value)
    end
end

player:GetPropertyChangedSignal("leaderstats"):Connect(updateStats)
task.spawn(function()
    while task.wait(1) do
        updateStats()
    end
end)
