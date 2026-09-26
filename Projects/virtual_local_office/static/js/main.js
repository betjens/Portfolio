import { t, getLanguage, setLanguage, applyTranslations } from './i18n.js';
import { $, request, escapeHtml, showError } from './dom.js';
import { markdownHtml, copyMarkdown, worklogMarkdown } from './markdown.js';
import { openAgentEditor, initEditors, refreshEditorLanguage } from './editors.js';
import { setupDragging, migrateSprites, initRpg } from './rpg.js';

let showPrior = false;
let rawMarkdown = false;
let current = null;
let renderedSignature = null;
let models = {};
let images = {};
const deskSlots = [
  [19, 40], [40, 40], [19, 60], [40, 60],
  [19, 72], [40, 72], [29, 50], [29, 68],
];
try {
  images = JSON.parse(localStorage.getItem('atomicOfficeSprites') || '{}');
} catch {}
/**
 * Identify state changes that require a full redraw.
 * Identifica los cambios de estado que requieren actualizar la vista.
 *
 * @param {Object} state Current server state. / Estado actual.
 *
 * @return {string} Stable JSON signature. / Firma JSON estable.
 */
function signature(state) {
  const run = state.runs[0];
  return JSON.stringify({
    agents: state.agents,
    base_url: state.base_url,
    model: state.model,
    model_timeout: state.model_timeout,
    stream: state.stream,
    temperature: state.temperature,
    run: run && [run.id, run.status, run.active, run.steps.length, run.error],
  });
}
/**
 * Arrange at least four desks in the left work area.
 * Coloca al menos cuatro escritorios a la izquierda.
 *
 * @param {Array<Object>} agents Ordered agent profiles. / Agentes ordenados.
 */
function renderDesks(agents) {
  const used = [];
  const count = Math.max(4, agents.length);
  $('desks').innerHTML = Array.from({ length: count }, (_, i) => {
    const agent = agents[i];
    const saved = agent && agent.x >= 10 && agent.x <= 48 &&
      agent.y >= 39 && agent.y <= 72 ? [agent.x, agent.y] : null;
    /**
     * Check whether a desk slot is clear of placed desks.
     * Comprueba si una posición está libre.
     *
     * @param {Array<number>} point Candidate desk position. / Posición candidata.
     *
     * @return {boolean} True when the slot has room. / Verdadero si hay espacio.
     */
    const available = (point) => used.every(
      ([x, y]) => Math.abs(x - point[0]) >= 10 || Math.abs(y - point[1]) >= 10,
    );
    const position = saved && available(saved) ? saved :
      deskSlots.find(available) || deskSlots[i % deskSlots.length];
    used.push(position);
    const [x, y] = position;
    const id = agent ? `data-id="${escapeHtml(agent.id)}"` : '';
    return [
      `<div class="station ${agent ? '' : 'vacant'}" ${id}`,
      ` style="left:${x}%;top:${y}%"><div class="workstation">`,
      '<div class="desk-screen">▣</div><div class="desk-surface"></div>',
      '<div class="desk-legs"></div><div class="desk-chair"></div>',
      '</div></div>',
    ].join('');
  }).join('');
}
/**
 * Build the latest run preview and response controls.
 * Crea la vista y los controles de la última tarea.
 *
 * @param {Object} run Latest run state. / Datos de la tarea.
 *
 * @param {?Object} finalStep Final agent response, when available. / Respuesta final, si está disponible.
 *
 * @param {Function} display Callback that renders Markdown or raw text. / Función que muestra el texto.
 *
 * @return {string} Activity panel HTML. / HTML del panel de actividad.
 */
