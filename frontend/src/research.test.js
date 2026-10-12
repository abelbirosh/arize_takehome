import { test } from 'node:test';
import assert from 'node:assert/strict';
import { validateResearch, emptyResearch } from './research.js';
test('accepts the empty research shell and real research', () => {
  assert.deepEqual(validateResearch(emptyResearch), emptyResearch);
  assert.equal(validateResearch({ ...emptyResearch, status: 'ready', findings: [{ title: 'Measured result', body: 'Evidence goes here.' }] }).status, 'ready');
});
test('rejects malformed imports, unsafe URLs, and false readiness', () => {
  for (const value of [null, {}, { ...emptyResearch, findings: 'bad' }, { ...emptyResearch, status: 'ready' }, { ...emptyResearch, findings: [{}] }, { ...emptyResearch, sources: [{ title: 'Unsafe', url: 'javascript:alert(1)' }] }]) {
    assert.throws(() => validateResearch(value));
  }
});
