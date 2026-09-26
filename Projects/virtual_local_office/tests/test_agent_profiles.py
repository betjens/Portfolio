"""A direct file edit and an editor save must agree on agent behavior.

Las ediciones de disco e interfaz determinan el comportamiento.
"""

from tests.helpers import OfficeTestCase


class AgentProfileTests(OfficeTestCase):
    def test_ui_save_then_disk_edit_changes_next_prompt(self):
        """Verify UI and disk edits affect the next agent prompt.

        Comprueba que las ediciones del perfil cambian el siguiente mensaje.
        """
        self.configure_model()
        agents = self.get("/api/state")["agents"]
        agents[0]["skill"] = "# Planner behavior\nReturn concise steps."
        self.post("/api/agents", {"agents": agents})
        folder = self.root / "agents" / "planner"
        self.assertIn(
            "Return concise steps.",
            (folder / "skill.md").read_text(encoding="utf-8"),
        )
        (folder / "skill.md").write_text(
            "# New behavior\nInclude risks.", encoding="utf-8"
        )
        config = folder / "config.ini"
        config.write_text(
            config.read_text(encoding="utf-8").replace(
                "name = Planner", "name = Lead Planner"
            ),
            encoding="utf-8",
        )
        self.assertEqual(
            self.get("/api/state")["agents"][0]["name"], "Lead Planner"
        )
        run_id = self.post("/api/runs", {"task": "Plan a release"})["id"]
        self.assertEqual(self.wait_for_run(run_id)["status"], "done")
        self.assertIn(
            "Include risks.", self.model.requests[0]["messages"][0]["content"]
        )
        self.assertEqual(len(self.model.requests), 4)

    def test_removed_agent_keeps_disabled_folder(self):
        """Verify removing an agent disables rather than deletes its folder.

        Comprueba que quitar un agente deshabilita su carpeta sin borrarla.
        """
        agents = self.get("/api/state")["agents"]
        self.post("/api/agents", {"agents": agents[:2]})
        self.assertNotIn(
            "reviewer", [a["id"] for a in self.get("/api/state")["agents"]]
        )
        self.assertIn(
            "enabled = no",
            (self.root / "agents" / "reviewer" / "config.ini").read_text(
                encoding="utf-8"
            ),
        )

    def test_individual_edit_preserves_other_agent_files(self):
        """Verify editing one agent leaves other profiles unchanged.

        Comprueba que editar un agente conserva los demás perfiles.
        """
        agents = self.get("/api/state")["agents"]
        builder_path = self.root / "agents" / "builder" / "skill.md"
        builder_path.write_text("Builder custom behavior", encoding="utf-8")
        planner = dict(
            agents[0], name="My Planner", skill="Individual edit instructions"
        )
        self.post("/api/agent", {"agent": planner})
        self.assertEqual(
            self.get("/api/state")["agents"][0]["name"], "My Planner"
        )
        self.assertEqual(
            builder_path.read_text(encoding="utf-8"), "Builder custom behavior"
        )
        self.assertEqual(
            (self.root / "agents" / "planner" / "skill.md").read_text(
                encoding="utf-8"
            ),
            "Individual edit instructions",
        )

    def test_add_agent_runs_before_finalizer(self):
        """Verify new agents run before the final response agent.

        Comprueba que los agentes nuevos actúan antes del agente final.
        """
        result = self.post(
            "/api/agent-create",
            {
                "agent": {
                    "name": "Research Helper",
                    "role": "Summarize the provided facts",
                    "skill": "# Research Helper\nOnly use provided context.",
                    "space": "main",
                }
            },
        )
        agents = self.get("/api/state")["agents"]
        self.assertEqual(agents[-2]["id"], result["id"])
        self.assertTrue(agents[-1]["final"])
        self.assertTrue(
            (self.root / "agents" / result["id"] / "config.ini").exists()
        )

    def test_profile_settings_match_in_single_and_bulk_edits(self):
        """Verify single and bulk edits validate sprite settings equally.

        Comprueba que ambas vías de edición validan igual los sprites.
        """
        created = self.post(
            "/api/agent-create",
            {
                "agent": {
                    "name": "Map Artist",
                    "role": "Draw maps",
                    "space": "main",
                    "sprite_fps": 99,
                }
            },
        )
        agent_id = created["id"]
        current = self.get("/api/state")["agents"]
        artist = next(agent for agent in current if agent["id"] == agent_id)
        self.assertEqual(artist["sprite_fps"], 24)
        self.assertEqual(artist["frame_width"], 32)
        artist["sprite_frames"] = 99
        self.post("/api/agent", {"agent": artist})
        current = self.get("/api/state")["agents"]
        artist = next(agent for agent in current if agent["id"] == agent_id)
        self.assertEqual(artist["sprite_frames"], 32)
        artist["sprite_row"] = 99
        self.post("/api/agents", {"agents": current})
        current = self.get("/api/state")["agents"]
        artist = next(agent for agent in current if agent["id"] == agent_id)
        self.assertEqual(artist["sprite_row"], 50)
        self.assertTrue(current[-1]["final"])

    def test_model_timeout_setting_is_persisted_and_validated(self):
        """Verify timeout settings persist and invalid values fail.

        Comprueba que el tiempo de espera se guarda y se valida.
        """
        self.post(
            "/api/settings",
            {
                "base_url": f"http://127.0.0.1:{self.model_port}/v1",
                "model": "test-model",
                "model_timeout": 900,
            },
        )
        self.assertEqual(self.get("/api/state")["model_timeout"], 900)
        import json
        import urllib.error

        self.assertEqual(
            json.loads(
                (self.root / "office-data.json").read_text(encoding="utf-8")
            )["model_timeout"],
            900,
        )
        with self.assertRaises(urllib.error.HTTPError) as error:
            self.post(
                "/api/settings",
                {
                    "base_url": f"http://127.0.0.1:{self.model_port}/v1",
                    "model": "test-model",
                    "model_timeout": 9999,
                },
            )
        self.assertEqual(error.exception.code, 400)
        with self.assertRaises(urllib.error.HTTPError):
            self.post(
                "/api/settings",
                {
                    "base_url": "http://localhost:9999/v1",
                    "model": "changed",
                    "model_timeout": "not-a-number",
                },
            )
        current = self.get("/api/state")
        self.assertEqual(current["model_timeout"], 900)
        self.assertEqual(current["model"], "test-model")
