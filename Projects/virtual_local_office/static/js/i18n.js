/** Translations for the office interface / Traducciones de la interfaz. */
const translations = {
  en: {
    localStudio: 'LOCAL AGENT STUDIO', workspace: 'WORKSPACE',
    office: 'Office', agentTeam: 'Agent team', activity: 'Activity',
    localMachine: 'Everything runs on your machine',
    overview: 'WORKSPACE / OVERVIEW', yourOffice: 'Your agent office',
    intro: 'Give your local AI team a task. Watch the work unfold.',
    language: 'Language', localFirst: '● LOCAL FIRST', liveView: 'LIVE VIEW',
    theOffice: 'The office', live: 'LIVE', questBoard: 'QUEST BOARD',
    cafeBar: 'Café bar', newAssignment: 'NEW ASSIGNMENT',
    taskQuestion: 'What should the team work on?',
    taskPlaceholder: 'e.g. Draft a technical plan for my new project…',
    modeHint: 'Each agent builds on the previous result',
    startAssignment: 'Start assignment', workLog: 'WORK LOG',
    latestAssignment: 'Latest assignment', noRuns: 'No runs yet',
    emptyWork: 'Start an assignment to see each agent’s work here.',
    yourPeople: 'YOUR PEOPLE', addAgent: '+ Add agent',
    connection: 'CONNECTION', apiEndpoint: 'API endpoint', model: 'Model',
    selectModel: 'Select a model…', timeout: 'Response timeout (seconds)',
    streamResponses: 'Stream responses as agents work',
    temperature: 'Temperature (optional, 0–2)',
    modelDefault: 'Use model default', detectModels: '↻ Detect models',
    save: 'Save', connectionHint: 'Enable the local API server in Atomic Chat ' +
      'and load a model first.',
    tipTitle: 'A little office, a lot of possibility.',
    tipBody: 'Your agents use the same local model with different ' +
      'responsibilities.',
    teamBuilder: 'TEAM BUILDER', customizeAgents: 'Customize your agents',
    editorHelp: 'Set this agent’s role, behavior and character image.',
    cancel: 'Cancel', saveTeam: 'Save team', mainOffice: 'Main office',
    edit: 'Edit', agentWorking: '{name} is working…',
    assignmentCompleted: 'Assignment completed',
    needsAttention: 'Something needs attention',
    teamReady: 'Your team is ready for work', running: 'RUNNING',
    done: 'DONE', error: 'ERROR',
    copyWorklog: 'Copy full worklog', finalResponse: 'Final response',
    preview: 'Preview', markdown: 'Markdown', copyMarkdown: 'Copy Markdown',
    downloadFinal: 'Download final output ↓', agentWork: 'Agent work ({count})',
    streaming: 'Streaming', incomplete: 'Incomplete response',
    agentError: 'Agent error', working: 'Working…',
    connected: 'Atomic Chat connected', offline: 'Atomic Chat offline',
    checking: 'Checking Atomic Chat…', settingsSaved: 'Settings saved',
    newAgent: 'New agent', editAgent: 'Edit agent', addAnAgent: 'Add an agent',
    editNamed: 'Edit {name}', moveUp: 'Move up', moveDown: 'Move down',
    removeAgent: 'Remove agent', name: 'Name', role: 'Role',
    characterImage: 'Character image / sprite sheet',
    customImage: 'Custom image loaded', builtInImage: 'Built-in animated character',
    frameWidth: 'Frame width', frameHeight: 'Frame height', row: 'Row',
    frames: 'Frames', fps: 'FPS', imageHelp: 'One frame works for a portrait; ' +
      'use multiple equal frames for animation.',
    resetImage: 'Reset image', behavior: 'Behavior (SKILL.md)',
    skillPlaceholder: 'Describe how this agent should work, its priorities ' +
      'and output format…',
    skillHelp: 'Markdown is sent as this agent’s instructions. This does ' +
      'not install tools or run code from the file.',
    skillTooLarge: 'Keep SKILL.md under 12,000 characters',
    imageTooLarge: 'Use an image smaller than 1.5 MB',
    imageReady: 'Image ready to save', imageReset: 'Image will be reset on Save',
    newAgentRole: 'Describe this agent’s responsibility.',
    maximumAgents: 'Maximum 12 agents', copied: 'Markdown copied to clipboard',
    copyUnavailable: 'Copy unavailable', requestFailed: 'Request failed',
    worklogTitle: 'Atomic Office worklog', task: 'Task', status: 'Status',
  },
  es: {
    localStudio: 'ESTUDIO LOCAL DE AGENTES', workspace: 'ESPACIO DE TRABAJO',
    office: 'Oficina', agentTeam: 'Equipo de agentes', activity: 'Actividad',
    localMachine: 'Todo funciona en tu equipo',
    overview: 'ESPACIO DE TRABAJO / RESUMEN', yourOffice: 'Tu oficina de agentes',
    intro: 'Asigna una tarea a tu equipo de IA local. Sigue su progreso.',
    language: 'Idioma', localFirst: '● FUNCIONA EN LOCAL',
    liveView: 'VISTA EN VIVO', theOffice: 'La oficina', live: 'EN VIVO',
    questBoard: 'TABLÓN DE TAREAS', cafeBar: 'Cafetería',
    newAssignment: 'NUEVA TAREA', taskQuestion: '¿En qué trabajará el equipo?',
    taskPlaceholder: 'p. ej., prepara un plan técnico para mi proyecto…',
    modeHint: 'Cada agente continúa el trabajo del anterior',
    startAssignment: 'Iniciar tarea', workLog: 'REGISTRO DE TRABAJO',
    latestAssignment: 'Última tarea', noRuns: 'Aún no hay tareas',
    emptyWork: 'Inicia una tarea para ver aquí el trabajo de cada agente.',
    yourPeople: 'TU EQUIPO', addAgent: '+ Añadir agente',
    connection: 'CONEXIÓN', apiEndpoint: 'Dirección de la API',
    model: 'Modelo', selectModel: 'Selecciona un modelo…',
    timeout: 'Tiempo de espera (segundos)',
    streamResponses: 'Mostrar respuestas mientras trabajan los agentes',
    temperature: 'Temperatura (opcional, 0–2)',
    modelDefault: 'Usar valor del modelo',
    detectModels: '↻ Detectar modelos', save: 'Guardar',
    connectionHint: 'Activa la API local de Atomic Chat y carga un modelo.',
    tipTitle: 'Una pequeña oficina, muchas posibilidades.',
    tipBody: 'Tus agentes usan el mismo modelo local con distintas funciones.',
    teamBuilder: 'CONFIGURAR EQUIPO',
    customizeAgents: 'Personaliza tus agentes',
    editorHelp: 'Configura la función, el comportamiento y la imagen del agente.',
    cancel: 'Cancelar', saveTeam: 'Guardar equipo',
    mainOffice: 'Oficina principal', edit: 'Editar',
    agentWorking: '{name} está trabajando…',
    assignmentCompleted: 'Tarea completada',
    needsAttention: 'Hay algo que requiere atención',
    teamReady: 'El equipo está listo para trabajar',
    running: 'EN CURSO', done: 'COMPLETADA', error: 'ERROR',
    copyWorklog: 'Copiar registro completo', finalResponse: 'Respuesta final',
    preview: 'Vista previa', markdown: 'Markdown',
    copyMarkdown: 'Copiar Markdown',
    downloadFinal: 'Descargar respuesta final ↓',
    agentWork: 'Trabajo de los agentes ({count})',
    streaming: 'Generando', incomplete: 'Respuesta incompleta',
    agentError: 'Error del agente', working: 'Trabajando…',
    connected: 'Atomic Chat conectado', offline: 'Atomic Chat sin conexión',
    checking: 'Comprobando Atomic Chat…',
    settingsSaved: 'Configuración guardada',
    newAgent: 'Nuevo agente', editAgent: 'Editar agente',
    addAnAgent: 'Añadir un agente', editNamed: 'Editar a {name}',
    moveUp: 'Subir', moveDown: 'Bajar', removeAgent: 'Eliminar agente',
    name: 'Nombre', role: 'Función',
    characterImage: 'Imagen del personaje / hoja de sprites',
    customImage: 'Imagen personalizada cargada',
    builtInImage: 'Personaje animado incluido',
    frameWidth: 'Ancho del fotograma', frameHeight: 'Alto del fotograma',
    row: 'Fila', frames: 'Fotogramas', fps: 'FPS',
    imageHelp: 'Un fotograma sirve como retrato; usa varios fotogramas ' +
      'del mismo tamaño para animarlo.',
    resetImage: 'Restablecer imagen', behavior: 'Comportamiento (SKILL.md)',
    skillPlaceholder: 'Describe cómo debe trabajar el agente, sus ' +
      'prioridades y el formato de respuesta…',
    skillHelp: 'El Markdown se envía como instrucciones del agente. ' +
      'El archivo no instala herramientas ni ejecuta código.',
    skillTooLarge: 'Mantén SKILL.md por debajo de 12 000 caracteres',
    imageTooLarge: 'Usa una imagen de menos de 1,5 MB',
    imageReady: 'Imagen lista para guardar',
    imageReset: 'La imagen se restablecerá al guardar',
    newAgentRole: 'Describe la función de este agente.',
    maximumAgents: 'Máximo de 12 agentes',
    copied: 'Markdown copiado al portapapeles',
    copyUnavailable: 'No se puede copiar', requestFailed: 'Solicitud fallida',
    worklogTitle: 'Registro de Atomic Office', task: 'Tarea', status: 'Estado',
  },
};

