"""Test prompt definitions across complexity levels.

Each prompt defines:
- id: unique test identifier
- level: "simple" | "medium" | "full"
- prompt: the natural language input
- expected_genre: expected Genre enum value
- min_systems: minimum number of game systems expected
- min_files: minimum number of output files expected
- expected_systems: list of SystemType values expected to be detected
- description: human-readable description
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class TestPrompt:
    """A test prompt with expected outcomes."""

    id: str
    level: str  # "simple" | "medium" | "full"
    prompt: str
    expected_genre: str
    min_systems: int
    min_files: int
    expected_systems: list[str] = field(default_factory=list)
    description: str = ""


# ─── SIMPLE: Single-domain prompts (1-2 systems) ──────────────────────

SIMPLE_PROMPTS = [
    TestPrompt(
        id="simple-obby-01",
        level="simple",
        prompt="Make a simple obstacle course game",
        expected_genre="obby",
        min_systems=1,
        min_files=3,
        expected_systems=["checkpoint"],
        description="Basic obby with minimal systems",
    ),
    TestPrompt(
        id="simple-tycoon-01",
        level="simple",
        prompt="Create a basic tycoon game",
        expected_genre="tycoon",
        min_systems=1,
        min_files=3,
        expected_systems=["tycoon_core"],
        description="Basic tycoon with core mechanics only",
    ),
    TestPrompt(
        id="simple-fps-01",
        level="simple",
        prompt="Build a shooter arena game",
        expected_genre="fps",
        min_systems=1,
        min_files=3,
        expected_systems=["combat"],
        description="Basic FPS with combat only",
    ),
    TestPrompt(
        id="simple-racing-01",
        level="simple",
        prompt="Make a racing game with checkpoints",
        expected_genre="racing",
        min_systems=1,
        min_files=3,
        expected_systems=["checkpoint"],
        description="Basic racing with checkpoints",
    ),
    TestPrompt(
        id="simple-horror-01",
        level="simple",
        prompt="Create a horror escape room",
        expected_genre="horror",
        min_systems=1,
        min_files=3,
        expected_systems=["dialog"],
        description="Basic horror with dialog",
    ),
]

# ─── MEDIUM: Multi-domain prompts (3-6 systems) ───────────────────────

MEDIUM_PROMPTS = [
    TestPrompt(
        id="medium-survival-01",
        level="medium",
        prompt="Make a zombie survival game with inventory, combat, and wave spawner",
        expected_genre="survival",
        min_systems=3,
        min_files=6,
        expected_systems=["combat", "inventory", "wave_spawner"],
        description="Survival with combat + inventory + waves",
    ),
    TestPrompt(
        id="medium-rpg-01",
        level="medium",
        prompt="Create an RPG adventure with quests, dialog, and combat system",
        expected_genre="rpg",
        min_systems=3,
        min_files=6,
        expected_systems=["quest", "dialog", "combat"],
        description="RPG with quest + dialog + combat",
    ),
    TestPrompt(
        id="medium-tycoon-02",
        level="medium",
        prompt="Build a restaurant tycoon with economy, shop, and leaderboard",
        expected_genre="tycoon",
        min_systems=3,
        min_files=6,
        expected_systems=["economy", "shop", "leaderboard"],
        description="Tycoon with economy + shop + leaderboard",
    ),
    TestPrompt(
        id="medium-simulator-01",
        level="medium",
        prompt="Create a mining simulator with pets, economy, and inventory",
        expected_genre="simulator",
        min_systems=3,
        min_files=6,
        expected_systems=["pet", "economy", "inventory"],
        description="Simulator with pets + economy + inventory",
    ),
    TestPrompt(
        id="medium-obby-02",
        level="medium",
        prompt="Make an obstacle course with leaderboard, checkpoint system, and shop for skins",
        expected_genre="obby",
        min_systems=3,
        min_files=6,
        expected_systems=["leaderboard", "checkpoint", "shop"],
        description="Obby with leaderboard + checkpoint + shop",
    ),
]

# ─── FULL: 10+ domain prompts (MyWorldZoo-level complexity) ───────────

FULL_PROMPTS = [
    TestPrompt(
        id="full-zoo-sim-01",
        level="full",
        prompt=(
            "Create a zoo simulator game like MyWorldZoo. Include: animal collection with "
            "inventory system, pet management, economy with coins and gems, shop for buying "
            "animals, quest system with daily missions, leaderboard for best zoos, crafting "
            "for building facilities, dialog system for NPCs, gamepass support for VIP perks, "
            "and a trading system between players."
        ),
        expected_genre="simulator",
        min_systems=10,
        min_files=15,
        expected_systems=[
            "inventory", "pet", "economy", "shop", "quest",
            "leaderboard", "crafting", "dialog", "gamepass", "trading",
        ],
        description="Full zoo simulator (MyWorldZoo complexity)",
    ),
    TestPrompt(
        id="full-survival-rpg-01",
        level="full",
        prompt=(
            "Build a massive survival RPG game. Need combat system with weapons and armor, "
            "inventory for item management, economy with gold, shop to buy equipment, "
            "wave spawner for zombie hordes, quest system with story missions, dialog for "
            "NPC conversations, leaderboard ranking, crafting system to make weapons, "
            "pet companions that fight with you, and a trading marketplace."
        ),
        expected_genre="survival",
        min_systems=10,
        min_files=15,
        expected_systems=[
            "combat", "inventory", "economy", "shop", "wave_spawner",
            "quest", "dialog", "leaderboard", "crafting", "pet", "trading",
        ],
        description="Full survival RPG (10+ domains)",
    ),
    TestPrompt(
        id="full-tycoon-01",
        level="full",
        prompt=(
            "Make a pizza restaurant tycoon with full features: tycoon core mechanics with "
            "dropper and conveyor, economy system with cash and premium currency, shop for "
            "upgrades, inventory management for recipes, quest system for challenges, "
            "leaderboard for richest players, dialog for customer orders, gamepass for "
            "2x earnings, dev products for instant cash, pet helpers that cook, crafting "
            "for new recipes."
        ),
        expected_genre="tycoon",
        min_systems=10,
        min_files=15,
        expected_systems=[
            "tycoon_core", "economy", "shop", "inventory", "quest",
            "leaderboard", "dialog", "gamepass", "dev_product", "pet", "crafting",
        ],
        description="Full pizza tycoon (10+ domains)",
    ),
    TestPrompt(
        id="full-korean-01",
        level="full",
        prompt=(
            "동물원 시뮬레이터 게임을 만들어주세요. 인벤토리 시스템, 펫 시스템, "
            "경제 시스템(코인과 젬), 상점, 퀘스트 시스템, 리더보드, 제작 시스템, "
            "대화 시스템, 게임패스 지원, 그리고 거래 시스템이 필요합니다."
        ),
        expected_genre="simulator",
        min_systems=10,
        min_files=15,
        expected_systems=[
            "inventory", "pet", "economy", "shop", "quest",
            "leaderboard", "crafting", "dialog", "gamepass",
        ],
        description="Full simulator in Korean (i18n test)",
    ),
]

# ─── All prompts combined ─────────────────────────────────────────────

ALL_PROMPTS = SIMPLE_PROMPTS + MEDIUM_PROMPTS + FULL_PROMPTS


def get_prompts_by_level(level: str) -> list[TestPrompt]:
    """Get test prompts filtered by complexity level."""
    if level == "all":
        return ALL_PROMPTS
    return [p for p in ALL_PROMPTS if p.level == level]
