import React, { useEffect, useRef, useState } from 'react';
import { createRoot } from 'react-dom/client';
import './styles.css';
import { emptyResearch, validateBenchmark, validateResearch } from './research.js';

const chapters = [
  { id: 'question', name: 'Question', title: 'Can a decision model choose the next steps of a research agent as well as a reasoning model?' },
  { id: 'methodology', name: 'Methodology', title: 'Methodology' },
  { id: 'detailed-results', name: 'Detailed results', title: 'Detailed results' },
  { id: 'phoenix', name: 'How I used Phoenix?', title: 'How I used Phoenix?' },
  { id: 'challenges', name: 'What went wrong and how I fixed it?', title: 'What went wrong and how I fixed it?' },
  { id: 'takeaways', name: 'Takeaways', title: 'Takeaways' },
];
const legacyIds = { 'when-to-jev': 'question', mechanism: 'methodology', experiment: 'methodology', results: 'detailed-results', findings: 'detailed-results', learnings: 'phoenix', practice: 'takeaways', sources: 'phoenix' };
// Chapters live at clean paths (/methodology); the opening chapter is the root.
const chapterPath = id => id === 'question' ? '/' : `/${id}`;
const indexFromPath = () => {
  const id = window.location.pathname.replace(/^\/+|\/+$/g, '') || 'question';
  return Math.max(0, chapters.findIndex(c => c.id === (legacyIds[id] || id)));
};
// Old links used #chapter fragments; move them onto the matching path.
const redirectLegacyHash = () => {
  const hash = window.location.hash.slice(1);
  const index = chapters.findIndex(c => c.id === (legacyIds[hash] || hash));
  if (index >= 0) window.history.replaceState(null, '', chapterPath(chapters[index].id));
};
redirectLegacyHash();

function Icon({ name, ...props }) {
  if (name === 'github') return <svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor" aria-hidden="true" {...props}><path d="M12 .297a12 12 0 0 0-3.793 23.385c.6.111.82-.261.82-.577v-2.234c-3.338.726-4.043-1.416-4.043-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.09-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.835 2.809 1.305 3.493.998.108-.776.419-1.305.762-1.605-2.665-.305-5.467-1.334-5.467-5.931 0-1.31.469-2.381 1.236-3.221-.124-.303-.536-1.524.117-3.176 0 0 1.008-.322 3.301 1.23a11.52 11.52 0 0 1 6.006 0c2.291-1.552 3.297-1.23 3.297-1.23.655 1.652.243 2.873.119 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.216.694.825.576A12.001 12.001 0 0 0 12 .297Z"/></svg>;
  const paths = { arrow: <><path d="M4 12h16M14 6l6 6-6 6"/></>, close: <path d="m6 6 12 12M6 18 18 6"/> };
  return <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true" {...props}>{paths[name] || paths.arrow}</svg>;
}

const formatValue = (format, v) => ({
  percent: () => `${Math.round(v * 100)}%`,
  usd: () => v === 0 ? '$0' : `$${v < 0.01 ? v.toFixed(4) : v.toFixed(3)}`,
  cents: () => v === 0 ? '0¢' : `${(v * 100).toPrecision(2)}¢`,
  seconds: () => `${v.toFixed(1)} s`,
  decimal: () => v.toFixed(1),
  count: () => String(v),
  ms: () => `${Math.round(v).toLocaleString('en-US')} ms`,
})[format]();

const kindLabels = { decision: 'Decision model', reasoning: 'Claude model', fixed: 'Fixed sequence' };

function MetricChart({ metric, deciders }) {
  const excluded = metric.excluded || {};
  // Best on the left, worst on the right; ties keep the decider order.
  const ranked = deciders.filter(d => !(d.id in excluded))
    .sort((a, b) => metric.better === 'higher' ? metric.values[b.id] - metric.values[a.id] : metric.values[a.id] - metric.values[b.id]);
  const left = deciders.filter(d => d.id in excluded);
  const max = metric.max ?? (Math.max(...ranked.map(d => metric.values[d.id])) || 1);
  const notes = [...new Set(Object.values(excluded))];
  return <figure className="metric">
    <figcaption><h2>{metric.label}</h2></figcaption>
    <div className="bars" aria-hidden="true">
      {ranked.map(d => <div className={`bar-col kind-${d.kind} ${d.id === 'jev' ? 'is-jev' : ''}`} key={d.id}>
        <span className="bar-value">{formatValue(metric.format, metric.values[d.id])}</span>
        <span className="bar" style={{ height: `${metric.values[d.id] / max * 100}%` }}/>
        <span className="bar-name">{d.short}</span>
      </div>)}
      {left.map(d => <div className={`bar-col kind-${d.kind} is-excluded`} key={d.id}>
        <span className="bar-value">*</span>
        <span className="bar-name">{d.short}</span>
      </div>)}
    </div>
    {metric.scale && <div className="metric-scale" aria-hidden="true"><span>{metric.scale[0]}</span><span className="scale-arrow"/><span>{metric.scale[1]}</span></div>}
    <p className="metric-description">{metric.description}</p>
    {notes.map(note => <p className="metric-note" key={note}>* {note}</p>)}
    <div className="visually-hidden"><table><caption>{metric.label}, best to worst</caption><thead><tr><th scope="col">Decider</th><th scope="col">{metric.label}</th></tr></thead>
      <tbody>{ranked.map(d => <tr key={d.id}><th scope="row">{d.name}</th><td>{formatValue(metric.format, metric.values[d.id])}</td></tr>)}{left.map(d => <tr key={d.id}><th scope="row">{d.name}</th><td>Not plotted. {excluded[d.id]}</td></tr>)}</tbody></table></div>
  </figure>;
}

