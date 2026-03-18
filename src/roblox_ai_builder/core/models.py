"""Core data models for Roblox AI Builder."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Genre(str, Enum):
    OBBY = "obby"
    TYCOON = "tycoon"
    SIMULATOR = "simulator"
    RPG = "rpg"
    FPS = "fps"
    SURVIVAL = "survival"
    HORROR = "horror"
    RACING = "racing"
    CUSTOM = "custom"


class ScriptType(str, Enum):
    SERVER = "server"
    CLIENT = "client"
    MODULE = "module"


class SystemType(str, Enum):
    INVENTORY = "inventory"
    COMBAT = "combat"
    SHOP = "shop"
    LEADERBOARD = "leaderboard"
    WAVE_SPAWNER = "wave_spawner"
    ECONOMY = "economy"
    CRAFTING = "crafting"
    QUEST = "quest"
    DIALOG = "dialog"
    GAMEPASS = "gamepass"
    DEV_PRODUCT = "dev_product"
    CHECKPOINT = "checkpoint"
    TYCOON_CORE = "tycoon_core"
    PET = "pet"
    TRADING = "trading"


class UIType(str, Enum):
    HUD = "hud"
    SHOP_GUI = "shop_gui"
    INVENTORY_GUI = "inventory_gui"
    MENU = "menu"
    SETTINGS = "settings"
    LEADERBOARD_GUI = "leaderboard_gui"
    DIALOG_GUI = "dialog_gui"
    WAVE_COUNTER = "wave_counter"


GENRE_KEYWORDS: dict[str, Genre] = {
    "obby": Genre.OBBY,
    "obstacle": Genre.OBBY,
    "parkour": Genre.OBBY,
    "장애물": Genre.OBBY,
    "점프맵": Genre.OBBY,
    "tycoon": Genre.TYCOON,
    "타이쿤": Genre.TYCOON,
    "simulator": Genre.SIMULATOR,
    "시뮬레이터": Genre.SIMULATOR,
    "rpg": Genre.RPG,
    "역할": Genre.RPG,
    "fps": Genre.FPS,
    "shooter": Genre.FPS,
    "슈팅": Genre.FPS,
    "총": Genre.FPS,
    "survival": Genre.SURVIVAL,
    "서바이벌": Genre.SURVIVAL,
    "생존": Genre.SURVIVAL,
    "좀비": Genre.SURVIVAL,
    "horror": Genre.HORROR,
    "공포": Genre.HORROR,
    "racing": Genre.RACING,
    "레이싱": Genre.RACING,
}

SYSTEM_KEYWORDS: dict[str, SystemType] = {
    "inventory": SystemType.INVENTORY,
    "인벤토리": SystemType.INVENTORY,
    "아이템": SystemType.INVENTORY,
    "combat": SystemType.COMBAT,
    "전투": SystemType.COMBAT,
    "fight": SystemType.COMBAT,
    "shop": SystemType.SHOP,
    "상점": SystemType.SHOP,
    "store": SystemType.SHOP,
    "leaderboard": SystemType.LEADERBOARD,
    "리더보드": SystemType.LEADERBOARD,
    "순위": SystemType.LEADERBOARD,
    "wave": SystemType.WAVE_SPAWNER,
    "웨이브": SystemType.WAVE_SPAWNER,
    "economy": SystemType.ECONOMY,
    "경제": SystemType.ECONOMY,
    "코인": SystemType.ECONOMY,
    "crafting": SystemType.CRAFTING,
    "제작": SystemType.CRAFTING,
    "quest": SystemType.QUEST,
    "퀘스트": SystemType.QUEST,
    "미션": SystemType.QUEST,
    "dialog": SystemType.DIALOG,
    "대화": SystemType.DIALOG,
    "gamepass": SystemType.GAMEPASS,
    "게임패스": SystemType.GAMEPASS,
    "checkpoint": SystemType.CHECKPOINT,
    "체크포인트": SystemType.CHECKPOINT,
    "pet": SystemType.PET,
    "펫": SystemType.PET,
    "trading": SystemType.TRADING,
    "거래": SystemType.TRADING,
    "교환": SystemType.TRADING,
}

UI_KEYWORDS: dict[str, UIType] = {
    "hud": UIType.HUD,
    "shop_gui": UIType.SHOP_GUI,
    "상점ui": UIType.SHOP_GUI,
    "inventory_gui": UIType.INVENTORY_GUI,
    "인벤토리ui": UIType.INVENTORY_GUI,
    "menu": UIType.MENU,
    "메뉴": UIType.MENU,
    "settings": UIType.SETTINGS,
    "설정": UIType.SETTINGS,
    "leaderboard_gui": UIType.LEADERBOARD_GUI,
    "순위표": UIType.LEADERBOARD_GUI,
}

SYSTEM_DEPENDENCIES: dict[SystemType, list[SystemType]] = {
    SystemType.SHOP: [SystemType.INVENTORY, SystemType.ECONOMY],
    SystemType.CRAFTING: [SystemType.INVENTORY],
    SystemType.GAMEPASS: [SystemType.ECONOMY],
    SystemType.DEV_PRODUCT: [SystemType.ECONOMY],
    SystemType.QUEST: [SystemType.DIALOG],
    SystemType.TRADING: [SystemType.INVENTORY],
    SystemType.WAVE_SPAWNER: [SystemType.COMBAT],
}

SYSTEM_UI_MAPPING: dict[SystemType, list[UIType]] = {
    SystemType.SHOP: [UIType.SHOP_GUI],
    SystemType.INVENTORY: [UIType.INVENTORY_GUI],
    SystemType.LEADERBOARD: [UIType.LEADERBOARD_GUI],
    SystemType.DIALOG: [UIType.DIALOG_GUI],
    SystemType.WAVE_SPAWNER: [UIType.WAVE_COUNTER],
}


@dataclass
class ParsedPrompt:
    """Structured result from prompt parsing."""

    raw: str
    language: str = "en"
    genre: Genre = Genre.CUSTOM
    systems: list[SystemType] = field(default_factory=list)
    ui_requests: list[UIType] = field(default_factory=list)
    asset_hints: list[str] = field(default_factory=list)
    custom_params: dict = field(default_factory=dict)
    game_name: str = ""


@dataclass
class ScriptSpec:
    """Specification for a script to generate."""

    name: str
    script_type: ScriptType
    description: str = ""
    dependencies: list[str] = field(default_factory=list)
    systems: list[SystemType] = field(default_factory=list)


@dataclass
class GamePlan:
    """Complete game generation plan."""

    genre: Genre
    preset_id: str
    game_name: str
    scripts: list[ScriptSpec] = field(default_factory=list)
    ui_specs: list[UIType] = field(default_factory=list)
    systems: list[SystemType] = field(default_factory=list)
    asset_hints: list[str] = field(default_factory=list)
    custom_params: dict = field(default_factory=dict)


@dataclass
class GeneratedFile:
    """A single generated file."""

    path: str
    content: str
    source: str = "ai"  # "ai" | "preset" | "template"


@dataclass
class GeneratedProject:
    """Complete generated project."""

    name: str
    genre: Genre
    files: list[GeneratedFile] = field(default_factory=list)
    asset_guide: str = ""
    readme: str = ""
    metadata: dict = field(default_factory=dict)
