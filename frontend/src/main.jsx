import React, { useEffect, useRef, useState } from 'react';
import { createRoot } from 'react-dom/client';
import './styles.css';
import { emptyResearch, validateBenchmark, validateResearch } from './research.js';

const chapters = [
  { id: 'question', name: 'Question', title: 'Can a decision model choose the next steps of a research agent as well as a reasoning model?' },
  { id: 'methodology', name: 'Methodology', title: 'Methodology' },
  { id: 'detailed-results', name: 'Detailed results', title: 'Detailed results' },
  { id: 'phoenix', name: 'How I used Phoenix?', title: 'How I used Phoenix?' },
  { id: 'challenges', name: 'What went wrong and how we fixed it?', title: 'What went wrong and how we fixed it?' },
  { id: 'takeaways', name: 'Takeaways', title: 'Takeaways' },
];
const legacyHashes = { 'when-to-jev': 'question', mechanism: 'methodology', experiment: 'methodology', results: 'detailed-results', findings: 'detailed-results', learnings: 'phoenix', practice: 'takeaways', sources: 'phoenix' };
const indexFromHash = () => {
  const hash = window.location.hash.slice(1);
  return Math.max(0, chapters.findIndex(c => c.id === (legacyHashes[hash] || hash)));
};

function Icon({ name, ...props }) {
  if (name === 'github') return <svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor" aria-hidden="true" {...props}><path d="M12 .297a12 12 0 0 0-3.793 23.385c.6.111.82-.261.82-.577v-2.234c-3.338.726-4.043-1.416-4.043-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.09-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.835 2.809 1.305 3.493.998.108-.776.419-1.305.762-1.605-2.665-.305-5.467-1.334-5.467-5.931 0-1.31.469-2.381 1.236-3.221-.124-.303-.536-1.524.117-3.176 0 0 1.008-.322 3.301 1.23a11.52 11.52 0 0 1 6.006 0c2.291-1.552 3.297-1.23 3.297-1.23.655 1.652.243 2.873.119 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.216.694.825.576A12.001 12.001 0 0 0 12 .297Z"/></svg>;
  const paths = { arrow: <><path d="M4 12h16M14 6l6 6-6 6"/></>, expand: <path d="M9 3H3v6m12-6h6v6M3 15v6h6m12-6v6h-6"/>, close: <path d="m6 6 12 12M6 18 18 6"/> };
  return <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" {...props}>{paths[name] || paths.arrow}</svg>;
}

function ReferenceLinks({ links = [] }) {
  if (!links.length) return null;
  return <ul className="reference-links" aria-label="Attached links">{links.map((link, i) => <li key={i}><a href={link.url} target="_blank" rel="noreferrer">{link.title}<Icon name="arrow"/></a></li>)}</ul>;
}

function ResearchNotes({ items, challenges = false, emptyTitle }) {
  if (!items.length) return <div className="empty-evidence"><h2>{emptyTitle}</h2><p>Research for this section is pending.</p><span className="status-label"><span/>Awaiting research</span></div>;
  return <div className={`evidence-list ${challenges ? 'challenge-list' : ''}`}>{items.map((item, i) => <article key={i}>
    <h2>{item.title}</h2>
    {challenges ? <div className="challenge-pair"><div><h3>Challenge</h3><p>{item.challenge}</p></div><div><h3>Solution</h3><p>{item.solution}</p></div></div> : <p>{item.body}</p>}
    <ReferenceLinks links={item.links}/>
  </article>)}</div>;
}

const kindLabels = { decision: 'Decision model', reasoning: 'Claude model', fixed: 'Fixed sequence' };
const formatValue = (format, v) => ({
  percent: () => `${Math.round(v * 100)}%`,
  usd: () => v === 0 ? '$0' : `$${v < 0.01 ? v.toFixed(4) : v.toFixed(3)}`,
  seconds: () => `${v.toFixed(1)} s`,
  decimal: () => v.toFixed(1),
  count: () => String(v),
  ms: () => `${Math.round(v).toLocaleString('en-US')} ms`,
})[format]();

