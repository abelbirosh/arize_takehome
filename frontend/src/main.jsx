import React, { useEffect, useRef, useState } from 'react';
import { createRoot } from 'react-dom/client';
import './styles.css';
import { emptyResearch, validateResearch } from './research.js';

const chapters = [
  { id: 'question', name: 'Question', title: 'When should I use a system one model, and how?' },
  { id: 'results', name: 'Results', title: 'Results' },
  { id: 'phoenix', name: 'How I used Phoenix?', title: 'How I used Phoenix?' },
  { id: 'challenges', name: 'What went wrong and how we fixed it?', title: 'What went wrong and how we fixed it?' },
  { id: 'takeaways', name: 'Takeaways', title: 'Takeaways' },
];
const legacyHashes = { 'when-to-jev': 'question', mechanism: 'question', experiment: 'question', findings: 'results', learnings: 'phoenix', practice: 'takeaways', sources: 'phoenix' };
const indexFromHash = () => {
  const hash = window.location.hash.slice(1);
  return Math.max(0, chapters.findIndex(c => c.id === (legacyHashes[hash] || hash)));
};

function Icon({ name, ...props }) {
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

function Thesis({ thesis }) {
  return <>
    <p className="intro wide">{thesis.body || 'The thesis and study design will appear here when research is loaded.'}</p>
    <div className="thesis-grid"><div><h2>Why test this?</h2><p className="thesis-copy">{thesis.why || 'The motivation for the experiment is pending.'}</p><h2 className="thesis-subheading">What the experiment changes</h2><p className="thesis-copy">{thesis.method || 'The experiment design is pending.'}</p><ReferenceLinks links={thesis.links}/></div></div>
    <p className="study-note">These are the conditions being tested, not a measured recommendation.</p>
    <div className="when-grid"><section><h2>When Jev is worth testing</h2><ul>{thesis.when.map((text, i) => <li key={i}>{text}</li>)}</ul></section><section><h2>When to use another approach</h2><ul>{thesis.whenNot.map((text, i) => <li key={i}>{text}</li>)}</ul></section></div>
  </>;
}

function App() {
  const [chapter, setChapter] = useState(indexFromHash);
  const [research, setResearch] = useState(emptyResearch);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [presenting, setPresenting] = useState(false);
  const [loading, setLoading] = useState(true);
  const heading = useRef(null);
  const chapterNav = useRef(null);
  const current = chapters[chapter];

  useEffect(() => {
    const controller = new AbortController();
    fetch('/research.json', { signal: controller.signal }).then(r => { if (!r.ok) throw new Error(); return r.json(); }).then(data => setResearch(validateResearch(data))).catch(e => { if (e.name !== 'AbortError') setError('Research could not be loaded. Please refresh to try again.'); }).finally(() => setLoading(false));
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
  const researchNote = loading ? 'Loading presentation content.' : ready ? 'Research and attached links are available.' : research.learnings.length ? 'Implementation learnings are loaded.\nFinal analysis is pending.' : 'The question is set.\nResearch content is pending.';
  return <div className={`app ${presenting ? 'presenting' : ''}`}>
    <a href="#main" className="skip-link">Skip to presentation</a>
    <header className="topbar"><a className="brand" href="#question" onClick={() => navigate(0)} aria-label="Presentation home">When and When Not to Jev</a><div className="header-actions"><button className="present-button" onClick={togglePresentation}><Icon name={presenting ? 'close' : 'expand'}/>{presenting ? 'Exit presentation' : 'Present'}</button></div></header>
    <div className="workspace">
      <aside className="sidebar"><nav ref={chapterNav} aria-label="Presentation chapters">{chapters.map((item, i) => <a key={item.id} href={`#${item.id}`} onClick={e => { e.preventDefault(); navigate(i); }} aria-current={chapter === i ? 'step' : undefined}><span className="chapter-number">{String(i + 1).padStart(2, '0')}</span><span>{item.name}</span>{chapter === i && <Icon name="arrow"/>}</a>)}</nav><div className="sidebar-note"><span className={`status-label ${ready ? 'ready' : ''}`}><span/>{loading ? 'Loading research' : ready ? 'Research loaded' : 'Research in progress'}</span><p>{researchNote}</p></div></aside>
      <main id="main" className={`main chapter-${current.id}`}>
        {(message || error) && <div className={`notice ${error ? 'error' : ''}`} role={error ? 'alert' : 'status'}><span>{error || message}</span><button aria-label="Dismiss message" onClick={() => { setMessage(''); setError(''); }}><Icon name="close"/></button></div>}
        <div className="chapter-meta"><span>{String(chapter + 1).padStart(2, '0')} <span className="meta-slash">/</span> {String(chapters.length).padStart(2, '0')}</span></div>
        <div className="chapter-content" key={current.id}>
          {chapter === 0 ? <>
            <div className="cover-grid"><div className="cover-copy"><h1 ref={heading} tabIndex="-1">When should I use a <em>system one</em> model, and how?</h1><p className="intro">Testing how much model a research agent needs to decide what happens next.</p><button className="primary-button" onClick={() => navigate(1)}>View the results<Icon name="arrow"/></button><p className="cover-note">Decision models · Claude deciders · Fixed baseline</p></div></div>
            <Thesis thesis={research.thesis}/>
            <div className="cover-bottom"><span className="question-mark">?</span><p>One question. Two parts.</p><div><strong>When</strong><span>Where does a decision model belong?</span></div><div><strong>How</strong><span>How do we put it to the test?</span></div></div>
          </> : <>
            <h1 className="chapter-title" ref={heading} tabIndex="-1">{current.title}</h1>
            {chapter === 1 && <>
              <p className="intro wide">{research.results.length ? 'The measured outcomes of the controller comparison, with supporting evidence.' : 'The study compares answer quality, evidence support, cost, and active latency. Final measured results have not been added to this presentation yet.'}</p>
              <ResearchNotes items={research.results} emptyTitle="Results are being analyzed."/>
              <ReferenceLinks links={research.thesis.links}/>
            </>}
            {chapter === 2 && <>
              <p className="intro wide">How Phoenix helped organize the experiments, trace the research agent, and evaluate the outcomes.</p>
              <ResearchNotes items={research.phoenix} emptyTitle="The Phoenix walkthrough is on its way."/>
              {research.sources.length > 0 && <section className="supporting-sources"><h2>Further reading & notes</h2><ReferenceLinks links={research.sources}/></section>}
            </>}
            {chapter === 3 && <>
              <p className="intro wide">The problems that surfaced during the experiment, and the changes made to resolve them.</p>
              <ResearchNotes items={research.challenges} challenges emptyTitle="Challenges and solutions are on their way."/>
            </>}
            {chapter === 4 && <>
              <p className="intro wide">{ready ? 'The practical recommendations from the research, with the supporting evidence attached.' : 'Working takeaways from the implementation. Performance recommendations await the full-run analysis.'}</p>
              <ResearchNotes items={research.takeaways} emptyTitle="Takeaways are on their way."/>
            </>}

          </>}
        </div>
        <footer className="chapter-footer"><span className="keyboard-hint"><kbd>←</kbd><kbd>→</kbd> to navigate</span><div className="pager"><button className="previous-button" onClick={() => navigate(chapter - 1)} disabled={chapter === 0} aria-label="Previous chapter"><Icon name="arrow"/></button>{chapter < chapters.length - 1 ? <button className="next-button" onClick={() => navigate(chapter + 1)}><span>{chapters[chapter + 1].name}</span><Icon name="arrow"/></button> : <button className="next-button" onClick={() => navigate(0)}><span>Back to the question</span><Icon name="arrow"/></button>}</div></footer>
      </main>
    </div>
  </div>;
}
createRoot(document.getElementById('root')).render(<App/>);
