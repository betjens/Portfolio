"""Sequential agent workflow.

Flujo secuencial de agentes.
"""

from .state import LOCK, STATE
from .atomic import complete


def execute(run_id):
    """Run the agents sequentially and update in-memory progress.

    Ejecuta los agentes en orden y actualiza su progreso.

    Args:
        run_id: Identifier of the run to process or inspect. / Identificador de
            la tarea.
    """
    with LOCK:
        run = next(r for r in STATE["runs"] if r["id"] == run_id)
        agents = [dict(agent) for agent in STATE["agents"]]
        task = run["task"]
    for agent in agents:
        with LOCK:
            if run["status"] != "running":
                break
            run["active"] = agent["id"]
            prior = list(run["steps"])
        try:
            def progress(partial):
                """Publish the current streamed response in memory.

                Publica la respuesta parcial en memoria.

                Args:
                    partial: Current partial response text. / Texto actual de la
                        respuesta parcial.
                """
                with LOCK:
                    run["partial"] = {
                        "agent": agent["name"],
                        "id": agent["id"],
                        "output": partial,
                        "final": agent.get("final", False),
                    }

            output = complete(agent, task, prior, on_delta=progress)
            with LOCK:
                run["steps"].append(
                    {
                        "agent": agent["name"],
                        "id": agent["id"],
                        "output": output,
                        "final": agent.get("final", False),
                    }
                )
                run["active"] = None
                run.pop("partial", None)
        except Exception as error:
            with LOCK:
                run["status"] = "error"
                run["error"] = f"{agent['name']}: {error}"
                run["active"] = None
            break
    with LOCK:
        if run["status"] == "running":
            run["status"] = "done"
        run["active"] = None
