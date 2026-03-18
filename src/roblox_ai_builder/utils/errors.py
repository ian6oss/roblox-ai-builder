"""Error types for Roblox AI Builder."""


class RABError(Exception):
    """Base error for Roblox AI Builder."""


class PromptParseError(RABError):
    """Failed to parse user prompt."""


class AIGenerationError(RABError):
    """AI code generation failed."""


class PresetNotFoundError(RABError):
    """Requested preset not found."""


class APIKeyError(RABError):
    """API key not configured or invalid."""


class RojoWriteError(RABError):
    """Failed to write Rojo project files."""