function renderSteps(run, finalStep, display) {
  if (!run) {
    return `<div class="empty">${t('emptyWork')}</div>`;
  }
  const parts = [
    `<div class="task-title">${escapeHtml(run.task)} `,
    `<button class="text-button copy-worklog">${t('copyWorklog')}`,
    '</button></div>',
  ];
  if (finalStep) {
    parts.push(
      '<div class="final-output"><div class="final-head">',
      `<strong>${t('finalResponse')}</strong><div>`,
      `<button class="text-button toggle-markdown">${rawMarkdown
        ? t('preview') : t('markdown')}</button>`,
      `<button class="text-button copy-final">${t('copyMarkdown')}</button>`,
      '<button class="download-final" type="button">',
      `${t('downloadFinal')}</button></div></div>`,
      display(finalStep.output), '</div>',
    );
  }
  const previous = run.steps.filter((step) => !step.final);
  parts.push(
    `<details class="prior-work" ${finalStep && !showPrior
      ? '' : 'open'}><summary>${t('agentWork', {count: previous.length})}</summary>`,
  );
  for (const step of previous) {
    parts.push(
      '<div class="step"><div class="step-head">',
      `<strong>${escapeHtml(step.agent)}</strong>`,
      `<button class="text-button copy-agent" data-agent="${
        escapeHtml(step.id)}">${t('copyMarkdown')}</button></div>`,
      display(step.output), '</div>',
    );
  }
  parts.push('</details>');
  if (run.partial?.output) {
    const label = run.status === 'running'
      ? t('streaming') : t('incomplete');
    parts.push(
      '<div class="step live-response"><div class="step-head">',
      `<strong>${escapeHtml(run.partial.agent)} · ${label}</strong>`,
      '</div><pre class="raw-markdown">',
      escapeHtml(run.partial.output), '</pre></div>',
    );
  }
  if (run.error) {
    parts.push(`<div class="error-box"><strong>${t('agentError')}</strong><p>`,
      escapeHtml(run.error), '</p></div>');
  }
  if (run.status === 'running' && !run.partial?.output) {
    parts.push(`<div class="empty">${t('working')}</div>`);
  }
  return parts.join('');
}
/**
 * Render the office, team, settings, and latest run.
 * Muestra la oficina, el equipo, los ajustes y la tarea.
 *
 * @param {Object} state Current server state. / Estado actual.
 */
