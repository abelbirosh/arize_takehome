// A standalone page for the judge study, sent separately from the presentation.
// It shares the presentation's stylesheet but none of its content.
import React, { useEffect, useRef, useState } from 'react';
import { createRoot } from 'react-dom/client';
import './styles.css';
import './judges.css';

const BASE = '/judges';
const chapters = [
  { id: 'problem', name: 'Comparing different judge methods and human annotation', title: 'Comparing different judge methods and human annotation' },
  { id: 'annotator', name: 'Human data annotator', title: 'Human data annotator' },
];
const chapterPath = id => id === chapters[0].id ? BASE : `${BASE}/${id}`;
const indexFromPath = () => {
  const id = window.location.pathname.replace(/^\/judges(\.html)?\/?/, '').replace(/\/+$/, '');
  return Math.max(0, chapters.findIndex(c => c.id === id));
};

function Icon({ name }) {
  if (name === 'github') return <svg viewBox="0 0 24 24" width="18" height="18" fill="currentColor" aria-hidden="true"><path d="M12 .297a12 12 0 0 0-3.793 23.385c.6.111.82-.261.82-.577v-2.234c-3.338.726-4.043-1.416-4.043-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.09-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.835 2.809 1.305 3.493.998.108-.776.419-1.305.762-1.605-2.665-.305-5.467-1.334-5.467-5.931 0-1.31.469-2.381 1.236-3.221-.124-.303-.536-1.524.117-3.176 0 0 1.008-.322 3.301 1.23a11.52 11.52 0 0 1 6.006 0c2.291-1.552 3.297-1.23 3.297-1.23.655 1.652.243 2.873.119 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.216.694.825.576A12.001 12.001 0 0 0 12 .297Z"/></svg>;
  return <svg viewBox="0 0 24 24" width="18" height="18" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" aria-hidden="true"><path d="m6 6 12 12M6 18 18 6"/></svg>;
}

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

const judgeSample = [
  ['Correct', 'Supported', 6, 203], ['Correct', 'Unsupported', 3, 33],
  ['Hedged', 'Supported', 3, 25], ['Hedged', 'Unsupported', 3, 23],
  ['Incorrect', 'Supported', 3, 16], ['Incorrect', 'Unsupported', 3, 15],
  ['No answer', 'Not applicable', 2, 15], ['No answer', 'Unsupported', 1, 13],
  ['No answer', 'Supported', 1, 7],
];

function JudgeProblem() {
  return <>
    <section className="subsection"><h2>Problem</h2>
      <ul className="method-list">
        <li>Every accuracy number in this benchmark comes from one LLM judge: GPT-6.1 Sol at low reasoning effort, grading correctness against a gold answer and groundedness against the agent's own notes.</li>
        <li>If the judge is wrong, the decider ranking can be wrong too. Hedged answers are the clearest risk, because they count as wrong.</li>
      </ul>
    </section>
    <section className="subsection"><h2>Questions</h2>
      <ul className="method-list">
        <li>How often does the judge agree with a human grader?</li>
        <li>Does a stronger reasoning model judge better, and is it worth the cost?</li>
        <li>Can a decision model, the same kind of model that routed the agent, do the judging at a fraction of the cost?</li>
      </ul>
    </section>
    <section className="subsection"><h2>Approach</h2>
      <ul className="method-list">
        <li>I graded a blind sample of 25 runs by hand, one per question, with the hard cases taking 19 of the 25 slots.</li>
        <li>The same 25 runs go to reasoning-model judges (GPT-6.1 Sol at low and high effort, Claude Opus 5.5) and decision-model judges (Jev, Microsoft Decision 1, OpenAI GPT-6 Luna Decisions), all with the same label definitions.</li>
        <li>Each judge is scored by its agreement with the human labels, raw and as Cohen's κ, and by its cost and time per grade.</li>
      </ul>
    </section>
    <section className="subsection"><h2>Sample</h2>
      <div className="table-scroll"><table className="data-table">
        <thead><tr><th scope="col">Correctness</th><th scope="col">Grounded</th><th scope="col" className="num">Sampled</th><th scope="col" className="num">In 350 runs</th></tr></thead>
        <tbody>{judgeSample.map(([c, g, n, all]) => <tr key={c + g}><td>{c}</td><td>{g}</td><td className="num">{n}</td><td className="num">{all}</td></tr>)}</tbody>
      </table></div>
    </section>
  </>;
}

