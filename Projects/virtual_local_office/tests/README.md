# Testing Atomic Office

Run from the project root with Python 3.10+:

```bash
python -m unittest discover -s tests -v
```

Install `requirements.txt` first. `helpers.py` starts a mock OpenAI-compatible
API and a **temporary copy** of the office server. Every test receives fresh
`agents/` and `office-data.json` files, which are discarded afterward. Run
responses stay in memory; no `output/` folder is created. Your own files are
never used.

## Add a case

Create `tests/test_my_feature.py`:

```python
from tests.helpers import OfficeTestCase

 class MyFeatureTests(OfficeTestCase):     def test_my_case(self):
"""Verify the final agent completes a small assignment."""
self.configure_model()         run_id = self.post("/api/runs", {"task": "Draft
a small plan"})["id"]         run = self.wait_for_run(run_id)
self.assertEqual(run["status"], "done")
self.assertEqual(len(run["steps"]), 4)  # includes Finalizer
self.assertTrue(run["steps"][-1]["final"])         self.assertFalse((self.root
/ "output").exists()) ```

Test files must start with `test_`; methods must start with `test_`. Use
`self.root` to inspect temporary agent folders or saved settings. Use
`self.model.requests` to inspect messages sent to the model, and set
`self.model.answer = lambda request: 'Your test response'` for a specific
reply. Use `self.post` and `self.get` to interact with the real local HTTP
server. Keep each test independent and assert a visible outcome, such as the
run state or message passed to the next agent.

To run one class:

```bash
python -m unittest tests.test_worklogs.WorklogTests -v
```