function render(state) {
  renderedSignature = signature(state);
  for (const a of state.agents) {
    if (images[a.name] && !images[a.id]) {
      images[a.id] = images[a.name];
      delete images[a.name];
      try {
        localStorage.setItem('atomicOfficeSprites', JSON.stringify(images));
      } catch {}
    }
  }
  current = state;
  $('endpoint').value =
    document.activeElement === $('endpoint')
      ? $('endpoint').value
      : state.base_url;
  if (document.activeElement !== $('modelTimeout'))
    $('modelTimeout').value = state.model_timeout || 600;
  if (document.activeElement !== $('streamResponse'))
    $('streamResponse').checked = !!state.stream;
  if (document.activeElement !== $('temperature'))
    $('temperature').value = state.temperature ?? '';
  if (document.activeElement !== $('model')) $('model').value = state.model;
  const run = state.runs[0];
  $('runButton').disabled = !!state.runs.find((r) => r.status === 'running');
  const faces = [
    '👩🏽‍💻', '🧑🏽‍💻', '👨🏾‍💻', '👩🏻‍💻',
    '🧑🏻‍💻', '👨🏻‍💻', '👩🏾‍💻', '🧑🏿‍💻',
  ];
  renderDesks(state.agents);
  $('characters').innerHTML = state.agents
    .map((a) => {
      const busy = run?.active === a.id;
      const done = run?.steps.some((step) => step.id === a.id);
      const status = busy ? '✎' : done ? '✓' : '·';
      return [
        `<div class="walker ${busy ? 'busy' : done ? 'done' : ''}"`,
        ` data-id="${escapeHtml(a.id)}">`,
        '<span class="chat-bubble" aria-hidden="true"></span>',
        `<span class="walker-status">${status}</span>`,
        `<canvas class="sprite-canvas" data-agent="${escapeHtml(a.id)}"`,
        ' width="32" height="32"></canvas>',
        `<span class="walker-name">${escapeHtml(a.name)}</span></div>`,
      ].join('');
    })
    .join('');
  setupDragging();
  $('teamList').innerHTML = state.agents
    .map(
      (a, i) => [
        `<div class="team-member"><div class="avatar">${faces[i]}</div>`,
        `<div><strong>${escapeHtml(a.name)}</strong>`,
        `<small>${escapeHtml(a.role)} · ${t('mainOffice')}</small></div>`,
        `<button class="text-button edit-one" data-id="${
          escapeHtml(a.id)}">${t('edit')}</button></div>`,
      ].join(''),
    )
    .join('');
  document
    .querySelectorAll('.edit-one')
    .forEach(
      (button) => (button.onclick = () => openAgentEditor(button.dataset.id)),
    );
  $('officeCaption').textContent = run?.active
    ? t('agentWorking', {name: state.agents.find(
      (a) => a.id === run.active)?.name || t('newAgent')})
    : run?.status === 'done'
      ? t('assignmentCompleted')
      : run?.status === 'error'
        ? t('needsAttention')
        : t('teamReady');
  $('runStatus').textContent = run ? t(run.status) : t('noRuns');
  const finalStep = run?.steps.find((s) => s.final);
  /**
   * Render the response in raw or preview mode.
   * Muestra la respuesta como texto o vista previa.
   *
   * @param {string} value Markdown or display text. / Texto de entrada.
   *
   * @return {string} Response HTML. / HTML de la respuesta.
   */
  const display = (value) =>
    rawMarkdown
      ? `<pre class="raw-markdown">${escapeHtml(value)}</pre>`
      : `<div class="markdown-rendered">${markdownHtml(value)}</div>`;
  $('steps').innerHTML = renderSteps(run, finalStep, display);
  if (run) {
    $('steps').querySelector('.prior-work').ontoggle = (event) => {
      showPrior = event.target.open;
    };
    $('steps').querySelector('.copy-worklog').onclick = () =>
      copyMarkdown(worklogMarkdown(run));
    const toggle = $('steps').querySelector('.toggle-markdown');
    if (toggle)
      toggle.onclick = () => {
        rawMarkdown = !rawMarkdown;
        render(current);
      };
    const download = $('steps').querySelector('.download-final');
    if (download)
      download.onclick = async () => {
        try {
          download.disabled = true;
          const file = new Blob([finalStep.output + '\n'], {
            type: 'text/markdown;charset=utf-8',
          });
          const url = URL.createObjectURL(file);
          const link = document.createElement('a');
          link.href = url;
          link.download = `atomic-office-${run.id}-final.md`;
          document.body.append(link);
          link.click();
          link.remove();
          setTimeout(() => URL.revokeObjectURL(url), 1000);
        } catch (error) {
          showError(error);
        } finally {
          download.disabled = false;
        }
      };
    const copy = $('steps').querySelector('.copy-final');
    if (copy) copy.onclick = () => copyMarkdown(finalStep.output);
    $('steps')
      .querySelectorAll('.copy-agent')
      .forEach(
        (button) =>
          (button.onclick = () => {
            const step = run.steps.find(
              (s) => s.id === button.dataset.agent && !s.final,
            );
            if (step) copyMarkdown(step.output);
          }),
      );
  }
}
/**
 * Refresh only the partial response during streaming.
 * Actualiza solo la respuesta parcial durante la generación.
 *
 * @param {Object} run Latest run state. / Datos de la tarea.
 */