function Annotator() {
  const [open, setOpen] = useState(null);
  const Shot = shot => <figure className="phoenix-shot annotator-shot">
    <button className="shot-button" aria-label={`Enlarge: ${shot.alt}`} onClick={() => setOpen(shot)}><img src={shot.src} alt={shot.alt} loading="lazy"/></button>
  </figure>;
  return <>
    {open && <Lightbox shot={open} onClose={() => setOpen(null)}/>}
    <section className="subsection"><h2>Grading Interface</h2>
      <ul className="method-list">
        <li>I built a local grading page (<code>grader/</code>) so the human labels follow the same rubric as the judges.</li>
        <li>It is blind: the page never loads the judge's labels or the name of the decider.</li>
        <li>Each run shows the question, the gold answer and its accepted variants beside the agent's answer, then the research notes, with matches of the gold answer highlighted.</li>
        <li>Two label groups mirror the judges, correctness (correct, hedged, incorrect, no answer) and grounded (supported, unsupported, not applicable), and each label shows the judge's own definition.</li>
      </ul>
      {Shot({ src: '/annotator/grader-run.webp', alt: 'Grading page: the run list on the left, the gold answer beside the agent answer with matches highlighted, research notes, and correctness and grounded labels on the right' })}
    </section>
    <section className="subsection"><h2>Workflow</h2>
      <ul className="method-list">
        <li>Keys 1 to 4 pick correctness, 5 to 7 pick grounded, and Ctrl+Enter moves to the next run.</li>
        <li>A comment box records why, for every run where the call was close.</li>
        <li>Grades save in the browser as I click, and Download labels.csv exports them for scoring against the judges.</li>
      </ul>
      {Shot({ src: '/annotator/grader-comment.webp', alt: 'A graded run marked hedged and supported, with a comment explaining the call' })}
    </section>
  </>;
}

function App() {
  const [chapter, setChapter] = useState(indexFromPath);
  const heading = useRef(null);
  const current = chapters[chapter];

  useEffect(() => {
    const onPop = () => setChapter(indexFromPath());
    window.addEventListener('popstate', onPop);
    return () => window.removeEventListener('popstate', onPop);
  }, []);

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
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [chapter]);

  return <div className="app">
    <a href="#main" className="skip-link">Skip to content</a>
    <header className="topbar"><a className="brand" href={BASE} onClick={e => { e.preventDefault(); navigate(0); }} aria-label="Comparing Judges home">Comparing Judges</a><div className="header-actions"><a className="present-button repo-link" href="https://github.com/abelbirosh/arize_takehome" target="_blank" rel="noreferrer"><Icon name="github"/>Github Repo</a></div></header>
    <div className="workspace">
      <aside className="sidebar"><nav aria-label="Chapters">{chapters.map((item, i) => <a key={item.id} href={chapterPath(item.id)} onClick={e => { e.preventDefault(); navigate(i); }} aria-current={chapter === i ? 'step' : undefined}><span className="chapter-number">{String(i + 1).padStart(2, '0')}</span><span>{item.name}</span></a>)}</nav></aside>
      <main id="main" className={`main chapter-${current.id}`}>
        <div className="chapter-content" key={current.id}>
          <h1 className="chapter-title" ref={heading} tabIndex="-1">{current.title}</h1>
          {current.id === 'problem' && <JudgeProblem/>}
          {current.id === 'annotator' && <Annotator/>}
        </div>
      </main>
    </div>
  </div>;
}
createRoot(document.getElementById('root')).render(<App/>);
