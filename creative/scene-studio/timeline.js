import { safeMedia } from './model.js';
import { buildSchedule, scheduleSignature, locateTime } from './timeline-model.js';

const stamp = value => {
  const n = Math.max(0, Number(value) || 0);
  return `${Math.floor(n / 60).toString().padStart(2, '0')}:${(n % 60).toFixed(1).padStart(4, '0')}`;
};

/** Continuous editorial preview; no media is generated or uploaded. */
export function createSequencePlayer({ dock, viewport, onOpen = () => {}, onClip = () => {} }) {
  if (!dock || !viewport) throw new Error('Le lecteur a besoin d’une piste et d’un écran.');
  dock.classList.add('sequence-dock');
  dock.setAttribute('aria-label', 'Lecture du montage');
  viewport.classList.add('sequence-viewport');
  dock.innerHTML = `<div class="sequence-controls">
    <div class="sequence-heading"><strong>Montage</strong><span class="sequence-summary"></span></div>
    <div class="sequence-transport"><button type="button" data-action="prev" aria-label="Plan précédent" title="Plan précédent">⏮</button><button type="button" data-action="play" aria-label="Lire le montage" title="Lire / pause · Espace">▶</button><button type="button" data-action="next" aria-label="Plan suivant" title="Plan suivant">⏭</button></div>
    <output class="sequence-time">00:00.0 / 00:00.0</output>
    <span class="sequence-now"></span>
    <button type="button" data-action="mute" aria-label="Activer le son" aria-pressed="true" title="Activer le son">Son coupé</button>
    <button type="button" data-action="loop" aria-label="Répéter le montage" aria-pressed="false">Boucle</button>
  </div><input class="sequence-seek" type="range" min="0" max="0" step="0.01" value="0" aria-label="Position dans le montage" />
  <div class="sequence-scroll"><div class="sequence-track"><div class="sequence-playhead" aria-hidden="true"></div></div></div>
  <div class="sequence-footer"><span class="sequence-status" role="status">Chargement du montage…</span><span>Cliquer sur un plan pour vérifier le raccord · Espace : lecture / pause</span></div>`;
  const $ = selector => dock.querySelector(selector);
  const playButton = $('[data-action="play"]'), muteButton = $('[data-action="mute"]'), loopButton = $('[data-action="loop"]');
  const seekInput = $('.sequence-seek'), track = $('.sequence-track'), scroll = $('.sequence-scroll');
  const clock = $('.sequence-time'), nowLabel = $('.sequence-now'), status = $('.sequence-status');
  const slate = document.createElement('div');
  slate.className = 'sequence-slate';
  slate.innerHTML = '<span class="sequence-slate-kicker"></span><strong></strong><p></p>';
  const videos = [0, 1].map(() => {
    const video = document.createElement('video');
    video.className = 'sequence-video'; video.playsInline = true; video.preload = 'auto'; video.muted = true;
    video.hidden = true; video.setAttribute('aria-label', 'Plan du montage'); viewport.append(video);
    return video;
  });
  viewport.append(slate);
  let project = null, signature = '', schedule = [], selectedId = null;
  let running = false, muted = true, loop = false, disposed = false, activeSlot = 0;
  let currentIndex = -1, globalTime = 0, slateStarted = 0, slateOffset = 0;
  let frame = 0, transition = 0, loading = false, projectRevision = 0;
  const slotEpoch = [0, 0];
  const durations = new Map(), failed = new Set(), probes = new Map();
  const total = () => schedule.at(-1)?.end || 0;
  const current = () => schedule[currentIndex];
  const isSlate = item => !item?.url || failed.has(item.url);
  const message = text => { status.textContent = text; };

  function renderTrack() {
    track.replaceChildren();
    track.style.width = `${Math.max(scroll.clientWidth || 720, total() * 24)}px`;
    for (const item of schedule) {
      const button = document.createElement('button');
      button.type = 'button'; button.className = 'sequence-clip'; button.dataset.index = item.index;
      button.style.width = `${total() ? item.duration / total() * 100 : 0}%`;
      button.classList.toggle('is-missing', isSlate(item));
      button.title = `${item.index + 1}. ${item.title} · ${stamp(item.duration)}${item.estimated ? ' (durée cible, à vérifier)' : ''}${isSlate(item) ? ' · rendu manquant' : ''}`;
      button.setAttribute('aria-label', button.title);
      if (safeMedia(item.poster)) {
        const image = document.createElement('img'); image.src = item.poster; image.alt = ''; image.loading = 'lazy'; button.append(image);
      }
      const label = document.createElement('span'); label.className = 'sequence-clip-label'; label.textContent = `${String(item.index + 1).padStart(2, '0')} · ${item.title}`;
      const length = document.createElement('small'); length.textContent = `${item.estimated ? '≈ ' : ''}${item.duration.toFixed(1)} s${isSlate(item) ? ' · À créer' : ''}`;
      button.append(label, length); track.append(button);
    }
    const cursor = document.createElement('div'); cursor.className = 'sequence-playhead'; cursor.setAttribute('aria-hidden', 'true'); track.append(cursor);
    const missing = schedule.filter(isSlate).length;
    $('.sequence-summary').textContent = `${schedule.length} plans${missing ? ` · ${missing} sans rendu` : ''}`;
    seekInput.max = total();
    updateDisplay();
  }

  function updateDisplay() {
    const item = current();
    clock.value = `${stamp(globalTime)} / ${stamp(total())}`;
    clock.textContent = clock.value;
    seekInput.value = Math.min(globalTime, total());
    seekInput.setAttribute('aria-valuetext', `${stamp(globalTime)} sur ${stamp(total())}`);
    const cursor = $('.sequence-playhead'); if (cursor) cursor.style.left = `${total() ? globalTime / total() * 100 : 0}%`;
    for (const button of track.querySelectorAll('.sequence-clip')) {
      const n = Number(button.dataset.index);
      button.classList.toggle('is-current', n === currentIndex);
      button.classList.toggle('is-selected', schedule[n]?.id === selectedId);
      button.setAttribute('aria-current', n === currentIndex ? 'true' : 'false');
    }
    nowLabel.textContent = item ? `${currentIndex + 1} / ${schedule.length} · ${item.title}` : 'Aucun plan';
    playButton.textContent = running ? 'Ⅱ' : '▶';
    playButton.setAttribute('aria-label', running ? 'Mettre en pause' : 'Lire le montage');
    playButton.disabled = !schedule.length;
  }

  function showSlate(item, reason = '') {
    for (const video of videos) video.hidden = true;
    slate.hidden = false;
    slate.querySelector('.sequence-slate-kicker').textContent = reason || 'RENDU MANQUANT';
    slate.querySelector('strong').textContent = item?.title || 'Aucun plan';
    slate.querySelector('p').textContent = item ? `Carton de ${item.duration.toFixed(1)} s · durée cible${running ? ' · la lecture se poursuit' : ''}` : 'Ajoute un plan au montage.';
  }

  function rememberDuration(url, duration) {
    if (!Number.isFinite(duration) || duration <= 0 || durations.get(url) === duration || !project) return;
    const oldItem = current(), offset = oldItem ? Math.max(0, globalTime - oldItem.start) : 0;
    durations.set(url, duration);
    schedule = buildSchedule(project, durations);
    const retained = schedule.findIndex(item => item.id === oldItem?.id);
    if (retained >= 0) { currentIndex = retained; globalTime = schedule[retained].start + Math.min(offset, schedule[retained].duration); }
    else globalTime = Math.min(globalTime, total());
    renderTrack();
  }

  function waitEvent(video, events, timeout = 8000) {
    return new Promise(resolve => {
      let timer;
      const finish = event => { clearTimeout(timer); for (const type of events) video.removeEventListener(type, finish); video.removeEventListener('error', finish); resolve(event?.type !== 'error' && event?.type !== 'timeout'); };
      for (const type of events) video.addEventListener(type, finish, { once: true });
      video.addEventListener('error', finish, { once: true });
      timer = setTimeout(() => finish({ type: 'timeout' }), timeout);
    });
  }

  async function prepare(slot, item, offset = 0) {
    const video = videos[slot];
    const epoch = ++slotEpoch[slot];
    const valid = () => !disposed && slotEpoch[slot] === epoch && video.dataset.source === item.url;
    if (!item?.url || failed.has(item.url)) return false;
    if (video.dataset.source !== item.url) {
      video.pause(); video.muted = true; video.dataset.source = item.url; video.src = item.url; video.load();
    }
    if (video.error) return false;
    if (video.readyState < 1 && !await waitEvent(video, ['loadedmetadata'])) return false;
    if (!valid()) return false;
    rememberDuration(item.url, video.duration);
    const refreshed = schedule.find(entry => entry.id === item.id) || item;
    if (!refreshed.url) return false;
    const time = Math.max(refreshed.inPoint, Math.min(refreshed.inPoint + offset, refreshed.outPoint - .001));
    if (Math.abs(video.currentTime - time) > .015) {
      video.currentTime = time;
      if (video.seeking && !await waitEvent(video, ['seeked'])) return false;
    }
    if (!valid()) return false;
    if (video.readyState < 2 && !await waitEvent(video, ['loadeddata', 'canplay'])) return false;
    return valid();
  }

  function preloadNext() {
    const next = schedule[currentIndex + 1] || (loop ? schedule[0] : null);
    const slot = 1 - activeSlot;
    videos[slot].pause(); videos[slot].muted = true;
    if (next?.url) prepare(slot, next).catch(() => {});
  }

  async function activate(index, offset = 0) {
    const item = schedule[index]; if (!item || disposed) return;
    const token = ++transition;
    loading = true;
    for (const video of videos) { video.pause(); video.muted = true; }
    const nextSlot = videos[1 - activeSlot].dataset.source === item.url ? 1 - activeSlot : activeSlot;
    currentIndex = index; globalTime = item.start + Math.min(offset, item.duration);
    const cursorX=total()?globalTime/total()*track.clientWidth:0;
    if(cursorX<scroll.scrollLeft||cursorX>scroll.scrollLeft+scroll.clientWidth-20)scroll.scrollLeft=Math.max(0,cursorX-scroll.clientWidth*.25);
    slateOffset = Math.min(offset, item.duration); slateStarted = performance.now();
    onClip({ title: item.title, index: index + 1, total: schedule.length });
    updateDisplay();
    if (isSlate(item)) {
      loading = false; showSlate(item, item.url ? 'MÉDIA INDISPONIBLE' : 'RENDU MANQUANT');
      message('Plan sans vidéo : sa durée cible reste visible dans le montage.');
      preloadNext(); return;
    }
    message('Préparation du plan…');
    let ok = false;
    try { ok = await prepare(nextSlot, item, offset); } catch { ok = false; }
    if (disposed || token !== transition) return;
    loading = false;
    if (!ok) {
      failed.add(item.url); showSlate(current(), 'MÉDIA INDISPONIBLE'); slateStarted = performance.now();
      message('Vidéo indisponible : carton conservé à sa place.'); renderTrack(); preloadNext(); return;
    }
    activeSlot = nextSlot;
    videos.forEach((video, n) => { video.hidden = n !== activeSlot; video.muted = n === activeSlot ? muted : true; });
    slate.hidden = true;
    message(current()?.estimated ? 'Durée cible provisoire · mesure du média en cours.' : 'Durées des médias conservées · coupes franches entre les plans.');
    if (running) {
      try { await videos[activeSlot].play(); }
      catch { if (token === transition) { pause(); message('Cliquer sur lecture pour démarrer ce média.'); } }
    }
    preloadNext();
  }

  function pause() {
    if (!running) { for (const video of videos) video.pause(); updateDisplay(); return; }
    if (running && isSlate(current()) && !loading) globalTime = Math.min(current().end, current().start + slateOffset + (performance.now() - slateStarted) / 1000);
    else if (current() && !loading) globalTime = Math.min(current().end, current().start + Math.max(0, videos[activeSlot].currentTime - current().inPoint));
    running = false; for (const video of videos) video.pause(); updateDisplay();
  }

  async function play() {
    if (!schedule.length || disposed) return;
    onOpen();
    running = true;
    if (globalTime >= total() - .001) globalTime = 0;
    const position = locateTime(schedule, globalTime);
    await activate(position.index, position.offset);
    updateDisplay();
  }

  function seek(time) {
    if (!schedule.length) return;
    onOpen();
    const position = locateTime(schedule, time);
    activate(position.index, position.offset);
  }

  function advance() {
    if (currentIndex + 1 < schedule.length) activate(currentIndex + 1);
    else if (loop) activate(0);
    else { pause(); globalTime = total(); message('Fin du montage.'); updateDisplay(); }
  }

  function tick() {
    if (disposed) return;
    if (running && !loading && current()) {
      const item = current();
      const local = isSlate(item) ? slateOffset + (performance.now() - slateStarted) / 1000 : Math.max(0, videos[activeSlot].currentTime - item.inPoint);
      globalTime = Math.min(item.end, item.start + local);
      if (local >= item.duration - .008 || (!isSlate(item) && videos[activeSlot].ended)) advance();
      updateDisplay();
    }
    frame = requestAnimationFrame(tick);
  }

  function click(event) {
    const button = event.target.closest('button'); if (!button) return;
    if (button.dataset.index !== undefined) { const item = schedule[Number(button.dataset.index)]; if (item) seek(item.start); return; }
    switch (button.dataset.action) {
      case 'play': running ? pause() : play(); break;
      case 'prev': seek(schedule[Math.max(0, currentIndex - 1)]?.start || 0); break;
      case 'next': seek(schedule[Math.min(schedule.length - 1, currentIndex + 1)]?.start || 0); break;
      case 'mute': muted = !muted; videos[activeSlot].muted = muted; muteButton.textContent = muted ? 'Son coupé' : 'Son actif'; muteButton.setAttribute('aria-pressed', String(muted)); muteButton.setAttribute('aria-label', muted ? 'Activer le son' : 'Couper le son'); break;
      case 'loop': loop = !loop; loopButton.setAttribute('aria-pressed', String(loop)); preloadNext(); break;
    }
  }
  function keyboard(event) {
    if (event.code === 'Space' && event.target.tagName !== 'INPUT') { event.preventDefault(); running ? pause() : play(); }
  }
  const changeSeek = () => seek(Number(seekInput.value));
  for (const [slot, video] of videos.entries()) video.addEventListener('error', () => {
    if (disposed || loading || slot !== activeSlot || !current()?.url) return;
    const item = current();
    slateOffset = Math.max(0, globalTime - item.start); slateStarted = performance.now();
    failed.add(item.url); video.pause(); video.muted = true;
    showSlate(item, 'MÉDIA INDISPONIBLE'); renderTrack();
    message('Lecture du média interrompue : carton conservé à sa place.');
  });
  dock.addEventListener('click', click); dock.addEventListener('keydown', keyboard); seekInput.addEventListener('input', changeSeek);
  const observer = new ResizeObserver(() => { if (schedule.length) track.style.width = `${Math.max(scroll.clientWidth, total() * 24)}px`; });
  observer.observe(scroll);

  function measureTakes() {
    const revision = projectRevision;
    for (const item of schedule.filter(item => item.kind === 'take' && item.url && !durations.has(item.url))) {
      if (probes.has(item.url)) continue;
      const probe = document.createElement('video'); probe.preload = 'metadata'; probe.muted = true;
      const cleanup = () => { clearTimeout(timeout); probe.removeAttribute('src'); probe.load(); probes.delete(item.url); };
      const timeout = setTimeout(cleanup, 15000);
      probe.onloadedmetadata = () => { if (!disposed && revision === projectRevision) rememberDuration(item.url, probe.duration); cleanup(); };
      probe.onerror = cleanup; probes.set(item.url, { probe, cleanup }); probe.src = item.url;
    }
  }

  function setProject(value, selection) {
    selectedId = selection;
    const nextSignature = scheduleSignature(value);
    if (nextSignature === signature) { updateDisplay(); return; }
    const oldItem = current(), offset = oldItem ? Math.max(0, globalTime - oldItem.start) : 0;
    pause(); ++transition; ++projectRevision;
    for (const entry of [...probes.values()]) entry.cleanup();
    signature = nextSignature; project = JSON.parse(JSON.stringify(value)); schedule = buildSchedule(project, durations);
    let index = schedule.findIndex(item => item.id === oldItem?.id);
    if (index < 0) index = Math.max(0, schedule.findIndex(item => item.id === selection));
    renderTrack();
    if (schedule.length) activate(index, oldItem?.id === schedule[index].id ? Math.min(offset, schedule[index].duration) : 0);
    else { currentIndex = -1; globalTime = 0; loading = false; showSlate(null); updateDisplay(); }
    measureTakes();
  }

  frame = requestAnimationFrame(tick);
  return {
    setProject, pause,
    dispose() {
      disposed = true; ++transition; slotEpoch[0]++; slotEpoch[1]++; cancelAnimationFrame(frame); observer.disconnect();
      for (const entry of [...probes.values()]) entry.cleanup();
      dock.removeEventListener('click', click); dock.removeEventListener('keydown', keyboard); seekInput.removeEventListener('input', changeSeek);
      for (const video of videos) { video.pause(); video.removeAttribute('src'); video.load(); video.remove(); }
      slate.remove(); dock.replaceChildren(); dock.classList.remove('sequence-dock'); viewport.classList.remove('sequence-viewport');
    }
  };
}