function BenchmarkCharts({ benchmark }) {
  const kinds = [...new Set(benchmark.deciders.map(d => d.kind))];
  return <section className="benchmark" aria-label="Benchmark results">
    <ul className="legend">{kinds.map(k => <li key={k}><span className={`swatch kind-${k}`}/>{kindLabels[k]}</li>)}</ul>
    <div className="metric-grid">{benchmark.metrics.map(m => <MetricChart key={m.id} metric={m} deciders={benchmark.deciders}/>)}</div>
  </section>;
}

const resultMarks = {
  correct: ['✓', 'Correct', 'Commits to the right answer, or rejects the false premise of an unanswerable question.'],
  hedged: ['~', 'Hedged', "Mentions the right answer but doesn't commit to it: lists other candidates or calls it unverified."],
  incorrect: ['✗', 'Incorrect', 'Commits to a wrong answer, or invents one for an unanswerable question.'],
  no_answer: ['–', 'No answer', "Says it couldn't determine the answer."],
};

const CODE = 'https://github.com/abelbirosh/arize_takehome/blob/b2982bc/src/research_agent/';
const tools = [
  { name: 'search_wikipedia', description: 'Haiku writes a query; the MediaWiki API returns the top 5 results.', file: 'tools.py', url: `${CODE}tools.py#L130-L155` },
  { name: 'search_web', description: 'Haiku writes a query; the TinyFish CLI returns the top 5 results.', file: 'tools.py', url: `${CODE}tools.py#L157-L183` },
  { name: 'read_source', description: 'Fetches one unread result, trims it to 15,000 characters, and Haiku extracts notes.', file: 'agent.py', url: `${CODE}agent.py#L130-L144` },
  { name: 'answer', description: 'Haiku writes the final answer from the notes.', file: 'llm.py', url: `${CODE}llm.py#L137-L154` },
];
const snapshotFields = ['The question', 'Step budget used and remaining', 'Searches already run', 'Notes so far', 'Sources already read', 'Up to 20 unread results, with title and snippet', 'Step history'];

function AgentLoop() {
  return <div className="loop-diagram" role="img" aria-label="Input, then a repeating decide, act, observe loop, then output">
    <div className="loop-node loop-io">Input</div>
    <span className="loop-arrow"/>
    <div className="loop-cycle">
      <div className="loop-node">Decide</div><span className="loop-arrow"/>
      <div className="loop-node">Act</div><span className="loop-arrow"/>
      <div className="loop-node">Observe</div>
      <span className="loop-return"/>
    </div>
    <span className="loop-arrow"/>
    <div className="loop-node loop-io">Output</div>
  </div>;
}

