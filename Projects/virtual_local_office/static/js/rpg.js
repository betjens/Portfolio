import { $, request, showError } from './dom.js';

/**
 * Supply live office state to animation callbacks.
 * Proporciona el estado de la oficina a la animación.
 */
let getContext = () => ({});
let tick = 0;
/**
 * Connect the animation to current office state.
 * Conecta la animación con el estado de la oficina.
 *
 * @param {Function} context Callback supplying current UI state. / Función que devuelve el estado actual.
 */
export function initRpg(context) {
  getContext = context;
}

/**
 * Allow desk positions to be changed in the left work area.
 * Permite mover los escritorios en el área izquierda.
 */
export function setupDragging() {
  document.querySelectorAll('.station').forEach((station) => {
    station.onpointerdown = (e) => {
      if (e.button !== 0 || !station.dataset.id) return;
      station.setPointerCapture(e.pointerId);
      const scene = $('officeScene');
      let moved = false;
      station.onpointermove = (event) => {
        if (!station.hasPointerCapture(event.pointerId)) return;
        moved = true;
        const rect = scene.getBoundingClientRect();
        const x = 100 * (event.clientX - rect.left) / rect.width;
        const y = 100 * (event.clientY - rect.top) / rect.height;
        station.style.left = `${Math.max(10, Math.min(48, x))}%`;
        station.style.top = `${Math.max(39, Math.min(72, y))}%`;
      };
      station.onpointerup = async () => {
        station.onpointermove = null;
        if (!moved) return;
        const x = Math.round(parseFloat(station.style.left)),
          y = Math.round(parseFloat(station.style.top));
        const agent = getContext().current.agents.find(
          (a) => a.id === station.dataset.id,
        );
        agent.x = x;
        agent.y = y;
        try {
          await request('/api/positions', {
            method: 'POST',
            body: JSON.stringify({ id: agent.id, x, y }),
          });
        } catch (error) {
          showError(error);
        }
      };
    };
  });
}
// Move older browser sprites into agent folders once.
const spriteCache = new Map();
let migrating = false;
/**
 * Move older browser sprites into agent folders.
 * Traslada imágenes anteriores a las carpetas de agentes.
 */
export async function migrateSprites() {
  if (migrating || !getContext().current) return;
  migrating = true;
  try {
    for (const agent of getContext().current.agents) {
      const old =
        getContext().images[agent.id] || getContext().images[agent.name];
      if (!old?.data) continue;
      const match = old.data.match(/^data:image\/(png|webp|gif);base64,(.+)$/);
      if (!agent.image && match) {
        await request('/api/agent-image', {
          method: 'POST',
          body: JSON.stringify({
            id: agent.id,
            extension: match[1],
            data: match[2],
          }),
        });
      }
      delete getContext().images[agent.id];
      delete getContext().images[agent.name];
    }
    localStorage.setItem(
      'atomicOfficeSprites',
      JSON.stringify(getContext().images),
    );
  } catch (error) {
    showError(error);
  } finally {
    migrating = false;
  }
}
/**
 * Draw an agent when it has no valid custom sprite.
 * Dibuja el personaje predeterminado del agente.
 *
 * @param {CanvasRenderingContext2D} ctx Canvas drawing context. / Valor proporcionado.
 *
 * @param {number} i Agent index in the team. / Índice del agente.
 *
 * @param {number} frame Animation frame number. / Valor proporcionado.
 *
 * @param {boolean} busy Whether the agent is currently responding. / Valor proporcionado.
 */
function drawDefault(ctx, i, frame, busy) {
  const shirts = [
    '#647fd1',
    '#d9a057',
    '#65a88d',
    '#c77c7c',
    '#a286c2',
    '#85a5b2',
    '#ca9472',
    '#8aaf75',
  ];
  const skin = ['#c99068', '#a76747', '#8a5038', '#e2aa7e'][i % 4];
  const hair = ['#302923', '#493626', '#251f25', '#594433'][i % 4];
  /**
   * Paint one pixel-art rectangle.
   * Dibuja un rectángulo de píxeles.
   *
   * @param {number} x Horizontal pixel coordinate. / Valor proporcionado.
   *
   * @param {number} y Vertical pixel coordinate. / Valor proporcionado.
   *
   * @param {number} w Rectangle width in pixels. / Valor proporcionado.
   *
   * @param {number} h Rectangle height in pixels. / Valor proporcionado.
   *
   * @param {string} color Rectangle fill color. / Valor proporcionado.
   */
  const px = (x, y, w, h, color) => {
    ctx.fillStyle = color;
    ctx.fillRect(x, y, w, h);
  };
  const shift = busy ? frame % 2 : frame % 4 === 3 ? 1 : 0;
  px(12, 2 + shift, 9, 3, hair);
  px(10, 5 + shift, 13, 8, hair);
  px(12, 7 + shift, 9, 7, skin);
  px(14, 9 + shift, 2, 2, '#2e3433');
  px(20, 9 + shift, 2, 2, '#2e3433');
  px(12, 15 + shift, 10, 10, shirts[i % shirts.length]);
  px(9, 16 + shift, 3, 8, skin);
  px(22, 16 + shift, 3, 8, skin);
  px(12, 25 + shift, 4, 5, '#34485d');
  px(18, 25 + shift, 4, 5, '#34485d');
  px(11, 29 + shift, 6, 2, '#393838');
  px(18, 29 + shift, 6, 2, '#393838');
  if (busy) {
    px(7, 20 + shift, 4, 3, skin);
    px(24, 20 + shift, 4, 3, skin);
  }
}
const walkerMotion = new Map();
const chatIcons = ['☕', '💬', '✨', '🍪', '🎵', '🙂', '💡'];
/**
 * Move agents between desks and café and draw each frame.
 * Mueve los agentes y dibuja cada fotograma.
 *
 * @param {number} timestamp Animation timestamp in milliseconds. / Valor proporcionado.
 */
