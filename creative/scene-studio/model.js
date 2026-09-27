export const copy = value => JSON.parse(JSON.stringify(value));
export const uid = () => globalThis.crypto?.randomUUID?.() || `scene-${Date.now()}-${Math.random().toString(16).slice(2)}`;
export const duration = project => project.scenes.reduce((sum, scene) => sum + Number(scene.duration || 0), 0);
export const seconds = value => `${Math.floor(value / 60).toString().padStart(2, '0')}:${Math.floor(value % 60).toString().padStart(2, '0')}`;
export function insertScene(project, afterId, {title = 'Nouveau souvenir', description = ''} = {}) {
  const index = project.scenes.findIndex(scene => scene.id === afterId);
  if (index < 0) throw new Error('Scène introuvable.');
  const previous = project.scenes[index];
  const scene = {id: uid(), title, description, duration: 4, prompt: description || 'Décrire ici l’action de ce nouveau plan.', references: copy(previous.references || []), blocking: copy(previous.blocking), versions: [], created: true, provenance: {kind: 'new', note: 'Nouveau plan. Décor et références hérités du plan précédent ; aucun rendu généré.'}};
  project.scenes.splice(index + 1, 0, scene);
  return scene;
}
export function moveScene(project, id, direction) {
  const index = project.scenes.findIndex(scene => scene.id === id);
  const target = index + direction;
  if (index < 0 || target < 0 || target >= project.scenes.length) return false;
  [project.scenes[index], project.scenes[target]] = [project.scenes[target], project.scenes[index]];
  return true;
}
export function snapshot(scene, reason) {
  scene.versions ||= [];
  scene.versions.unshift({id: uid(), at: new Date().toISOString(), reason, prompt: scene.prompt, blocking: copy(scene.blocking)});
  scene.versions = scene.versions.slice(0, 30);
}
export function applyDirection(scene, instruction) {
  const text = instruction.trim();
  if (!text) throw new Error('Décris la modification à apporter.');
  snapshot(scene, text);
  scene.prompt = `${scene.prompt.trim()}\n\nLATEST DIRECTOR NOTE (takes precedence where conflicting):\n${text}`;
  const changes = interpretDirection(scene.blocking, text);
  scene.blocking = changes.blocking;
  scene.modified = true;
  return changes.applied;
}
export function interpretDirection(current, input) {
  const blocking = copy(current || {location: 'attic', characters: [], camera: {position: [6, 4, 8], target: [0, 1, 0], fov: 42}, lighting: {warmth: .6, intensity: 1}});
  const text = input.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '');
  const applied = [];
  for (const [word, location] of [['grenier','attic'],['terrain de basket','basketball'],['salsa','salsa'],['mariage','wedding'],['bebe','nursery'],['transmission','handover']]) {
    if (text.includes(word)) {blocking.location = location; applied.push('Décor'); break;}
  }
  blocking.lighting ||= {warmth:.6,intensity:1};
  if (/nuit|plus sombre|night/.test(text)) {blocking.lighting.intensity = .35; applied.push('Lumière tamisée');}
  else if (/plus lumineux|eclaircir|bright/.test(text)) {blocking.lighting.intensity = 1.6; applied.push('Lumière renforcée');}
  if (/chaud|dore|coucher|golden/.test(text)) {blocking.lighting.warmth = .95; applied.push('Lumière chaude');}
  else if (/froid|bleute|cold/.test(text)) {blocking.lighting.warmth = .1; applied.push('Lumière froide');}
  blocking.camera ||= {position:[6,4,8],target:[0,1,0],fov:42};
  if (/gros plan|rapproch|close.?up/.test(text)) {blocking.camera.position = [2.2,1.8,3.3]; blocking.camera.target = [0,1.25,0]; blocking.camera.fov = 42; applied.push('Caméra rapprochée');}
  else if (/plan large|eloign|wide/.test(text)) {blocking.camera.position = [7,5,9]; blocking.camera.target = [0,1,0]; applied.push('Plan large');}
  if (/plongee|vue du dessus|top view/.test(text)) {blocking.camera.position = [.01,10,.1]; blocking.camera.target = [0,0,0]; applied.push('Vue du dessus');}
  for (const person of blocking.characters || []) {
    const name = `${person.id} ${person.label}`.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '');
    const named = /luna/.test(name) ? /luna/.test(text) : /rafa|grand/.test(name) ? /rafa|grand/.test(text) : /elena/.test(name) ? /elena/.test(text) : false;
    if (named && /a gauche/.test(text)) {person.position[0] -= .6; applied.push(`${person.label} à gauche`);}
    if (named && /a droite/.test(text)) {person.position[0] += .6; applied.push(`${person.label} à droite`);}
  }
  return {blocking, applied:[...new Set(applied)]};
}
export function validateProject(value) {
  if (!value || value.version !== 1 || !Array.isArray(value.scenes) || !value.scenes.length || value.scenes.length > 100) throw new Error('Projet invalide : 1 à 100 scènes au format Studio v1.');
  const ids = new Set();
  for (const s of value.scenes) {
    if (!s || typeof s.id !== 'string' || ids.has(s.id) || typeof s.title !== 'string' || typeof s.prompt !== 'string' || !Number.isFinite(s.duration) || s.duration < .25 || s.duration > 30) throw new Error('Une scène contient des données invalides.');
    ids.add(s.id);
    validateBlocking(s.blocking);
    if ((s.references || []).length > 16) throw new Error('Trop de références.');
    if (s.previewVideo?.url && !safeMedia(s.previewVideo.url)) throw new Error('Prévisualisation non autorisée.');
    for (const take of Object.values(s.selectedTakes || {})) if (!safeMedia(take.url)) throw new Error('Version média non autorisée.');
    if (s.source?.url && !safeMedia(s.source.url)) throw new Error('Source média non autorisée.');
    for (const r of s.references || []) if (!safeMedia(r.url)) throw new Error('Référence média non autorisée.');
    if (s.image && !safeMedia(s.image)) throw new Error('Image non autorisée.');
    if (s.poster && !safeMedia(s.poster)) throw new Error('Affiche non autorisée.');
  }
  return copy(value);
}
export function safeMedia(url) {
  if (typeof url !== 'string') return false;
  if (/^\/api\/studio\/jobs\/[a-f0-9]{32}\/artifact$/.test(url)) return true;
  if (url.startsWith('/creative/') && !url.includes('..') && !/[\\\x00]/.test(url)) return true;
  try {const u = new URL(url); return u.protocol === 'https:' && !u.username && !u.password && ['d8j0ntlcm91z4.cloudfront.net','d2ol7oe51mr4n9.cloudfront.net','cdn.higgsfield.ai','media.higgsfield.ai','assets.higgsfield.ai','cdn.arcads.ai','assets.arcads.ai'].includes(u.hostname);} catch {return false;}
}

