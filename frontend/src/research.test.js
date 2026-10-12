import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { validateResearch, emptyResearch } from './research.js';

test('loads the published presentation and Phoenix evidence links', () => {
  const data = validateResearch(JSON.parse(readFileSync(new URL('../public/research.json', import.meta.url))));
  assert.equal(data.version, 2);
  assert.ok(data.thesis.body && data.thesis.why);
  assert.ok(data.learnings.length && data.challenges.length && data.takeaways.length);
  assert.ok(data.phoenix.length && data.phoenix.every(row => row.links.length));
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
