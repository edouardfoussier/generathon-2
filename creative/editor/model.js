/** Pure editing operations. All intervals are half-open, in integer 24 fps frames. */
const FPS = 24;
const MAX_SEGMENTS = 200;
const MAX_FRAMES = 80 * FPS;
let splitCounter = 1;

function integer(value, name, minimum = 0) {
  if (!Number.isSafeInteger(value) || value < minimum) {
    throw new Error(`${name} must be an integer of at least ${minimum}.`);
  }
  return value;
}

function nonempty(value, name) {
  if (typeof value !== 'string' || !value.trim()) {
    throw new Error(`${name} must be a non-empty string.`);
  }
  return value;
}

function sourceIds(meta) {
  const sources = meta?.sourceIds ?? meta?.sources;
  if (Array.isArray(sources)) {
    return new Set(sources.map(source => typeof source === 'string' ? source : source?.id));
  }
  if (sources && typeof sources === 'object') return new Set(Object.keys(sources));
  throw new Error('Source metadata is missing. Reload the editor.');
}

export function sourceDuration(meta, id) {
  const sources = meta?.sources;
  const source = Array.isArray(sources) ? sources.find(item => item?.id === id) : sources?.[id];
  return integer(source?.durationFrames ?? meta?.durationFrames, 'Source duration', 1);
}

function segmentIndex(project, id) {
  const index = project.segments.findIndex(segment => segment.id === id);
  if (index < 0) throw new Error(`Segment ${id} does not exist.`);
  return index;
}

function replace(project, segments) {
  if (segments.length > MAX_SEGMENTS) {
    throw new Error(`A project can contain at most ${MAX_SEGMENTS} segments.`);
  }
  const next = { ...project, segments };
  if (durationFrames(next) > MAX_FRAMES) {
    throw new Error('The final cut must be 80 seconds or shorter.');
  }
  return next;
}

export function createProject(meta) {
  const bounds = meta?.boundariesFrames;
  if (!Array.isArray(bounds) || bounds.length < 2) {
    throw new Error('At least two scene boundaries are required.');
  }
  bounds.forEach((frame, index) => {
    integer(frame, `Scene boundary ${index + 1}`);
    if (index > 0 && frame <= bounds[index - 1]) {
      throw new Error('Scene boundaries must be strictly increasing.');
    }
  });
  if (bounds[0] !== 0 || bounds.at(-1) !== meta.durationFrames) {
    throw new Error('Scene boundaries must cover the complete source video.');
  }
  const project = {
    version: 1,
    fps: FPS,
    segments: bounds.slice(0, -1).map((inFrame, index) => ({
      id: `shot${String(index + 1).padStart(3, '0')}`,
      sourceId: 'veo31',
      inFrame,
      outFrame: bounds[index + 1],
    })),
  };
  validateProject(project, meta);
  return project;
}

/** Validate imported recipes and export requests; returns the validated object unchanged. */
export function validateProject(project, meta) {
  if (!project || typeof project !== 'object' || Array.isArray(project)) {
    throw new Error('The project must be a JSON object.');
  }
  if (project.version !== 1) throw new Error('Unsupported project version. Expected version 1.');
  if (project.fps !== FPS || (meta?.fps !== undefined && meta.fps !== FPS)) {
    throw new Error('This editor requires 24 fps projects and sources.');
  }
  const allowedSources = sourceIds(meta);
  if (project.audioMode !== undefined && !['source', 'veo', 'silent'].includes(project.audioMode)) {
    throw new Error('Unknown audio mode.');
  }
  if (project.soundtrackId !== undefined && project.soundtrackId !== null) nonempty(project.soundtrackId, 'Soundtrack ID');
  if (!Array.isArray(project.segments) || project.segments.length === 0) {
    throw new Error('Keep at least one segment in the final cut.');
  }
  if (project.segments.length > MAX_SEGMENTS) {
    throw new Error(`A project can contain at most ${MAX_SEGMENTS} segments.`);
  }
  const ids = new Set();
  let total = 0;
  project.segments.forEach((segment, index) => {
    const label = `Segment ${index + 1}`;
    if (!segment || typeof segment !== 'object' || Array.isArray(segment)) {
      throw new Error(`${label} must be an object.`);
    }
    nonempty(segment.id, `${label} ID`);
    if (segment.id.length > 100) throw new Error(`${label} ID must be at most 100 characters.`);
    if (ids.has(segment.id)) throw new Error(`Duplicate segment ID: ${segment.id}.`);
    ids.add(segment.id);
    if (!allowedSources.has(segment.sourceId)) {
      throw new Error(`${label} uses an unknown video source.`);
    }
    integer(segment.inFrame, `${label} in point`);
    integer(segment.outFrame, `${label} out point`, 1);
    if (segment.inFrame >= segment.outFrame) {
      throw new Error(`${label} must contain at least one frame.`);
    }
    if (segment.outFrame > sourceDuration(meta, segment.sourceId)) {
      throw new Error(`${label} extends beyond the source video.`);
    }
    total += segment.outFrame - segment.inFrame;
  });
  if (total > MAX_FRAMES) throw new Error('The final cut must be 80 seconds or shorter.');
  return project;
}

