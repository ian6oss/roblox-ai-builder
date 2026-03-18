"""UI builder - generates Roblox ScreenGui code."""

from __future__ import annotations

from roblox_ai_builder.core.models import GeneratedFile, Genre, UIType


# Pre-built UI templates
UI_TEMPLATES: dict[UIType, str] = {
    UIType.HUD: '''-- HUD: Heads-up display showing player stats
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
''',
    UIType.SHOP_GUI: '''-- ShopGui: In-game shop interface
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local player = Players.LocalPlayer

local screenGui = Instance.new("ScreenGui")
screenGui.Name = "ShopGui"
screenGui.ResetOnSpawn = false
screenGui.Enabled = false
screenGui.Parent = player:WaitForChild("PlayerGui")

-- Main frame
local mainFrame = Instance.new("Frame")
mainFrame.Name = "MainFrame"
mainFrame.Size = UDim2.new(0.5, 0, 0.6, 0)
mainFrame.Position = UDim2.new(0.25, 0, 0.2, 0)
mainFrame.BackgroundColor3 = Color3.fromRGB(30, 30, 40)
mainFrame.BorderSizePixel = 0
mainFrame.Parent = screenGui

local corner = Instance.new("UICorner")
corner.CornerRadius = UDim.new(0, 12)
corner.Parent = mainFrame

-- Title
local title = Instance.new("TextLabel")
title.Name = "Title"
title.Size = UDim2.new(1, 0, 0.1, 0)
title.BackgroundTransparency = 1
title.TextColor3 = Color3.fromRGB(255, 215, 0)
title.TextScaled = true
title.Font = Enum.Font.GothamBold
title.Text = "SHOP"
title.Parent = mainFrame

-- Close button
local closeBtn = Instance.new("TextButton")
closeBtn.Name = "CloseButton"
closeBtn.Size = UDim2.new(0.06, 0, 0.08, 0)
closeBtn.Position = UDim2.new(0.93, 0, 0.01, 0)
closeBtn.BackgroundColor3 = Color3.fromRGB(200, 50, 50)
closeBtn.TextColor3 = Color3.fromRGB(255, 255, 255)
closeBtn.Text = "X"
closeBtn.Font = Enum.Font.GothamBold
closeBtn.TextScaled = true
closeBtn.BorderSizePixel = 0
closeBtn.Parent = mainFrame

local closeCorner = Instance.new("UICorner")
closeCorner.CornerRadius = UDim.new(0, 6)
closeCorner.Parent = closeBtn

-- Scroll frame for items
local scrollFrame = Instance.new("ScrollingFrame")
scrollFrame.Name = "ItemList"
scrollFrame.Size = UDim2.new(0.9, 0, 0.8, 0)
scrollFrame.Position = UDim2.new(0.05, 0, 0.15, 0)
scrollFrame.BackgroundTransparency = 1
scrollFrame.ScrollBarThickness = 6
scrollFrame.Parent = mainFrame

local listLayout = Instance.new("UIListLayout")
listLayout.Padding = UDim.new(0, 8)
listLayout.Parent = scrollFrame

-- Toggle shop
closeBtn.MouseButton1Click:Connect(function()
    screenGui.Enabled = false
end)

-- Create item buttons from shop data
local function createItemButton(item: {id: string, name: string, price: number})
    local btn = Instance.new("TextButton")
    btn.Name = item.id
    btn.Size = UDim2.new(1, 0, 0, 50)
    btn.BackgroundColor3 = Color3.fromRGB(50, 50, 65)
    btn.TextColor3 = Color3.fromRGB(255, 255, 255)
    btn.Font = Enum.Font.Gotham
    btn.TextScaled = true
    btn.Text = string.format("%s - $%d", item.name, item.price)
    btn.BorderSizePixel = 0
    btn.Parent = scrollFrame

    local btnCorner = Instance.new("UICorner")
    btnCorner.CornerRadius = UDim.new(0, 8)
    btnCorner.Parent = btn

    btn.MouseButton1Click:Connect(function()
        local remotes = ReplicatedStorage:FindFirstChild("ShopRemotes")
        if remotes then
            local buyFunc = remotes:FindFirstChild("BuyItem")
            if buyFunc then
                local success, msg = buyFunc:InvokeServer(item.id)
                if success then
                    btn.BackgroundColor3 = Color3.fromRGB(0, 150, 0)
                    task.wait(0.5)
                    btn.BackgroundColor3 = Color3.fromRGB(50, 50, 65)
                end
            end
        end
    end)
end

-- Load shop items
task.spawn(function()
    task.wait(2)
    local remotes = ReplicatedStorage:WaitForChild("ShopRemotes", 10)
    if remotes then
        local getItems = remotes:FindFirstChild("GetShopItems")
        if getItems then
            local items = getItems:InvokeServer()
            for _, item in items do
                createItemButton(item)
            end
        end
    end
end)

-- Keybind to toggle shop (B key)
local UserInputService = game:GetService("UserInputService")
UserInputService.InputBegan:Connect(function(input, gameProcessed)
    if gameProcessed then return end
    if input.KeyCode == Enum.KeyCode.B then
        screenGui.Enabled = not screenGui.Enabled
    end
end)
''',
    UIType.INVENTORY_GUI: '''-- InventoryGui: Player inventory display
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local player = Players.LocalPlayer

local screenGui = Instance.new("ScreenGui")
screenGui.Name = "InventoryGui"
screenGui.ResetOnSpawn = false
screenGui.Enabled = false
screenGui.Parent = player:WaitForChild("PlayerGui")

-- Main frame
local mainFrame = Instance.new("Frame")
mainFrame.Name = "MainFrame"
mainFrame.Size = UDim2.new(0.4, 0, 0.5, 0)
mainFrame.Position = UDim2.new(0.3, 0, 0.25, 0)
mainFrame.BackgroundColor3 = Color3.fromRGB(30, 30, 40)
mainFrame.BorderSizePixel = 0
mainFrame.Parent = screenGui

local corner = Instance.new("UICorner")
corner.CornerRadius = UDim.new(0, 12)
corner.Parent = mainFrame

-- Title
local title = Instance.new("TextLabel")
title.Size = UDim2.new(1, 0, 0.12, 0)
title.BackgroundTransparency = 1
title.TextColor3 = Color3.fromRGB(255, 255, 255)
title.TextScaled = true
title.Font = Enum.Font.GothamBold
title.Text = "INVENTORY"
title.Parent = mainFrame

-- Close button
local closeBtn = Instance.new("TextButton")
closeBtn.Size = UDim2.new(0.08, 0, 0.1, 0)
closeBtn.Position = UDim2.new(0.91, 0, 0.01, 0)
closeBtn.BackgroundColor3 = Color3.fromRGB(200, 50, 50)
closeBtn.TextColor3 = Color3.fromRGB(255, 255, 255)
closeBtn.Text = "X"
closeBtn.Font = Enum.Font.GothamBold
closeBtn.TextScaled = true
closeBtn.BorderSizePixel = 0
closeBtn.Parent = mainFrame

local closeCorner = Instance.new("UICorner")
closeCorner.CornerRadius = UDim.new(0, 6)
closeCorner.Parent = closeBtn

-- Grid for items
local gridFrame = Instance.new("Frame")
gridFrame.Size = UDim2.new(0.9, 0, 0.8, 0)
gridFrame.Position = UDim2.new(0.05, 0, 0.15, 0)
gridFrame.BackgroundTransparency = 1
gridFrame.Parent = mainFrame

local gridLayout = Instance.new("UIGridLayout")
gridLayout.CellSize = UDim2.new(0, 60, 0, 60)
gridLayout.CellPadding = UDim2.new(0, 8, 0, 8)
gridLayout.Parent = gridFrame

closeBtn.MouseButton1Click:Connect(function()
    screenGui.Enabled = false
end)

-- Refresh inventory display
local function refreshInventory()
    for _, child in gridFrame:GetChildren() do
        if child:IsA("Frame") then
            child:Destroy()
        end
    end

    local remotes = ReplicatedStorage:FindFirstChild("InventoryRemotes")
    if not remotes then return end

    local getInv = remotes:FindFirstChild("GetInventory")
    if not getInv then return end

    local inventory = getInv:InvokeServer()
    for itemId, count in inventory do
        local slot = Instance.new("Frame")
        slot.BackgroundColor3 = Color3.fromRGB(50, 50, 65)
        slot.BorderSizePixel = 0
        slot.Parent = gridFrame

        local slotCorner = Instance.new("UICorner")
        slotCorner.CornerRadius = UDim.new(0, 8)
        slotCorner.Parent = slot

        local label = Instance.new("TextLabel")
        label.Size = UDim2.new(1, 0, 0.7, 0)
        label.BackgroundTransparency = 1
        label.TextColor3 = Color3.fromRGB(255, 255, 255)
        label.TextScaled = true
        label.Font = Enum.Font.Gotham
        label.Text = itemId
        label.Parent = slot

        local countLabel = Instance.new("TextLabel")
        countLabel.Size = UDim2.new(1, 0, 0.3, 0)
        countLabel.Position = UDim2.new(0, 0, 0.7, 0)
        countLabel.BackgroundTransparency = 1
        countLabel.TextColor3 = Color3.fromRGB(200, 200, 200)
        countLabel.TextScaled = true
        countLabel.Font = Enum.Font.Gotham
        countLabel.Text = "x" .. tostring(count)
        countLabel.Parent = slot
    end
end

-- Toggle with I key
local UserInputService = game:GetService("UserInputService")
UserInputService.InputBegan:Connect(function(input, gameProcessed)
    if gameProcessed then return end
    if input.KeyCode == Enum.KeyCode.I then
        screenGui.Enabled = not screenGui.Enabled
        if screenGui.Enabled then
            refreshInventory()
        end
    end
end)
''',
    UIType.WAVE_COUNTER: '''-- WaveCounter: Display current wave and enemies remaining
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
''',
    UIType.MENU: '''-- MainMenu: Game start menu
local Players = game:GetService("Players")
local player = Players.LocalPlayer

local screenGui = Instance.new("ScreenGui")
screenGui.Name = "MainMenu"
screenGui.ResetOnSpawn = false
screenGui.Parent = player:WaitForChild("PlayerGui")

local frame = Instance.new("Frame")
frame.Size = UDim2.new(1, 0, 1, 0)
frame.BackgroundColor3 = Color3.fromRGB(20, 20, 30)
frame.BackgroundTransparency = 0.3
frame.BorderSizePixel = 0
frame.Parent = screenGui

local title = Instance.new("TextLabel")
title.Size = UDim2.new(0.6, 0, 0.15, 0)
title.Position = UDim2.new(0.2, 0, 0.2, 0)
title.BackgroundTransparency = 1
title.TextColor3 = Color3.fromRGB(255, 255, 255)
title.TextScaled = true
title.Font = Enum.Font.GothamBold
title.Text = "GAME TITLE"
title.Parent = frame

local playBtn = Instance.new("TextButton")
playBtn.Size = UDim2.new(0.2, 0, 0.08, 0)
playBtn.Position = UDim2.new(0.4, 0, 0.5, 0)
playBtn.BackgroundColor3 = Color3.fromRGB(0, 150, 0)
playBtn.TextColor3 = Color3.fromRGB(255, 255, 255)
playBtn.Text = "PLAY"
playBtn.Font = Enum.Font.GothamBold
playBtn.TextScaled = true
playBtn.BorderSizePixel = 0
playBtn.Parent = frame

local playCorner = Instance.new("UICorner")
playCorner.CornerRadius = UDim.new(0, 8)
playCorner.Parent = playBtn

playBtn.MouseButton1Click:Connect(function()
    screenGui:Destroy()
end)
''',
    UIType.LEADERBOARD_GUI: '''-- LeaderboardGui: Custom leaderboard display
-- Uses default Roblox leaderboard (leaderstats folder)
-- This script is a placeholder for custom leaderboard UI if needed
local Players = game:GetService("Players")
print("[LeaderboardGui] Using default Roblox leaderboard via leaderstats")
''',
    UIType.SETTINGS: '''-- Settings GUI placeholder
local Players = game:GetService("Players")
local player = Players.LocalPlayer
print("[SettingsGui] Settings GUI initialized for " .. player.Name)
''',
}


