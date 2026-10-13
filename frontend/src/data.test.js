import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { validateBenchmark, validateFixes } from './data.js';

const load = name => JSON.parse(readFileSync(new URL(`../public/${name}`, import.meta.url)));

test('loads the published problem/fix list', () => {
  const fixes = validateFixes(load('fixes.json'));
  assert.ok(fixes.length && fixes.every(f => f.problem && f.fix && f.links.length));
});

test('rejects incomplete entries and unsafe links', () => {
  for (const value of [null, {}, [null], [{ problem: 'Only a problem.' }], [{ problem: 'P.', fix: 'F.', links: [{ title: 'Bad', url: 'javascript:alert(1)' }] }]]) {
    assert.throws(() => validateFixes(value));
  }
});

test('loads the generated benchmark and rejects missing values', () => {
  const data = validateBenchmark(load('benchmark.json'));
  assert.equal(data.deciders.length, 7);
  assert.ok(data.metrics.length >= 7);
  assert.equal(data.tests.length, data.counts.questions);
  assert.equal(data.tiers.reduce((n, t) => n + t.count, 0), data.tests.length);
  assert.ok(data.tests.every(t => data.deciders.every(d => t.results[d.id])));
  assert.throws(() => validateBenchmark({ ...data, metrics: [{ ...data.metrics[0], values: { jev: 0.7 } }] }));
});
