"""OpenAI-compatible local model client.

Cliente del modelo local compatible con OpenAI.
"""

import json
import urllib.error
import urllib.request
from urllib.parse import urlparse

from .state import STATE


def endpoint():
    """Validate the configured local model URL.

    Valida la dirección configurada del modelo local.

    Returns:
        Validated base URL. / Dirección base validada.

    Raises:
        ValueError: Invalid model response or configuration /
            Configuración o respuesta del modelo no válida.
    """
    base = STATE["base_url"].rstrip("/")
    parsed = urlparse(base)
    if (
        parsed.scheme != "http"
        or parsed.hostname not in ("localhost", "127.0.0.1", "::1")
        or parsed.username
        or parsed.password
        or parsed.query
        or parsed.fragment
        or parsed.path.rstrip("/") != "/v1"
    ):
        raise ValueError(
            "The model endpoint must be a local http://localhost:PORT/v1 URL."
        )
    return base


def read_stream(response, on_delta):
    """Collect text from an OpenAI-compatible event stream.

    Recopila texto de un flujo de eventos compatible con OpenAI.

    Args:
        response: Open model HTTP response stream. / Flujo HTTP de respuesta del
            modelo.
        on_delta: Callback receiving the accumulated streamed text. / Función
            que recibe el texto acumulado.

    Returns:
        Completed response text. / Texto completo de la respuesta.

    Raises:
        ValueError: Invalid model response or configuration /
            Configuración o respuesta del modelo no válida.
    """
    if "text/event-stream" not in response.headers.get("Content-Type", ""):
        raw = response.read(200_000)
        raise ValueError(
            "Atomic Chat did not return an event stream. "
            "Turn off Stream responses for this model. "
            f"Server reply: {raw[:300].decode('utf-8', 'replace')}"
        )
    total_bytes = 0
    data_lines = []
    chunks = []

    def consume():
        """Parse buffered event data and emit its text delta.

        Procesa el evento pendiente y emite el fragmento de texto.

        Returns:
        True when the final event was received. / Verdadero al recibir el evento final.
        """
        if not data_lines:
            return False
        data = b"\n".join(data_lines).decode("utf-8-sig")
        data_lines.clear()
        if data.strip() == "[DONE]":
            return True
        try:
            event = json.loads(data)
            if event.get("error"):
                raise ValueError(f"Atomic Chat stream error: {event['error']}")
            delta = event["choices"][0].get("delta", {})
            content = delta.get("content") or ""
            if isinstance(content, list):
                content = "".join(str(part.get("text", "")) for part in content)
            if content:
                chunks.append(str(content))
                on_delta("".join(chunks))
        except (UnicodeDecodeError, json.JSONDecodeError, KeyError,
                IndexError, TypeError) as error:
            raise ValueError(
                f"Malformed Atomic Chat stream event: {error}"
            ) from error
        return False

    while True:
        line = response.readline()
        if not line:
            consume()
            break
        total_bytes += len(line)
        if total_bytes > 20_000_000:
            raise ValueError("Atomic Chat stream exceeded 20 MB")
        if not line.strip():
            if consume():
                break
        elif line.startswith(b"data:"):
            data_lines.append(line[5:].strip())
    if not chunks:
        raise ValueError("Atomic Chat stream contained no response text")
    return "".join(chunks).strip() or "(Empty response)"


