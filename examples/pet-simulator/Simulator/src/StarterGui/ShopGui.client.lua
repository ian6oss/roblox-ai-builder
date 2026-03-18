-- ShopGui: In-game shop interface
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