function MetricChart({ metric, deciders }) {
  const excluded = metric.excluded || {};
  // Best on the left, worst on the right; ties keep the decider order.
  const ranked = deciders.filter(d => !(d.id in excluded))
    .sort((a, b) => metric.better === 'higher' ? metric.values[b.id] - metric.values[a.id] : metric.values[a.id] - metric.values[b.id]);
  const left = deciders.filter(d => d.id in excluded);
  const max = metric.max ?? (Math.max(...ranked.map(d => metric.values[d.id])) || 1);
  const notes = [...new Set(Object.values(excluded))];
  return <figure className="metric">
    <figcaption><h2>{metric.label}</h2><span>{metric.better === 'higher' ? 'Higher' : 'Lower'} is better</span></figcaption>
    <div className="bars" aria-hidden="true">
      {ranked.map(d => <div className={`bar-col kind-${d.kind} ${d.id === 'jev' ? 'is-jev' : ''}`} key={d.id}>
        <span className="bar-value">{formatValue(metric.format, metric.values[d.id])}</span>
        <span className="bar" style={{ height: `${metric.values[d.id] / max * 100}%` }}/>
        <span className="bar-name">{d.short}</span>
        <span className="bar-tip">{d.name}<br/>{formatValue(metric.format, metric.values[d.id])}</span>
      </div>)}
      {left.map(d => <div className={`bar-col kind-${d.kind} is-excluded`} key={d.id}>
        <span className="bar-value">*</span>
        <span className="bar-name">{d.short}</span>
      </div>)}
    </div>
    <p className="metric-description">{metric.description}</p>
    {notes.map(note => <p className="metric-note" key={note}>* {note}</p>)}
    <div className="visually-hidden"><table><caption>{metric.label}, best to worst</caption><thead><tr><th scope="col">Decider</th><th scope="col">{metric.label}</th></tr></thead>
      <tbody>{ranked.map(d => <tr key={d.id}><th scope="row">{d.name}</th><td>{formatValue(metric.format, metric.values[d.id])}</td></tr>)}{left.map(d => <tr key={d.id}><th scope="row">{d.name}</th><td>Not plotted. {excluded[d.id]}</td></tr>)}</tbody></table></div>
  </figure>;
}

function BenchmarkCharts({ benchmark }) {
  const kinds = [...new Set(benchmark.deciders.map(d => d.kind))];
  return <section className="benchmark" aria-label="Benchmark results">
    <div className="benchmark-key">
      <p>{benchmark.questions} questions × {benchmark.deciders.length} deciders, {benchmark.runs} runs. Each chart runs best to worst, left to right.</p>
      <ul className="legend">{kinds.map(k => <li key={k}><span className={`swatch kind-${k}`}/>{kindLabels[k]}</li>)}</ul>
    </div>
    <div className="metric-grid">{benchmark.metrics.map(m => <MetricChart key={m.id} metric={m} deciders={benchmark.deciders}/>)}</div>
  </section>;
}

