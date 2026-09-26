"""Mutable office operations shared by the FastAPI routes.

Acciones de la oficina compartidas por las rutas FastAPI.
"""

import base64
import configparser
import math
import re
import threading
import time
import uuid

from .state import AGENTS, LOCK, STATE
from .storage import agent_dir, read_agents, save, write_agent
from .atomic import endpoint
from .runner import execute


SPRITE_FIELDS = {
    "frame_width": (8, 512, 32),
    "frame_height": (8, 512, 32),
    "sprite_row": (0, 50, 0),
    "sprite_frames": (1, 32, 1),
    "sprite_fps": (1, 24, 6),
}


def sprite_settings(submitted, defaults=None):
    """Clamp sprite settings to supported ranges.

    Limita los ajustes de sprites a los valores admitidos.

    Args:
        submitted: Untrusted profile or sprite fields. / Campos de perfil o
            sprite sin validar.
        defaults: Fallback sprite settings. / Ajustes alternativos de sprites.

    Returns:
        Dictionary of validated sprite settings. / Diccionario con ajustes de sprites validados.
    """
    defaults = defaults or {}
    return {
        field: max(
            low,
            min(high, int(submitted.get(field, defaults.get(field, default)))),
        )
        for field, (low, high, default) in SPRITE_FIELDS.items()
    }


def profile(submitted, *, bulk=False):
    """Validate editable agent name, role, and instructions.

    Valida el nombre, la función y las instrucciones del agente.

    Args:
        submitted: Untrusted profile or sprite fields. / Campos de perfil o
            sprite sin validar.
        bulk: Whether to use bulk-edit validation messages. / Indica si se usan
            errores de edición masiva.

    Returns:
        Sanitized agent profile fields. / Campos validados del perfil.
    """
    name = str(submitted.get("name", "")).strip()[:40]
    role = str(submitted.get("role", "")).strip()[:500]
    skill = str(submitted.get("skill", ""))
    if not name or not role:
        message = (
            "Each agent needs a name and role"
            if bulk
            else "Name and role are required"
        )
        raise ValueError(message)
    if len(skill) > 12000:
        message = (
            "Each behavior file must be under 12,000 characters"
            if bulk
            else "Behavior must be under 12,000 characters"
        )
        raise ValueError(message)
    return {"name": name, "role": role, "skill": skill}


def available_id(name, reserved=()):
    """Find an unused folder ID based on an agent name.

    Busca un identificador de carpeta libre para el agente.

    Args:
        name: Requested agent display name. / Nombre visible del agente.
        reserved: Agent IDs already chosen in this operation. / Identificadores
            ya elegidos.

    Returns:
        Unique lowercase agent ID. / Identificador único en minúsculas.
    """
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")[:40] or "agent"
    agent_id = slug
    while (AGENTS / agent_id).exists() or agent_id in reserved:
        agent_id = slug[:35] + "-" + uuid.uuid4().hex[:5]
    return agent_id


def settings(body):
    """Validate and save connection settings.

    Valida y guarda la configuración de conexión.

    Args:
        body: Parsed JSON request body. / Cuerpo JSON analizado.

    Returns:
        Success response and HTTP status. / Respuesta correcta y estado HTTP.
    """
    base_url = str(body.get("base_url", "")).strip()
    model = str(body.get("model", "")).strip()
    timeout = int(body.get("model_timeout", STATE.get("model_timeout", 600)))
    if not 5 <= timeout <= 3600:
        raise ValueError("Timeout must be 5 to 3600 seconds")
    stream = body.get("stream", STATE.get("stream", False))
    if not isinstance(stream, bool):
        raise ValueError("Streaming must be on or off")
    temperature = body.get("temperature", STATE.get("temperature"))
    if temperature in ("", None):
        temperature = None
    else:
        temperature = float(temperature)
        if not math.isfinite(temperature) or not 0 <= temperature <= 2:
            raise ValueError("Temperature must be between 0 and 2")
    # Validate the proposed URL without leaving partially changed settings.
    previous_url = STATE["base_url"]
    try:
        STATE["base_url"] = base_url
        endpoint()
    finally:
        STATE["base_url"] = previous_url
    STATE.update(base_url=base_url, model=model, model_timeout=timeout,
                 stream=stream, temperature=temperature)
    save()
    return {"ok": True}, 200


