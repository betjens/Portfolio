"""Run results stay in memory, including streamed text and API errors.

Las respuestas y los errores permanecen en memoria.
"""

import json
import time
import urllib.error

from tests.helpers import OfficeTestCase


class WorklogTests(OfficeTestCase):
    def assert_no_saved_runs(self):
        """Verify run outputs never appear in persistent office files.

        Comprueba que las respuestas no se guardan en archivos.
        """
        self.assertFalse((self.root / "output").exists())
        settings = json.loads(
            (self.root / "office-data.json").read_text(encoding="utf-8")
        )
        self.assertNotIn("runs", settings)

    def test_stream_shows_live_text_and_final_response(self):
        """Verify streamed progress and the final response remain in memory.

        Comprueba el progreso en vivo y la respuesta final en memoria.
        """
        self.configure_model()
        self.assertFalse(self.get("/api/state")["stream"])
        self.assertIsNone(self.get("/api/state")["temperature"])
        self.post("/api/settings", {
            "base_url": f"http://127.0.0.1:{self.model_port}/v1",
            "model": "test-model", "stream": True, "temperature": 0.7,
        })
        self.model.stream_chunks = ["Hola ", "🌍"]
        self.model.stream_delay = 0.3
        run_id = self.post("/api/runs", {"task": "Say hello"})["id"]
        partial = None
        for _ in range(100):
            run = self.get("/api/state")["runs"][0]
            if run.get("partial", {}).get("output") == "Hola ":
                partial = run["partial"]
                break
            time.sleep(0.02)
        self.assertIsNotNone(partial)
        run = self.wait_for_run(run_id)
        self.assertEqual(run["status"], "done")
        self.assertEqual(run["steps"][-1]["output"], "Hola 🌍")
        self.assertTrue(all(r["stream"] for r in self.model.requests))
        self.assertTrue(all(r["temperature"] == 0.7
                            for r in self.model.requests))
        self.assert_no_saved_runs()

    def test_temperature_defaults_and_validation(self):
        """Verify optional temperature defaults and range validation.

        Comprueba el valor opcional de temperatura y sus límites.
        """
        self.configure_model()
        run_id = self.post("/api/runs", {"task": "Default options"})["id"]
        self.assertEqual(self.wait_for_run(run_id)["status"], "done")
        self.assertNotIn("temperature", self.model.requests[0])
        self.assertFalse(self.model.requests[0]["stream"])
        with self.assertRaises(urllib.error.HTTPError):
            self.post("/api/settings", {
                "base_url": f"http://127.0.0.1:{self.model_port}/v1",
                "model": "test-model", "temperature": 2.1,
            })
        self.assertIsNone(self.get("/api/state")["temperature"])

    def test_unsupported_stream_reports_error_in_ui(self):
        """Verify unsupported streaming reports a useful run error.

        Comprueba que los flujos incompatibles muestran un error útil.
        """
        self.configure_model()
        self.post("/api/settings", {
            "base_url": f"http://127.0.0.1:{self.model_port}/v1",
            "model": "test-model", "stream": True,
        })
        self.model.stream_json_response = True
        run_id = self.post("/api/runs", {"task": "Explain"})["id"]
        run = self.wait_for_run(run_id)
        self.assertEqual(run["status"], "error")
        self.assertIn("Turn off Stream responses", run["error"])
        self.assertIn("JSON", run["error"])
        self.assert_no_saved_runs()

    def test_unicode_output_and_sequential_handoff(self):
        """Verify Unicode content passes through sequential agent prompts.

        Comprueba que Unicode pasa entre los agentes en orden.
        """
        self.configure_model()
        self.model.answer = lambda _request: "Español, żółw, 中文, 🚀"
        run_id = self.post("/api/runs", {"task": "Escribe sobre café ☕"})["id"]
        run = self.wait_for_run(run_id)
        self.assertEqual(run["status"], "done", run.get("error"))
        self.assertEqual(len(run["steps"]), 4)
        self.assertIn(
            "Planner: Español", self.model.requests[1]["messages"][1]["content"]
        )
        self.assertIn("café ☕", run["task"])
        self.assertTrue(run["steps"][-1]["final"])
        self.assertEqual(run["steps"][-1]["output"], "Español, żółw, 中文, 🚀")
        self.assert_no_saved_runs()

    def test_model_failure_stays_in_memory(self):
        """Verify model failures remain visible without output files.

        Comprueba que los fallos son visibles sin crear archivos.
        """
        self.configure_model()
        self.model.answer = lambda _request: None
        run_id = self.post("/api/runs", {"task": "Check failure"})["id"]
        run = self.wait_for_run(run_id)
        self.assertEqual(run["status"], "error")
        self.assertIn("HTTP 503", run["error"])
        self.assert_no_saved_runs()

    def test_control_characters_are_escaped_in_atomic_request(self):
        """Verify JSON escapes control characters in model requests.

        Comprueba el escape JSON de los caracteres de control.
        """
        self.configure_model()
        task = "First line\nSecond line\x00third\x1fend"
        run_id = self.post("/api/runs", {"task": task})["id"]
        self.assertEqual(self.wait_for_run(run_id)["status"], "done")
        raw = self.model.raw_requests[0]
        self.assertNotIn(b"\x00", raw)
        self.assertNotIn(b"\x1f", raw)
        self.assertEqual(
            json.loads(raw)["messages"][1]["content"].split(
                "\n\nPrevious work:"
            )[0],
            "Task: " + task,
        )
        self.assert_no_saved_runs()

    def test_http_and_json_errors_are_visible(self):
        """Verify HTTP and malformed JSON failures reach the UI state.

        Comprueba que los fallos HTTP y JSON llegan a la interfaz.
        """
        self.configure_model()
        self.model.error_body = "Invalid JSON body: control character"
        run_id = self.post("/api/runs", {"task": "Explain"})["id"]
        run = self.wait_for_run(run_id)
        self.assertEqual(run["status"], "error")
        self.assertIn("HTTP 400", run["error"])
        self.assertIn("Invalid JSON body", run["error"])
        self.model.error_body = None
        self.model.malformed_response = b'{"choices": "bad\ncontrol"}'
        run_id = self.post("/api/runs", {"task": "Summarize"})["id"]
        run = self.wait_for_run(run_id)
        self.assertEqual(run["status"], "error")
        self.assertIn("malformed JSON", run["error"])
        self.assert_no_saved_runs()
