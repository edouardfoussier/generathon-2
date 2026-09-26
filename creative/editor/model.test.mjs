import test from 'node:test';
import assert from 'node:assert/strict';
import {
  createProject, validateProject, timeline, locate, splitSegment, setSource,
  trimSegment, removeSegment, moveSegment, durationFrames, formatTime,
} from './model.js';

const meta = {
  fps: 24,
  durationFrames: 1824,
  boundariesFrames: [0, 144, 240, 360, 528, 624, 696, 864, 936, 1128, 1224, 1320, 1512, 1584, 1728, 1824],
  sources: [{ id: 'veo31' }, { id: 'kling3' }, { id: 'seedance25' }],
};

function freeze(value) {
  Object.freeze(value);
  for (const child of Object.values(value)) if (child && typeof child === 'object') freeze(child);
  return value;
}

function shortProject() {
  return {
    version: 1,
    fps: 24,
    segments: [
      { id: 'a', sourceId: 'veo31', inFrame: 24, outFrame: 72 },
      { id: 'b', sourceId: 'kling3', inFrame: 240, outFrame: 264 },
      { id: 'c', sourceId: 'seedance25', inFrame: 1000, outFrame: 1036 },
    ],
  };
}

test('new project covers all 76 seconds with Veo defaults and original scene boundaries', () => {
  const project = createProject(freeze(structuredClone(meta)));
  assert.equal(project.version, 1);
  assert.equal(project.fps, 24);
  assert.equal(project.segments.length, 15);
  assert.equal(durationFrames(project), 1824);
  assert.ok(project.segments.every(segment => segment.sourceId === 'veo31'));
  assert.equal(project.segments[0].id, 'shot001');
  assert.equal(project.segments.at(-1).outFrame, 1824);
  assert.equal(validateProject(project, meta), project);
});

test('deep sequential splits keep unique IDs inside the export API limit', () => {
  let project = createProject(meta);
  // Keep splitting the new right-hand portion, the path that formerly grew
  // nested "-split-N" suffixes beyond the backend's 100-character limit.
  for (let frame = 1; frame <= 120; frame += 1) {
    project = splitSegment(project, locate(project, frame).id, frame);
  }
  assert.equal(project.segments.length, 135);
  assert.equal(durationFrames(project), 1824);
  assert.equal(new Set(project.segments.map(segment => segment.id)).size, project.segments.length);
  assert.ok(project.segments.every(segment => segment.id.length <= 100));
  assert.equal(validateProject(project, meta), project);

  const imported = structuredClone(project);
  imported.segments[0].id = 'x'.repeat(101);
  assert.throws(() => validateProject(imported, meta), /at most 100/);
  imported.segments[0].id = 'x'.repeat(100);
  assert.equal(validateProject(imported, meta), imported);
});

test('source choices, a split, a trim and reordering map every output frame to the intended source', () => {
  const original = freeze(shortProject());
  let edited = splitSegment(original, 'b', 60);
  const rightId = edited.segments[2].id;
  edited = setSource(edited, rightId, 'veo31');
  edited = trimSegment(edited, 'a', 30, 72);
  edited = moveSegment(edited, 'c', -1);
  validateProject(edited, meta);
  const expected = [
    ...Array.from({ length: 42 }, (_, i) => ['veo31', 30 + i]),
    ...Array.from({ length: 12 }, (_, i) => ['kling3', 240 + i]),
    ...Array.from({ length: 36 }, (_, i) => ['seedance25', 1000 + i]),
    ...Array.from({ length: 12 }, (_, i) => ['veo31', 252 + i]),
  ];
  assert.equal(durationFrames(edited), expected.length);
  expected.forEach(([sourceId, sourceFrame], frame) => {
    const actual = locate(edited, frame);
    assert.equal(actual.sourceId, sourceId, `source at output frame ${frame}`);
    assert.equal(actual.sourceFrame, sourceFrame, `source frame at output frame ${frame}`);
  });
  assert.deepEqual(original, shortProject());
});

test('timeline reports half-open intervals without adding properties to source segments', () => {
  const project = freeze(shortProject());
  assert.deepEqual(timeline(project).map(({ startFrame, endFrame, durationFrames, index }) =>
    [startFrame, endFrame, durationFrames, index]), [[0, 48, 48, 0], [48, 72, 24, 1], [72, 108, 36, 2]]);
  assert.equal(locate(project, 47).id, 'a');
  assert.equal(locate(project, 48).id, 'b');
  assert.equal(locate(project, 72).id, 'c');
  assert.equal(locate(project, -100).sourceFrame, 24);
  assert.equal(locate(project, 108).sourceFrame, 1035);
  assert.equal(locate(project, 999999).sourceFrame, 1035);
});

test('splitting at a boundary or outside the selected interval is a no-op', () => {
  const project = freeze(shortProject());
  for (const frame of [0, 47, 48, 72, 108]) {
    assert.equal(splitSegment(project, 'b', frame), project);
  }
});

test('repeated splits allocate unique IDs and preserve total duration', () => {
  let project = shortProject();
  project = splitSegment(project, 'a', 10);
  project = splitSegment(project, 'a', 5);
  project = splitSegment(project, project.segments[2].id, 11);
  assert.equal(new Set(project.segments.map(segment => segment.id)).size, project.segments.length);
  assert.equal(durationFrames(project), 108);
  assert.doesNotThrow(() => validateProject(project, meta));
});