function App() {
  const [chapter, setChapter] = useState(indexFromHash);
  const [research, setResearch] = useState(emptyResearch);
  const [benchmark, setBenchmark] = useState(null);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [presenting, setPresenting] = useState(false);
  const heading = useRef(null);
  const chapterNav = useRef(null);
  const current = chapters[chapter];

  useEffect(() => {
    const controller = new AbortController();
    fetch('/research.json', { signal: controller.signal }).then(r => { if (!r.ok) throw new Error(); return r.json(); }).then(data => setResearch(validateResearch(data))).catch(e => { if (e.name !== 'AbortError') setError('Research could not be loaded. Please refresh to try again.'); });
    fetch('/benchmark.json', { signal: controller.signal }).then(r => { if (!r.ok) throw new Error(); return r.json(); }).then(data => setBenchmark(validateBenchmark(data))).catch(e => { if (e.name !== 'AbortError') setError('Benchmark results could not be loaded. Please refresh to try again.'); });
    const hash = () => setChapter(indexFromHash());
    const full = () => setPresenting(Boolean(document.fullscreenElement));
    window.addEventListener('hashchange', hash);
    document.addEventListener('fullscreenchange', full);
    return () => { controller.abort(); window.removeEventListener('hashchange', hash); document.removeEventListener('fullscreenchange', full); };
  }, []);

  useEffect(() => {
    const nav = chapterNav.current;
    const active = nav?.querySelector('[aria-current="step"]');
    if (active && nav.scrollWidth > nav.clientWidth) {
      nav.scrollLeft += active.getBoundingClientRect().left - nav.getBoundingClientRect().left - 10;
    }
  }, [chapter]);

  function navigate(index) {
    const next = Math.min(chapters.length - 1, Math.max(0, index));
    if (next === chapter) return;
    window.location.hash = chapters[next].id;
    setChapter(next);
    window.scrollTo({ top: 0 });
    requestAnimationFrame(() => heading.current?.focus({ preventScroll: true }));
  }
  useEffect(() => {
    const onKey = e => {
      if (/INPUT|TEXTAREA|SELECT|BUTTON|A/.test(e.target.tagName) || e.altKey || e.ctrlKey || e.metaKey) return;
      if (e.key === 'ArrowRight' || e.key === 'PageDown') { e.preventDefault(); navigate(chapter + 1); }
      if (e.key === 'ArrowLeft' || e.key === 'PageUp') { e.preventDefault(); navigate(chapter - 1); }
      if (e.key === 'Home') { e.preventDefault(); navigate(0); }
      if (e.key === 'End') { e.preventDefault(); navigate(chapters.length - 1); }
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [chapter]);

  async function togglePresentation() {
    try {
      if (document.fullscreenElement) await document.exitFullscreen();
      else if (document.documentElement.requestFullscreen) await document.documentElement.requestFullscreen();
      else { setPresenting(!presenting); setMessage('Focus view enabled. Use the exit button to return.'); }
    } catch { setPresenting(!presenting); setMessage('Full screen is unavailable. Focus view is enabled instead.'); }
  }

  const ready = research.status === 'ready';
  return <div className={`app ${presenting ? 'presenting' : ''}`}>
    <a href="#main" className="skip-link">Skip to presentation</a>
    <header className="topbar"><a className="brand" href="#question" onClick={() => navigate(0)} aria-label="Presentation home">When and When Not to Jev</a><div className="header-actions"><a className="present-button repo-link" href="https://github.com/abelbirosh/arize_takehome" target="_blank" rel="noreferrer"><Icon name="github"/>Github Repo</a><button className="present-button" onClick={togglePresentation}><Icon name={presenting ? 'close' : 'expand'}/>{presenting ? 'Exit presentation' : 'Present'}</button></div></header>
    <div className="workspace">
      <aside className="sidebar"><nav ref={chapterNav} aria-label="Presentation chapters">{chapters.map((item, i) => <a key={item.id} href={`#${item.id}`} onClick={e => { e.preventDefault(); navigate(i); }} aria-current={chapter === i ? 'step' : undefined}><span className="chapter-number">{String(i + 1).padStart(2, '0')}</span><span>{item.name}</span>{chapter === i && <Icon name="arrow"/>}</a>)}</nav></aside>
      <main id="main" className={`main chapter-${current.id}`}>
        {(message || error) && <div className={`notice ${error ? 'error' : ''}`} role={error ? 'alert' : 'status'}><span>{error || message}</span><button aria-label="Dismiss message" onClick={() => { setMessage(''); setError(''); }}><Icon name="close"/></button></div>}
        <div className="chapter-content" key={current.id}>
          {chapter === 0 ? <>
            <div className="cover-grid"><div className="cover-copy"><h1 ref={heading} tabIndex="-1">Empirical analysis of usage of decision model for agent design</h1><h2 className="question-followup">{current.title}</h2></div></div>
            {benchmark && <BenchmarkCharts benchmark={benchmark}/>}
          </> : <>
            <h1 className="chapter-title" ref={heading} tabIndex="-1">{current.title}</h1>
            {current.id === 'methodology' && <>
              <p className="intro wide">How the benchmark was set up: what changes between runs, what stays fixed, and how each run is graded.</p>
              <ResearchNotes items={research.methodology} emptyTitle="The methodology is on its way."/>
              <ReferenceLinks links={research.thesis.links}/>
            </>}
            {current.id === 'detailed-results' && <>
              <p className="intro wide">{research.results.length ? 'The measured outcomes of the controller comparison, with supporting evidence.' : 'The study compares answer quality, evidence support, cost, and active latency. Final measured results have not been added to this presentation yet.'}</p>
              <ResearchNotes items={research.results} emptyTitle="Results are being analyzed."/>
            </>}
            {current.id === 'phoenix' && <>
              <p className="intro wide">How Phoenix helped organize the experiments, trace the research agent, and evaluate the outcomes.</p>
              <ResearchNotes items={research.phoenix} emptyTitle="The Phoenix walkthrough is on its way."/>
              {research.sources.length > 0 && <section className="supporting-sources"><h2>Further reading & notes</h2><ReferenceLinks links={research.sources}/></section>}
            </>}
            {current.id === 'challenges' && <>
              <p className="intro wide">The problems that surfaced during the experiment, and the changes made to resolve them.</p>
              <ResearchNotes items={research.challenges} challenges emptyTitle="Challenges and solutions are on their way."/>
            </>}
            {current.id === 'takeaways' && <>
              <p className="intro wide">{ready ? 'The practical recommendations from the research, with the supporting evidence attached.' : 'Working takeaways from the implementation. Performance recommendations await the full-run analysis.'}</p>
              <ResearchNotes items={research.takeaways} emptyTitle="Takeaways are on their way."/>
            </>}

          </>}
        </div>

      </main>
    </div>
  </div>;
}
createRoot(document.getElementById('root')).render(<App/>);
