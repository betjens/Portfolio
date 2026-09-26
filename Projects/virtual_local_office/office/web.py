"""FastAPI routes for the local office and its bundled UI.

Rutas FastAPI de la oficina y su interfaz.
"""

import binascii
import json
import mimetypes
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from starlette.concurrency import run_in_threadpool

from .atomic import api
from .operations import update
from .state import LOCK, ROOT, STATE
from .storage import agent_dir, initialize, read_agents


@asynccontextmanager
async def lifespan(_app):
    """Initialize office data during application startup.

    Inicializa los datos de la oficina al arrancar la aplicación.

    Args:
        _app: FastAPI application supplied by the lifecycle hook. / Aplicación
            FastAPI.

    Yields:
        Async lifecycle yield. / Ciclo de vida asíncrono.
    """
    initialize()
    yield


app = FastAPI(title="Atomic Office", lifespan=lifespan)


@app.get("/api/state")
def get_state():
    """Return a snapshot of the current office state.

    Devuelve una copia del estado actual de la oficina.

    Returns:
        JSON-compatible state dictionary. / Diccionario de estado compatible con JSON.
    """
    with LOCK:
        STATE["agents"] = read_agents()
        return json.loads(json.dumps(STATE, ensure_ascii=False))


@app.get("/api/models")
def get_models():
    """List available models from the local API.

    Enumera los modelos disponibles en la API local.

    Returns:
        Model list or HTTP error response. / Lista de modelos o respuesta de error HTTP.
    """
    try:
        return api("/models")
    except Exception as error:
        return JSONResponse({"error": str(error)}, status_code=502)


@app.get("/api/agent-image/{agent_id}")
def get_agent_image(agent_id: str):
    """Serve the saved sprite for an agent.

    Devuelve la imagen guardada de un agente.

    Args:
        agent_id: Agent folder identifier. / Identificador de la carpeta del
            agente.

    Returns:
        Sprite file response; raises 404 if missing. / Información
        correspondiente / Sprite file response; raises 404 if missing
    """
    try:
        folder = agent_dir(agent_id)
    except ValueError:
        raise HTTPException(404) from None
    image = next(
        (
            path
            for path in (
                folder / "sprite.png",
                folder / "sprite.webp",
                folder / "sprite.gif",
            )
            if path.is_file()
        ),
        None,
    )
    if image is None:
        raise HTTPException(404)
    return FileResponse(
        image,
        media_type=mimetypes.guess_type(image.name)[0],
        headers={"Cache-Control": "no-store"},
    )


@app.post("/api/{action}")
async def post_action(action: str, request: Request):
    """Validate and dispatch a supported API action.

    Valida y ejecuta una acción de la API.

    Args:
        action: API action name. / Nombre de la acción de la API.
        request: Incoming FastAPI request. / Solicitud FastAPI recibida.

    Returns:
        JSON response with action status. / Respuesta JSON con el estado de la acción.
    """
    if action not in {
        "settings",
        "agent",
        "agent-create",
        "agents",
        "positions",
        "agent-image",
        "runs",
        "stop",
    }:
        return JSONResponse({"error": "Not found"}, status_code=404)
    raw = await request.body()
    if len(raw) > 2_200_000:
        return JSONResponse({"error": "Request too large"}, status_code=400)
    try:
        body = json.loads(raw)
        if not isinstance(body, dict):
            raise ValueError("Expected a JSON object")
        result, status = await run_in_threadpool(update, f"/api/{action}", body)
        return JSONResponse(result, status_code=status)
    except (ValueError, KeyError, TypeError, binascii.Error) as error:
        return JSONResponse({"error": str(error)}, status_code=400)


app.mount("/", StaticFiles(directory=ROOT / "static", html=True), name="static")