test('deleting shifts later clips and never deletes the final remaining clip', () => {
  const original = freeze(shortProject());
  let project = removeSegment(original, 'a');
  assert.equal(locate(project, 0).sourceFrame, 240);
  project = removeSegment(project, 'b');
  assert.equal(project.segments.length, 1);
  assert.equal(removeSegment(project, 'c'), project);
  assert.deepEqual(original, shortProject());
});

test('moving at an edge is a no-op; an invalid direction is rejected', () => {
  const project = freeze(shortProject());
  assert.equal(moveSegment(project, 'a', -1), project);
  assert.equal(moveSegment(project, 'c', 1), project);
  assert.throws(() => moveSegment(project, 'a', 2), /direction/);
  assert.throws(() => moveSegment(project, 'missing', 1), /does not exist/);
});

test('validation accepts alternate metadata source shapes', () => {
  const project = shortProject();
  assert.doesNotThrow(() => validateProject(project, { ...meta, sources: ['veo31', 'kling3', 'seedance25'] }));
  assert.doesNotThrow(() => validateProject(project, { ...meta, sources: { veo31: {}, kling3: {}, seedance25: {} } }));
  assert.doesNotThrow(() => validateProject(project, { ...meta, sources: undefined, sourceIds: ['veo31', 'kling3', 'seedance25'] }));
});

test('invalid imports reject noninteger, nonfinite, backwards and out-of-range source intervals', () => {
  const invalidRanges = [
    [NaN, 24], [0, Infinity], [0.5, 24], [0, 23.5], [-1, 24],
    [24, 24], [25, 24], [0, 1825], [0, '24'], [0, Number.MAX_SAFE_INTEGER + 1],
  ];
  for (const [inFrame, outFrame] of invalidRanges) {
    const project = shortProject();
    Object.assign(project.segments[0], { inFrame, outFrame });
    assert.throws(() => validateProject(project, meta), undefined, `${inFrame}..${outFrame}`);
  }
});

test('invalid imports reject unknown sources, duplicate IDs, empty clips and wrong version/fps', () => {
  const invalid = [
    null, [], {},
    { ...shortProject(), version: 2 },
    { ...shortProject(), fps: 30 },
    { ...shortProject(), segments: [] },
    { ...shortProject(), segments: [null] },
    { ...shortProject(), segments: [{ id: 'x', sourceId: 'unknown', inFrame: 0, outFrame: 24 }] },
    { ...shortProject(), segments: [{ id: '', sourceId: 'veo31', inFrame: 0, outFrame: 24 }] },
    { ...shortProject(), segments: [shortProject().segments[0], shortProject().segments[0]] },
  ];
  for (const project of invalid) assert.throws(() => validateProject(project, meta));
});

test('one frame and exactly 80 seconds are valid, while 80 seconds plus a frame is rejected', () => {
  const single = { version: 1, fps: 24, segments: [{ id: 'one', sourceId: 'veo31', inFrame: 0, outFrame: 1 }] };
  assert.doesNotThrow(() => validateProject(single, meta));
  const project = { ...single, segments: [
    { id: 'a', sourceId: 'veo31', inFrame: 0, outFrame: 1824 },
    { id: 'b', sourceId: 'kling3', inFrame: 0, outFrame: 96 },
  ] };
  assert.doesNotThrow(() => validateProject(project, meta));
  project.segments[1].outFrame = 97;
  assert.throws(() => validateProject(project, meta), /80 seconds/);
});

test('segment limits apply both to imported projects and interactive splitting', () => {
  const project = { version: 1, fps: 24, segments: Array.from({ length: 200 }, (_, index) => ({
    id: `seg${index}`, sourceId: 'veo31', inFrame: 0, outFrame: 2,
  })) };
  assert.doesNotThrow(() => validateProject(project, meta));
  assert.throws(() => splitSegment(project, 'seg0', 1), /200 segments/);
  project.segments.push({ id: 'extra', sourceId: 'veo31', inFrame: 0, outFrame: 1 });
  assert.throws(() => validateProject(project, meta), /200 segments/);
});

test('interactive edits reject malformed local values and overlong final cuts', () => {
  const project = shortProject();
  assert.throws(() => trimSegment(project, 'a', 0.1, 20), /integer/);
  assert.throws(() => trimSegment(project, 'a', 20, 20), /one frame/);
  assert.throws(() => trimSegment(project, 'a', 0, 1920), /80 seconds/);
  assert.throws(() => setSource(project, 'a', ''), /Source ID/);
  assert.throws(() => locate(project, NaN), /integer frame/);
  assert.throws(() => splitSegment(project, 'a', Infinity), /integer/);
});

test('malformed scene metadata cannot silently create gaps or zero-length default clips', () => {
  for (const boundariesFrames of [[0], [0, 144, 144, 1824], [1, 1824], [0, 1823], [0, 1.5, 1824]]) {
    assert.throws(() => createProject({ ...meta, boundariesFrames }));
  }
  assert.throws(() => createProject({ ...meta, fps: 30 }), /24 fps/);
});

test('timecode renders exact frame boundaries and values longer than a minute', () => {
  assert.equal(formatTime(0), '00:00:00');
  assert.equal(formatTime(23), '00:00:23');
  assert.equal(formatTime(24), '00:01:00');
  assert.equal(formatTime(1823), '01:15:23');
  assert.equal(formatTime(1920), '01:20:00');
  assert.equal(formatTime(25, 25), '00:01:00');
  assert.throws(() => formatTime(-1), /integer/);
  assert.throws(() => formatTime(1, 0), /integer/);
});