def api(path, payload=None, on_delta=None):
    """Send a request to the configured local model API.

    Envía una solicitud a la API local configurada.

    Args:
        path: Local file path or API route. / Ruta de archivo local o de la API.
        payload: Optional JSON body for the API request. / Cuerpo JSON opcional.
        on_delta: Callback receiving the accumulated streamed text. / Función
            que recibe el texto acumulado.

    Returns:
        Decoded JSON response or streamed text. / Respuesta JSON o texto
        generado.

    Raises:
        ValueError: Invalid model response or configuration /
            Configuración o respuesta del modelo no válida.
    """
    url = endpoint() + path
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "Authorization": "Bearer local",
    }
    encoded = None
    if payload is not None:
        # Serialize once. json.dumps escapes control characters in prompts.
        encoded = json.dumps(
            payload, ensure_ascii=False, allow_nan=False
        ).encode("utf-8")
        json.loads(encoded.decode("utf-8"))
    req = urllib.request.Request(
        url,
        data=encoded,
        headers=headers,
        method="GET" if encoded is None else "POST",
    )
    try:
        with urllib.request.urlopen(
            req, timeout=int(STATE.get("model_timeout", 600)) if encoded else 8
        ) as response:
            if on_delta is not None:
                return read_stream(response, on_delta)
            raw = response.read()
            try:
                return json.loads(raw.decode("utf-8-sig"))
            except (UnicodeDecodeError, json.JSONDecodeError) as error:
                raise ValueError(
                    f"Atomic Chat returned malformed JSON: {error}."
                ) from error
    except urllib.error.HTTPError as error:
        raw = error.read(200000)
        details = raw.decode("utf-8", "replace").strip()[:800]
        raise ValueError(
            f"Atomic Chat rejected the request (HTTP {error.code}): "
            f"{details or error.reason}."
        ) from error
    except urllib.error.URLError as error:
        if isinstance(error.reason, TimeoutError):
            raise ValueError(
                "Atomic Chat did not respond within "
                f"{STATE.get('model_timeout', 600)} seconds. "
                "Increase the model timeout in Connection settings."
            ) from error
        raise ValueError(f"Cannot reach Atomic Chat: {error.reason}") from error
    except TimeoutError as error:
        raise ValueError(
            "Atomic Chat did not respond within "
            f"{STATE.get('model_timeout', 600)} seconds. "
            "Increase the model timeout in Connection settings."
        ) from error
    except (ConnectionError, OSError) as error:
        raise ValueError(f"Atomic Chat connection failed: {error}") from error


def complete(agent, task, prior, on_delta=None):
    """Ask one agent to respond using the task and prior work.

    Solicita una respuesta al agente con la tarea y el trabajo previo.

    Args:
        agent: Agent profile or prompt settings. / Perfil o instrucciones del
            agente.
        task: User assignment text. / Texto de la tarea del usuario.
        prior: Completed steps from earlier agents. / Pasos terminados de
            agentes anteriores.
        on_delta: Callback receiving the accumulated streamed text. / Función
            que recibe el texto acumulado.

    Returns:
        Agent response text. / Texto de respuesta del agente.
    """
    context = "\n\n".join(
        f"{step['agent']}: {step['output']}" for step in prior
    )
    messages = [
        {
            "role": "system",
            "content": (
                f"You are {agent['name']}. Your responsibility: "
                f"{agent['role']}\n\n"
                "Agent behavior instructions (SKILL.md):\n"
                f"{agent.get('skill', '')[:12000]}\n\n"
                "Work only on the user's task. Be concrete and concise. "
                "If previous agent output exists, build on it. "
                "Never claim to have run tools or changed files."
            ),
        },
        {
            "role": "user",
            "content": (
                f"Task: {task}\n\nPrevious work:\n"
                f"{context[-14000:] if context else 'None'}"
            ),
        },
    ]
    payload = {
        "model": STATE["model"],
        "messages": messages,
        "stream": bool(STATE.get("stream", False)),
    }
    if STATE.get("temperature") is not None:
        payload["temperature"] = STATE["temperature"]
    result = api(
        "/chat/completions",
        payload,
        on_delta=on_delta if payload["stream"] else None,
    )
    if payload["stream"]:
        return result
    try:
        content = result["choices"][0]["message"].get("content", "")
    except (KeyError, IndexError, TypeError) as error:
        raise ValueError(
            "Atomic Chat returned JSON without choices[0].message.content."
        ) from error
    if isinstance(content, list):
        content = "\n".join(str(part.get("text", "")) for part in content)
    return str(content).strip() or "(Empty response)"
