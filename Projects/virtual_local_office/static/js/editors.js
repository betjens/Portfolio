import { t } from './i18n.js';
import { $, request, escapeHtml } from './dom.js';

/**
 * Supply current UI state to editor callbacks.
 * Proporciona el estado de la interfaz al editor.
 *
 * @return {Object} Current editor context. / Contexto actual del editor.
 */
let getContext = () => ({});
/**
 * Refresh editor state after saving.
 * Actualiza el editor después de guardar.
 *
 * @return {Promise<void>} Promise for the refresh. / Valor devuelto.
 */
let refresh = async () => {};
/**
 * Connect the agent editor to shared UI state.
 * Conecta el editor con el estado compartido.
 *
 * @param {Function} context Callback supplying current UI state. / Función que devuelve el estado actual.
 *
 * @param {Function} refreshFn Callback used after editor changes. / Función para actualizar el editor.
 */
export function initEditors(context, refreshFn) {
  getContext = context;
  refresh = refreshFn;
}

let draftAgents = [];
let focusedAgentId = null;
/**
 * Copy an agent profile before editing.
 * Copia el perfil antes de editarlo.
 *
 * @param {Object} a Agent profile. / Perfil del agente.
 *
 * @return {Object} Shallow profile copy. / Copia superficial del perfil.
 */
const copyAgent = (a) => ({ ...a });
/**
 * Create the form markup for one agent.
 * Crea el formulario de un agente.
 *
 * @param {Object} a Agent profile. / Perfil del agente.
 *
 * @param {number} i Agent index in the team. / Índice del agente.
 *
 * @return {string} Agent editor HTML. / HTML del editor de agentes.
 */
function agentCard(a, i) {
  const images = getContext().images;
  const imageHint = a.image || images[a.id]?.data
    ? t('customImage') : t('builtInImage');
  const spriteFields = [
    [t('frameWidth'), 'sprite-w', a.frame_width || images[a.id]?.w || 32, 8, 512],
    [t('frameHeight'), 'sprite-h',
      a.frame_height || images[a.id]?.h || 32, 8, 512],
    [t('row'), 'sprite-row', a.sprite_row ?? images[a.id]?.row ?? 0, 0, 50],
    [t('frames'), 'sprite-count',
      a.sprite_frames || images[a.id]?.frames || 1, 1, 32],
    [t('fps'), 'sprite-fps', a.sprite_fps || images[a.id]?.fps || 6, 1, 24],
  ];
  return [
    `<div class="agent-edit-card" data-index="${i}">`,
    '<div class="agent-edit-top"><strong>',
    focusedAgentId === 'new' ? t('newAgent') : t('editAgent'),
    '</strong><div class="team-only">',
    '<button type="button" class="text-button move-up"',
    ` title="${t('moveUp')}">↑</button>`,
    '<button type="button" class="text-button move-down"',
    ` title="${t('moveDown')}">↓</button>`,
    '<button type="button" class="text-button remove-agent"',
    ` title="${t('removeAgent')}">✕</button>`,
    '</div></div><div class="agent-edit-grid">',
    `<label>${t('name')}<input class="agent-name" value="${escapeHtml(a.name || '')}">`,
    '</label>',
    `<label>${t('role')}<input class="agent-role" value="${escapeHtml(a.role || '')}">`,
    '</label></div>',
    `<label class="upload-label">${t('characterImage')}`,
    '<input type="file" class="agent-image"',
    ' accept="image/png,image/webp,image/gif"></label>',
    '<div class="image-details">',
    ...spriteFields.map(([label, cls, value, min, max]) =>
      `<label>${label}<input class="${cls}" type="number"` +
      ` min="${min}" max="${max}" value="${value}"></label>`),
    '</div>',
    `<small class="asset-hint">${imageHint} · `,
    `${t('imageHelp')}</small>`,
    `<button type="button" class="text-button clear-image">${t('resetImage')}`,
    `</button><label class="upload-label">${t('behavior')}`,
    '<input type="file" class="agent-skill-file"',
    ' accept=".md,text/markdown,text/plain"></label>',
    '<textarea class="agent-skill"',
    ` placeholder="${escapeHtml(t('skillPlaceholder'))}"`,
    `>${escapeHtml(a.skill || '')}`,
    `</textarea><small class="asset-hint">${t('skillHelp')}`,

    '</small></div>',
  ].join('');
}
/**
 * Copy visible form values into the agent draft.
 * Copia los valores del formulario al borrador.
 */
