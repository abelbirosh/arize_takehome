import React, { useEffect, useRef, useState } from 'react';
import { createRoot } from 'react-dom/client';
import '@fontsource/dm-sans/400.css';
import '@fontsource/dm-sans/500.css';
import '@fontsource/dm-sans/600.css';
import '@fontsource/instrument-serif/400.css';
import '@fontsource/instrument-serif/400-italic.css';
import './styles.css';
import { emptyResearch, validateResearch } from './research.js';

const chapters = [
  { id: 'question', name: 'The question', title: 'When should I use a system one model, and how?' },
  { id: 'mechanism', name: 'The mechanism', title: 'Separate the decision from the generation.' },
  { id: 'experiment', name: 'The experiment', title: 'Change the controller. Compare the outcome.' },
  { id: 'findings', name: 'The findings', title: 'Let the evidence make the case.' },
  { id: 'practice', name: 'In practice', title: 'From results to a routing strategy.' },
  { id: 'sources', name: 'Sources & notes', title: 'Keep the evidence within reach.' },
];
const indexFromHash = () => Math.max(0, chapters.findIndex(c => c.id === window.location.hash.slice(1)));

function Icon({ name, ...props }) {
  const paths = { arrow: <><path d="M4 12h16M14 6l6 6-6 6"/></>, upload: <><path d="M12 16V3m-5 5 5-5 5 5M4 15v5h16v-5"/></>, expand: <path d="M9 3H3v6m12-6h6v6M3 15v6h6m12-6v6h-6"/>, close: <path d="m6 6 12 12M6 18 18 6"/>, download: <path d="M12 3v13m-5-5 5 5 5-5M4 17v4h16v-4"/>, check: <path d="m5 12 4 4L19 6"/> };
  return <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" {...props}>{paths[name] || paths.arrow}</svg>;
}

function RoutingDiagram({ detailed = false }) {
  const [active, setActive] = useState(0);
  const actions = ['Search', 'Read', 'Answer'];
  return <div className={`routing-diagram ${detailed ? 'detailed' : ''}`}>
    <div className="diagram-top"><span>Inside the research agent</span><span className="diagram-dot"/> </div>
    <div className="context-node"><span>Question + evidence</span><small>The current state</small></div>
    <div className="connector"/>
    <div className="decision-node"><svg viewBox="0 0 24 24" width="28" height="28" fill="none" stroke="currentColor" strokeWidth="1.5" aria-hidden="true"><path d="m14 2-9 12h7l-2 8 9-12h-7Z"/></svg><div><strong>System one</strong><span>Choose the next action</span></div><span className="node-tag">Jev</span></div>
    <div className="branches"><span/><span/><span/></div>
    <div className="action-choices" role="group" aria-label="Explore routing actions">{actions.map((action, i) => <button key={action} onClick={() => setActive(i)} aria-pressed={active === i} className={active === i ? 'selected' : ''}>{action}{active === i && <span className="choice-dot"/>}</button>)}</div>
    <div className="connector"/>
    <div className="generation-node"><span>Language model</span><small>{['Write a search query', 'Take notes from a source', 'Write the final answer'][active]}</small></div>
    <div className="diagram-caption"><svg className="loop-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true"><path d="M5 4v11h14m-4-4 4 4-4 4"/></svg> Decide → act → observe → repeat</div>
  </div>;
}

function EmptyEvidence({ title, children }) {
  return <div className="empty-evidence"><div className="empty-chart" aria-hidden="true"><span/><span/><span/><span/><i/></div><h2>{title}</h2><p>{children}</p><span className="status-label"><span/>Awaiting research</span></div>;
}