/**
 * Return the saved UI language, defaulting to English.
 * Devuelve el idioma guardado o inglés de forma predeterminada.
 *
 * @return {string} Supported language code / Código de idioma compatible.
 */
export function getLanguage() {
  try {
    return localStorage.getItem('atomicOfficeLanguage') === 'es' ? 'es' : 'en';
  } catch {
    return 'en';
  }
}

/**
 * Save the selected language for later visits.
 * Guarda el idioma elegido para futuras visitas.
 *
 * @param {string} language Language code / Código de idioma.
 */
export function setLanguage(language) {
  try {
    localStorage.setItem('atomicOfficeLanguage', language === 'es' ? 'es' : 'en');
  } catch {}
}

/**
 * Translate a UI key and replace named placeholders.
 * Traduce una clave de la interfaz y sustituye sus marcadores.
 *
 * @param {string} key Translation key / Clave de traducción.
 * @param {Object<string, *>} values Placeholder values / Valores insertados.
 * @return {string} Localized text / Texto traducido.
 */
export function t(key, values = {}) {
  const template = translations[getLanguage()][key] ?? translations.en[key] ?? key;
  return template.replace(/\{(\w+)\}/g, (_, name) => String(values[name] ?? ''));
}

/**
 * Update the translated page elements and document language.
 * Actualiza los elementos traducidos y el idioma del documento.
 */
export function applyTranslations() {
  document.documentElement.lang = getLanguage();
  document.querySelectorAll('[data-i18n]').forEach((element) => {
    element.textContent = t(element.dataset.i18n);
  });
  document.querySelectorAll('[data-i18n-placeholder]').forEach((element) => {
    element.placeholder = t(element.dataset.i18nPlaceholder);
  });
  document.querySelectorAll('[data-i18n-aria]').forEach((element) => {
    element.setAttribute('aria-label', t(element.dataset.i18nAria));
  });
}