function animate(timestamp) {
  tick++;
  document.querySelectorAll('.walker').forEach((walker, i) => {
    const canvas = walker.querySelector('.sprite-canvas');
    const ctx = canvas.getContext('2d');
    ctx.clearRect(0, 0, 32, 32);
    ctx.imageSmoothingEnabled = false;
    const id = walker.dataset.id;
    const agent = getContext().current?.agents.find((a) => a.id === id);
    if (!agent) return;
    const config = agent || getContext().images[id];
    const busy = walker.classList.contains('busy');
    const station = document.querySelector(`.station[data-id="${id}"]`);
    if (!station) return;
    const deskX = parseFloat(station.style.left),
      deskY = parseFloat(station.style.top);
    const seatX = 68 + (i % 4) * 6;
    const seatY = 67 + (i % 2) * 8;
    const homeX = deskX;
    const homeY = Math.min(84, deskY + 7);
    let motion = walkerMotion.get(id);
    if (!motion) {
      motion = {
        x: homeX, y: homeY, last: timestamp, face: 1,
        mode: i < 2 ? 'toCafe' : 'atDesk',
        until: timestamp + i * 1600,
      };
      walkerMotion.set(id, motion);
    }
    const dt = Math.min(0.05, Math.max(0, (timestamp - motion.last) / 1000));
    motion.last = timestamp;
    if (busy) {
      motion.mode = 'working';
    } else if (motion.mode === 'working') {
      motion.mode = 'toCafe';
    } else if (motion.mode === 'atDesk' && timestamp >= motion.until) {
      motion.mode = 'toCafe';
    } else if (motion.mode === 'resting' && timestamp >= motion.until) {
      motion.mode = 'toDesk';
    }
    const goingToCafe = motion.mode === 'toCafe';
    const goingHome = motion.mode === 'toDesk' || motion.mode === 'working';
    // Use the aisle as a waypoint so agents walk around the furniture.
    const crossing = goingToCafe
      ? motion.x < 55.9
      : goingHome && motion.x > 56.1;
    const targetX = crossing ? 56 : goingToCafe || motion.mode === 'resting'
      ? seatX : homeX;
    const targetY = crossing ? 70 : goingToCafe || motion.mode === 'resting'
      ? seatY : homeY;
    const scene = $('officeScene');
    const dx = (targetX - motion.x) * scene.clientWidth / 100;
    const dy = (targetY - motion.y) * scene.clientHeight / 100;
    const distance = Math.hypot(dx, dy);
    const travel = Math.min(distance, dt * (busy ? 105 : 75));
    if (distance > 0.5) {
      motion.x += (dx / distance) * travel / scene.clientWidth * 100;
      motion.y += (dy / distance) * travel / scene.clientHeight * 100;
      if (Math.abs(dx) > 0.5) motion.face = dx > 0 ? 1 : -1;
    }
    const walking = distance > 2;
    const arrived = distance < 9 && !crossing;
    if (arrived && motion.mode === 'toCafe') {
      motion.mode = 'resting';
      motion.until = timestamp + 17000 + Math.random() * 5000;
      motion.nextIcon = 0;
    } else if (arrived && motion.mode === 'toDesk') {
      motion.mode = 'atDesk';
      motion.until = timestamp + 6000 + Math.random() * 4000;
    }
    const resting = motion.mode === 'resting';
    const bubble = walker.querySelector('.chat-bubble');
    walker.classList.toggle('chatting', resting);
    if (resting && timestamp >= motion.nextIcon) {
      motion.chatIcon = chatIcons[Math.floor(Math.random() * chatIcons.length)];
      motion.nextIcon = timestamp + 2500 + Math.random() * 1500;
    }
    if (!resting) motion.chatIcon = null;
    bubble.textContent = motion.chatIcon || '';
    walker.style.left = motion.x + '%';
    walker.style.top = motion.y + '%';
    walker.style.zIndex = String(Math.round(motion.y));
    const bob = walking ? Math.sin(timestamp / 105 + i) * 2 : 0;
    canvas.style.transform = `translateY(${bob}px) scaleX(${motion.face})`;
    const src = agent.image || config?.data;
    if (src) {
      let img = spriteCache.get(id);
      if (!img || img.src !== new URL(src, location.href).href) {
        img = new Image();
        img.src = src;
        spriteCache.set(id, img);
      }
      if (img.complete && img.naturalWidth) {
        const w = Number(config.frame_width || config.w) || 32,
          h = Number(config.frame_height || config.h) || 32,
          row = Number(config.sprite_row ?? config.row) || 0,
          count = Math.min(
            Number(config.sprite_frames || config.frames) || 1,
            Math.floor(img.naturalWidth / w),
          );
        if (count > 0 && img.naturalHeight >= (row + 1) * h) {
          const frame =
            Math.floor(
              tick /
                Math.max(
                  1,
                  Math.round(
                    60 / (Number(config.sprite_fps || config.fps) || 6),
                  ),
                ),
            ) % count;
          ctx.drawImage(img, frame * w, row * h, w, h, 0, 0, 32, 32);
          return;
        }
      }
    }
    drawDefault(ctx, i, Math.floor(tick / 16), busy);
  });
  requestAnimationFrame(animate);
}
requestAnimationFrame(animate);