function syncEditor() {
  document.querySelectorAll('.agent-edit-card').forEach((el, i) => {
    draftAgents[i].name = el.querySelector('.agent-name').value;
    draftAgents[i].role = el.querySelector('.agent-role').value;
    draftAgents[i].skill = el.querySelector('.agent-skill').value;
    for (const [key, selector] of [
      ['frame_width', '.sprite-w'],
      ['frame_height', '.sprite-h'],
      ['sprite_row', '.sprite-row'],
      ['sprite_frames', '.sprite-count'],
      ['sprite_fps', '.sprite-fps'],
    ])
      draftAgents[i][key] = +el.querySelector(selector).value;
  });
}
/**
 * Render draft profiles and bind their controls.
 * Muestra los borradores y conecta sus controles.
 */
function renderEditor() {
  $('agentEditor').innerHTML = draftAgents.map(agentCard).join('');
  document.querySelectorAll('.agent-edit-card').forEach((el, i) => {
    el.querySelector('.move-up').onclick = () => {
      syncEditor();
      if (i > 0)
        [draftAgents[i - 1], draftAgents[i]] = [
          draftAgents[i],
          draftAgents[i - 1],
        ];
      renderEditor();
    };
    el.querySelector('.move-down').onclick = () => {
      syncEditor();
      if (i < draftAgents.length - 1)
        [draftAgents[i + 1], draftAgents[i]] = [
          draftAgents[i],
          draftAgents[i + 1],
        ];
      renderEditor();
    };
    el.querySelector('.remove-agent').onclick = () => {
      syncEditor();
      if (draftAgents.length > 1) {
        draftAgents.splice(i, 1);
        renderEditor();
      }
    };
    el.querySelector('.agent-skill-file').onchange = async (event) => {
      const file = event.target.files[0];
      if (!file) return;
      if (file.size > 15000) {
        alert(t('skillTooLarge'));
        return;
      }
      el.querySelector('.agent-skill').value = await file.text();
      syncEditor();
    };
    el.querySelector('.agent-image').onchange = (event) => {
      const file = event.target.files[0];
      if (!file) return;
      if (file.size > 1500000) {
        alert(t('imageTooLarge'));
        return;
      }
      const reader = new FileReader();
      reader.onload = () => {
        draftAgents[i].pendingImage = {
          data: String(reader.result).split(',')[1],
          extension: file.name.split('.').pop().toLowerCase(),
        };
        el.querySelector('.asset-hint').textContent = t('imageReady');
      };
      reader.readAsDataURL(file);
    };
    el.querySelector('.clear-image').onclick = () => {
      draftAgents[i].resetImage = true;
      draftAgents[i].pendingImage = null;
      el.querySelector('.asset-hint').textContent =
        t('imageReset');
    };
  });
}
/**
 * Open an agent editor for an existing or new agent.
 * Abre el editor para un agente nuevo o existente.
 *
 * @param {string} id DOM or agent identifier. / Identificador.
 */
export function openAgentEditor(id) {
  focusedAgentId = id;
  if (id === 'new') {
    draftAgents = [
      {
        id: 'new',
        name: t('newAgent'),
        role: t('newAgentRole'),
        skill: '',
        x: 50,
        y: 63,
      },
    ];
  } else {
    draftAgents = [
      copyAgent(getContext().current.agents.find((a) => a.id === id)),
    ];
  }
  $('teamDialog').querySelector('h2').textContent =
    id === 'new' ? t('addAnAgent') :
      t('editNamed', {name: draftAgents[0].name});
  renderEditor();
  $('teamDialog').showModal();
}
$('addPerson').onclick = () => {
  if (getContext().current.agents.length >= 12) {
    alert(t('maximumAgents'));
    return;
  }
  openAgentEditor('new');
};
$('closeDialog').onclick = $('cancelTeam').onclick = () =>
  $('teamDialog').close();
$('saveTeam').onclick = async () => {
  try {
    syncEditor();
    const agent = draftAgents[0];
    const { pendingImage, resetImage, ...profile } = agent;
    let id = agent.id;
    if (focusedAgentId === 'new') {
      const result = await request('/api/agent-create', {
        method: 'POST',
        body: JSON.stringify({ agent: profile }),
      });
      id = result.id;
    } else {
      await request('/api/agent', {
        method: 'POST',
        body: JSON.stringify({ agent: profile }),
      });
    }
    if (resetImage)
      await request('/api/agent-image', {
        method: 'POST',
        body: JSON.stringify({ id, reset: true }),
      });
    if (pendingImage)
      await request('/api/agent-image', {
        method: 'POST',
        body: JSON.stringify({ id, ...pendingImage }),
      });
    $('teamDialog').close();
    focusedAgentId = null;
    await refresh();
  } catch (error) {
    alert(error.message);
  }
};

/**
 * Redraw an open agent editor after a language change.
 * Vuelve a dibujar el editor abierto al cambiar de idioma.
 */
export function refreshEditorLanguage() {
  if (!$('teamDialog').open) return;
  syncEditor();
  $('teamDialog').querySelector('h2').textContent = focusedAgentId === 'new'
    ? t('addAnAgent') : t('editNamed', {name: draftAgents[0].name});
  renderEditor();
}
