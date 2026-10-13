export const emptyResearch = {
  version: 2, status: 'pending',
  thesis: { body: '', why: '', when: [], whenNot: [], method: '', links: [] },
  learnings: [], methodology: [], results: [], phoenix: [], challenges: [], takeaways: [], sources: [],
};

function validateLinks(links, label) {
  if (!Array.isArray(links) || links.length > 100) throw new Error(`${label} must be a list of up to 100 links.`);
  for (const link of links) {
    if (!link || typeof link.title !== 'string' || !link.title.trim()) throw new Error('Each link needs a title.');
    let url;
    try { url = new URL(link.url); } catch { throw new Error('Each link needs a valid web URL.'); }
    if (!['https:', 'http:'].includes(url.protocol)) throw new Error('Links must use an http or https URL.');
  }
  return links.map(({ title, url }) => ({ title, url }));
}

function validateRows(rows, name, fields) {
  if (!Array.isArray(rows) || rows.length > 100) throw new Error(`${name} must be a list of up to 100 entries.`);
  return rows.map(row => {
    if (!row || fields.some(key => typeof row[key] !== 'string' || !row[key].trim())) throw new Error(`Each ${name} entry needs ${fields.join(', ')}.`);
    return { ...Object.fromEntries(fields.map(key => [key, row[key]])), links: validateLinks(row.links ?? [], 'Attached links') };
  });
}

export function validateResearch(value) {
  if (!value || ![1, 2].includes(value.version) || !['pending', 'ready'].includes(value.status)) throw new Error('Use research format version 1 or 2 with a status of pending or ready.');
  // Preserve files created with the original presentation template.
  if (value.version === 1) {
    return validateResearch({ ...emptyResearch, status: value.status, learnings: value.findings, takeaways: value.recommendations, sources: value.sources });
  }
  const thesis = value.thesis;
  if (!thesis || ['body', 'why', 'method'].some(key => typeof thesis[key] !== 'string')) throw new Error('The thesis needs body, why, and method text.');
  for (const key of ['when', 'whenNot']) {
    if (!Array.isArray(thesis[key]) || thesis[key].length > 100 || thesis[key].some(text => typeof text !== 'string' || !text.trim())) throw new Error(`Thesis ${key} must be a list of text entries.`);
  }
  const result = {
    version: 2, status: value.status,
    thesis: { body: thesis.body, why: thesis.why, method: thesis.method, when: thesis.when, whenNot: thesis.whenNot, links: validateLinks(thesis.links ?? [], 'Thesis links') },
    learnings: validateRows(value.learnings, 'learnings', ['title', 'body']),
    methodology: validateRows(value.methodology ?? [], 'methodology', ['title', 'body']),
    results: validateRows(value.results ?? [], 'results', ['title', 'body']),
    phoenix: validateRows(value.phoenix ?? [], 'phoenix', ['title', 'body']),
    challenges: validateRows(value.challenges, 'challenges', ['title', 'challenge', 'solution']),
    takeaways: validateRows(value.takeaways, 'takeaways', ['title', 'body']),
    sources: validateLinks(value.sources, 'Sources'),
  };
  if (result.status === 'ready' && !result.results.length && !result.learnings.length) throw new Error('Add at least one result before marking the research ready.');
  return result;
}

const METRIC_FORMATS = ['percent', 'usd', 'cents', 'seconds', 'decimal', 'count', 'ms'];

export function validateBenchmark(value) {
  if (!value || !Array.isArray(value.deciders) || !Array.isArray(value.metrics)) throw new Error('The benchmark needs deciders and metrics.');
  const ids = value.deciders.map(d => d.id);
  if (value.deciders.some(d => !d || typeof d.id !== 'string' || typeof d.short !== 'string' || typeof d.name !== 'string' || !['decision', 'reasoning', 'fixed'].includes(d.kind))) throw new Error('Each decider needs an id, short name, name, and kind.');
  for (const m of value.metrics) {
    if (!m || typeof m.label !== 'string' || typeof m.description !== 'string' || !METRIC_FORMATS.includes(m.format) || !['higher', 'lower'].includes(m.better)) throw new Error('Each metric needs a label, description, format, and direction.');
    if (ids.some(id => typeof m.values?.[id] !== 'number' || !Number.isFinite(m.values[id]))) throw new Error(`${m.label} needs a number for every decider.`);
  }
  return value;
}
