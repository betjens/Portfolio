"""Isolated HTTP test harness. Never touches the user's agents/ or output/.

Servidores aislados para las pruebas de integración.
"""

import json
import os
import shutil
import socket
import subprocess
import sys
import tempfile
import threading
import time
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from unittest import TestCase

SOURCE = Path(__file__).resolve().parents[1]


def free_port():
    """Reserve an available loopback port for a test server.

    Reserva un puerto local disponible para las pruebas.

    Returns:
        Available port number. / Número de puerto disponible.
    """
    with socket.socket() as sock:
        sock.bind(("127.0.0.1", 0))
        return sock.getsockname()[1]


class MockAtomic(BaseHTTPRequestHandler):
    def do_GET(self):
        """Serve mock model discovery requests.

        Atiende las solicitudes simuladas de búsqueda de modelos.

        Args:
            self: Current request handler or test case. / Instancia del
                controlador o de la prueba.
        """
        if self.path != "/v1/models":
            self.send_error(404)
            return
        self.respond({"data": [{"id": "test-model"}]})

    def do_POST(self):
        """Serve mock completions and record incoming requests.

        Atiende las respuestas simuladas y registra las solicitudes.

        Args:
            self: Current request handler or test case. / Instancia del
                controlador o de la prueba.
        """
        raw = self.rfile.read(int(self.headers["Content-Length"]))
        self.server.raw_requests.append(raw)
        data = json.loads(raw)
        self.server.requests.append(data)
        if self.server.error_body is not None:
            payload = self.server.error_body.encode("utf-8")
            self.send_response(400)
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return
        if self.server.malformed_response is not None:
            payload = self.server.malformed_response
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return
        if data.get("stream") and self.server.stream_json_response:
            self.respond({"choices": [{"message": {"content": "JSON"}}]})
            return
        if data.get("stream"):
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream; charset=utf-8")
            self.end_headers()
            for chunk in self.server.stream_chunks:
                event = {"choices": [{"delta": {"content": chunk}}]}
                packet = ("data: " + json.dumps(event, ensure_ascii=False)
                          + "\n\n").encode("utf-8")
                self.wfile.write(packet)
                self.wfile.flush()
                time.sleep(self.server.stream_delay)
            self.wfile.write(b"data: [DONE]\n\n")
            self.wfile.flush()
            return
        answer = self.server.answer(data)
        if answer is None:
            self.respond({"error": "Mock model unavailable"}, code=503)
        else:
            self.respond({"choices": [{"message": {"content": answer}}]})

    def respond(self, data, code=200):
        """Send a JSON response from the mock model.

        Envía una respuesta JSON desde el modelo simulado.

        Args:
            self: Current request handler or test case. / Instancia del
                controlador o de la prueba.
            data: JSON-serializable model response or request payload. / Datos
                JSON de la respuesta o solicitud.
            code: HTTP response status code. / Código de estado HTTP.
        """
        payload = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.end_headers()
        self.wfile.write(payload)

    def log_message(self, *_args):
        """Silence request logs in isolated tests.

        Silencia los registros de solicitudes en las pruebas.

        Args:
            self: Current request handler or test case. / Instancia del
                controlador o de la prueba.
            _args: Unused log arguments. / Argumentos de registro no utilizados.
        """
        pass


