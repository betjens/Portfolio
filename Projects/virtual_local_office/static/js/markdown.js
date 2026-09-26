import { t } from './i18n.js';
import { $, escapeHtml, showError } from './dom.js';

/**
 * Render supported Markdown as safe HTML.
 * Convierte el Markdown compatible en HTML seguro.
 *
 * @param {string} value Markdown or display text. / Texto de entrada.
 *
 * @return {string} Escaped HTML markup. / HTML escapado.
 */
export function markdownHtml(value) {
  /**
   * Render escaped inline code and bold text.
   * Convierte el código en línea y el texto en negrita.
   *
   * @param {string} value Markdown or display text. / Texto de entrada.
   *
   * @return {string} Inline HTML markup. / HTML en línea.
   */
  const inline = (value) =>
    escapeHtml(value)
      .replace(/`([^`]+)`/g, '<code>$1</code>')
      .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
  const lines = String(value).split(/\r?\n/);
  let html = '',
    code = false,
    list = false;
  /**
   * Close an open bullet list in the current markup.
   * Cierra la lista de viñetas abierta.
   */
  const closeList = () => {
    if (list) {
      html += '</ul>';
      list = false;
    }
  };
  for (const line of lines) {
    if (/^```/.test(line)) {
      closeList();
      html += code ? '</code></pre>' : '<pre><code>';
      code = !code;
      continue;
    }
    if (code) {
      html += escapeHtml(line) + '\n';
      continue;
    }
    if (!line.trim()) {
      closeList();
      continue;
    }
    const heading = line.match(/^(#{1,4})\s+(.+)$/);
    if (heading) {
      closeList();
      const n = heading[1].length;
      html += `<h${n}>${inline(heading[2])}</h${n}>`;
      continue;
    }
    const bullet = line.match(/^\s*[-*]\s+(.+)$/);
    if (bullet) {
      if (!list) {
        html += '<ul>';
        list = true;
      }
      html += `<li>${inline(bullet[1])}</li>`;
      continue;
    }
    closeList();
    html += `<p>${inline(line)}</p>`;
  }
  closeList();
  if (code) html += '</code></pre>';
  return html;
}
/**
 * Compose all agent steps as one Markdown worklog.
 * Combina los pasos en un registro Markdown.
 *
 * @param {Object} run Latest run state. / Datos de la tarea.
 *
 * @return {string} Complete worklog text. / Texto completo del registro.
 */
export function worklogMarkdown(run) {
  const lines = [
    `# ${t('worklogTitle')}`, '', `${t('task')}: ${run.task}`, '',
    `${t('status')}: ${t(run.status)}`, '',
  ];
  run.steps.forEach((step, index) => {
    lines.push(`## ${index + 1}. ${step.agent}`, '', step.output, '');
  });
  if (run.partial?.output && run.status === 'error') {
    lines.push(`## ${t('incomplete')}`, '', run.partial.output, '');
  }
  if (run.error) lines.push(`## ${t('error')}`, '', run.error, '');
  return lines.join('\n');
}
/**
 * Copy Markdown using the clipboard or fallback.
 * Copia Markdown mediante el portapapeles.
 *
 * @param {string} value Markdown or display text. / Texto de entrada.
 */
export async function copyMarkdown(value) {
  try {
    if (navigator.clipboard?.writeText) {
      await navigator.clipboard.writeText(value);
    } else {
      const input = document.createElement('textarea');
      input.value = value;
      document.body.append(input);
      input.select();
      if (!document.execCommand('copy')) throw Error(t('copyUnavailable'));
      input.remove();
    }
    $('message').textContent = t('copied');
  } catch (error) {
    showError(error);
  }
}
