-- InventoryGui: Player inventory display
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
