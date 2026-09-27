import { safeMedia } from './model.js';

const positive = value => typeof value === 'number' && Number.isFinite(value) && value > 0;
const targetDuration = scene => positive(scene.duration) ? scene.duration : 4;
const metadataDuration = media => media?.duration ?? media?.durationSeconds;
const posterFor = scene => [scene.selectedTakes?.image?.url, scene.poster, scene.image].find(safeMedia) || null;

/** Ordered playback clips. Frame out-points are exclusive; all returned times are seconds. */
export function buildSchedule(project, durations = new Map()) {
  let cursor = 0;
  return (project?.scenes || []).map((scene, index) => {
    const candidates = [
      ['take', scene.selectedTakes?.video],
      ['preview', scene.previewVideo],
      ['source', scene.source],
    ];
    const [kind, media] = candidates.find(([, candidate]) => candidate?.url) || ['missing', null];
    const fallback = targetDuration(scene);
    const result = {id: scene.id, title: scene.title, index, url: null, start: cursor, end: cursor + fallback, duration: fallback, inPoint: 0, outPoint: fallback, kind: 'missing', estimated: true, poster: posterFor(scene)};
    if (media && safeMedia(media.url)) {
      const measured = durations.has(media.url);
      const known = measured ? durations.get(media.url) : metadataDuration(media);
      const hasKnown = known !== undefined && known !== null;
      let inPoint = 0;
      let outPoint = positive(known) ? known : fallback;
      let estimated = !hasKnown;
      let valid = !hasKnown || positive(known);
      if (kind !== 'take' || media.inFrame !== undefined || media.outFrame !== undefined) {
        const fps = media.fps ?? project?.fps ?? 24;
        valid &&= positive(fps);
        const first = media.inFrame ?? 0;
        const last = media.outFrame;
        valid &&= Number.isFinite(first) && first >= 0;
        inPoint = first / fps;
        if (last !== undefined && last !== null) {
          valid &&= Number.isFinite(last) && last > first;
          outPoint = last / fps;
          estimated = false;
        } else {
          outPoint = positive(known) ? known : inPoint + fallback;
          estimated = !hasKnown;
        }
        if (positive(known)) {
          inPoint = Math.min(inPoint, known);
          outPoint = Math.min(outPoint, known);
        }
      }
      const duration = outPoint - inPoint;
      if (valid && positive(duration)) {
        Object.assign(result, {url: media.url, inPoint, outPoint, duration, end: cursor + duration, kind, estimated});
      }
    }
    cursor = result.end;
    return result;
  });
}

/** Changes only when project fields affecting playback, ordering or its labels change. */
export function scheduleSignature(project) {
  const media = value => value ? [value.url, value.inFrame, value.outFrame, value.fps, value.duration, value.durationSeconds] : null;
  return JSON.stringify([project?.fps, (project?.scenes || []).map(scene => [
    scene.id, scene.title, scene.duration, media(scene.selectedTakes?.video),
    media(scene.previewVideo), media(scene.source), posterFor(scene),
  ])]);
}

/** Exact cut boundaries select the following shot, except the final endpoint. */
export function locateTime(schedule, requestedTime) {
  if (!schedule?.length) return {item: null, index: -1, offset: 0, time: 0};
  const total = schedule[schedule.length - 1].end;
  const numeric = Number(requestedTime);
  const time = Math.min(total, Math.max(0, Number.isNaN(numeric) ? 0 : numeric));
  const found = schedule.findIndex(item => time < item.end);
  const index = found < 0 ? schedule.length - 1 : found;
  const item = schedule[index];
  return {item, index, offset: Math.max(0, Math.min(item.duration, time - item.start)), time};
}
