"""The served UI includes the RPG map and moving character layer.

La interfaz incluye el mapa, la cafetería y personajes animados.
"""

from urllib.error import HTTPError
from urllib.request import Request, urlopen
from tests.helpers import OfficeTestCase


class OfficeViewTests(OfficeTestCase):
    def test_rpg_map_and_walkers_are_served(self):
        """Verify the office scene, café, animation, and CSS are served.

        Comprueba que se sirven la escena, la cafetería, la animación y el CSS.
        """
        with urlopen(self.base + "/") as response:
            html = response.read().decode("utf-8")
        self.assertIn('id="officeScene"', html)
        self.assertIn('class="characters"', html)
        self.assertIn('class="map-cafe"', html)
        self.assertIn('<div class="cafe-seats"', html)
        self.assertIn('<i></i>' * 6, html)
        self.assertNotIn('id="editSpaces"', html)
        with urlopen(self.base + "/js/rpg.js") as response:
            script = response.read().decode("utf-8")
        self.assertIn("walkerMotion", script)
        self.assertIn("requestAnimationFrame(animate)", script)
        self.assertIn("walker.classList.toggle('chatting'", script)
        self.assertIn('Math.random() * chatIcons.length', script)
        self.assertIn('Math.min(distance, dt *', script)
        with urlopen(self.base + "/js/main.js") as response:
            main = response.read().decode("utf-8")
        self.assertIn("Math.max(4, agents.length)", main)
        self.assertIn('[19, 40], [40, 40], [19, 60], [40, 60]', main)
        with self.assertRaises(HTTPError) as error:
            urlopen(Request(self.base + "/api/spaces", data=b"{}"))
        self.assertEqual(error.exception.code, 404)
        with urlopen(self.base + "/tailwind.css") as response:
            css = response.read().decode("utf-8")
        self.assertIn(".rpg-map", css)
        self.assertIn(".rounded-2xl", css)

    def test_system_font_and_explicit_final_download(self):
        """Verify system fonts and browser-only final downloads.

        Comprueba las fuentes del sistema y la descarga local de respuestas.
        """
        with urlopen(self.base + "/tailwind.css") as response:
            css = response.read().decode("utf-8")
        self.assertIn("system-ui", css)
        self.assertNotIn("/fonts/", css)
        with urlopen(self.base + "/js/main.js") as response:
            script = response.read().decode("utf-8")
        self.assertIn('class="download-final"', script)
        self.assertIn("download.onclick = async", script)
        self.assertIn(
            "link.download = `atomic-office-${run.id}-final.md`", script
        )
        self.assertIn("new Blob([finalStep.output", script)
        self.assertNotIn("/api/output/", script)
        with self.assertRaises(HTTPError) as error:
            urlopen(self.base + "/api/output/000000000000/final.md")
        self.assertEqual(error.exception.code, 404)
