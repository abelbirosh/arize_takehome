export const emptyResearch = { version: 1, status: 'pending', findings: [], recommendations: [], sources: [] };

export function validateResearch(value) {
  if (!value || value.version !== 1 || !['pending', 'ready'].includes(value.status)) throw new Error('Use research format version 1 with a status of pending or ready.');
  for (const name of ['findings', 'recommendations', 'sources']) {
    if (!Array.isArray(value[name]) || value[name].length > 100) throw new Error(`${name} must be a list of up to 100 entries.`);
  }
  for (const row of [...value.findings, ...value.recommendations]) {
    if (typeof row.title !== 'string' || typeof row.body !== 'string' || !row.title.trim() || !row.body.trim()) throw new Error('Each finding and recommendation needs a title and body.');
  }
  for (const source of value.sources) {
    if (typeof source.title !== 'string' || !source.title.trim()) throw new Error('Each source needs a title.');
    let url;
    try { url = new URL(source.url); } catch { throw new Error('Each source needs a valid web URL.'); }
    if (!['https:', 'http:'].includes(url.protocol)) throw new Error('Sources must use an http or https URL.');
  }
  if (value.status === 'ready' && !value.findings.length) throw new Error('Add at least one finding before marking the research ready.');
  return { version: 1, status: value.status, findings: value.findings, recommendations: value.recommendations, sources: value.sources };
}
