-- WaveCounter: Display current wave and enemies remaining
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local player = Players.LocalPlayer

local screenGui = Instance.new("ScreenGui")
screenGui.Name = "WaveCounter"
screenGui.ResetOnSpawn = false
screenGui.Parent = player:WaitForChild("PlayerGui")

local frame = Instance.new("Frame")
frame.Size = UDim2.new(0.15, 0, 0.08, 0)
frame.Position = UDim2.new(0.425, 0, 0.01, 0)
frame.BackgroundTransparency = 0.3
frame.BackgroundColor3 = Color3.fromRGB(0, 0, 0)
frame.BorderSizePixel = 0
frame.Parent = screenGui

local frameCorner = Instance.new("UICorner")
frameCorner.CornerRadius = UDim.new(0, 8)
frameCorner.Parent = frame

local waveLabel = Instance.new("TextLabel")
waveLabel.Size = UDim2.new(1, 0, 0.5, 0)
waveLabel.BackgroundTransparency = 1
waveLabel.TextColor3 = Color3.fromRGB(255, 100, 100)
waveLabel.TextScaled = true
waveLabel.Font = Enum.Font.GothamBold
waveLabel.Text = "WAVE 0"
waveLabel.Parent = frame

local enemyLabel = Instance.new("TextLabel")
enemyLabel.Size = UDim2.new(1, 0, 0.5, 0)
enemyLabel.Position = UDim2.new(0, 0, 0.5, 0)
enemyLabel.BackgroundTransparency = 1
enemyLabel.TextColor3 = Color3.fromRGB(200, 200, 200)
enemyLabel.TextScaled = true
enemyLabel.Font = Enum.Font.Gotham
enemyLabel.Text = "Enemies: 0"
enemyLabel.Parent = frame

-- Listen for wave changes
task.spawn(function()
    local waveValue = ReplicatedStorage:WaitForChild("CurrentWave", 30)
    if waveValue then
        waveValue.Changed:Connect(function(newWave)
            waveLabel.Text = "WAVE " .. tostring(newWave)
        end)
    end

    local enemyCount = ReplicatedStorage:WaitForChild("EnemiesAlive", 30)
    if enemyCount then
        enemyCount.Changed:Connect(function(newCount)
            enemyLabel.Text = "Enemies: " .. tostring(newCount)
        end)
    end
end)