export function generationPrompt(scene, type, useCamera) {
  const interval = scene.source ? `Source excerpt: ${(scene.source.inFrame / (scene.source.fps || 24)).toFixed(3)}–${(scene.source.outFrame / (scene.source.fps || 24)).toFixed(3)} seconds of its source clip.` : 'New inserted shot.';
  return `DELIVERABLE: Generate ONE ${type === 'video' ? `${scene.duration}-second video shot` : 'single still keyframe'} for the Luna/Rafa film.
SELECTED SHOT: ${scene.title}. ${scene.description || ''}
${interval}
The production brief below may describe multiple scenes or a longer original generation. Generate ONLY the selected shot, with the requested duration; do not reproduce the full film or multi-panel contact sheets.
${useCamera ? 'A 3D staging image is included as a camera/composition guide ONLY. Keep the character identities, costumes and hand-painted gouache appearance from the supplied identity/location/product references; do not copy the proxy mannequin faces or low-poly materials. If a source reference conflicts with the layout image, use the identity reference for appearance and the layout image for framing.' : 'Use the supplied identity, location and product references.'}

SOURCE BRIEF AND CURRENT DIRECTOR NOTES:
${scene.prompt}`;
}

export function validateBlocking(b) {
  const vector = v => Array.isArray(v) && v.length === 3 && v.every(n => Number.isFinite(n) && Math.abs(n) <= 100);
  if (!b || !['attic','basketball','salsa','wedding','nursery','handover','product'].includes(b.location) || !Array.isArray(b.characters) || b.characters.length > 12) throw new Error('Maquette 3D invalide.');
  for (const c of b.characters) if (!c || typeof c.id !== 'string' || !vector(c.position) || (c.label !== undefined && typeof c.label !== 'string')) throw new Error('Placement de personnage invalide.');
  if (b.camera && (!vector(b.camera.position) || !vector(b.camera.target) || !Number.isFinite(b.camera.fov) || b.camera.fov < 10 || b.camera.fov > 100)) throw new Error('Caméra invalide.');
  if (b.lighting && (!Number.isFinite(b.lighting.warmth) || b.lighting.warmth < 0 || b.lighting.warmth > 1 || !Number.isFinite(b.lighting.intensity) || b.lighting.intensity < .2 || b.lighting.intensity > 2)) throw new Error('Lumière invalide.');
  if (b.props && (!Array.isArray(b.props) || b.props.length > 80 || b.props.some(p => !p || (p.position && !vector(p.position))))) throw new Error('Accessoires invalides.');
  return copy(b);
}
export function mergeBlocking(base, patch) {
  return validateBlocking({...copy(base),...copy(patch),camera:{...base.camera,...patch.camera},lighting:{...base.lighting,...patch.lighting}});
}

export function replaceReference(scene, referenceId, next, reason = 'Nouvelle référence') {
  const current = scene.references.find(r => r.id === referenceId);
  if (!current || !safeMedia(next.url)) throw new Error('Référence introuvable ou résultat non autorisé.');
  scene.referenceVersions ||= {};
  const history = scene.referenceVersions[referenceId] ||= [];
  history.unshift({ ...copy(current), at: new Date().toISOString(), reason });
  current.url = next.url;
  scene.modified = true;
  return current;
}

export function referencePrompt(scene, reference, note) {
  if (!note.trim()) throw new Error('Décris la modification de cet élément.');
  return `DELIVERABLE: ONE revised reference image of the single asset "${reference.label}" (${reference.id}, ${reference.role || 'reference'}).
Edit the supplied asset reference only. Preserve the existing identity, illustration style and all details unless the director explicitly requests changing them. Produce the same kind of reference sheet or isolated asset as the input, not a full scene, film frame or video.
Selected scene context: ${scene.title}. ${scene.description || ''}
DIRECTOR'S ASSET CHANGE:\n${note.trim()}`;
}
