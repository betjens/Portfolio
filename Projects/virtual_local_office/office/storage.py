"""Agent folders and persistent office settings.

Carpetas de agentes y configuración persistente.
"""

import configparser
import json
import re
import uuid

from .state import AGENTS, DATA, STATE


def agent_dir(agent_id):
    """Validate an agent ID and locate its directory.

    Valida el identificador del agente y localiza su carpeta.

    Args:
        agent_id: Agent folder identifier. / Identificador de la carpeta del
            agente.

    Returns:
        Path to the agent directory. / Ruta de la carpeta del agente.
    """
    if not re.fullmatch(r"[a-z0-9][a-z0-9_-]{0,49}", agent_id):
        raise ValueError("Invalid agent folder name")
    return AGENTS / agent_id


def write_agent(agent, order):
    """Save one agent profile and behavior file.

    Guarda el perfil y las instrucciones de un agente.

    Args:
        agent: Agent profile or prompt settings. / Perfil o instrucciones del
            agente.
        order: Execution order in the agent directory. / Orden de ejecución en
            la carpeta.
    """
    folder = agent_dir(agent["id"])
    folder.mkdir(exist_ok=True)
    config = configparser.ConfigParser(interpolation=None)
    config["agent"] = {
        "name": agent["name"],
        "role": agent["role"],
        "order": str(order),
        "x": str(agent.get("x", 50)),
        "y": str(agent.get("y", 63)),
        "enabled": "yes",
        "frame_width": str(agent.get("frame_width", 32)),
        "frame_height": str(agent.get("frame_height", 32)),
        "sprite_row": str(agent.get("sprite_row", 0)),
        "sprite_frames": str(agent.get("sprite_frames", 1)),
        "sprite_fps": str(agent.get("sprite_fps", 6)),
        "final": "yes" if agent.get("final", False) else "no",
    }
    temporary = folder / "config.ini.tmp"
    with temporary.open("w", encoding="utf-8") as file:
        config.write(file)
    temporary.replace(folder / "config.ini")
    (folder / "skill.md").write_text(agent.get("skill", ""), encoding="utf-8")


def read_agents():
    """Load enabled agent profiles from disk in run order.

    Carga los agentes habilitados en orden de ejecución.

    Returns:
        Ordered list of agent dictionaries. / Lista ordenada de agentes.
    """
    found = []
    for folder in AGENTS.iterdir():
        if not folder.is_dir() or not re.fullmatch(
            r"[a-z0-9][a-z0-9_-]{0,49}", folder.name
        ):
            continue
        config_file = folder / "config.ini"
        if not config_file.exists():
            continue
        config = configparser.ConfigParser(interpolation=None)
        config.read(config_file, encoding="utf-8")
        if not config.has_section("agent") or not config.getboolean(
            "agent", "enabled", fallback=True
        ):
            continue
        get = config["agent"].get
        image = next(
            (
                p.name
                for p in (
                    folder / "sprite.png",
                    folder / "sprite.webp",
                    folder / "sprite.gif",
                )
                if p.is_file()
            ),
            "",
        )
        skill_file = folder / "skill.md"
        if not skill_file.exists():
            skill_file = folder / "SKILL.md"
        found.append(
            {
                "id": folder.name,
                "name": get("name", folder.name),
                "role": get("role", ""),
                "skill": skill_file.read_text(encoding="utf-8")[:12000]
                if skill_file.exists()
                else "",
                "x": config.getint("agent", "x", fallback=50),
                "y": config.getint("agent", "y", fallback=63),
                "image": f"/api/agent-image/{folder.name}" if image else "",
                "frame_width": config.getint(
                    "agent", "frame_width", fallback=32
                ),
                "frame_height": config.getint(
                    "agent", "frame_height", fallback=32
                ),
                "sprite_row": config.getint("agent", "sprite_row", fallback=0),
                "sprite_frames": config.getint(
                    "agent", "sprite_frames", fallback=1
                ),
                "sprite_fps": config.getint("agent", "sprite_fps", fallback=6),
                "order": config.getint("agent", "order", fallback=999),
                "final": config.getboolean("agent", "final", fallback=False),
            }
        )
    return sorted(
        found, key=lambda agent: (agent["final"], agent["order"], agent["id"])
    )


def write_utf8(path, content):
    """Replace a text file atomically using UTF-8.

    Reemplaza un archivo de texto de forma atómica con UTF-8.

    Args:
        path: Local file path or API route. / Ruta de archivo local o de la API.
        content: UTF-8 text to write. / Texto UTF-8 que se escribirá.
    """
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(content, encoding="utf-8", newline="\n")
    temporary.replace(path)


def save():
    """Persist connection settings without run responses.

    Guarda la conexión sin incluir las respuestas.
    """
    write_utf8(
        DATA,
        json.dumps(
            {
                key: STATE[key]
                for key in (
                    "base_url", "model", "model_timeout", "stream",
                    "temperature",
                )
            },
            ensure_ascii=False,
            indent=2,
        ),
    )


def initialize():
    """Create default profiles if needed and load agents.

    Crea los perfiles predeterminados y carga los agentes.
    """
    if not any(AGENTS.iterdir()):
        for index, agent in enumerate(STATE["agents"]):
            agent["id"] = (
                re.sub(r"[^a-z0-9_-]", "-", agent.get("id", "agent").lower())[
                    :50
                ]
                or uuid.uuid4().hex[:10]
            )
            write_agent(agent, index)
    STATE["agents"] = read_agents()
    if not any(agent["final"] for agent in STATE["agents"]):
        write_agent(
            {
                "id": "finalizer",
                "name": "Finalizer",
                "role": (
                    "Compose the final user-facing answer from the "
                    "preceding agent work."
                ),
                "skill": (
                    "# Final response\n\nRead the task and all preceding "
                    "work. Produce one coherent final response that "
                    "directly fulfills the task. Resolve contradictions "
                    "and omit internal planning notes. Never claim to "
                    "have created files or used tools. This response "
                    "becomes the downloadable final output."
                ),
                "x": 81,
                "y": 63,
                "final": True,
            },
            999,
        )
        STATE["agents"] = read_agents()
    # Drop historical run text stored by older versions of office-data.json.
    save()
