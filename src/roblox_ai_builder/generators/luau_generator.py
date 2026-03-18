"""Luau script generator using Claude API."""

from __future__ import annotations

from roblox_ai_builder.core.models import (
    GamePlan,
    GeneratedFile,
    ScriptSpec,
    ScriptType,
)
from roblox_ai_builder.utils.ai_client import AIClient
from roblox_ai_builder.utils.errors import AIGenerationError


LUAU_SYSTEM_PROMPT = """You are a Roblox Luau expert developer. Generate production-quality
Luau scripts for Roblox games.

STRICT RULES:
1. Use modern Luau syntax with type annotations
2. Follow Roblox conventions: PascalCase for modules, camelCase for variables/functions
3. Use proper services: game:GetService("Players"), game:GetService("ReplicatedStorage"), etc.
4. Include error handling with pcall/xpcall where appropriate
5. Add brief comments for non-obvious logic
6. Use ModuleScript pattern (return table) for shared code
7. Handle client-server communication with RemoteEvents/RemoteFunctions
8. NEVER use deprecated APIs: use task.wait() not wait(), task.spawn() not spawn()
9. Use task.delay() not delay()
10. All scripts must be complete and runnable without modification

For each script, output it in this format:
```lua:ExactFileName.type.lua
-- code here
```

Where type is: server, client, or module (for .lua only)"""


class LuauGenerator:
    """Generates Luau scripts using Claude API."""

    def __init__(self, ai_client: AIClient):
        self.ai_client = ai_client

    async def generate(
        self,
        plan: GamePlan,
        preset_context: list[GeneratedFile],
    ) -> list[GeneratedFile]:
        """Generate Luau scripts for the game plan."""
        # Separate scripts by type for batching
        server_scripts = [s for s in plan.scripts if s.script_type == ScriptType.SERVER]
        client_scripts = [s for s in plan.scripts if s.script_type == ScriptType.CLIENT]
        module_scripts = [s for s in plan.scripts if s.script_type == ScriptType.MODULE]

        files: list[GeneratedFile] = []

        # Filter out scripts already covered by presets
        preset_names = {f.path.split("/")[-1].split(".")[0] for f in preset_context}

        server_to_gen = [s for s in server_scripts if s.name not in preset_names]
        client_to_gen = client_scripts
        module_to_gen = module_scripts

        # Build context from presets
        context_str = self._build_context(preset_context)

        # Generate server scripts (batch)
        if server_to_gen:
            try:
                server_files = await self._generate_batch(
                    server_to_gen, "server", plan, context_str
                )
                files.extend(server_files)
            except Exception:
                files.extend(self._fallback_scripts(server_to_gen))

        # Generate client scripts
        if client_to_gen:
            try:
                client_files = await self._generate_batch(
                    client_to_gen, "client", plan, context_str
                )
                files.extend(client_files)
            except Exception:
                files.extend(self._fallback_scripts(client_to_gen))

        # Generate module scripts
        if module_to_gen:
            try:
                module_files = await self._generate_batch(
                    module_to_gen, "module", plan, context_str
                )
                files.extend(module_files)
            except Exception:
                files.extend(self._fallback_scripts(module_to_gen))

        return files

    async def _generate_batch(
        self,
        scripts: list[ScriptSpec],
        batch_type: str,
        plan: GamePlan,
        context: str,
    ) -> list[GeneratedFile]:
        """Generate a batch of related scripts in one API call."""
        script_specs = "\n".join(
            f"- {s.name} ({s.script_type.value}): {s.description}"
            for s in scripts
        )

        systems_str = ", ".join(s.value for s in plan.systems)

        prompt = f"""Generate the following {batch_type} scripts for a Roblox {plan.genre.value} game called "{plan.game_name}".

Game Systems: {systems_str}

Scripts to generate:
{script_specs}

{context}

Generate ALL scripts listed above. Each script must be complete and functional.
Use the format ```lua:FileName.{batch_type}.lua for each script."""

        raw_scripts = await self.ai_client.generate_luau_scripts(
            prompt, system=LUAU_SYSTEM_PROMPT
        )

        files: list[GeneratedFile] = []
        for filename, code in raw_scripts.items():
            rojo_path = self._to_rojo_path(filename, batch_type)
            files.append(GeneratedFile(path=rojo_path, content=code, source="ai"))

        return files

    @staticmethod
    def _build_context(preset_files: list[GeneratedFile]) -> str:
        """Build context string from preset files."""
        if not preset_files:
            return ""

        parts = ["Existing preset code for reference (do NOT regenerate these):"]
        for f in preset_files[:3]:  # Limit context
            name = f.path.split("/")[-1]
            parts.append(f"\n--- {name} ---\n{f.content[:500]}...")
        return "\n".join(parts)

    @staticmethod
    def _to_rojo_path(filename: str, batch_type: str) -> str:
        """Convert filename to Rojo path."""
        if batch_type == "server" or ".server." in filename:
            return f"src/ServerScriptService/{filename}"
        elif batch_type == "client" or ".client." in filename:
            return f"src/StarterPlayerScripts/{filename}"
        else:
            return f"src/ReplicatedStorage/{filename}"

    @staticmethod
    def _fallback_scripts(scripts: list[ScriptSpec]) -> list[GeneratedFile]:
        """Generate minimal fallback scripts when AI fails."""
        files: list[GeneratedFile] = []
        for spec in scripts:
            suffix_map = {
                ScriptType.SERVER: "server",
                ScriptType.CLIENT: "client",
                ScriptType.MODULE: "module",
            }
            suffix = suffix_map.get(spec.script_type, "module")
            filename = f"{spec.name}.{suffix}.lua"

            if spec.script_type == ScriptType.MODULE:
                code = f"""-- {spec.name}: {spec.description}
-- Auto-generated fallback (AI generation was unavailable)

local {spec.name} = {{}}

function {spec.name}.init()
    -- TODO: Implement {spec.description}
end

return {spec.name}
"""
            else:
                code = f"""-- {spec.name}: {spec.description}
-- Auto-generated fallback (AI generation was unavailable)

-- TODO: Implement {spec.description}
print("[{spec.name}] Initialized")
"""

            path_map = {
                ScriptType.SERVER: f"src/ServerScriptService/{filename}",
                ScriptType.CLIENT: f"src/StarterPlayerScripts/{filename}",
                ScriptType.MODULE: f"src/ReplicatedStorage/{filename}",
            }

            files.append(
                GeneratedFile(
                    path=path_map.get(spec.script_type, f"src/ReplicatedStorage/{filename}"),
                    content=code,
                    source="fallback",
                )
            )
        return files