export function durationFrames(project) {
  return project.segments.reduce((sum, segment) => sum + segment.outFrame - segment.inFrame, 0);
}

export function timeline(project) {
  let cursor = 0;
  return project.segments.map((segment, index) => {
    const startFrame = cursor;
    const duration = segment.outFrame - segment.inFrame;
    cursor += duration;
    return { ...segment, startFrame, endFrame: cursor, durationFrames: duration, index };
  });
}

export function locate(project, timelineFrame) {
  if (!Number.isSafeInteger(timelineFrame)) throw new Error('The playhead must be an integer frame.');
  const segments = timeline(project);
  if (!segments.length) throw new Error('The final cut has no segments.');
  const frame = Math.max(0, Math.min(timelineFrame, segments.at(-1).endFrame - 1));
  const segment = segments.find(item => frame < item.endFrame);
  return { ...segment, sourceFrame: segment.inFrame + frame - segment.startFrame };
}

export function splitSegment(project, id, timelineFrame) {
  integer(timelineFrame, 'Split point');
  const index = segmentIndex(project, id);
  const segment = timeline(project)[index];
  if (timelineFrame <= segment.startFrame || timelineFrame >= segment.endFrame) return project;
  const sourceSplit = segment.inFrame + timelineFrame - segment.startFrame;
  const usedIds = new Set(project.segments.map(item => item.id));
  let newId;
  do { newId = `split-${splitCounter++}`; } while (usedIds.has(newId));
  const original = project.segments[index];
  const segments = project.segments.slice();
  segments.splice(index, 1,
    { ...original, outFrame: sourceSplit },
    { ...original, id: newId, inFrame: sourceSplit },
  );
  return replace(project, segments);
}

export function setSource(project, id, sourceId) {
  nonempty(sourceId, 'Source ID');
  const index = segmentIndex(project, id);
  if (project.segments[index].sourceId === sourceId) return project;
  const segments = project.segments.slice();
  segments[index] = { ...segments[index], sourceId };
  return { ...project, segments };
}

/** Insert a library clip. Its time is independent from the original three films. */
export function addSegment(project, afterId, sourceId, inFrame, outFrame, meta) {
  integer(inFrame, 'In point'); integer(outFrame, 'Out point', 1);
  if (inFrame >= outFrame) throw new Error('A segment must contain at least one frame.');
  const segments = project.segments.slice();
  let id;
  do { id = `library-${splitCounter++}`; } while (segments.some(item => item.id === id));
  const index = afterId ? segmentIndex(project, afterId) + 1 : segments.length;
  segments.splice(index, 0, { id, sourceId, inFrame, outFrame });
  const next = replace(project, segments);
  validateProject(next, meta);
  return next;
}

/** A new take starts at zero; do not reuse unrelated source timecodes. */
export function replaceTake(project, id, sourceId, meta, inFrame = 0, outFrame) {
  const index = segmentIndex(project, id);
  integer(inFrame, 'In point');
  const previous = project.segments[index];
  const end = outFrame ?? Math.min(sourceDuration(meta, sourceId), inFrame + previous.outFrame - previous.inFrame);
  const segments = project.segments.slice();
  segments[index] = { ...previous, sourceId, inFrame, outFrame: end };
  const next = replace(project, segments);
  validateProject(next, meta);
  return next;
}

/** Begin an independent cut from a library range; history is managed by the caller. */
export function projectFromClip(sourceId, inFrame, outFrame, meta) {
  const project = {
    version: 1, fps: FPS, audioMode: 'source',
    segments: [{ id: `first-${splitCounter++}`, sourceId, inFrame, outFrame }],
  };
  validateProject(project, meta);
  return project;
}

export function trimSegment(project, id, inFrame, outFrame) {
  integer(inFrame, 'In point');
  integer(outFrame, 'Out point', 1);
  if (inFrame >= outFrame) throw new Error('A segment must contain at least one frame.');
  const index = segmentIndex(project, id);
  const segments = project.segments.slice();
  segments[index] = { ...segments[index], inFrame, outFrame };
  return replace(project, segments);
}

export function removeSegment(project, id) {
  const index = segmentIndex(project, id);
  if (project.segments.length === 1) return project;
  return { ...project, segments: project.segments.filter((_, i) => i !== index) };
}

export function moveSegment(project, id, delta) {
  if (delta !== -1 && delta !== 1) throw new Error('Move direction must be -1 or 1.');
  const index = segmentIndex(project, id);
  const destination = index + delta;
  if (destination < 0 || destination >= project.segments.length) return project;
  const segments = project.segments.slice();
  [segments[index], segments[destination]] = [segments[destination], segments[index]];
  return { ...project, segments };
}

export function formatTime(frame, fps = FPS) {
  integer(frame, 'Timecode frame');
  integer(fps, 'Timecode frame rate', 1);
  const seconds = Math.floor(frame / fps);
  return [Math.floor(seconds / 60), seconds % 60, frame % fps]
    .map(part => String(part).padStart(2, '0')).join(':');
}
