(() => {
  'use strict';
  const data = window.CONVERSE_REFINEMENTS || {assets:[], references:[], notes:{}};
  const assets = new Map(data.assets.map(asset => [asset.id, asset]));
  const storageKey = 'converse-refinement-v4-choices';
  const languageKey = 'converse-board-language';
  let language = 'fr';
  let choices = {};
  let groupedPlayback = null;
  try { language = localStorage.getItem(languageKey) || 'fr'; choices = JSON.parse(localStorage.getItem(storageKey) || '{}'); } catch (_) {}
  const requested = new URLSearchParams(location.search).get('lang');
  if (requested === 'en' || requested === 'fr') language = requested;
  if (!['en', 'fr'].includes(language)) language = 'fr';
  if (!choices || Array.isArray(choices) || typeof choices !== 'object') choices = {};
  const copy = {
    fr: {
      back:'← La planche',eyebrow:'Atelier 13 · Raffinements',headline:'La même histoire.\nPlus de caractère.',intro:'Comparons la matière des visages, le téléphone dans le grenier et deux nouvelles musiques. Le film FG01 reste notre référence.',facesNav:'01 · Visages',phoneNav:'02 · Téléphone',musicNav:'03 · Films & musique',scriptNav:'04 · Scénario',choicesNav:'Mes choix ↓',facesEyebrow:'01 · Une seule matière',facesTitle:'Les visages, côte à côte.',facesNote:'A : le film actuel. B : les mêmes références GPT, avec un prompt peinture renforcé. C : une référence repeinte, puis le même langage vidéo.',method1:'Regarder la peau et les contours, pas seulement la netteté.',method2:'Vérifier que le personnage reste reconnaissable.',method3:'Comparer le visage, les mains et le décor dans la même matière.',comparisonLimit:'Ces essais comparent des prises différentes d’une même scène. Les gestes et le cadrage peuvent varier ; ce n’est pas une comparaison image par image. Les lectures groupées sont muettes et s’arrêtent à la fin de la prise la plus courte.',referenceTitle:'Voir les nouvelles références repeintes',phoneEyebrow:'02 · Le téléphone appartient au monde',phoneTitle:'Rester avec Luna.',phoneNote:'La photo, ses mains, le coffre et le grenier racontent le geste. L’écran cesse d’interrompre le film.',musicEyebrow:'03 · Le rythme, puis l’émotion',musicTitle:'Deux nouvelles pulsations.',musicNote:'Deux bandes originales instrumentales, créées avec ElevenLabs via Arcads. Les versions A et B utilisent le même montage de travail pour comparer leur énergie.',filmLimit:'Les montages de travail sont des propositions. Choisir un visage ci-dessus ne remonte pas automatiquement la vidéo et ne modifie pas FG01.',scriptEyebrow:'04 · Retrouver le découpage',scriptTitle:'Le v2 n’a pas été perdu.',scriptNote:'Il a donné l’animatique de 26 plans. Le v3 a ensuite suivi votre nouveau récit. On reprend maintenant la précision du v2 dans l’histoire actuelle.',audit1Title:'La voix traverse la coupe',audit1:'Faire commencer l’appel de Maman pendant le souvenir : le son ramène Luna avant même que l’image ne change.',audit2Title:'Un geste, plusieurs échelles',audit2:'Semelle, main, regard : quelques inserts courts relancent le rythme, puis les sourires ont le temps d’exister.',audit3Title:'Un effet a une raison',audit3:'Une trace de pigment suit un appui ou un pivot. Trois accents précis suffisent ; l’émotion reste lisible.',auditLink:'Lire l’audit v2 → v3 → FG01 ↗',planLink:'Lire le découpage v4 proposé · 76 s ↗',inspirationLink:'Référence Converse · MAKE. MOVE. REPEAT. ↗',choicesEyebrow:'À décider ensemble',choicesTitle:'Vos préférences.',choicesNote:'Un choix par scène, sauvegardé dans ce navigateur. Exportez-le pour le partager à l’équipe.',exportChoices:'Télécharger mes choix ↗',footer:'Essais de direction artistique et montages de travail · Conserve what matters.',footerBack:'Retour à toutes les explorations ↗',playTogether:'Lire ensemble ↻',pauseTogether:'Arrêter la comparaison',pending:'EN PRÉPARATION',pendingNote:'Le lecteur apparaîtra quand le fichier sera prêt.',download:'Ouvrir le fichier ↗',choose:'＋ Préférer',chosen:'✓ Mon choix',noChoices:'Aucune préférence choisie pour le moment.',luna:'Luna · le retour au grenier',salsa:'Rafa & Elena · la rencontre',originalTitle:'A · Rendu actuel',promptTitle:'B · Prompt peinture renforcé',proTitle:'C · Référence repeinte',originalNote:'Extrait du film FG01 · références GPT Image 2.5 Sunburst.',promptNote:'Références GPT conservées · même Seedance 2.5, matière des visages davantage précisée.',proNote:'Référence repeinte depuis les planches GPT · Seedance 2.5. Nano Banana Pro demandé ; le fournisseur indique Nano Banana 2.',phoneOriginalTitle:'Avant · écran isolé',phoneOriginalNote:'Le passage graphique actuel, extrait de FG01.',phoneCorrectedTitle:'Essai 2 · raccord de la photo',phoneCorrectedNote:'Nouvel essai à partir de l’image du coffre FG01, pour conserver le format paysage de la photo.',phoneNewTitle:'Essai 1 · photo dans le grenier',phoneNewNote:'Luna photographie le portrait de Rafa. Le téléphone reste dans la scène peinte.',filmOriginalTitle:'FG01 · le film de référence',filmOriginalNote:'Version appréciée par l’équipe · image et bande-son conservées.',filmATitle:'V4 A · rythme + groove latin',filmANote:'Montage rythme + musique A · visages FG01 conservés.',filmBTitle:'V4 B · rythme + piano',filmBNote:'Même montage rythme que A · musique B · visages FG01 conservés.',audioA:'Musique A · groove latin',audioB:'Musique B · percussion & piano',audioNote:'Instrumental original · écoute séparée',saved:'Préférence sauvegardée dans ce navigateur.',playError:'La lecture groupée n’a pas pu démarrer. Utilisez les commandes de chaque vidéo.',lunaRef:'Luna · référence repeinte',salsaRef:'Rafa & Elena · référence repeinte, continuité corrigée'
    },
    en: {
      back:'← The board',eyebrow:'Workshop 13 · Refinements',headline:'The same story.\nMore character.',intro:'Compare painted faces, a phone scene inside the attic and two new soundtracks. FG01 remains our reference film.',facesNav:'01 · Faces',phoneNav:'02 · Phone',musicNav:'03 · Films & music',scriptNav:'04 · Script',choicesNav:'My choices ↓',facesEyebrow:'01 · One shared medium',facesTitle:'Faces, side by side.',facesNote:'A: the current film. B: the same GPT references with stronger painting instructions. C: a repainted reference, then the same video treatment.',method1:'Look at skin and outlines, not just sharpness.',method2:'Check that the character remains recognizable.',method3:'Compare the face, hands and setting as one painted world.',comparisonLimit:'These are different takes of the same scene. Acting and framing can vary; this is not a frame-matched comparison. Group playback is muted and stops at the end of the shortest take.',referenceTitle:'View the new repainted references',phoneEyebrow:'02 · The phone belongs in the world',phoneTitle:'Stay with Luna.',phoneNote:'The photograph, her hands, the box and the attic tell the story. The screen no longer interrupts the film.',musicEyebrow:'03 · Rhythm, then emotion',musicTitle:'Two new pulses.',musicNote:'Two original instrumental scores, created with ElevenLabs through Arcads. Versions A and B use the same working picture edit so you can compare their energy.',filmLimit:'The working cuts are proposals. Choosing a face above does not automatically re-edit the video or change FG01.',scriptEyebrow:'04 · Recover the shot design',scriptTitle:'V2 was not lost.',scriptNote:'It became the 26-shot animatic. V3 then followed your revised story. We are bringing v2’s precision into the current narrative.',audit1Title:'The voice crosses the cut',audit1:'Start Mom’s call inside the memory: sound brings Luna back before the picture changes.',audit2Title:'One gesture, several scales',audit2:'Sole, hand, glance: a few short inserts give the edit energy, then smiles have time to land.',audit3Title:'Every effect has a reason',audit3:'A pigment trail follows a footfall or pivot. Three precise accents are enough; emotion stays readable.',auditLink:'Read the v2 → v3 → FG01 audit ↗',planLink:'Read the proposed v4 shot plan · 76 s ↗',inspirationLink:'Converse reference · MAKE. MOVE. REPEAT. ↗',choicesEyebrow:'Choose together',choicesTitle:'Your preferences.',choicesNote:'One choice per scene, saved in this browser. Export your choices to share with the team.',exportChoices:'Download my choices ↗',footer:'Art direction trials and working cuts · Conserve what matters.',footerBack:'Back to all explorations ↗',playTogether:'Play together ↻',pauseTogether:'Stop comparison',pending:'IN PREPARATION',pendingNote:'A player will appear when the file is ready.',download:'Open file ↗',choose:'＋ Prefer',chosen:'✓ My choice',noChoices:'No preferences chosen yet.',luna:'Luna · returning to the attic',salsa:'Rafa & Elena · their first meeting',originalTitle:'A · Current rendering',promptTitle:'B · Stronger painting prompt',proTitle:'C · Repainted reference',originalNote:'Excerpt from FG01 · GPT Image 2.5 Sunburst references.',promptNote:'Same GPT references · Seedance 2.5 with more specific instructions for painted faces.',proNote:'Reference repainted from the GPT sheets · Seedance 2.5. Nano Banana Pro requested; the provider reports Nano Banana 2.',phoneOriginalTitle:'Before · isolated screen',phoneOriginalNote:'The current graphic passage, extracted from FG01.',phoneCorrectedTitle:'Trial 2 · matching the photograph',phoneCorrectedNote:'New trial guided by FG01’s shoebox frame, to keep the physical photograph in landscape format.',phoneNewTitle:'Trial 1 · photograph in the attic',phoneNewNote:'Luna photographs Rafa’s portrait. The phone stays inside the painted scene.',filmOriginalTitle:'FG01 · reference film',filmOriginalNote:'The version the team liked · original picture and soundtrack preserved.',filmATitle:'V4 A · rhythm + Latin groove',filmANote:'Rhythm + soundtrack A · FG01 faces retained.',filmBTitle:'V4 B · rhythm + piano',filmBNote:'Same rhythm edit as A · soundtrack B · FG01 faces retained.',audioA:'Music A · Latin groove',audioB:'Music B · percussion & piano',audioNote:'Original instrumental · separate listening',saved:'Preference saved in this browser.',playError:'Group playback could not start. Use each video’s own controls.',lunaRef:'Luna · repainted reference',salsaRef:'Rafa & Elena · repainted reference, continuity corrected'
    }
  };
  const specs = [
    {id:'luna-original',code:'FG01-L',group:'luna',title:'originalTitle',description:'originalNote'},
    {id:'luna-prompt',code:'RF01',group:'luna',title:'promptTitle',description:'promptNote'},
    {id:'luna-pro',code:'RF03',group:'luna',title:'proTitle',description:'proNote'},
    {id:'salsa-original',code:'FG01-S',group:'salsa',title:'originalTitle',description:'originalNote'},
    {id:'salsa-prompt',code:'RF02',group:'salsa',title:'promptTitle',description:'promptNote'},
    {id:'salsa-pro',code:'RF04',group:'salsa',title:'proTitle',description:'proNote'},
    {id:'phone-original',code:'FG01-P',group:'phone',title:'phoneOriginalTitle',description:'phoneOriginalNote'},
    {id:'phone-attic',code:'RF05',group:'phone',title:'phoneNewTitle',description:'phoneNewNote'},
    {id:'phone-attic-v2',code:'RF06',group:'phone',title:'phoneCorrectedTitle',description:'phoneCorrectedNote'},
    {id:'film-original',code:'FG01',group:'film',title:'filmOriginalTitle',description:'filmOriginalNote'},
    {id:'film-a',code:'V4-A',group:'film',title:'filmATitle',description:'filmANote'},
    {id:'film-b',code:'V4-B',group:'film',title:'filmBTitle',description:'filmBNote'},
  ];
  const $ = id => document.getElementById(id);
  const t = key => copy[language][key] || key;
  const escape = value => String(value).replace(/[&<>"']/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
  const safePath = value => typeof value === 'string' && !/^(?:[a-z][a-z0-9+.-]*:|\/\/)/i.test(value) ? value : '';
  const note = id => {
    const entry = (data.notes || {})[id];
    return entry && typeof entry === 'object' ? (entry[language] || entry.en || entry.fr || '') : '';
  };
  function card(spec) {
    const asset = assets.get(spec.id);
    const chosen = choices[spec.group] === spec.id;
    const header = '<h3 class="card-title">' + escape(t(spec.title)) + '</h3><p class="card-description">' + escape(t(spec.description)) + '</p>';
    if (!asset || !safePath(asset.file)) return '<article class="media-card"><div class="pending"><span>' + t('pending') + ' · ' + spec.code + '</span><p>' + t('pendingNote') + '</p></div><div class="card-body">' + header + '</div></article>';
    const silent = spec.group !== 'film';
    return '<article class="media-card' + (chosen ? ' is-selected' : '') + '" data-card="' + spec.id + '"><div class="media-wrap"><video controls playsinline preload="metadata"' + (silent ? ' muted' : '') + ' data-media="' + spec.id + '" data-group="' + spec.group + '" poster="' + escape(safePath(asset.poster)) + '" aria-label="' + escape(t(spec.title)) + '"><source src="' + escape(asset.file) + '" type="video/mp4"></video><span class="card-code">' + spec.code + '</span></div><div class="card-body">' + header + '<div class="card-actions"><span class="duration">' + asset.duration.toFixed(1) + ' s · <a class="download" href="' + escape(asset.file) + '">' + t('download') + '</a></span><button class="choose" type="button" data-choice="' + spec.id + '" aria-pressed="' + chosen + '">' + (chosen ? t('chosen') : t('choose')) + '</button></div>' + (note(spec.id) ? '<p class="card-note">' + escape(note(spec.id)) + '</p>' : '') + '</div></article>';
  }
  function render() {
    document.querySelectorAll('video,audio').forEach(media => media.pause());
    groupedPlayback = null;
    document.documentElement.lang = language;
    document.title = 'Converse — ' + (language === 'fr' ? 'Raffinements' : 'Refinements');
    document.querySelectorAll('[data-t]').forEach(el => el.textContent = t(el.dataset.t));
    document.querySelectorAll('[data-lang]').forEach(button => button.setAttribute('aria-pressed', String(button.dataset.lang === language)));
    const back = '../selection/index.html?category=motionlab&lang=' + language;
    $('back-link').href = back; $('footer-back').href = back;
    $('face-rows').innerHTML = ['luna','salsa'].map(group => '<div class="comparison-row"><div class="row-head"><h3>' + t(group) + '</h3><button type="button" data-play-group="' + group + '"' + (specs.filter(s => s.group === group && assets.has(s.id)).length < 2 ? ' disabled' : '') + '>' + t('playTogether') + '</button></div><div class="three-grid">' + specs.filter(spec => spec.group === group).map(card).join('') + '</div></div>').join('');
    $('phone-cards').innerHTML = specs.filter(spec => spec.group === 'phone').map(card).join('');
    $('film-cards').innerHTML = specs.filter(spec => spec.group === 'film').map(card).join('');
    $('audio-cards').innerHTML = ['a','b'].map(kind => {
      const asset = assets.get('music-' + kind);
      if (!asset || !safePath(asset.file)) return '';
      return '<article class="audio-card"><h3>' + t(kind === 'a' ? 'audioA' : 'audioB') + '</h3><p>' + t('audioNote') + ' · ' + asset.duration.toFixed(1) + ' s</p><audio controls preload="metadata" src="' + escape(asset.file) + '"></audio></article>';
    }).join('');
    $('reference-images').innerHTML = data.references.map(path => '<div class="reference"><a href="' + escape(safePath(path)) + '"><img loading="lazy" src="' + escape(safePath(path)) + '" alt="' + escape(t(path.includes('luna') ? 'lunaRef' : 'salsaRef')) + '"></a><p>' + t(path.includes('luna') ? 'lunaRef' : 'salsaRef') + '</p></div>').join('');
    renderChoices();
  }
  function renderChoices() {
    const selected = specs.filter(spec => choices[spec.group] === spec.id && assets.has(spec.id));
    $('choice-list').innerHTML = selected.length ? selected.map(spec => '<span class="choice-chip">' + spec.code + ' · ' + escape(t(spec.title)) + '</span>').join('') : '<span class="no-choice">' + t('noChoices') + '</span>';
    $('export-choices').disabled = !selected.length;
    document.querySelectorAll('[data-choice]').forEach(button => {
      const spec = specs.find(item => item.id === button.dataset.choice);
      const chosen = choices[spec.group] === spec.id;
      button.setAttribute('aria-pressed', String(chosen));
      button.textContent = chosen ? t('chosen') : t('choose');
      button.closest('.media-card').classList.toggle('is-selected', chosen);
    });
  }
  function stopGroup() {
    if (!groupedPlayback) return;
    const group = groupedPlayback.group;
    groupedPlayback = null;
    document.querySelectorAll('video[data-group="' + group + '"]').forEach(video => video.pause());
    const button = document.querySelector('[data-play-group="' + group + '"]');
    if (button) button.textContent = t('playTogether');
  }
  document.addEventListener('click', async event => {
    const languageButton = event.target.closest('[data-lang]');
    if (languageButton) {
      language = languageButton.dataset.lang;
      try { localStorage.setItem(languageKey, language); const url = new URL(location.href); url.searchParams.set('lang', language); history.replaceState(null, '', url); } catch (_) {}
      render(); return;
    }
    const choiceButton = event.target.closest('[data-choice]');
    if (choiceButton) {
      const spec = specs.find(item => item.id === choiceButton.dataset.choice);
      if (choices[spec.group] === spec.id) delete choices[spec.group]; else choices[spec.group] = spec.id;
      try { localStorage.setItem(storageKey, JSON.stringify(choices)); } catch (_) {}
      renderChoices(); $('status').textContent = t('saved'); return;
    }
    const playButton = event.target.closest('[data-play-group]');
    if (playButton) {
      const group = playButton.dataset.playGroup;
      if (groupedPlayback?.group === group) { stopGroup(); return; }
      stopGroup();
      document.querySelectorAll('video,audio').forEach(media => media.pause());
      const videos = [...document.querySelectorAll('video[data-group="' + group + '"]')];
      const limit = Math.min(...videos.map(video => assets.get(video.dataset.media).duration));
      groupedPlayback = {group, limit};
      videos.forEach(video => { video.currentTime = 0; video.muted = true; video.playbackRate = 1; });
      const results = await Promise.allSettled(videos.map(video => video.play()));
      if (results.some(result => result.status === 'rejected')) { stopGroup(); $('status').textContent = t('playError'); }
      else playButton.textContent = t('pauseTogether');
    }
  });
  document.addEventListener('play', event => {
    if (!event.target.matches('video,audio')) return;
    const target = event.target;
    if (groupedPlayback && target.dataset.group === groupedPlayback.group) return;
    stopGroup();
    document.querySelectorAll('video,audio').forEach(media => { if (media !== target) media.pause(); });
  }, true);
  document.addEventListener('timeupdate', event => {
    if (groupedPlayback && event.target.dataset.group === groupedPlayback.group && event.target.currentTime >= groupedPlayback.limit - 0.06) stopGroup();
  }, true);
  document.addEventListener('ended', event => { if (groupedPlayback && event.target.dataset.group === groupedPlayback.group) stopGroup(); }, true);
  $('export-choices').addEventListener('click', () => {
    const selected = specs.filter(spec => choices[spec.group] === spec.id && assets.has(spec.id));
    const exported = {project:'Converse — Conserve what matters',workshop:'refinement-v4',language,exportedAt:new Date().toISOString(),choices:selected.map(spec => ({scene:spec.group,id:spec.id,code:spec.code,title:t(spec.title),file:assets.get(spec.id).file}))};
    const url = URL.createObjectURL(new Blob([JSON.stringify(exported,null,2)],{type:'application/json'}));
    const link = document.createElement('a'); link.href = url; link.download = 'converse-refinement-choices.json'; link.click(); setTimeout(() => URL.revokeObjectURL(url),1000);
  });
  render();
})();
