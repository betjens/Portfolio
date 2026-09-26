# Atomic Office

A local animated virtual office for a small team of AI agents using Atomic
Chat's OpenAI-compatible API. The server uses FastAPI and Uvicorn. The UI uses
a bundled Tailwind CSS build and needs no internet connection.

## Start

1. In Atomic Chat, start the local API at `http://localhost:1337/v1` and
   load a chat model.
2. In this folder run `python -m pip install -r requirements.txt`, then
   `python server.py` (Windows: `py -m pip install -r requirements.txt`,
   then `py server.py`).
3. Visit `http://127.0.0.1:8765`, detect models, select one and save.

Agents run **sequentially**. Each agent sees the task and prior agents'
responses. The Finalizer runs last and writes the final user-facing response.
One model is shared across agents; their instructions differ. The office
visualizes which agent is active. It does not run shell commands or modify
project files.

## Agent directories

Every active agent has a folder under `agents/`:

```text
agents/
  planner/
    config.ini
    skill.md
    sprite.png       # optional; sprite.webp or sprite.gif also supported
  builder/
    config.ini
    skill.md
  reviewer/
    config.ini
    skill.md
  finalizer/
    config.ini
    skill.md
    sprite.png
```

`config.ini` contains `[agent]` fields `name`, `role`, `order`, `x`, `y`,
`enabled`, `final`, `frame_width`, `frame_height`, `sprite_row`,
`sprite_frames`, and `sprite_fps`. The `final = yes` agent always runs last.
Edit a file directly and refresh the page; the server reads agent folders on
every state request and before starting a task. Rename a folder to change its
ID; change `name` to change its display name. New folders need a valid
`config.ini` with an `[agent]` section. Lowercase folder names can contain
letters, digits, hyphens and underscores. `skill.md` contains the agent's
behavior instructions. Uppercase `SKILL.md` can also be read, but the UI
writes `skill.md`.

Use **Edit** beside an agent to change its profile, or **Add agent** at the
bottom of Your People to create a new folder. These actions write the files
for that agent. A new agent gets a folder based on its name. A removed agent's
folder remains intact with `enabled = no`, so you can restore it by changing
that setting to `yes`. Upload an image in the UI or put `sprite.png`,
`sprite.webp`, or `sprite.gif` in its folder. If more than one exists, PNG
takes precedence. Frame dimensions, starting row, count, and FPS control a
horizontal sprite sheet; use 1 frame for a static image. The app also migrates
existing character images stored by earlier versions in this browser into the
agent folders where possible.

## Live view and data

In Connection settings, **Stream responses** is off by default. Turn it on to
display each agent's text as Atomic Chat sends it. Streaming requires the
model endpoint to support OpenAI-compatible `text/event-stream` responses;
turn it off if your model does not support them. **Temperature** is optional:
leave it blank to use the model's default, or enter a value from 0 to 2. Both
settings are saved with the other connection settings. Runs remain sequential,
and only the completed Finalizer response is downloadable. Live text appears
as plain Markdown while the model is generating; completed responses receive
the formatted preview. Polling updates the live text without rebuilding the
office scene or completed responses.

The live view is a single office with four computers on the left and a café
with six seats on the right. Idle agents walk between their desks and the
café, where changing icons suggest conversation; these social animations do
not make model requests. Drag a desk within the left work area to reposition
it. Atomic Chat settings live in `office-data.json`; agent profiles and images
live in `agents/`. Set **Response timeout (seconds)** in Connection settings
if your model needs longer to answer. The default is 600 seconds per model
request; allowed values are 5–3600. Runs and agent responses stay in server
memory until the server restarts. The app creates no `output/` directory.
Click **Download final output** to create a Markdown download in your browser,
**Copy Markdown** to copy a response, or **Copy full worklog** to copy all
agent responses. The Markdown button toggles between formatted preview and raw
text. Stop the server with Ctrl+C. Set `OFFICE_PORT=8766` to change the office
port on Linux/macOS.

Keep images under 1.5 MB when uploading through the UI and `skill.md` under
12,000 characters. Behavior instructions guide model responses; the app does
not install tools from `skill.md`.

## Tests

Run `python -m unittest discover -s tests -v` from this directory. The tests
use a temporary office and mock model API, so they do not alter your agents or
outputs. See `tests/README.md` for a template and instructions for adding your
own cases.

## Starter profiles and safe updates

The **starter archive** includes filled `agents/planner`, `agents/builder`,
`agents/reviewer`, and `agents/finalizer` folders with `config.ini`,
`skill.md`, and animated `sprite.png`. Use it for a fresh installation. The
**update archive** contains the app and tests without `agents/` or
`office-data.json`, so you can extract it into an existing installation
without replacing those files. On a fresh install of the update archive, the
server creates plain default agent folders at first startup. Existing
`output/` folders from older releases are not used; remove them manually when
you no longer need their files.

## Diagnose Atomic Chat errors

The office shows model request failures in the UI, including HTTP rejections,
malformed response JSON, missing completion fields, timeouts, and connection
errors. It keeps completed steps in memory so you can copy their text while
the server is running. It does not write request or response traces to disk.

## RPG office map

The office uses a top-down pixel-art floor with four computers, a café
counter, furniture, and moving characters. Idle agents alternate between their
desks and café breaks; the active agent walks to its computer. Desk locations
move by dragging, and uploaded sprite sheets remain supported. The map and
fallback characters are built into HTML/CSS/Canvas and work offline.

## Project structure and development

```text
server.py                 # small startup entry point
office/state.py           # paths and shared runtime state
office/storage.py         # agent folders and settings
office/atomic.py          # Atomic Chat HTTP client
office/runner.py          # sequential agent workflow
office/web.py             # FastAPI routes and static files
office/operations.py      # action handlers and shared profile validation
static/index.html         # application shell
static/js/main.js         # state polling and screen rendering
static/js/i18n.js         # English/Spanish interface translations
static/js/editors.js      # agent editor
static/js/rpg.js          # map interaction, sprites and walking
static/js/dom.js          # HTTP and DOM helpers
static/js/markdown.js     # preview and copy helpers
src/input.css             # Tailwind entry and design tokens
src/components.css        # application controls and layout
src/map.css               # RPG map and animation styles
static/tailwind.css       # compiled CSS used at runtime
```

The server runs with `python server.py`. To rebuild the bundled stylesheet
after editing styles, run `python -m pytailwindcss -i src/input.css -o
static/tailwind.css --minify`. The first build may download Tailwind's
standalone executable. Test with `python -m unittest discover -s tests -v`.

The interface uses system fonts through Tailwind and works offline. Choose
English or Español in the page header; the choice is saved in your browser.
Agent names, instructions, and model-generated text retain their original
language. Python docstrings follow Google Python style with English and
Spanish descriptions; JavaScript uses bilingual Google-style JSDoc.

## Dependencies

Python 3.10+ is required. Install dependencies with `python -m pip install -r
requirements.txt`. The bundled UI works without a build step.