def agent(body):
    """Update one existing agent profile.

    Actualiza el perfil de un agente existente.

    Args:
        body: Parsed JSON request body. / Cuerpo JSON analizado.

    Returns:
        Success response and HTTP status. / Respuesta correcta y estado HTTP.
    """
    submitted = body.get("agent", {})
    agent_id = str(submitted.get("id", ""))
    existing = next(
        (agent for agent in STATE["agents"] if agent["id"] == agent_id),
        None,
    )
    if existing is None:
        raise ValueError("Agent not found")
    updated = dict(existing, **profile(submitted))
    updated.update(sprite_settings(submitted, existing))
    write_agent(updated, existing["order"])
    STATE["agents"] = read_agents()
    return {"ok": True}, 200


def agent_create(body):
    """Create a new agent profile and folder.

    Crea un agente nuevo y su carpeta.

    Args:
        body: Parsed JSON request body. / Cuerpo JSON analizado.

    Returns:
        Created agent ID and HTTP status. / Identificador creado y estado HTTP.
    """
    submitted = body.get("agent", {})
    if len(STATE["agents"]) >= 12:
        raise ValueError("Maximum 12 agents")
    details = profile(submitted)
    agent_id = available_id(details["name"])
    order = (
        max(
            (a["order"] for a in STATE["agents"] if not a["final"]),
            default=-1,
        )
        + 1
    )
    new_agent = {
        "id": agent_id,
        **details,
        "x": 50,
        "y": 63,
        "final": False,
        **sprite_settings(submitted),
    }
    write_agent(new_agent, order)
    STATE["agents"] = read_agents()
    return {"ok": True, "id": agent_id}, 201


def agents(body):
    """Apply a bulk agent edit while preserving the finalizer.

    Edita varios agentes conservando el agente final.

    Args:
        body: Parsed JSON request body. / Cuerpo JSON analizado.

    Returns:
        Success response and HTTP status. / Respuesta correcta y estado HTTP.
    """
    agents = body.get("agents")
    if not isinstance(agents, list) or not 1 <= len(agents) <= 12:
        raise ValueError("Use 1 to 12 agents")
    clean = []
    for agent in agents:
        details = profile(agent, bulk=True)
        candidate_id = str(agent.get("id", ""))
        known = {a["id"] for a in STATE["agents"]}
        reserved = {a["id"] for a in clean}
        agent_id = (
            candidate_id
            if candidate_id in known and candidate_id not in reserved
            else available_id(details["name"], reserved)
        )
        x = max(8, min(92, int(agent.get("x", 15 + len(clean) * 22))))
        y = max(38, min(78, int(agent.get("y", 63))))
        sprite = sprite_settings(agent)
        is_final = next(
            (a["final"] for a in STATE["agents"] if a["id"] == agent_id),
            False,
        )
        clean.append(
            {
                "id": agent_id,
                **details,
                "x": x,
                "y": y,
                "final": is_final,
                **sprite,
            }
        )
    if not any(agent["final"] for agent in clean):
        clean.extend(agent for agent in STATE["agents"] if agent["final"])
    retained = {agent["id"] for agent in clean}
    for old in STATE["agents"]:
        if old["id"] not in retained:
            folder = agent_dir(old["id"])
            config = configparser.ConfigParser(interpolation=None)
            config.read(folder / "config.ini", encoding="utf-8")
            config["agent"]["enabled"] = "no"
            with (folder / "config.ini").open("w", encoding="utf-8") as file:
                config.write(file)
    for index, agent in enumerate(clean):
        write_agent(agent, index)
    STATE["agents"] = read_agents()
    save()
    return {"ok": True}, 200


def positions(body):
    """Save a desk position inside the work area.

    Guarda la posición del escritorio dentro del área de trabajo.

    Args:
        body: Parsed JSON request body. / Cuerpo JSON analizado.

    Returns:
        Success response and HTTP status. / Respuesta correcta y estado HTTP.
    """
    agent_id = str(body.get("id", ""))
    agent = next(
        (a for a in STATE["agents"] if a["id"] == agent_id),
        None,
    )
    if agent is None:
        raise ValueError("Agent not found")
    agent["x"] = max(10, min(48, int(body["x"])))
    agent["y"] = max(39, min(72, int(body["y"])))
    write_agent(agent, agent.get("order", STATE["agents"].index(agent)))
    save()
    return {"ok": True}, 200