class OfficeTestCase(TestCase):
    def setUp(self):
        """Start isolated office and model servers for a test.

        Inicia servidores aislados de oficina y modelo para la prueba.

        Args:
            self: Current request handler or test case. / Instancia del
                controlador o de la prueba.
        """
        self.temp = tempfile.TemporaryDirectory(prefix="atomic-office-test-")
        self.root = Path(self.temp.name)
        shutil.copy2(SOURCE / "server.py", self.root / "server.py")
        shutil.copytree(
            SOURCE / "office",
            self.root / "office",
            ignore=shutil.ignore_patterns("__pycache__"),
        )
        shutil.copytree(SOURCE / "static", self.root / "static")
        self.model_port = free_port()
        self.office_port = free_port()
        self.model = ThreadingHTTPServer(
            ("127.0.0.1", self.model_port), MockAtomic
        )
        self.model.requests = []
        self.model.raw_requests = []
        self.model.error_body = None
        self.model.malformed_response = None
        self.model.stream_chunks = ["Hello ", "world"]
        self.model.stream_delay = 0.0
        self.model.stream_json_response = False
        self.model.answer = lambda _request: "Sample response"
        self.model_thread = threading.Thread(
            target=self.model.serve_forever, daemon=True
        )
        self.model_thread.start()
        env = {
            **os.environ,
            "OFFICE_PORT": str(self.office_port),
            "PYTHONUTF8": "0",
            "LC_ALL": "C",
            "PYTHONIOENCODING": "cp1252",
        }
        self.office = subprocess.Popen(
            [sys.executable, "server.py"],
            cwd=self.root,
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
        )
        self.base = f"http://127.0.0.1:{self.office_port}"
        for _ in range(100):
            try:
                self.get("/api/state")
                break
            except (urllib.error.URLError, ConnectionError):
                if self.office.poll() is not None:
                    raise AssertionError(
                        self.office.stderr.read().decode("utf-8", "replace")
                    )
                time.sleep(0.03)
        else:
            self.fail("Office did not start")

    def tearDown(self):
        """Stop test servers and delete temporary files.

        Detiene los servidores y elimina los archivos temporales.

        Args:
            self: Current request handler or test case. / Instancia del
                controlador o de la prueba.
        """
        self.office.terminate()
        try:
            self.office.communicate(timeout=3)
        except subprocess.TimeoutExpired:
            self.office.kill()
            self.office.communicate()
        self.model.shutdown()
        self.model.server_close()
        self.model_thread.join(timeout=3)
        self.temp.cleanup()

    def get(self, path):
        """Fetch and parse JSON from the isolated office.

        Solicita y analiza JSON de la oficina aislada.

        Args:
            self: Current request handler or test case. / Instancia del
                controlador o de la prueba.
            path: Local file path or API route. / Ruta de archivo local o de la
                API.

        Returns:
            Parsed JSON value. / Valor JSON analizado.
        """
        with urllib.request.urlopen(self.base + path, timeout=4) as response:
            return json.load(response)

    def post(self, path, data):
        """Send JSON to the isolated office and parse its reply.

        Envía JSON a la oficina aislada y analiza la respuesta.

        Args:
            self: Current request handler or test case. / Instancia del
                controlador o de la prueba.
            path: Local file path or API route. / Ruta de archivo local o de la
                API.
            data: JSON-serializable model response or request payload. / Datos
                JSON de la respuesta o solicitud.

        Returns:
            Parsed JSON value. / Valor JSON analizado.
        """
        body = json.dumps(data, ensure_ascii=False).encode("utf-8")
        request = urllib.request.Request(
            self.base + path, body, headers={"Content-Type": "application/json"}
        )
        with urllib.request.urlopen(request, timeout=4) as response:
            return json.load(response)

    def configure_model(self):
        """Point the office to the mock local model.

        Conecta la oficina con el modelo local simulado.

        Args:
            self: Current request handler or test case. / Instancia del
                controlador o de la prueba.
        """
        self.post(
            "/api/settings",
            {
                "base_url": f"http://127.0.0.1:{self.model_port}/v1",
                "model": "test-model",
            },
        )

    def wait_for_run(self, run_id):
        """Poll until a background run leaves running status.

        Espera hasta que una tarea deje de estar en curso.

        Args:
            self: Current request handler or test case. / Instancia del
                controlador o de la prueba.
            run_id: Identifier of the run to process or inspect. / Identificador
                de la tarea.

        Returns:
            Completed run record. / Registro de tarea finalizada.
        """
        for _ in range(120):
            run = next(
                r for r in self.get("/api/state")["runs"] if r["id"] == run_id
            )
            if run["status"] != "running":
                return run
            time.sleep(0.03)
        self.fail(f"Run {run_id} timed out")
