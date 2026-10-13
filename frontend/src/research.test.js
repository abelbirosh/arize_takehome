import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { validateResearch, validateBenchmark, emptyResearch } from './research.js';

test('loads the published presentation and Phoenix evidence links', () => {
  const data = validateResearch(JSON.parse(readFileSync(new URL('../public/research.json', import.meta.url))));
  assert.equal(data.version, 2);
  assert.ok(data.thesis.body && data.thesis.why);
  assert.ok(data.learnings.length && data.challenges.length);
  assert.ok(data.challenges.every(row => row.challenge && row.solution && row.links.length));
  assert.ok(Array.isArray(data.results));
  assert.deepEqual(validateResearch(emptyResearch), emptyResearch);
});

test('preserves older research imports when upgrading to the new sections', () => {
  const data = validateResearch({ version: 1, status: 'ready', findings: [{ title: 'Finding', body: 'Evidence.' }], recommendations: [{ title: 'Recommendation', body: 'Guidance.' }], sources: [] });
  assert.equal(data.version, 2);
  assert.equal(data.learnings[0].title, 'Finding');
  assert.equal(data.takeaways[0].title, 'Recommendation');
  assert.deepEqual(data.challenges, []);
});

test('rejects malformed sections, incomplete challenge pairs, unsafe links and false readiness', () => {
  for (const value of [null, {}, { ...emptyResearch, learnings: 'bad' }, { ...emptyResearch, status: 'ready' }, { ...emptyResearch, learnings: [null] }, { ...emptyResearch, challenges: [{ title: 'Problem', challenge: 'Problem.' }] }, { ...emptyResearch, thesis: { ...emptyResearch.thesis, when: [null] } }, { ...emptyResearch, sources: [{ title: 'Unsafe', url: 'javascript:alert(1)' }] }, { ...emptyResearch, learnings: [{ title: 'Learning', body: 'Text.', links: [{ title: 'Unsafe', url: 'data:text/html,test' }] }] }, { version: 1, status: 'pending', findings: [], sources: [] }]) {
    assert.throws(() => validateResearch(value));
  }
});

test("accepts a results-first research file", () => {
  const data = validateResearch({ ...emptyResearch, status: "ready", results: [{ title: "Synthetic test result", body: "Schema validation fixture." }] });
  assert.equal(data.results.length, 1);
});

test('loads the generated benchmark charts and rejects missing values', () => {
  const data = validateBenchmark(JSON.parse(readFileSync(new URL('../public/benchmark.json', import.meta.url))));
  assert.equal(data.deciders.length, 7);
  assert.ok(data.metrics.length >= 7);
  assert.equal(data.tests.length, data.counts.questions);
  assert.equal(data.tiers.reduce((n, t) => n + t.count, 0), data.tests.length);
  assert.ok(data.tests.every(t => data.deciders.every(d => t.results[d.id])));
  const broken = { ...data, metrics: [{ ...data.metrics[0], values: { jev: 0.7 } }] };
  assert.throws(() => validateBenchmark(broken));
});
