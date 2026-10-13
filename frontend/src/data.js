// Validators for the two content files the presentation loads from public/.

function validateLinks(links) {
  if (!Array.isArray(links)) throw new Error('Links must be a list.');
  for (const link of links) {
    if (!link || typeof link.title !== 'string' || !link.title.trim()) throw new Error('Each link needs a title.');
    let url;
    try { url = new URL(link.url); } catch { throw new Error('Each link needs a valid web URL.'); }
    if (!['https:', 'http:'].includes(url.protocol)) throw new Error('Links must use an http or https URL.');
  }
  return links.map(({ title, url }) => ({ title, url }));
}

export function validateFixes(value) {
  if (!Array.isArray(value)) throw new Error('fixes.json must be a list.');
  return value.map(row => {
    if (!row || ['problem', 'fix'].some(key => typeof row[key] !== 'string' || !row[key].trim())) throw new Error('Each entry needs a problem and a fix.');
    return { problem: row.problem, fix: row.fix, links: validateLinks(row.links ?? []) };
  });
}

const RESULT_LABELS = ['correct', 'hedged', 'incorrect', 'no_answer'];
const METRIC_FORMATS = ['percent', 'usd', 'cents', 'seconds', 'decimal', 'count', 'ms'];

export function validateBenchmark(value) {
  if (!value || !Array.isArray(value.deciders) || !Array.isArray(value.metrics)) throw new Error('The benchmark needs deciders and metrics.');
  const ids = value.deciders.map(d => d.id);
  if (value.deciders.some(d => !d || typeof d.id !== 'string' || typeof d.short !== 'string' || typeof d.name !== 'string' || !['decision', 'reasoning', 'fixed'].includes(d.kind))) throw new Error('Each decider needs an id, short name, name, and kind.');
  for (const m of value.metrics) {
    if (!m || typeof m.label !== 'string' || typeof m.description !== 'string' || !METRIC_FORMATS.includes(m.format) || !['higher', 'lower'].includes(m.better)) throw new Error('Each metric needs a label, description, format, and direction.');
    if (ids.some(id => typeof m.values?.[id] !== 'number' || !Number.isFinite(m.values[id]))) throw new Error(`${m.label} needs a number for every decider.`);
  }
  const tiers = new Set((value.tiers ?? []).map(t => t.id));
  for (const t of value.tests ?? []) {
    if (!t || !Number.isInteger(t.n) || typeof t.question !== 'string' || typeof t.answer !== 'string' || !tiers.has(t.tier)) throw new Error('Each test needs a number, question, answer, and known tier.');
    if (ids.some(id => !RESULT_LABELS.includes(t.results?.[id]))) throw new Error(`Test ${t.n} needs a result for every decider.`);
  }
  return value;
}
