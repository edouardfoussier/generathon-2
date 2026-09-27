(() => {
  'use strict';
  const KEYS = { language: 'rafa-luna-v5-language', favorites: 'rafa-luna-v5-favorites' };
  const i18n = {
    fr: {
      skip: 'Aller à la planche', brandSubtitle: 'Atelier du récit · V5', archive: 'Les essais précédents ↗',
      eyebrow: 'Une histoire de transmission. Un nouveau départ.', title: 'À son tour.', lede: 'Les traces de Rafa donnent à Luna le courage de laisser les siennes.', script: 'Lire le scénario v5 · 78 secondes ↗',
      directionTitle: 'Le récit avant le mouvement.', directionBody: 'Même famille, même paire. On affine d’abord les images et leurs raccords. Le son et le montage viendront ensuite.', candidateNote: 'Images et essais de mouvement à comparer. Aucun choix ici ne remplace les films et les essais existants.',
      pathEyebrow: 'Le fil de Luna', pathTitle: 'Un geste commencé. Puis accompli.', pathNote: 'L’évolution doit se comprendre dans les images, même sans lire le scénario.',
      gestureEyebrow: 'Début → Résolution', gestureTitle: 'Le geste change de sens.', gestureNote: 'Même paire, même intention. Le feutre arrêté au début trouve sa place à la fin.', gestureBefore: 'Le geste commencé', gestureAfter: 'Le geste accompli',
      transitionEyebrow: 'Présent → Souvenir', transitionTitle: 'Le même appui, une autre époque.', transitionNote: 'Comparer le pied, son orientation et sa taille dans le cadre. La matière change ; le raccord reste lisible.',
      galleryEyebrow: 'La planche de travail', galleryTitle: 'Choisir ce qui raconte.', reload: 'Actualiser la planche ↻', all: 'Tout', luna: 'Luna', memories: 'Les souvenirs', transitions: 'Les raccords', favorites: 'Mes favoris', zoomHint: 'Images à agrandir · Vidéos à lire',
      choicesEyebrow: 'Pour la discussion d’équipe', choicesTitle: 'Une sélection à partager.', choicesBody: 'Les favoris restent dans ce navigateur. Téléchargez vos choix pour les envoyer à l’équipe ; ils ne valident pas automatiquement la production.', export: 'Télécharger mes choix ↓',
      footer: 'Publicité spéculative non officielle · Projet de hackathon · Converse n’est pas partenaire.', continuity: 'Règles de continuité ↗',
      filterLabel: 'Filtrer la planche', imageCount: (images, videos) => videos ? `${images} image${images > 1 ? 's' : ''} · ${videos} vidéo${videos > 1 ? 's' : ''}` : `${images} image${images > 1 ? 's' : ''} sur la planche`, selectedCount: n => `${n} favori${n > 1 ? 's' : ''} dans ce navigateur`, updated: 'Mise à jour',
      candidate: 'Candidat · à comparer', correction: 'À corriger', favorite: '♡ Retenir', selected: '♥ Retenu', inspect: 'À vérifier dans cette image', generation: 'Génération, références et prompt', model: 'Modèle', source: 'Références', credits: 'Crédits', assetId: 'ID de génération', prompt: 'Prompt de génération', unavailable: 'Non renseigné',
      view: 'Agrandir', video: 'Essai de mouvement', close: 'Fermer', previous: 'Média précédent', next: 'Média suivant', loadingTitle: 'La planche arrive.', loadingBody: 'Chargement de cette nouvelle planche. Les autres essais restent accessibles depuis le lien en haut de page.',
      noAssetsTitle: 'La nouvelle série est en préparation.', noAssetsBody: 'Les médias s’afficheront ici une fois ajoutés au manifeste. Utilisez « Actualiser la planche » pour récupérer la dernière version.',
      noFavoritesTitle: 'Votre sélection commence ici.', noFavoritesBody: 'Retenez une image ou une vidéo avec le bouton « Retenir ». Les favoris sont enregistrés uniquement dans ce navigateur et peuvent être exportés.',
      noGroupTitle: 'Pas encore de média dans cette section.', noGroupBody: 'Les autres sections restent disponibles. Actualisez la planche lorsque les prochaines générations sont prêtes.',
      errorTitle: 'La planche n’a pas pu être chargée.', errorBody: 'Le fichier manifest.json est absent ou inaccessible. Ouvrez cette page avec le serveur local du projet, puis actualisez. Les essais précédents restent disponibles.',
      imageError: 'Image indisponible pour le moment. Actualisez lorsque le fichier est prêt.', videoError: 'Vidéo indisponible pour le moment. Actualisez lorsque le fichier est prêt.', favoriteAdded: 'Média ajouté aux favoris.', favoriteRemoved: 'Média retiré des favoris.', exportDone: 'Vos choix ont été téléchargés.', localFailure: 'Le stockage local est indisponible. Vous pouvez toujours télécharger vos choix avant de fermer cette page.', ready: 'Voir l’image', pending: 'Image à venir',
      milestones: [ ['K01', 'Elle hésite', 'Approcher le feutre. Puis arrêter le geste.'], ['K06', 'Elle comprend', 'Le souvenir rejoint sa relation avec Maman.'], ['K07', 'Elle ose', 'Ajouter sa trace, à côté de celle de Rafa.'], ['K08', 'Elle continue', 'Une impulsion. La paire repart vivre.'] ]
    },
    en: {
      skip: 'Skip to the board', brandSubtitle: 'Story workshop · V5', archive: 'Previous explorations ↗',
      eyebrow: 'An inherited story. A new beginning.', title: 'Her turn.', lede: 'Rafa’s marks give Luna the courage to leave her own.', script: 'Read the v5 script · 78 seconds ↗',
      directionTitle: 'Story before motion.', directionBody: 'The same family, the same pair. First, refine the images and their transitions. Sound and the final edit come later.', candidateNote: 'Candidate images and motion tests to compare. Choices here do not replace any existing films or explorations.',
      pathEyebrow: 'Luna’s journey', pathTitle: 'A gesture begun. Then completed.', pathNote: 'Her change should be visible in the images, even without reading the script.',
      gestureEyebrow: 'Opening → Resolution', gestureTitle: 'The gesture takes on meaning.', gestureNote: 'The same pair, the same intention. The marker that stopped at the beginning finds its place at the end.', gestureBefore: 'The gesture begun', gestureAfter: 'The gesture completed',
      transitionEyebrow: 'Present → Memory', transitionTitle: 'The same step, another time.', transitionNote: 'Compare the foot, its orientation and its size in the frame. The texture changes; the match stays clear.',
      galleryEyebrow: 'The working board', galleryTitle: 'Choose what tells the story.', reload: 'Refresh the board ↻', all: 'All', luna: 'Luna', memories: 'The memories', transitions: 'The transitions', favorites: 'My favorites', zoomHint: 'Enlarge images · Play motion tests',
      choicesEyebrow: 'For the team discussion', choicesTitle: 'A selection to share.', choicesBody: 'Favorites stay in this browser. Download your choices to share them with the team; they do not automatically approve production.', export: 'Download my choices ↓',
      footer: 'Unofficial speculative ad · Hackathon project · Converse is not a partner.', continuity: 'Continuity guidelines ↗',
      filterLabel: 'Filter the board', imageCount: (images, videos) => videos ? `${images} image${images === 1 ? '' : 's'} · ${videos} video${videos === 1 ? '' : 's'}` : `${images} image${images === 1 ? '' : 's'} on the board`, selectedCount: n => `${n} favorite${n === 1 ? '' : 's'} in this browser`, updated: 'Updated',
      candidate: 'Candidate · compare', correction: 'Needs correction', favorite: '♡ Keep', selected: '♥ Selected', inspect: 'Check in this image', generation: 'Generation, references & prompt', model: 'Model', source: 'References', credits: 'Credits', assetId: 'Generation ID', prompt: 'Generation prompt', unavailable: 'Not recorded',
      view: 'Enlarge', video: 'Motion test', close: 'Close', previous: 'Previous media', next: 'Next media', loadingTitle: 'The board is on its way.', loadingBody: 'Loading this new board. Previous explorations remain available through the link at the top of the page.',
      noAssetsTitle: 'The new series is being prepared.', noAssetsBody: 'Media will appear here once added to the manifest. Use “Refresh the board” to retrieve the latest version.',
      noFavoritesTitle: 'Your selection starts here.', noFavoritesBody: 'Use “Keep” to save an image or video. Favorites are stored only in this browser and can be exported.',
      noGroupTitle: 'No media in this section yet.', noGroupBody: 'The other sections are still available. Refresh the board when the next generations are ready.',
      errorTitle: 'The board could not be loaded.', errorBody: 'The manifest.json file is missing or unavailable. Open this page using the project’s local server, then refresh. Previous explorations remain available.',
      imageError: 'This image is not available yet. Refresh when the file is ready.', videoError: 'This video is not available yet. Refresh when the file is ready.', favoriteAdded: 'Media added to favorites.', favoriteRemoved: 'Media removed from favorites.', exportDone: 'Your choices have been downloaded.', localFailure: 'Local storage is unavailable. You can still download your choices before closing this page.', ready: 'View image', pending: 'Image coming soon',
      milestones: [ ['K01', 'She hesitates', 'Bring the marker close. Then stop.'], ['K06', 'She understands', 'The memory connects her to Mom.'], ['K07', 'She dares', 'Add her own mark beside Rafa’s.'], ['K08', 'She continues', 'One push. The pair goes on living.'] ]
    }
  };
  const readStored = (key, fallback) => { try { const value = localStorage.getItem(key); return value === null ? fallback : value; } catch { return fallback; } };
  const params = new URLSearchParams(location.search);
  let lang = params.get('lang') || readStored(KEYS.language, 'fr');
  if (!i18n[lang]) lang = 'fr';
  let saved;
  try { saved = JSON.parse(readStored(KEYS.favorites, '[]')); } catch { saved = []; }
  const favorites = new Set(Array.isArray(saved) ? saved.filter(value => typeof value === 'string') : []);
  let manifest = { assets: [] }, assets = [], group = 'all', loadState = 'loading', currentCode = null, fetchVersion = 0;
  const $ = id => document.getElementById(id);
  const textFor = value => typeof value === 'string' ? value : (value && (value[lang] || value.fr || value.en)) || '';
  const tr = key => i18n[lang][key];
  const el = (tag, cls, text) => { const node = document.createElement(tag); if (cls) node.className = cls; if (text !== undefined) node.textContent = text; return node; };
  const announce = text => { $('announcer').textContent = text; };
  function persist(key, value) { try { localStorage.setItem(key, value); } catch { announce(tr('localFailure')); } }
  function safeFile(file) {
    if (typeof file !== 'string' || !file.trim()) return null;
    try { const url = new URL(file, location.href); return ['http:', 'https:', 'file:'].includes(url.protocol) ? url.href : null; } catch { return null; }
  }
  const visibleAssets = () => assets.filter(asset => group === 'all' || (group === 'favorites' ? favorites.has(asset.code) : asset.group === group));
  const isVideo = asset => asset.kind === 'video';
  function pauseVideos(root = document) { root.querySelectorAll('video').forEach(video => video.pause()); }
  function assetImage(asset, cls = '') {
    if (isVideo(asset)) {
      const wrap = el('div', `video-media ${cls}`.trim()), video = el('video');
      video.controls = true; video.preload = 'metadata'; video.playsInline = true;
      video.setAttribute('aria-label', `${tr('video')} ${asset.code} — ${textFor(asset.title)}`);
      const poster = safeFile(asset.poster); if (poster) video.poster = poster;
      const unavailable = () => { video.hidden = true; if (!wrap.querySelector('.image-error')) wrap.append(el('span', 'image-error', tr('videoError'))); enlarge.disabled = true; };
      video.addEventListener('error', unavailable, { once: true });
      video.addEventListener('play', () => { document.querySelectorAll('video').forEach(other => { if (other !== video) other.pause(); }); });
      const enlarge = el('button', 'video-enlarge', `${tr('view')} ↗`); enlarge.type = 'button'; enlarge.setAttribute('aria-label', `${tr('view')} ${asset.code} — ${textFor(asset.title)}`);
      enlarge.addEventListener('click', () => openLightbox(asset.code));
      wrap.append(video, el('span', 'image-code', `${asset.code} · ${tr('video')}`), enlarge);
      const src = safeFile(asset.file); if (src) video.src = src; else unavailable();
      return wrap;
    }
    const button = el('button', `image-button ${cls}`.trim()); button.type = 'button';
    button.setAttribute('aria-label', `${tr('view')} ${asset.code} — ${textFor(asset.title)}`);
    const image = el('img'); image.alt = `${asset.code} — ${textFor(asset.title)}`; image.loading = 'lazy'; image.decoding = 'async';
    const unavailable = () => { image.hidden = true; if (!button.querySelector('.image-error')) button.append(el('span', 'image-error', tr('imageError'))); button.disabled = true; };
    image.addEventListener('error', unavailable, { once: true });
    const src = safeFile(asset.file); if (src) image.src = src; else unavailable();
    button.append(image, el('span', 'image-code', asset.code), el('span', 'image-expand', '↗'));
    button.addEventListener('click', () => openLightbox(asset.code));
    return button;
  }
  function findCode(code) { return assets.find(asset => asset.code === code) || assets.find(asset => asset.code.startsWith(`${code}-`) || asset.code.startsWith(`${code}_`)); }
  function renderMilestones() {
    $('milestones').replaceChildren();
    for (const [code, title, description] of tr('milestones')) {
      const asset = findCode(code), button = el('button', `milestone${asset ? ' is-ready' : ''}`); button.type = 'button'; button.disabled = !asset;
      button.append(el('span', 'milestone-code', code), el('span', 'arrow', asset ? '↗' : '·'), el('h3', '', title), el('p', '', description));
      button.title = asset ? tr('ready') : tr('pending');
      if (asset) button.addEventListener('click', () => { setGroup('all'); const target = document.getElementById(`asset-${asset.code}`); if (target) { target.scrollIntoView({ behavior: matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth', block: 'center' }); target.classList.remove('flash-card'); void target.offsetWidth; target.classList.add('flash-card'); target.querySelector('.image-button').focus({ preventScroll: true }); } });
      $('milestones').append(button);
    }
  }
  function renderTransitions() {
    const pair = [findCode('T01A'), findCode('T01B')];
    $('transition-section').hidden = !pair.every(Boolean); $('transition-pair').replaceChildren();
    if (pair.every(Boolean)) for (const asset of pair) { const figure = el('figure'); const caption = el('figcaption'); caption.append(el('strong', '', asset.code), document.createTextNode(textFor(asset.title))); figure.append(assetImage(asset), caption); $('transition-pair').append(figure); }
  }
  function renderGesture() {
    const pair = [findCode('K01'), findCode('K07')];
    const ready = pair.every(asset => asset && safeFile(asset.file) && !isVideo(asset) && !['pending', 'failed', 'generating'].includes(asset.status));
    $('gesture-section').hidden = !ready; $('gesture-pair').replaceChildren();
    if (ready) pair.forEach((asset, index) => {
      const figure = el('figure'), caption = el('figcaption');
      caption.append(el('strong', '', asset.code), el('span', 'gesture-label', tr(index ? 'gestureAfter' : 'gestureBefore')), el('p', 'gesture-caption', textFor(asset.title)));
      figure.append(assetImage(asset), caption); $('gesture-pair').append(figure);
    });
  }
  function stringify(value) { if (value === null || value === undefined || value === '') return tr('unavailable'); if (Array.isArray(value)) return value.map(stringify).join('\n'); if (typeof value === 'object') return JSON.stringify(value, null, 2); return String(value); }
  function card(asset) {
    const article = el('article', `asset-card${favorites.has(asset.code) ? ' is-favorite' : ''}`); article.id = `asset-${asset.code}`;
    const copy = el('div', 'card-copy'), top = el('div', 'card-top'), correction = asset.reviewStatus === 'needs-correction';
    top.append(el('span', `badge${correction ? ' correction' : ''}`, tr(correction ? 'correction' : 'candidate')));
    const favorite = el('button', 'favorite-button', tr(favorites.has(asset.code) ? 'selected' : 'favorite')); favorite.type = 'button'; favorite.setAttribute('aria-pressed', String(favorites.has(asset.code))); favorite.setAttribute('aria-label', `${tr(favorites.has(asset.code) ? 'selected' : 'favorite')} — ${asset.code}`);
    favorite.addEventListener('click', () => { const adding = !favorites.has(asset.code); if (adding) favorites.add(asset.code); else favorites.delete(asset.code); persist(KEYS.favorites, JSON.stringify([...favorites])); renderGallery(); updateCounts(); announce(tr(adding ? 'favoriteAdded' : 'favoriteRemoved')); const newButton = document.getElementById(`asset-${asset.code}`)?.querySelector('.favorite-button'); if (newButton) newButton.focus({ preventScroll: true }); });
    top.append(favorite); copy.append(top, el('h3', '', textFor(asset.title) || asset.code));
    if (textFor(asset.description)) copy.append(el('p', 'description', textFor(asset.description)));
    if (textFor(asset.qa)) { const note = el('p', `qa-note${correction ? ' correction-note' : ''}`); note.append(el('strong', '', tr('inspect')), document.createTextNode(textFor(asset.qa))); copy.append(note); }
    const details = el('details', 'technical'); details.append(el('summary', '', `${asset.model || tr('unavailable')} · ${tr('generation')}`));
    const dl = el('dl');
    for (const [label, value] of [['model', asset.model], ['assetId', asset.assetId], ['credits', asset.creditsCharged], ['source', asset.references]]) { dl.append(el('dt', '', tr(label)), el('dd', '', stringify(value))); }
    details.append(dl); if (asset.prompt) details.append(el('p', 'prompt-title', tr('prompt')), el('pre', 'prompt', stringify(asset.prompt)));
    copy.append(details); article.append(assetImage(asset), copy); return article;
  }
  function setEmpty(title, body) { $('empty-state').hidden = false; $('empty-title').textContent = tr(title); $('empty-body').textContent = tr(body); }
  function renderGallery() {
    pauseVideos($('gallery'));
    $('gallery').replaceChildren(); $('empty-state').hidden = true; $('gallery').setAttribute('aria-busy', String(loadState === 'loading'));
    if (loadState === 'loading') { setEmpty('loadingTitle', 'loadingBody'); return; }
    if (loadState === 'error') { setEmpty('errorTitle', 'errorBody'); return; }
    const selected = visibleAssets();
    if (!assets.length) setEmpty('noAssetsTitle', 'noAssetsBody');
    else if (!selected.length) setEmpty(group === 'favorites' ? 'noFavoritesTitle' : 'noGroupTitle', group === 'favorites' ? 'noFavoritesBody' : 'noGroupBody');
    else $('gallery').append(...selected.map(card));
  }
  function updateCounts() {
    const videos = assets.filter(isVideo).length;
    $('asset-count').textContent = tr('imageCount')(assets.length - videos, videos);
    $('choice-count').textContent = tr('selectedCount')(favorites.size);
    $('export').disabled = favorites.size === 0;
    const date = manifest.updatedAt && new Date(manifest.updatedAt);
    $('updated-at').textContent = date && !Number.isNaN(date.getTime()) ? `${tr('updated')} · ${new Intl.DateTimeFormat(lang, { dateStyle: 'short', timeStyle: 'short' }).format(date)}` : '';
  }
  function setGroup(next) { group = next; document.querySelectorAll('[data-group]').forEach(button => button.setAttribute('aria-pressed', String(button.dataset.group === group))); renderGallery(); }
  function applyLanguage() {
    document.documentElement.lang = lang; document.title = `Rafa & Luna · V5 ${lang === 'fr' ? 'planche de récit' : 'storyboard'}`;
    document.querySelectorAll('[data-t]').forEach(node => { const value = tr(node.dataset.t); if (typeof value === 'string') node.textContent = value; });
    document.querySelectorAll('[data-lang]').forEach(button => button.setAttribute('aria-pressed', String(button.dataset.lang === lang)));
    $('filters').setAttribute('aria-label', tr('filterLabel')); $('close-lightbox').setAttribute('aria-label', tr('close')); $('previous').setAttribute('aria-label', tr('previous')); $('next').setAttribute('aria-label', tr('next'));
    for (const link of document.querySelectorAll('a[href*="refinement-v4"]')) { const url = new URL(link.getAttribute('href'), location.href); url.searchParams.set('lang', lang); link.href = url.href; }
    renderMilestones(); renderGesture(); renderTransitions(); renderGallery(); updateCounts(); if ($('lightbox').open) fillLightbox(currentCode);
  }
  async function loadManifest() {
    const version = ++fetchVersion; loadState = 'loading'; $('reload').disabled = true; renderGallery();
    try {
      const response = await fetch('manifest.json', { cache: 'no-store' }); if (!response.ok) throw new Error(`HTTP ${response.status}`);
      const data = await response.json(); if (!data || !Array.isArray(data.assets)) throw new Error('Invalid manifest');
      if (version !== fetchVersion) return;
      manifest = data; const seen = new Set(); assets = data.assets.filter(asset => { if (!asset || typeof asset.code !== 'string' || !asset.code.trim() || seen.has(asset.code)) return false; seen.add(asset.code); return true; }); loadState = 'ready';
    } catch { if (version !== fetchVersion) return; loadState = 'error'; }
    finally { if (version === fetchVersion) { $('reload').disabled = false; renderMilestones(); renderGesture(); renderTransitions(); renderGallery(); updateCounts(); } }
  }
  function lightboxAssets() { const current = visibleAssets(); return current.some(asset => asset.code === currentCode) ? current : assets; }
  function fillLightbox(code) {
    const asset = assets.find(item => item.code === code); if (!asset) return; currentCode = code;
    const video = $('lightbox-video'), image = $('lightbox-image'); video.pause();
    $('lightbox-code').textContent = asset.code; $('lightbox-title').textContent = textFor(asset.title); $('lightbox-description').textContent = textFor(asset.description);
    const src = safeFile(asset.file), motion = isVideo(asset);
    image.hidden = motion; video.hidden = !motion;
    if (motion) {
      image.removeAttribute('src');
      if (src) video.src = src; else video.removeAttribute('src');
      const poster = safeFile(asset.poster); if (poster) video.poster = poster; else video.removeAttribute('poster');
      video.setAttribute('aria-label', `${asset.code} — ${textFor(asset.title)}`);
    } else {
      video.removeAttribute('src'); video.load();
      if (src) image.src = src; else image.removeAttribute('src'); image.alt = `${asset.code} — ${textFor(asset.title)}`;
    }
    const list = lightboxAssets(), index = list.findIndex(item => item.code === code); $('lightbox-position').textContent = `${index + 1} / ${list.length}`; $('previous').disabled = index <= 0; $('next').disabled = index >= list.length - 1;
  }
  function openLightbox(code) { pauseVideos(); fillLightbox(code); if (!$('lightbox').open) $('lightbox').showModal(); }
  function stepLightbox(delta) { const list = lightboxAssets(), index = list.findIndex(asset => asset.code === currentCode), next = list[index + delta]; if (next) fillLightbox(next.code); }
  $('close-lightbox').addEventListener('click', () => $('lightbox').close());
  $('lightbox').addEventListener('close', () => $('lightbox-video').pause());
  $('lightbox').addEventListener('click', event => { if (event.target === $('lightbox')) { const rect = $('lightbox').getBoundingClientRect(); if (event.clientX < rect.left || event.clientX > rect.right || event.clientY < rect.top || event.clientY > rect.bottom) $('lightbox').close(); } });
  $('lightbox').addEventListener('keydown', event => { if (event.target.tagName === 'VIDEO') return; if (event.key === 'ArrowLeft') { event.preventDefault(); stepLightbox(-1); } else if (event.key === 'ArrowRight') { event.preventDefault(); stepLightbox(1); } });
  $('previous').addEventListener('click', () => stepLightbox(-1)); $('next').addEventListener('click', () => stepLightbox(1));
  document.querySelectorAll('[data-lang]').forEach(button => button.addEventListener('click', () => { lang = button.dataset.lang; persist(KEYS.language, lang); const url = new URL(location.href); url.searchParams.set('lang', lang); try { history.replaceState(null, '', url); } catch {} applyLanguage(); }));
  document.querySelectorAll('[data-group]').forEach(button => button.addEventListener('click', () => setGroup(button.dataset.group)));
  $('reload').addEventListener('click', loadManifest);
  $('export').addEventListener('click', () => {
    const output = { project: 'Rafa & Luna', storyboard: 'v5', manifestVersion: manifest.version || null, exportedAt: new Date().toISOString(), language: lang, scope: 'Local preferences only; not production approval', favorites: [...favorites].map(code => { const asset = assets.find(item => item.code === code); return asset ? { code, kind: asset.kind || 'image', title: asset.title, file: asset.file, model: asset.model, assetId: asset.assetId || null, reviewStatus: asset.reviewStatus || 'candidate' } : { code, absentFromCurrentManifest: true }; }) };
    const url = URL.createObjectURL(new Blob([JSON.stringify(output, null, 2)], { type: 'application/json' })); const link = el('a'); link.href = url; link.download = `rafa-luna-v5-choices-${new Date().toISOString().slice(0, 10)}.json`; document.body.append(link); link.click(); link.remove(); setTimeout(() => URL.revokeObjectURL(url), 1000); announce(tr('exportDone'));
  });
  window.addEventListener('storage', event => { if (event.key === KEYS.favorites) { try { const updated = JSON.parse(event.newValue || '[]'); if (Array.isArray(updated)) { favorites.clear(); updated.filter(value => typeof value === 'string').forEach(value => favorites.add(value)); renderGallery(); updateCounts(); } } catch {} } });
  applyLanguage(); loadManifest();
})();
