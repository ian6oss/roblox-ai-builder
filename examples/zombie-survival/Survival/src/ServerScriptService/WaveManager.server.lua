-- WaveManager: Wave-based enemy spawning system
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local WaveManager = {}
WaveManager.__index = WaveManager

local currentWave = 0
local enemiesAlive = 0
local isWaveActive = false

local WAVE_CONFIG = {
    baseEnemies = 5,
    enemiesPerWave = 3,
    spawnDelay = 1.5,
    waveDelay = 10,
    maxWaves = 0, -- 0 = infinite
}

function WaveManager.init()
    local waveValue = Instance.new("IntValue")
    waveValue.Name = "CurrentWave"
    waveValue.Value = 0
    waveValue.Parent = ReplicatedStorage

    local enemyCount = Instance.new("IntValue")
    enemyCount.Name = "EnemiesAlive"
    enemyCount.Value = 0
    enemyCount.Parent = ReplicatedStorage

    -- Auto-start when players join
    Players.PlayerAdded:Connect(function(_player)
        if not isWaveActive and #Players:GetPlayers() > 0 then
            task.wait(5)
            WaveManager.startNextWave()
        end
    end)
end

function WaveManager.startNextWave()
    if isWaveActive then return end

    currentWave = currentWave + 1
    isWaveActive = true

    local waveValue = ReplicatedStorage:FindFirstChild("CurrentWave")
    if waveValue then
        waveValue.Value = currentWave
    end

    local enemyCount = WAVE_CONFIG.baseEnemies + (currentWave - 1) * WAVE_CONFIG.enemiesPerWave
    enemiesAlive = enemyCount

    local enemyCountValue = ReplicatedStorage:FindFirstChild("EnemiesAlive")
    if enemyCountValue then
        enemyCountValue.Value = enemiesAlive
    end

    -- Spawn enemies
    for i = 1, enemyCount do
        task.wait(WAVE_CONFIG.spawnDelay)
        WaveManager.spawnEnemy()
    end
end

function WaveManager.spawnEnemy()
    local spawnPoints = workspace:FindFirstChild("EnemySpawns")
    if not spawnPoints then return end

    local spawns = spawnPoints:GetChildren()
    if #spawns == 0 then return end

    local spawn = spawns[math.random(1, #spawns)]

    -- Create basic enemy
    local enemy = Instance.new("Model")
    enemy.Name = "Enemy_Wave" .. currentWave

    local part = Instance.new("Part")
    part.Name = "HumanoidRootPart"
    part.Size = Vector3.new(2, 5, 2)
    part.Position = spawn.Position + Vector3.new(0, 3, 0)
    part.Anchored = false
    part.BrickColor = BrickColor.new("Bright red")
    part.Parent = enemy

    local humanoid = Instance.new("Humanoid")
    humanoid.MaxHealth = 50 + currentWave * 10
    humanoid.Health = humanoid.MaxHealth
    humanoid.WalkSpeed = 12 + currentWave
    humanoid.Parent = enemy

    humanoid.Died:Connect(function()
        WaveManager.onEnemyDied(enemy)
    end)

    enemy.PrimaryPart = part
    enemy.Parent = workspace
end

function WaveManager.onEnemyDied(enemy: Model)
    enemiesAlive = enemiesAlive - 1

    local enemyCountValue = ReplicatedStorage:FindFirstChild("EnemiesAlive")
    if enemyCountValue then
        enemyCountValue.Value = enemiesAlive
    end

    task.wait(1)
    enemy:Destroy()

    if enemiesAlive <= 0 then
        isWaveActive = false
        task.wait(WAVE_CONFIG.waveDelay)
        WaveManager.startNextWave()
    end
end

function WaveManager.getCurrentWave(): number
    return currentWave
end

return WaveManager
