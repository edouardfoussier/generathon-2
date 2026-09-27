import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { buildSchedule, locateTime, scheduleSignature } from './timeline-model.js';

const url = name => `/creative/test/${name}.mp4`;
const scene = (id, fields = {}) => ({id, title: id, duration: 4, ...fields});
const ranged = (name, start = 24, end = 168) => ({url: url(name), inFrame: start, outFrame: end, fps: 24});

test('real project preserves every shot and contiguous timing', async () => {
  const project = JSON.parse(await readFile(new URL('./project.json', import.meta.url), 'utf8'));
  const schedule = buildSchedule(project);
  assert.deepEqual(schedule.map(s => s.id), project.scenes.map(s => s.id));
  assert.ok(schedule.every(s => s.kind === 'preview' && !s.estimated && s.duration > 0));
  assert.equal(schedule[0].start, 0);
  for (let i = 1; i < schedule.length; i++) assert.equal(schedule[i].start, schedule[i - 1].end);
});

test('take, preview, source priority; complete take uses measured duration without scene truncation', () => {
  const project = {scenes: [scene('A', {selectedTakes: {video: {url: url('take'), duration: 8, inFrame: 10, outFrame: 20}}, previewVideo: ranged('preview'), source: ranged('source')})]};
  const item = buildSchedule(project, new Map([[url('take'), 12]]))[0];
  assert.equal(item.kind, 'take'); assert.equal(item.url, url('take'));
  assert.equal(item.duration, 12); assert.equal(item.inPoint, 0); assert.equal(item.outPoint, 12); assert.equal(item.estimated, false);
  delete project.scenes[0].selectedTakes;
  assert.equal(buildSchedule(project)[0].kind, 'preview');
  delete project.scenes[0].previewVideo;
  assert.equal(buildSchedule(project)[0].kind, 'source');
});

test('take metadata supports durationSeconds and unknown duration is explicitly estimated', () => {
  const project = {scenes: [scene('metadata', {selectedTakes: {video: {url: url('a'), durationSeconds: 9}}}), scene('unknown', {selectedTakes: {video: {url: url('b')}}})]};
  assert.deepEqual(buildSchedule(project).map(s => [s.duration, s.estimated, s.start]), [[9, false, 0], [4, true, 9]]);
});

test('frame range overrides target, clamps to metadata, exhausted and reversed ranges become slates', () => {
  const project = {scenes: [scene('long', {duration: .5, source: ranged('long')}), scene('clamp', {source: ranged('clamp')}), scene('exhausted', {source: ranged('exhausted')}), scene('reversed', {source: ranged('reversed', 72, 48)})]};
  const clips = buildSchedule(project, new Map([[url('clamp'), 3], [url('exhausted'), .5]]));
  assert.deepEqual(clips.map(s => [s.kind, s.inPoint, s.outPoint, s.duration]), [['source', 1, 7, 6], ['source', 1, 3, 2], ['missing', 0, 4, 4], ['missing', 0, 4, 4]]);
});

test('open source ends at real media end; absent media uses safe duration and poster', () => {
  const project = {fps: 24, scenes: [scene('open', {source: {url: url('open'), inFrame: 48}}), scene('missing', {duration: 3, poster: '/creative/poster.jpg'}), scene('invalid', {duration: NaN, source: {url: 'javascript:bad'}})]};
  const clips = buildSchedule(project, new Map([[url('open'), 11]]));
  assert.equal(clips[0].duration, 9); assert.equal(clips[0].inPoint, 2);
  assert.equal(clips[1].duration, 3); assert.equal(clips[1].poster, '/creative/poster.jpg');
  assert.equal(clips[2].kind, 'missing'); assert.equal(clips[2].duration, 4);
});

test('unsafe selected takes and zero or nonfinite metadata do not fall back silently', () => {
  const project = {scenes: [scene('unsafe', {selectedTakes: {video: {url: 'https://evil.invalid/clip.mp4'}}, previewVideo: ranged('preview')}), scene('zero', {selectedTakes: {video: {url: url('zero')}}}), scene('bad', {source: ranged('bad')})]};
  const clips = buildSchedule(project, new Map([[url('zero'), 0], [url('bad'), Infinity]]));
  assert.ok(clips.every(s => s.kind === 'missing' && s.url === null));
});

test('global seeking clamps, selects next at cuts and retains last endpoint', () => {
  const clips = buildSchedule({scenes: [scene('a'), scene('b', {duration: 6})]});
  for (const [requested, index, offset, time] of [[-3, 0, 0, 0], [3, 0, 3, 3], [4, 1, 0, 4], [9, 1, 5, 9], [10, 1, 6, 10], [Infinity, 1, 6, 10], [NaN, 0, 0, 0]]) {
    const actual = locateTime(clips, requested);
    assert.equal(actual.index, index); assert.equal(actual.offset, offset); assert.equal(actual.time, time); assert.equal(actual.item, clips[index]);
  }
  assert.deepEqual(locateTime([], 10), {item: null, index: -1, offset: 0, time: 0});
});

test('signature catches order, selected take, range and poster changes without prompt-only churn', () => {
  const original = {scenes: [scene('a', {source: ranged('a')}), scene('b')]};
  const signature = scheduleSignature(original);
  const promptOnly = structuredClone(original); promptOnly.scenes[0].prompt = 'new direction';
  assert.equal(scheduleSignature(promptOnly), signature);
  for (const change of [p => p.scenes.reverse(), p => p.scenes[0].source.outFrame++, p => p.scenes[0].selectedTakes = {video: {url: url('new')}}, p => p.scenes[0].poster = '/creative/new.jpg']) {
    const changed = structuredClone(original); change(changed);
    assert.notEqual(scheduleSignature(changed), signature);
  }
});
