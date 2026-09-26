(() => {
  'use strict';
  const strings = window.CONVERSE_I18N;
  const languageKey = 'converse-board-language';
  const storageKey = 'converse-exploration-01-selection';
  let language = 'fr';
  try {
    const saved = localStorage.getItem(languageKey);
    if (saved === 'en' || saved === 'fr') language = saved;
  } catch (_) {}
  try {
    const requested = new URLSearchParams(location.search).get('lang');
    if (requested === 'en' || requested === 'fr') language = requested;
  } catch (_) {}
  const t = key => strings[language][key] || strings.fr[key] || key;
  const field = (asset, key) => (language === 'en' ? asset[key + 'En'] : asset[key]) || asset[key] || '';
  const categories = ['enfants', 'grands-peres', 'paires', 'ambiances', 'styles', 'equipe', 'hybrides', 'production'].map((id, index) => ({
    id, number: String(index + 1).padStart(2, '0'),
    get label() { return strings[language].categories[id].label; },
    get title() { return strings[language].categories[id].title; },
    get detail() { return strings[language].categories[id].detail; }
  }));
  const categoryIds = new Set(categories.map(c => c.id));
  const seen = new Set();
  const assets = (Array.isArray(window.CONVERSE_ASSETS) ? window.CONVERSE_ASSETS : []).filter(a => {
    if (!a || typeof a.code !== 'string' || !categoryIds.has(a.category) || seen.has(a.code)) return false;
    seen.add(a.code); return true;
  });
  const assetMap = new Map(assets.map(a => [a.code, a]));
  let selected = new Set();
  let activeCategory = 'all';
  try {
    const requestedCategory = new URLSearchParams(location.search).get('category');
    if (categoryIds.has(requestedCategory)) activeCategory = requestedCategory;
  } catch (_) {}
  let favoritesOnly = false;
  let lightboxCode = null;
  let lightboxItems = [];
  let returnFocus = null;
  let toastTimer;
  let lastBodyOverflow = '';
  const $ = id => document.getElementById(id);
  const escapeHtml = value => String(value == null ? '' : value).replace(/[&<>"']/g, c => ({
    '&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;', "'":'&#39;'
  }[c]));
  const icons = {
    plus:'<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.4" aria-hidden="true"><path d="M8 3v10M3 8h10"/></svg>',
    check:'<svg viewBox="0 0 16 16" fill="none" stroke="currentColor" stroke-width="1.5" aria-hidden="true"><path d="m3 8 3.2 3.2L13 4.5"/></svg>',
    expand:'<svg width="14" height="14" viewBox="0 0 20 20" fill="none" stroke="currentColor" stroke-width="1.3" aria-hidden="true"><path d="M7 3H3v4m10-4h4v4M3 13v4h4m10-4v4h-4"/></svg>'
  };
  try {
    const saved = JSON.parse(localStorage.getItem(storageKey) || '[]');
    if (Array.isArray(saved)) selected = new Set(saved.filter(code => typeof code === 'string' && assetMap.has(code)));
  } catch (_) {}
  function persist() {
    try { localStorage.setItem(storageKey, JSON.stringify([...selected])); } catch (_) {}
  }
  function visibleAssets() {
    return assets.filter(a => (activeCategory === 'all' || a.category === activeCategory) && (!favoritesOnly || selected.has(a.code)));
  }
  function safeImageSource(asset) {
    const filename = typeof asset.filename === 'string' ? asset.filename : '';
    return filename && !/^(?:[a-z][a-z0-9+.-]*:|\/\/)/i.test(filename) ? filename : '';
  }
  function renderStaticText() {
    document.documentElement.lang = language;
    document.title = t('pageTitle');
    document.querySelectorAll('[data-i18n]').forEach(el => { el.textContent = t(el.dataset.i18n); });
    // Only our own fixed translation strings contain HTML.
    document.querySelectorAll('[data-i18n-html]').forEach(el => { el.innerHTML = t(el.dataset.i18nHtml); });
    document.querySelectorAll('[data-i18n-aria-label]').forEach(el => {
      el.setAttribute('aria-label', t(el.dataset.i18nAriaLabel));
    });
    document.querySelectorAll('[data-language]').forEach(button => {
      button.setAttribute('aria-pressed', String(button.dataset.language === language));
    });
  }
  function setLanguage(next) {
    if (!strings[next] || next === language) return;
    language = next;
    try { localStorage.setItem(languageKey, language); } catch (_) {}
    try {
      const url = new URL(location.href);
      url.searchParams.set('lang', language);
      history.replaceState(null, '', url);
    } catch (_) {}
    renderStaticText(); renderFilters(); renderGallery(); renderSelection();
    if (lightboxCode) renderLightbox(lightboxCode);
    $('toast').hidden = true;
  }
  function renderFilters() {
    $('filters').innerHTML = [{id:'all', label:t('all')}, ...categories].map(c =>
      '<button type="button" class="filter" data-filter="' + c.id + '" aria-pressed="' +
      (activeCategory === c.id) + '">' + escapeHtml(c.label) + '</button>'
    ).join('');
    $('favorites').setAttribute('aria-pressed', String(favoritesOnly));
  }
  function imageFallback(asset) {
    return '<div class="image-fallback">' + t('preparing') + '<span>' + escapeHtml(asset.code) +
      (asset.status ? ' · ' + escapeHtml(t(asset.status)) : '') + '</span></div>';
  }
  function choiceContent(chosen) { return (chosen ? icons.check : icons.plus) + ' ' + t(chosen ? 'chosen' : 'choose'); }
  function card(asset) {
    const chosen = selected.has(asset.code), source = safeImageSource(asset);
    const code = escapeHtml(asset.code), title = field(asset, 'title'), subtitle = field(asset, 'subtitle');
    return '<article class="card' + (chosen ? ' is-selected' : '') + '" data-code="' + code + '">' +
      '<div class="image-wrap"><button class="image-button" type="button" data-preview="' + code +
      '" aria-label="' + t('enlarge') + ' ' + code + ' : ' + escapeHtml(title) + '"><div class="image-frame">' +
      (source ? '<img src="' + escapeHtml(source) + '" alt="' + escapeHtml(title + (subtitle ? ' — ' + subtitle : '')) +
      '" loading="lazy" decoding="async">' : imageFallback(asset)) + '</div><span class="card-code">' + code +
      '</span><span class="expand-mark">' + icons.expand + '</span></button></div>' +
      '<div class="card-content"><h3 class="card-title">' + escapeHtml(title || asset.code) +
      '</h3><p class="card-subtitle">' + escapeHtml(subtitle) + '</p><div class="card-bottom"><span class="model">' +
      escapeHtml(asset.model || t('exploratoryReference')) + '</span><button type="button" class="choose" data-choose="' +
      code + '" aria-pressed="' + chosen + '" aria-label="' + t(chosen ? 'unchoose' : 'choose') + ' ' + code + '">' +
      choiceContent(chosen) + '</button></div>' +
      (field(asset, 'note') ? '<p class="note">' + escapeHtml(field(asset, 'note')) + '</p>' : '') + '</div></article>';
  }
  function styleIntroduction() {
    return '<div class="style-intro"><div><h3>' + t('stylesIntroTitle') + '</h3><p>' + t('stylesIntro') +
      '</p></div><p class="style-method">' + t('stylesMethod') + '</p></div>';
  }
  function teamContent(items) {
    const groups = [
      {id:'story', index:'A', title:'teamStoryHeading', detail:'teamStoryDetail'},
      {id:'team-styles', index:'B', title:'teamStyleHeading', detail:'teamStyleDetail'},
      {id:'future', index:'C', title:'teamFutureHeading', detail:'teamFutureDetail'}
    ];
    return '<div class="team-pitch"><div><p class="eyebrow">' + t('teamKicker') +
      '</p><p class="team-premise">' + t('teamPremise') + '</p><p class="team-editorial">' +
      t('teamEditorial') + '</p></div><div class="team-signature"><p>' + t('teamPitchLabel') +
      '</p><div>CONVERSE.<br><em>Conserve<br>what matters.</em></div></div></div>' +
      groups.map(group => {
        const grouped = items.filter(a => a.group === group.id);
        if (group.id === 'story') {
          const order = ['T02','T05','T03','T04','T06','T01','T08'];
          grouped.sort((a, b) => order.indexOf(a.code) - order.indexOf(b.code));
        }
        if (!grouped.length) return '';
        return '<section class="team-group" aria-labelledby="team-' + group.id + '"><header class="team-group-heading">' +
          '<span class="section-index">' + group.index + '</span><div><h3 id="team-' + group.id + '">' +
          t(group.title) + '</h3><p>' + t(group.detail) + '</p></div></header><div class="grid">' +
          grouped.map(card).join('') + '</div></section>';
      }).join('') + '<details class="team-notes"><summary>' + t('teamNotesTitle') + '</summary><div>' +
      ['teamChronology','teamRelationship','teamFocus','teamStyleCaveat'].map(key => '<p>' + t(key) + '</p>').join('') +
      '</div></details>';
  }
  function hybridContent(items) {
    const looks = items.filter(a => a.group === 'looks');
    const frames = items.filter(a => a.group === 'transition');
    return '<div class="hybrid-pitch"><p class="eyebrow">' + t('hybridKicker') + '</p><h3>' +
      t('hybridPremise') + '</h3><p>' + t('hybridDirection') + '</p><div class="hybrid-rule"><span>' +
      t('hybridRuleTitle') + '</span><strong>' + t('hybridRule') + '</strong></div></div>' +
      '<aside class="reference-shelf" aria-labelledby="hybrid-references"><h3 id="hybrid-references">' +
      t('hybridReferenceTitle') + '</h3><div class="reference-grid"><article class="reference-card">' +
      '<a class="reference-image" href="references/hybrid-style-reference.png" target="_blank" rel="noopener noreferrer" aria-label="' +
      t('hybridOpenStill') + '"><img src="references/hybrid-style-reference.png" alt="' +
      escapeHtml(t('hybridReferenceStill')) + '" loading="lazy" decoding="async"></a><div><p class="reference-label">REF 01 / LOOK</p><h4>' +
      t('hybridReferenceStill') + '</h4><p>' + t('hybridReferenceStillNote') + '</p></div></article>' +
      '<article class="reference-card reference-video"><div><p class="reference-label">REF 02 / MOTION</p><h4>' +
      t('hybridReferenceReel') + '</h4><p>' + t('hybridReferenceReelNote') + '</p>' +
      '<a href="https://www.instagram.com/reel/DdrD7WQpYK7/" target="_blank" rel="noopener noreferrer">' +
      t('hybridOpenReel') + '</a></div></article></div></aside>' +
      (looks.length ? '<section class="team-group" aria-labelledby="hybrid-looks"><header class="team-group-heading">' +
        '<span class="section-index">A</span><div><h3 id="hybrid-looks">' + t('hybridLooksHeading') +
        '</h3><p>' + t('hybridLooksDetail') + '</p></div></header><div class="grid">' + looks.map(card).join('') + '</div></section>' : '') +
      (frames.length ? '<section class="team-group" aria-labelledby="hybrid-transition"><header class="team-group-heading">' +
        '<span class="section-index">B</span><div><h3 id="hybrid-transition">' + t('hybridTransitionHeading') +
        '</h3><p>' + t('hybridTransitionDetail') + '</p></div></header><div class="grid transition-grid">' + frames.map(card).join('') +
        '</div><div class="transition-note"><p>' + t('hybridTiming') + '</p><p>' + t('hybridCaveat') + '</p></div></section>' : '');
  }
  function productionContent(items) {
    const groups = [
      {id:'luna', index:'A', title:'productionLuna', detail:'productionLunaDetail'},
      {id:'grandpa', index:'B', title:'productionGrandpa', detail:'productionGrandpaDetail'},
      {id:'sets', index:'C', title:'productionSets', detail:'productionSetsDetail'}
    ].filter(group => items.some(a => a.group === group.id));
    const profile = '<div class="luna-profile">' +
      ['Identity','Wardrobe','Orange'].map(part => '<div><h4>' + t('luna' + part + 'Label') +
        '</h4><p>' + t('luna' + part) + '</p></div>').join('') +
      '<div><h4>' + t('lunaPaletteLabel') + '</h4><div class="luna-palette" aria-hidden="true">' +
      ['#353735','#74725b','#171918','#d7cfb9','#d06f33'].map(color => '<span style="background:' + color + '"></span>').join('') +
      '</div><p>' + t('lunaPaletteNames') + '</p><a href="references/luna-orange-watercolor.png" target="_blank" rel="noopener noreferrer">' +
      t('lunaWatercolorLink') + '</a></div></div>';
    return '<div class="production-pitch"><p class="eyebrow">' + t('productionKicker') + '</p><h3>' +
      t('productionTitle') + '</h3><p>' + t('productionIntro') + '</p><nav class="production-jumps" aria-label="' +
      t('productionJumpLabel') + '">' + groups.map(g => '<a href="#production-' + g.id + '">' + t(g.title) + ' ↓</a>').join('') +
      '</nav></div><aside class="production-anchors" aria-label="' + t('productionChoices') + '">' +
      [{code:'G01',key:'productionG01'},{code:'D06',key:'productionD06'}].map(ref =>
        '<a href="assets/' + ref.code + '.png" target="_blank" rel="noopener noreferrer"><img src="assets/' + ref.code +
        '.png" alt="' + t(ref.key) + '" loading="lazy"><span>' + t(ref.key) + ' ↗</span></a>').join('') + '</aside>' +
      groups.map(group => '<section class="team-group production-group" aria-labelledby="production-' + group.id +
        '"><header class="team-group-heading"><span class="section-index">' + group.index + '</span><div><h3 id="production-' +
        group.id + '">' + t(group.title) + '</h3><p>' + t(group.detail) + '</p></div></header>' +
        (group.id === 'luna' ? profile : '') + '<div class="grid production-grid">' +
        items.filter(a => a.group === group.id).map(card).join('') + '</div>' +
        (group.id === 'grandpa' ? '<p class="production-footnote">' + t('productionAgeNote') + '</p>' : '') + '</section>').join('') +
      '<p class="production-footnote">' + t('productionCaveat') + '</p>';
  }
  function renderGallery() {
    const visible = visibleAssets();
    if (!visible.length) {
      $('gallery').innerHTML = '<div class="empty"><h2>' + t(assets.length ? 'noReferences' : 'boardPreparing') +
        '</h2><p>' + t(assets.length ? 'noReferencesHint' : 'boardPreparingHint') + '</p>' +
        (assets.length ? '<button type="button" class="action reset-filter" id="reset-filter">' + t('resetFilters') +
        '</button>' : '') + '</div>';
      const reset = $('reset-filter');
      if (reset) reset.addEventListener('click', () => {
        activeCategory = 'all'; favoritesOnly = false; renderFilters(); renderGallery();
      });
      return;
    }
    $('gallery').innerHTML = categories.map(category => {
      const items = visible.filter(a => a.category === category.id);
      return items.length ? '<section class="category" data-category="' + category.id +
        '" aria-labelledby="title-' + category.id + '"><header class="section-heading"><div class="section-title">' +
        '<span class="section-index">' + category.number + '</span><h2 id="title-' + category.id + '">' +
        category.title + '</h2></div><p class="section-detail">' + category.detail + '</p></header>' +
        (category.id === 'equipe' ? teamContent(items) : category.id === 'hybrides' ? hybridContent(items) : category.id === 'production' ? productionContent(items) :
          (category.id === 'styles' ? styleIntroduction() : '') + '<div class="grid">' + items.map(card).join('') + '</div>') +
        '</section>' : '';
    }).join('');
    $('gallery').querySelectorAll('.card img').forEach(img => img.addEventListener('error', () => {
      const asset = assetMap.get(img.closest('.card').dataset.code);
      img.parentElement.innerHTML = imageFallback(asset);
    }, {once:true}));
  }
  function renderSelection() {
    const picked = assets.filter(a => selected.has(a.code));
    $('nav-count').textContent = String(picked.length);
    $('selection-count').textContent = '/ ' + String(picked.length).padStart(2, '0');
    $('selection-codes').innerHTML = picked.length ? picked.map(a =>
      '<button type="button" class="selected-code" data-remove="' + escapeHtml(a.code) + '" aria-label="' +
      escapeHtml(t('removeSelection').replace('{code}', a.code)) + '" title="' + escapeHtml(field(a, 'title')) +
      '">' + escapeHtml(a.code) + '<span aria-hidden="true">×</span></button>'
    ).join('') : '<p class="no-selection">' + t('selectionStart') + '</p>';
    $('selection-meta').innerHTML = categories.map(c => '<span>' + c.label + ' <strong>' +
      picked.filter(a => a.category === c.id).length + '</strong></span>').join('');
    $('copy').disabled = !picked.length; $('download').disabled = !picked.length;
    $('floating-count').textContent = String(picked.length);
    $('floating-label').textContent = t(picked.length === 1 ? 'referenceOne' : 'referenceMany');
    $('floating-selection').hidden = !picked.length;
    $('copy-fallback').hidden = true;
  }
  function updateCard(code) {
    const chosen = selected.has(code);
    $('gallery').querySelectorAll('.card').forEach(el => {
      if (el.dataset.code !== code) return;
      el.classList.toggle('is-selected', chosen);
      const button = el.querySelector('[data-choose]');
      button.setAttribute('aria-pressed', String(chosen));
      button.setAttribute('aria-label', t(chosen ? 'unchoose' : 'choose') + ' ' + code);
      button.innerHTML = choiceContent(chosen);
    });
  }
  function toggleSelection(code) {
    if (!assetMap.has(code)) return;
    if (selected.has(code)) selected.delete(code); else selected.add(code);
    persist();
    if (favoritesOnly) renderGallery(); else updateCard(code);
    renderSelection();
    if (lightboxCode) updateLightboxSelection();
  }
  function notify(message) {
    clearTimeout(toastTimer); $('toast').textContent = message; $('toast').hidden = false;
    toastTimer = setTimeout(() => { $('toast').hidden = true; }, 2600);
  }
  function selectionText() {
    return t('selectionTextTitle') + '\n' + categories.map(c => {
      const chosen = assets.filter(a => a.category === c.id && selected.has(a.code));
      return c.label + ' : ' + (chosen.length ? chosen.map(a => a.code).join(', ') : t('toChoose'));
    }).join('\n');
  }
  function updateLightboxSelection() {
    const chosen = selected.has(lightboxCode);
    $('lightbox-choose').setAttribute('aria-pressed', String(chosen));
    $('lightbox-choose').setAttribute('aria-label', t(chosen ? 'unchoose' : 'choose') + ' ' + lightboxCode);
    $('lightbox-choose').innerHTML = choiceContent(chosen);
  }
  function renderLightbox(code) {
    const asset = assetMap.get(code); if (!asset) return;
    lightboxCode = code;
    $('lightbox-code').textContent = code;
    $('lightbox-title').textContent = field(asset, 'title') || code;
    $('lightbox-info').textContent = [field(asset, 'subtitle'), field(asset, 'note')].filter(Boolean).join(' · ');
    $('lightbox-position').textContent = (lightboxItems.indexOf(code) + 1) + ' / ' + lightboxItems.length;
    const img = $('lightbox-image'), source = safeImageSource(asset);
    img.hidden = !source; $('lightbox-empty').hidden = !!source;
    img.alt = [field(asset, 'title'), field(asset, 'subtitle')].filter(Boolean).join(' — ');
    img.onerror = () => { img.hidden = true; $('lightbox-empty').hidden = false; };
    if (source) img.src = source; else img.removeAttribute('src');
    $('lightbox-prev').disabled = lightboxItems.length < 2; $('lightbox-next').disabled = lightboxItems.length < 2;
    updateLightboxSelection();
  }
  function openLightbox(code, trigger) {
    returnFocus = trigger;
    lightboxItems = visibleAssets().map(a => a.code);
    renderLightbox(code);
    lastBodyOverflow = document.body.style.overflow;
    document.body.style.overflow = 'hidden';
    $('lightbox').hidden = false;
    document.querySelector('.shell').inert = true; $('floating-selection').inert = true;
    $('lightbox-close').focus();
  }
  function closeLightbox() {
    $('lightbox').hidden = true; lightboxCode = null;
    document.body.style.overflow = lastBodyOverflow;
    document.querySelector('.shell').inert = false; $('floating-selection').inert = false;
    if (returnFocus && returnFocus.isConnected) returnFocus.focus(); else $('favorites').focus();
  }
  function moveLightbox(direction) {
    if (!lightboxItems.length) return;
    const current = lightboxItems.indexOf(lightboxCode);
    renderLightbox(lightboxItems[(current + direction + lightboxItems.length) % lightboxItems.length]);
  }
  document.querySelectorAll('[data-language]').forEach(button => {
    button.addEventListener('click', () => setLanguage(button.dataset.language));
  });
  function exploreCategory(category) {
    activeCategory = category; favoritesOnly = false; renderFilters(); renderGallery();
    $('gallery').scrollIntoView({behavior:matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth', block:'start'});
    const filter = [...$('filters').querySelectorAll('button')].find(b => b.dataset.filter === category);
    if (filter) filter.focus({preventScroll:true});
  }
  $('explore-styles').addEventListener('click', () => exploreCategory('styles'));
  $('explore-team').addEventListener('click', () => exploreCategory('equipe'));
  $('explore-hybrids').addEventListener('click', () => exploreCategory('hybrides'));
  $('explore-production').addEventListener('click', () => exploreCategory('production'));
  $('filters').addEventListener('click', e => {
    const button = e.target.closest('[data-filter]'); if (!button) return;
    activeCategory = button.dataset.filter; renderFilters(); renderGallery();
    const next = [...$('filters').querySelectorAll('button')].find(b => b.dataset.filter === activeCategory);
    if (next) next.focus({preventScroll:true});
  });
  $('favorites').addEventListener('click', () => { favoritesOnly = !favoritesOnly; renderFilters(); renderGallery(); });
  $('gallery').addEventListener('click', e => {
    const choose = e.target.closest('[data-choose]');
    if (choose) { toggleSelection(choose.dataset.choose); return; }
    const preview = e.target.closest('[data-preview]');
    if (preview) openLightbox(preview.dataset.preview, preview);
  });
  $('selection-codes').addEventListener('click', e => {
    const remove = e.target.closest('[data-remove]'); if (remove) toggleSelection(remove.dataset.remove);
  });
  $('copy').addEventListener('click', async () => {
    const value = selectionText();
    try {
      if (!navigator.clipboard || !navigator.clipboard.writeText) throw new Error('Clipboard unavailable');
      await navigator.clipboard.writeText(value); notify(t('copied'));
    } catch (_) {
      $('copy-fallback').hidden = false; $('copy-text').value = value; $('copy-text').focus(); $('copy-text').select();
      let copied = false; try { copied = document.execCommand('copy'); } catch (_) {}
      if (copied) { $('copy-fallback').hidden = true; $('copy').focus(); notify(t('copied')); }
      else notify(t('readyToCopy'));
    }
  });
  $('download').addEventListener('click', () => {
    const data = {
      project:t('projectName'), exploration:5, language, exportedAt:new Date().toISOString(),
      selection:assets.filter(a => selected.has(a.code)).map(a => ({
        ...a, title:field(a, 'title'), subtitle:field(a, 'subtitle'), ...(a.note ? {note:field(a, 'note')} : {})
      }))
    };
    const blob = new Blob([JSON.stringify(data, null, 2) + '\n'], {type:'application/json;charset=utf-8'});
    const url = URL.createObjectURL(blob), link = document.createElement('a');
    link.href = url; link.download = 'converse-selection-05.json'; document.body.appendChild(link);
    link.click(); link.remove(); setTimeout(() => URL.revokeObjectURL(url), 1000);
    notify(t('readyToDownload'));
  });
  $('see-selection').addEventListener('click', () => {
    $('selection').scrollIntoView({behavior:matchMedia('(prefers-reduced-motion: reduce)').matches ? 'auto' : 'smooth', block:'center'});
    $('copy').focus({preventScroll:true});
  });
  $('lightbox-close').addEventListener('click', closeLightbox);
  $('lightbox-prev').addEventListener('click', () => moveLightbox(-1));
  $('lightbox-next').addEventListener('click', () => moveLightbox(1));
  $('lightbox-choose').addEventListener('click', () => toggleSelection(lightboxCode));
  $('lightbox').addEventListener('click', e => {
    if (e.target === $('lightbox') || e.target === $('lightbox-backdrop')) closeLightbox();
  });
  document.addEventListener('keydown', e => {
    if (!lightboxCode) return;
    if (e.key === 'Escape') { e.preventDefault(); closeLightbox(); }
    if (e.key === 'ArrowLeft') { e.preventDefault(); moveLightbox(-1); }
    if (e.key === 'ArrowRight') { e.preventDefault(); moveLightbox(1); }
    if (e.key === 'Tab') {
      const buttons = [...$('lightbox').querySelectorAll('button:not(:disabled)')];
      const first = buttons[0], last = buttons[buttons.length - 1];
      if (e.shiftKey && document.activeElement === first) { e.preventDefault(); last.focus(); }
      else if (!e.shiftKey && document.activeElement === last) { e.preventDefault(); first.focus(); }
    }
  });
  renderStaticText(); renderFilters(); renderGallery(); renderSelection();
})();
