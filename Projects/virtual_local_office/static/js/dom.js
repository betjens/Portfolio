import { t } from './i18n.js';
/**
 * Find a DOM element by ID.
 * Busca un elemento del documento por su identificador.
 *
 * @param {string} id DOM or agent identifier. / Identificador.
 *
 * @return {?Element} DOM element or null. / Elemento o nulo.
 */
export const $ = (id) => document.getElementById(id);
/**
 * Send JSON to an office API endpoint.
 * Envía JSON a una ruta de la API de la oficina.
 *
 * @param {string} path API URL path. / Ruta de la API.
 *
 * @param {Object} options Optional fetch settings. / Opciones de solicitud.
 *
 * @return {Promise<Object>} Parsed response JSON. / Respuesta JSON analizada.
 */
export async function request(path, options = {}) {
  const res = await fetch(path, {
    ...options,
    headers: { 'Content-Type': 'application/json' },
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.error || t('requestFailed'));
  return data;
}
/**
 * Escape unsafe characters for HTML text and attributes.
 * Escapa los caracteres inseguros para HTML.
 *
 * @param {*} s Value to escape. / Valor que se escapará.
 *
 * @return {string} Escaped HTML string. / Cadena HTML escapada.
 */
export function escapeHtml(s) {
  return String(s).replace(
    /[&<>"']/g,
    (c) =>
      ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' })[
        c
      ],
  );
}

/**
 * Show a request error near the assignment form.
 * Muestra un error cerca del formulario de tareas.
 *
 * @param {Error} e Error to display. / Error que se mostrará.
 */
export function showError(e) {
  $('message').textContent = e.message || String(e);
}