function App() {
  const [chapter, setChapter] = useState(indexFromHash);
  const [research, setResearch] = useState(emptyResearch);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [presenting, setPresenting] = useState(false);
  const [loading, setLoading] = useState(true);
  const [importing, setImporting] = useState(false);
  const [localImport, setLocalImport] = useState(false);
  const upload = useRef(null);
  const heading = useRef(null);
  const current = chapters[chapter];

  useEffect(() => {
    const controller = new AbortController();
    fetch('/research.json', { signal: controller.signal }).then(r => { if (!r.ok) throw new Error(); return r.json(); }).then(data => setResearch(validateResearch(data))).catch(e => { if (e.name !== 'AbortError') setError('Research could not be loaded. Retry by refreshing, or load a research file.'); }).finally(() => setLoading(false));
    const hash = () => setChapter(indexFromHash());
    const full = () => setPresenting(Boolean(document.fullscreenElement));
    window.addEventListener('hashchange', hash);
    document.addEventListener('fullscreenchange', full);
    return () => { controller.abort(); window.removeEventListener('hashchange', hash); document.removeEventListener('fullscreenchange', full); };
  }, []);

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
  async function loadFile(e) {
    const file = e.target.files?.[0];
    if (!file) return;
    setImporting(true); setError(''); setMessage('');
    try {
      if (file.size > 2_000_000) throw new Error('Choose a research JSON file smaller than 2 MB.');
      const parsed = validateResearch(JSON.parse(await file.text()));
      setResearch(parsed); setLocalImport(true);
      setMessage(`Loaded ${file.name} for this browser session. Publish the file as research.json to share it.`);
    } catch (err) { setError(err instanceof SyntaxError ? 'This file is not valid JSON. Check its formatting and try again.' : err.message); }
    finally { setImporting(false); e.target.value = ''; }
  }

  const ready = research.status === 'ready';
  return <div className={`app ${presenting ? 'presenting' : ''}`}>
    <a href="#main" className="skip-link">Skip to presentation</a>
    <header className="topbar"><a className="brand" href="#question" onClick={() => navigate(0)} aria-label="Research presentation home"><span className="brand-symbol"><span/><span/></span><span>System one<span className="brand-divider"> / </span><span className="brand-subtitle">A research presentation</span></span></a><div className="header-actions"><button className="text-button import-button" onClick={() => upload.current?.click()} disabled={importing || loading}><Icon name="upload"/>{importing ? 'Loading…' : 'Load research'}</button><button className="present-button" onClick={togglePresentation}><Icon name={presenting ? 'close' : 'expand'}/>{presenting ? 'Exit presentation' : 'Present'}</button><input ref={upload} type="file" accept=".json,application/json" onChange={loadFile} className="file-input" aria-label="Load a research JSON file"/></div></header>
    <div className="workspace">
      <aside className="sidebar"><nav aria-label="Presentation chapters">{chapters.map((item, i) => <a key={item.id} href={`#${item.id}`} onClick={e => { e.preventDefault(); navigate(i); }} aria-current={chapter === i ? 'step' : undefined}><span className="chapter-number">{String(i + 1).padStart(2, '0')}</span><span>{item.name}</span>{chapter === i && <Icon name="arrow"/>}</a>)}</nav><div className="sidebar-note"><span className={`status-label ${ready ? 'ready' : ''}`}><span/>{loading ? 'Loading research' : ready ? 'Research loaded' : 'Research in progress'}</span><p>{ready ? (localImport ? 'Loaded for this browser session.' : 'Findings and sources are available.') : 'The question is set.\nThe evidence comes next.'}</p></div></aside>
      <main id="main" className={`main chapter-${current.id}`}>
        {(message || error) && <div className={`notice ${error ? 'error' : ''}`} role={error ? 'alert' : 'status'}><span>{error || message}</span><button aria-label="Dismiss message" onClick={() => { setMessage(''); setError(''); }}><Icon name="close"/></button></div>}
        <div className="chapter-meta"><span>{String(chapter + 1).padStart(2, '0')} <span className="meta-slash">/</span> {String(chapters.length).padStart(2, '0')}</span></div>
        <div className="chapter-content" key={current.id}>
          {chapter === 0 ? <>
            <div className="cover-grid"><div className="cover-copy"><h1 ref={heading} tabIndex="-1">When should I use a <em>system one</em> model, and how?</h1><p className="intro">An investigation into the decisions inside an AI agent—and who should make them.</p><button className="primary-button" onClick={() => navigate(1)}>Explore the research<Icon name="arrow"/></button><p className="cover-note">Jev · LLM · Hybrid · Fixed routing</p></div><RoutingDiagram/></div>
            <div className="cover-bottom"><span className="question-mark">?</span><p>One question. Two parts.</p><div><strong>When</strong><span>Where does a decision model belong?</span></div><div><strong>How</strong><span>How do we put it to the test?</span></div></div>
          </> : <>
            <h1 className="chapter-title" ref={heading} tabIndex="-1">{current.title}</h1>
            {chapter === 1 && <div className="mechanism-grid"><div><p className="intro">In this agent, the controller picks an action. A language model writes the query, takes notes, and produces the answer.</p><div className="role-row"><span>Decision</span><div><h2>What happens next?</h2><p>Choose between searching Wikipedia, searching the web, reading a source, or answering.</p></div></div><div className="role-row"><span>Generation</span><div><h2>What should it say?</h2><p>Turn the chosen action into a search query, source notes, or a final response.</p></div></div><p className="annotation">This is the architecture under study. Whether it improves outcomes is the question for the benchmark.</p></div><RoutingDiagram detailed/></div>}
            {chapter === 2 && <><p className="intro wide">The planned comparison changes the routing strategy while keeping the research task and generation setup consistent within each model.</p><div className="table-scroll"><table><caption>Controllers in the benchmark plan</caption><thead><tr><th>Controller</th><th>Who decides?</th><th>What it tests</th></tr></thead><tbody><tr><th>Jev</th><td>System one model</td><td>Dedicated decision routing</td></tr><tr><th>LLM</th><td>The language model</td><td>The model routes itself</td></tr><tr><th>Hybrid</th><td>Jev, with LLM escalation</td><td>Confidence-based fallback</td></tr><tr><th>Fixed</th><td>A predefined sequence</td><td>A baseline without model routing</td></tr></tbody></table></div><div className="measurement-strip"><div><h2>Quality</h2><p>Answer correctness</p></div><div><h2>Cost</h2><p>Total and routing cost</p></div><div><h2>Time</h2><p>Wall time and routing latency</p></div></div><p className="annotation">Study design from the repository’s benchmark plan. Final methodology and run counts will be loaded with the research.</p></>}
            {chapter === 3 && (research.findings.length ? <div className="evidence-list">{research.findings.map((finding, i) => <article key={i}><h2>{finding.title}</h2><p>{finding.body}</p></article>)}</div> : <><p className="intro wide">Accuracy, cost, and latency will determine the tradeoff. No measured conclusions have been loaded yet.</p><EmptyEvidence title="A place for the results.">The comparison will appear here when the research is ready. Until then, there are no benchmark numbers to interpret.</EmptyEvidence></>)}
            {chapter === 4 && (research.recommendations.length ? <div className="evidence-list">{research.recommendations.map((item, i) => <article key={i}><h2>{item.title}</h2><p>{item.body}</p></article>)}</div> : <><p className="intro wide">The final recommendations should connect a use case to evidence—not just to a faster routing call.</p><div className="practice-questions">{[['When to use it', 'Which tasks benefit from a dedicated decision model?'], ['How to integrate it', 'What actions, state, and fallback rules does it need?'], ['How to evaluate it', 'Does the whole agent improve on quality, cost, or time?']].map(([title, body]) => <article key={title}><h2>{title}</h2><p>{body}</p><span>Recommendation pending</span></article>)}</div></>)}
            {chapter === 5 && <><p className="intro wide">Source material stays attached to the presentation. Research citations will appear here as they are supplied.</p><div className="source-list">{research.sources.map((source, i) => <a key={i} href={source.url} target="_blank" rel="noreferrer"><div><strong>{source.title}</strong><span>{new URL(source.url).hostname}</span></div><Icon name="arrow"/></a>)}<a href="https://github.com/abelbirosh/arize_takehome" target="_blank" rel="noreferrer"><div><strong>Research agent repository</strong><span>Implementation and project documentation</span></div><Icon name="arrow"/></a></div><div className="load-panel"><div><h2>Bring the research into view.</h2><p>Load findings, recommendations, and source links from a research file. Local imports are visible only in this browser session.</p></div><a className="outline-button" href="/research.json" download="research-template.json"><Icon name="download"/>Download template</a><button className="primary-button" onClick={() => upload.current?.click()} disabled={importing || loading}><Icon name="upload"/>Load research</button></div></>}
          </>}
        </div>
        <footer className="chapter-footer"><span className="keyboard-hint"><kbd>←</kbd><kbd>→</kbd> to navigate</span><div className="pager"><button className="previous-button" onClick={() => navigate(chapter - 1)} disabled={chapter === 0} aria-label="Previous chapter"><Icon name="arrow"/></button>{chapter < chapters.length - 1 ? <button className="next-button" onClick={() => navigate(chapter + 1)}><span>{chapters[chapter + 1].name}</span><Icon name="arrow"/></button> : <button className="next-button" onClick={() => navigate(0)}><span>Back to the question</span><Icon name="arrow"/></button>}</div></footer>
      </main>
    </div>
  </div>;
}
createRoot(document.getElementById('root')).render(<App/>);