def agent_image(body):
    """Replace or clear an agent sprite image.

    Reemplaza o elimina la imagen del agente.

    Args:
        body: Parsed JSON request body. / Cuerpo JSON analizado.

    Returns:
        Success response and HTTP status. / Respuesta correcta y estado HTTP.
    """
    agent_id = str(body.get("id", ""))
    if agent_id not in {a["id"] for a in STATE["agents"]}:
        raise ValueError("Agent not found")
    if body.get("reset"):
        folder = agent_dir(agent_id)
        for old in ("sprite.png", "sprite.webp", "sprite.gif"):
            (folder / old).unlink(missing_ok=True)
        return {"ok": True}, 200
    ext = str(body.get("extension", "")).lower()
    if ext not in ("png", "webp", "gif"):
        raise ValueError("Use a PNG, WebP or GIF image")
    raw = base64.b64decode(body.get("data", ""), validate=True)
    if not raw or len(raw) > 1500000:
        raise ValueError("Image must be under 1.5 MB")
    if ext == "png" and not raw.startswith(b"\x89PNG\r\n\x1a\n"):
        raise ValueError("Invalid PNG")
    if ext == "webp" and not (raw.startswith(b"RIFF") and raw[8:12] == b"WEBP"):
        raise ValueError("Invalid WebP")
    if ext == "gif" and not raw.startswith((b"GIF87a", b"GIF89a")):
        raise ValueError("Invalid GIF")
    folder = agent_dir(agent_id)
    for old in ("sprite.png", "sprite.webp", "sprite.gif"):
        (folder / old).unlink(missing_ok=True)
    (folder / ("sprite." + ext)).write_bytes(raw)
    return {"ok": True}, 200


def runs(body):
    """Start a sequential run in a background thread.

    Inicia una tarea secuencial en segundo plano.

    Args:
        body: Parsed JSON request body. / Cuerpo JSON analizado.

    Returns:
        New run record and HTTP status. / Tarea nueva y estado HTTP.
    """
    task = str(body.get("task", "")).strip()
    if not task or len(task) > 4000:
        raise ValueError("Task must have 1 to 4000 characters")
    if not STATE["model"]:
        raise ValueError("Select an Atomic Chat model first")
    if not any(agent["final"] for agent in STATE["agents"]):
        raise ValueError("Enable a final response agent in agents/")
    if any(r["status"] == "running" for r in STATE["runs"]):
        raise ValueError("A run is already in progress")
    run = {
        "id": uuid.uuid4().hex[:12],
        "task": task,
        "status": "running",
        "active": None,
        "steps": [],
        "error": "",
        "created": int(time.time()),
    }
    STATE["runs"].insert(0, run)
    STATE["runs"] = STATE["runs"][:25]
    threading.Thread(target=execute, args=(run["id"],), daemon=True).start()
    return run, 201


def stop(body):
    """Mark running assignments as stopped.

    Marca las tareas en curso como detenidas.

    Args:
        body: Parsed JSON request body. / Cuerpo JSON analizado.

    Returns:
        Success response and HTTP status. / Respuesta correcta y estado HTTP.
    """
    for run in STATE["runs"]:
        if run["status"] == "running":
            run["status"] = "stopped"
    return {"ok": True}, 200


HANDLERS = {
    "settings": settings,
    "agent": agent,
    "agent-create": agent_create,
    "agents": agents,
    "positions": positions,
    "agent-image": agent_image,
    "runs": runs,
    "stop": stop,
}


def update(path, body):
    """Dispatch a validated action under the state lock.

    Valida y ejecuta una acción con el estado protegido.

    Args:
        path: Local file path or API route. / Ruta de archivo local o de la API.
        body: Parsed JSON request body. / Cuerpo JSON analizado.

    Returns:
        Action response and HTTP status. / Respuesta de la acción y estado HTTP.
    """
    with LOCK:
        STATE["agents"] = read_agents()
        handler = HANDLERS.get(path.removeprefix("/api/"))
        return handler(body) if handler else ({"error": "Not found"}, 404)