class UIBuilder:
    """Generates Roblox ScreenGui code from UI specifications."""

    def __init__(self, ai_client: AIClient | None = None):
        self.ai_client = ai_client

    async def generate(
        self,
        ui_specs: list[UIType],
        genre: Genre,
    ) -> list[GeneratedFile]:
        """Generate UI Luau scripts from specifications."""
        files: list[GeneratedFile] = []

        for ui_type in ui_specs:
            if ui_type in UI_TEMPLATES:
                code = UI_TEMPLATES[ui_type]
                source = "template"
            else:
                code = self._minimal_ui(ui_type)
                source = "fallback"

            filename = self._ui_to_filename(ui_type)
            files.append(
                GeneratedFile(
                    path=f"src/StarterGui/{filename}",
                    content=code,
                    source=source,
                )
            )

        return files

    @staticmethod
    def _ui_to_filename(ui_type: UIType) -> str:
        """Convert UIType to filename."""
        name_map = {
            UIType.HUD: "HUD.client.lua",
            UIType.SHOP_GUI: "ShopGui.client.lua",
            UIType.INVENTORY_GUI: "InventoryGui.client.lua",
            UIType.MENU: "MainMenu.client.lua",
            UIType.SETTINGS: "Settings.client.lua",
            UIType.LEADERBOARD_GUI: "LeaderboardGui.client.lua",
            UIType.DIALOG_GUI: "DialogGui.client.lua",
            UIType.WAVE_COUNTER: "WaveCounter.client.lua",
        }
        return name_map.get(ui_type, f"{ui_type.value}.client.lua")

    @staticmethod
    def _minimal_ui(ui_type: UIType) -> str:
        """Generate minimal UI placeholder."""
        return f"""-- {ui_type.value}: Auto-generated placeholder
local Players = game:GetService("Players")
local player = Players.LocalPlayer

local screenGui = Instance.new("ScreenGui")
screenGui.Name = "{ui_type.value}"
screenGui.ResetOnSpawn = false
screenGui.Parent = player:WaitForChild("PlayerGui")

print("[{ui_type.value}] UI initialized")
"""