function updateLive(run) {
  let live = $('steps').querySelector('.live-response');
  if (!run?.partial?.output) {
    live?.remove();
    return;
  }
  if (!live) {
    $('steps').querySelector('.empty')?.remove();
    $('steps').insertAdjacentHTML(
      'beforeend',
      '<div class="step live-response"></div>',
    );
    live = $('steps').querySelector('.live-response');
  }
  if (!live.querySelector('pre')) {
    live.innerHTML = [
      '<div class="step-head"><strong>',
      escapeHtml(run.partial.agent), ` · ${t('streaming')}</strong></div>`,
      '<pre class="raw-markdown"></pre>',
    ].join('');
  }
  const content = live.querySelector('pre');
  if (run.partial.output.startsWith(content.textContent)) {
    content.append(document.createTextNode(
      run.partial.output.slice(content.textContent.length),
    ));
  } else {
    content.textContent = run.partial.output;
  }
}
/**
 * Fetch state and redraw changed sections.
 * Consulta el estado y actualiza las secciones modificadas.
 */
async function refresh() {
  try {
    const state = await request('/api/state');
    if (signature(state) !== renderedSignature) {
      render(state);
    } else {
      const previousOutput = current?.runs[0]?.partial?.output;
      current = state;
      if (previousOutput !== state.runs[0]?.partial?.output) {
        updateLive(state.runs[0]);
      }
    }
  } catch (error) {
    showError(error);
  }
}
/**
 * Schedule regular state checks while the UI is open.
 * Programa consultas periódicas del estado.
 */
async function poll() {
  await refresh();
  const running = current?.runs[0]?.status === 'running';
  setTimeout(poll, running ? 400 : 1500);
}
/**
 * Load model choices and show connection status.
 * Carga los modelos y muestra el estado de conexión.
 */
async function detect() {
  try {
    const data = await request('/api/models');
    models = data.data || [];
    const old = current?.model || $('model').value;
    $('model').innerHTML =
      `<option value="">${t('selectModel')}</option>` +
      models
        .map(
          (m) =>
            `<option value="${escapeHtml(m.id)}">${escapeHtml(m.id)}</option>`,
        )
        .join('');
    $('model').value = models.some((m) => m.id === old) ? old : '';
    $('light').classList.add('on');
    $('connectionText').textContent = t('connected');
    $('message').textContent = '';
  } catch (e) {
    $('light').classList.remove('on');
    $('connectionText').textContent = t('offline');
    showError(e);
  }
}
$('refreshModels').onclick = async () => {
  try {
    await request('/api/settings', {
      method: 'POST',
      body: JSON.stringify({
        base_url: $('endpoint').value,
        model: $('model').value,
        model_timeout: +$('modelTimeout').value,
        stream: $('streamResponse').checked,
        temperature: $('temperature').value === ''
          ? null : +$('temperature').value,
      }),
    });
    await refresh();
    await detect();
  } catch (e) {
    showError(e);
  }
};
$('saveSettings').onclick = async () => {
  try {
    await request('/api/settings', {
      method: 'POST',
      body: JSON.stringify({
        base_url: $('endpoint').value,
        model: $('model').value,
        model_timeout: +$('modelTimeout').value,
        stream: $('streamResponse').checked,
        temperature: $('temperature').value === ''
          ? null : +$('temperature').value,
      }),
    });
    $('message').textContent = t('settingsSaved');
    await refresh();
  } catch (e) {
    showError(e);
  }
};
$('runButton').onclick = async () => {
  try {
    await request('/api/runs', {
      method: 'POST',
      body: JSON.stringify({ task: $('task').value }),
    });
    $('task').value = '';
    $('message').textContent = '';
    await refresh();
  } catch (e) {
    showError(e);
  }
};
$('languageSelect').value = getLanguage();
applyTranslations();
$('connectionText').textContent = t('checking');
$('languageSelect').onchange = () => {
  setLanguage($('languageSelect').value);
  applyTranslations();
  $('model').querySelector('option[value=""]').textContent = t('selectModel');
  $('connectionText').textContent = $('light').classList.contains('on')
    ? t('connected') : t('offline');
  if (current) render(current);
  refreshEditorLanguage();
};
initEditors(() => ({ current, images }), refresh);
initRpg(() => ({ current, images }));

refresh().then(async () => {
  await migrateSprites();
  await refresh();
  detect();
  poll();
});