function Methodology({ benchmark }) {
  const { counts, tiers, tests, deciders } = benchmark;
  const tierName = Object.fromEntries(tiers.map(t => [t.id, t.name]));
  const modelColumns = ['decision', 'reasoning'].map(kind => deciders.filter(d => d.kind === kind));
  return <>
    <section className="subsection"><h2>Agent Loop</h2><AgentLoop/></section>
    <section className="subsection"><h2>Available Tools</h2>
      <ul className="tool-list">{tools.map(t => <li key={t.name}><code>{t.name}</code><span>{t.description}</span>
        <a className="commit-link" href={t.url} target="_blank" rel="noreferrer">{t.file}<Icon name="arrow"/></a></li>)}</ul>
    </section>
    <section className="subsection"><h2>State</h2>
      <p className="subsection-copy">The decider gets a structured snapshot containing:</p>
      <ul className="method-list">{snapshotFields.map(f => <li key={f}>{f}</li>)}</ul>
    </section>
    <section className="subsection"><h2>Models Used as Decider</h2>
      <div className="model-columns">{modelColumns.map((column, i) => <ul key={i}>{column.map(d => <li key={d.id}><span className={`swatch kind-${d.kind}`}/>{d.name}</li>)}</ul>)}</div>
    </section>
    <p className="method-note">Note: I used a 8 step budget for testing cost reasons and to observe if knowledge of pending steps altered run behavior. I also do not rerun failed searches and solely note that into agent memory.</p>
    <section className="subsection"><h2>Testing Harness Design</h2>
      <ul className="method-list">
        <li><code>prepare_dataset.py</code> creates 50 testing questions with a gold answer version and accepted variants, along with question nature flags. These are uploaded into <strong>Phoenix</strong> as a dataset.</li>
        <li><code>run_experiments.py</code> creates one <strong>Phoenix</strong> experiment per decider and runs the deciders in parallel. Each run has a 900 second timeout. The logs of each run are recorded in <code>results/&lt;tag&gt;.jsonl</code>.</li>
      </ul>
    </section>
    <section className="subsection"><h2>Evaluators</h2>
      <ul className="method-list">
        <li>LLM as a judge for correctness and groundedness.</li>
        <li>Code checks for routing fit along with telemetry metrics like total cost, routing cost, routing latency, steps, invalid decisions, and web use.</li>
      </ul>
    </section>
    <section className="subsection"><h2>Fairness Measures</h2>
      <ul className="method-list">
        <li>Claude Haiku is used for all writing across runs.</li>
        <li>Per model rate limiter to adhere to OpenRouter's limits. The time spent in queue waiting is subtracted before latency calculations.</li>
        <li>The costs for the generator and decider (even if it's the same model) are counted separately.</li>
      </ul>
    </section>
    <section className="subsection"><h2>Test Counts</h2>
      <p className="subsection-copy">{counts.questions} questions × {counts.deciders} deciders = {counts.runs} runs. Each decider answered every question once with an {counts.max_steps}-step budget: {counts.main} questions in the main run and {counts.pilot} in a pilot on the same code.</p>
    </section>
    <section className="subsection"><h2>Test Tiers</h2>
      <div className="table-scroll"><table className="data-table tier-table">
        <thead><tr><th scope="col">Tier</th><th scope="col" className="num">Tests</th><th scope="col">What it checks</th></tr></thead>
        <tbody>{tiers.map(t => <tr key={t.id}><th scope="row">{t.name}</th><td className="num">{t.count}</td><td>{t.description}</td></tr>)}</tbody>
      </table></div>
    </section>
    <section className="subsection"><h2>Test List</h2>
      <ol className="test-list">{tests.map(t => <li key={t.id}><details>
        <summary><span className="test-n">{t.n}</span><span className="test-q">{t.question}</span><span className="test-tier">{tierName[t.tier]}</span></summary>
        <dl><dt>Answer</dt><dd>{t.answer}</dd></dl>
      </details></li>)}</ol>
    </section>
  </>;
}

const traceTree = `research_agent              AGENT      run metadata: decider, generator model, step budget
  step.N <action>           CHAIN      one per step
    route.<decider>         CHAIN      chosen action, confidence, valid, escalated, latency
      jev.decide            DECISION   decision-model call
      ChatCompletion        LLM        Claude decider call (auto-instrumented)
    wikipedia/web.search    RETRIEVER  the returned results
    read_source             TOOL       page read
    ChatCompletion          LLM        Haiku writing a query, notes, or the answer`;

function Lightbox({ shot, onClose }) {
  const close = useRef(null);
  useEffect(() => {
    const previous = document.activeElement;
    close.current?.focus();
    const onKey = e => { if (e.key === 'Escape') onClose(); };
    window.addEventListener('keydown', onKey);
    document.body.style.overflow = 'hidden';
    return () => { window.removeEventListener('keydown', onKey); document.body.style.overflow = ''; previous?.focus?.(); };
  }, [onClose]);
  return <div className="lightbox" role="dialog" aria-modal="true" aria-label={shot.alt} onClick={onClose}>
    <button ref={close} className="lightbox-close" aria-label="Close image" onClick={onClose}><Icon name="close"/></button>
    <img src={shot.src} alt={shot.alt} onClick={e => e.stopPropagation()}/>
  </div>;
}

function PhoenixUsage() {
  const [open, setOpen] = useState(null);
  const Shot = shot => <figure className="phoenix-shot">
    <button className="shot-button" aria-label={`Enlarge: ${shot.alt}`} onClick={() => setOpen(shot)}><img src={shot.src} alt={shot.alt} loading="lazy"/></button>
    <figcaption>{shot.caption}</figcaption>
  </figure>;
  return <>
    {open && <Lightbox shot={open} onClose={() => setOpen(null)}/>}
    <section className="subsection"><h2>Tracing Each Run</h2>
      <ul className="method-list">
        <li>Connected to Phoenix with <code>phoenix.otel.register(auto_instrument=True)</code>. Every run produces one OpenInference trace:</li>
      </ul>
      <pre className="trace-tree">{traceTree}</pre>
      {Shot({ src: "/phoenix/trace-tree.webp", alt: "Phoenix trace view: span tree of a Jev run next to the run's output and stats", caption: "Jev run's trace with the recorded answer and run stats" })}
      <ul className="method-list">
        <li>Decision-model calls use OpenInference's <code>DECISION</code> span kind and record the chosen action, confidence, full probabilities, evidence-sufficient probability, read target, token counts, latency, and cost.</li>
        <li>A Claude decider's routing call appears as an LLM span inside the same <code>route.*</code> span, so all seven deciders share one trace layout.</li>
        <li>The root span carries the run's stats (steps, costs, latency, forced answer).</li>
        <li>Sorting traces according to the metrics using Phoenix.</li>
      </ul>
      {Shot({ src: "/phoenix/traces-sorted.png", alt: "Phoenix trace list sorted by cumulative tokens, showing latency and cost columns", caption: "Traces sorted by cumulative tokens, with each run's latency and cost." })}
    </section>
    <section className="subsection"><h2>Dataset Storage</h2>
      <ul className="method-list">
        <li>I uploaded each set of questions as a dataset. Initially, the system used a 25 question set, which was then increased to 50. Uploading datasets for each of these tests made the process functionally easier.</li>
        <li>Before running the full suite, I ran testing pilots to ensure it was functioning. Phoenix dataset splits were helpful for this.</li>
      </ul>
      {Shot({ src: "/phoenix/dataset-splits.webp", alt: "Phoenix dataset examples, each tagged with a pilot or main split", caption: "50 question dataset with split enabled" })}
    </section>
    <section className="subsection"><h2>Running Experiments</h2>
      <ul className="method-list">
        <li>I used Phoenix experiment runner to run one experiment per decider in parallel. The experiment metadata recorded the decider, generator model, budgets, and reasoning settings.</li>
        <li>Phoenix's experiment comparison view was helpful to visualize decider comparisons. I stored the run details to <code>results/&lt;tag&gt;.jsonl</code> for cross-project analysis.</li>
      </ul>
      {Shot({ src: "/phoenix/experiments.webp", alt: "Phoenix experiments page for research-bench-v2 with score, latency and cost charts", caption: "Score, latency, and cost charts for the 7 experiments" })}
    </section>
    <section className="subsection"><h2>Evaluators (Inside the Experiment)</h2>
      <ul className="method-list">
        <li>LLM evaluators, which used GPT-6.1 Sol, were used for correctness and groundedness.</li>
        <li>Code evaluators for routing fit and telemetry metrics.</li>
      </ul>
      {Shot({ src: "/phoenix/evaluator-scores.webp", alt: "Mean correctness, forced-answer and grounded scores per experiment", caption: "Mean evaluator scores per experiment." })}
    </section>
  </>;
}

function DetailedResults({ benchmark }) {
  const { tests, deciders } = benchmark;
  return <>
    <ul className="result-key">{Object.entries(resultMarks).map(([k, [mark, label, meaning]]) => <li key={k} tabIndex="0" aria-describedby={`meaning-${k}`}><span className={`mark-${k}`} aria-hidden="true">{mark}</span>{label}<span className="key-tip" role="tooltip" id={`meaning-${k}`}>{meaning}</span></li>)}</ul>
    <div className="table-scroll"><table className="data-table results-table">
      <thead><tr><th scope="col" className="num">#</th><th scope="col">Question</th>{deciders.map(d => <th scope="col" key={d.id} className="mark-col"><span className={`swatch kind-${d.kind}`}/>{d.short}</th>)}</tr></thead>
      <tbody>{tests.map(t => <tr key={t.id}>
        <td className="num">{t.n}</td><td className="q-cell" title={t.question}>{t.question}</td>
        {deciders.map(d => { const [mark, label, meaning] = resultMarks[t.results[d.id]]; return <td key={d.id} className={`mark-col mark-${t.results[d.id]}`} title={`${label}: ${meaning}`}><span aria-hidden="true">{mark}</span><span className="visually-hidden">{label}</span></td>; })}
      </tr>)}</tbody>
      <tfoot><tr><th scope="row" colSpan="2">Correct</th>{deciders.map(d => <td key={d.id} className="mark-col">{tests.filter(t => t.results[d.id] === 'correct').length}/{tests.length}</td>)}</tr></tfoot>
    </table></div>
  </>;
}

function FixList({ items }) {
  return <div className="table-scroll"><table className="data-table fix-table">
    <thead><tr><th scope="col">Problem</th><th scope="col">Fix</th><th scope="col">Code</th></tr></thead>
    <tbody>{items.map((item, i) => <tr key={i}><td>{item.challenge}</td><td>{item.solution}</td>
      <td>{item.links.map(link => <a key={link.url} className="commit-link" href={link.url} target="_blank" rel="noreferrer">{link.title}<Icon name="arrow"/></a>)}</td></tr>)}</tbody>
  </table></div>;
}

function App() {
  const [chapter, setChapter] = useState(indexFromPath);
  const [research, setResearch] = useState(emptyResearch);
  const [benchmark, setBenchmark] = useState(null);
  const [error, setError] = useState('');
  const heading = useRef(null);
  const chapterNav = useRef(null);
  const current = chapters[chapter];

  useEffect(() => {
    const controller = new AbortController();
    fetch('/research.json', { signal: controller.signal }).then(r => { if (!r.ok) throw new Error(); return r.json(); }).then(data => setResearch(validateResearch(data))).catch(e => { if (e.name !== 'AbortError') setError('Research could not be loaded. Please refresh to try again.'); });
    fetch('/benchmark.json', { signal: controller.signal }).then(r => { if (!r.ok) throw new Error(); return r.json(); }).then(data => setBenchmark(validateBenchmark(data))).catch(e => { if (e.name !== 'AbortError') setError('Benchmark results could not be loaded. Please refresh to try again.'); });
    const onPop = () => setChapter(indexFromPath());
    const onHash = () => { redirectLegacyHash(); setChapter(indexFromPath()); };
    window.addEventListener('popstate', onPop);
    window.addEventListener('hashchange', onHash);
    return () => { controller.abort(); window.removeEventListener('popstate', onPop); window.removeEventListener('hashchange', onHash); };
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
    window.history.pushState(null, '', chapterPath(chapters[next].id));
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


  return <div className="app">
    <a href="#main" className="skip-link">Skip to presentation</a>
    <header className="topbar"><a className="brand" href="/" onClick={e => { e.preventDefault(); navigate(0); }} aria-label="Presentation home">When and When Not to Jev</a><div className="header-actions"><a className="present-button repo-link" href="https://github.com/abelbirosh/arize_takehome" target="_blank" rel="noreferrer"><Icon name="github"/>Github Repo</a></div></header>
    <div className="workspace">
      <aside className="sidebar"><nav ref={chapterNav} aria-label="Presentation chapters">{chapters.map((item, i) => <a key={item.id} href={chapterPath(item.id)} onClick={e => { e.preventDefault(); navigate(i); }} aria-current={chapter === i ? 'step' : undefined}><span className="chapter-number">{String(i + 1).padStart(2, '0')}</span><span>{item.name}</span></a>)}</nav></aside>
      <main id="main" className={`main chapter-${current.id}`}>
        {error && <div className="notice error" role="alert"><span>{error}</span><button aria-label="Dismiss message" onClick={() => setError('')}><Icon name="close"/></button></div>}
        <div className="chapter-content" key={current.id}>
          {chapter === 0 ? <>
            <div className="cover-grid"><div className="cover-copy"><h1 ref={heading} tabIndex="-1">Empirical analysis of usage of decision model for agent design</h1><h2 className="question-followup">{current.title}</h2><p className="question-summary">In the controlled experiment I ran with 50 searches across seven models, I found that decision models achieved similar accuracy with a fraction of the cost and latency. The examples covered a range of task complexities and failure cases, such as searches for unavailable information.</p></div></div>
            {benchmark && <BenchmarkCharts benchmark={benchmark}/>}
          </> : <>
            <h1 className="chapter-title" ref={heading} tabIndex="-1">{current.title}</h1>
            {current.id === 'methodology' && benchmark && <Methodology benchmark={benchmark}/>}
            {current.id === 'detailed-results' && benchmark && <DetailedResults benchmark={benchmark}/>}
            {current.id === 'phoenix' && <PhoenixUsage/>}
            {current.id === 'challenges' && <FixList items={research.challenges}/>}

          </>}
        </div>

      </main>
    </div>
  </div>;
}
createRoot(document.getElementById('root')).render(<App/>);
