// Blind grading page for the judge-validation sample. Data comes from
// results/human_validation/grading.js (window.GRADING), written by
// scripts/sample_validation.py. Grades stay in this browser; Download writes labels.csv.
(() => {
  const data = window.GRADING;
  const $ = (id) => document.getElementById(id);
  const app = document.querySelector(".app");
  const NAMES = {
    correct: "Correct", hedged: "Hedged", incorrect: "Incorrect", no_answer: "No answer",
    supported: "Supported", unsupported: "Unsupported", not_applicable: "Not applicable",
  };
  const KEYS = { correctness: ["1", "2", "3", "4"], grounded: ["5", "6", "7"] };

  if (!data || !Array.isArray(data.rows)) {
    $("item").innerHTML = `<div class="error-box" role="alert"><p>Couldn't load the grading data.</p>
      <p>Write it with <code>uv run python scripts/sample_validation.py results/full-v2-merged.jsonl</code>,
      then reload this page.</p></div>`;
    $("progress-text").textContent = "No sample loaded";
    $("download").disabled = true;
    return;
  }

  const rows = data.rows;
  const storeKey = `judge-validation:${data.sample_id}`;
  let storageOk = true;
  let grades = {};
  try {
    grades = JSON.parse(localStorage.getItem(storeKey) || "{}") || {};
  } catch {
    storageOk = false;
  }
  try {
    localStorage.setItem(`${storeKey}:probe`, "1");
    localStorage.removeItem(`${storeKey}:probe`);
  } catch {
    storageOk = false;
  }
  $("storage-note").hidden = storageOk;

  let current = Math.max(0, rows.findIndex((r) => !isDone(r.n)));
  if (current === -1) current = 0;
  let filter = "all";
  let savedAt = null;

  function gradeOf(n) { return grades[n] || {}; }
  function isDone(n) { const g = gradeOf(n); return Boolean(g.correctness && g.grounded); }
  function isStarted(n) { const g = gradeOf(n); return Boolean(g.correctness || g.grounded || g.comment); }

  function save(n, patch) {
    grades[n] = { ...gradeOf(n), ...patch };
    savedAt = new Date();
    if (storageOk) {
      try { localStorage.setItem(storeKey, JSON.stringify(grades)); } catch { storageOk = false; $("storage-note").hidden = false; }
    }
    renderQueue();
    renderProgress();
    const stamp = $("saved");
    if (stamp) stamp.textContent = savedText();
  }

  function savedText() {
    if (!savedAt) return storageOk ? "Saved in this browser" : "Not saved: download to keep";
    const t = savedAt.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
    return storageOk ? `Saved in this browser at ${t}` : `Not saved: download to keep`;
  }

  const sentence = (s) => s.charAt(0).toUpperCase() + s.slice(1);
  const escapeHtml = (s) => String(s ?? "").replace(/[&<>"']/g, (c) => (
    { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
  const escapeRe = (s) => s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");

  // The gold answer and its accepted variants, lit wherever they appear.
  function highlighter(row) {
    const terms = [row.gold, ...String(row.accepted || "").split(";")]
      .map((t) => t.trim()).filter((t) => t.length >= 3 && t.split(" ").length <= 8);
    if (!terms.length) return escapeHtml;
    const re = new RegExp(`(${[...new Set(terms)].sort((a, b) => b.length - a.length).map((t) => escapeRe(escapeHtml(t))).join("|")})`, "gi");
    return (text) => escapeHtml(text).replace(re, "<mark>$1</mark>");
  }

  function parseNotes(text) {
    if (!text || text === "(no notes)") return [];
    const notes = [];
    for (const line of text.split("\n")) {
      const head = line.match(/^\[(.*)\]$/);
      if (head) notes.push({ title: head[1], lines: [] });
      else if (line.trim() && notes.length) notes[notes.length - 1].lines.push(line);
      else if (line.trim()) notes.push({ title: "", lines: [line] });
    }
    return notes;
  }

  function noteHtml(note, lit) {
    const bullets = note.lines.filter((l) => /^\s*[-•]\s+/.test(l));
    const body = bullets.length === note.lines.length
      ? `<ul>${bullets.map((l) => `<li>${lit(l.replace(/^\s*[-•]\s+/, ""))}</li>`).join("")}</ul>`
      : note.lines.map((l) => `<p>${lit(l.replace(/^\s*[-•]\s+/, ""))}</p>`).join("");
    return `<article class="note">${note.title ? `<h3>${lit(note.title)}</h3>` : ""}${body}</article>`;
  }

  function groupHtml(kind, legend) {
    const options = data.rubric[kind];
    const chosen = gradeOf(rows[current].n)[kind];
    const shown = options.find((o) => o.label === chosen) || null;
    return `<fieldset class="group" data-kind="${kind}">
      <legend>${legend}</legend>
      ${options.map((o, i) => `<label class="option" data-label="${o.label}" title="${escapeHtml(sentence(o.definition))}">
        <input type="radio" name="${kind}" value="${o.label}" ${o.label === chosen ? "checked" : ""}>
        <span class="radio" aria-hidden="true"></span>
        <span class="label">${NAMES[o.label] || o.label}</span>
        <span class="key" aria-hidden="true">${KEYS[kind][i]}</span>
      </label>`).join("")}
      <p class="definition" id="def-${kind}" aria-live="polite">${escapeHtml(shown ? sentence(shown.definition) : "")}</p>
    </fieldset>`;
  }

  function renderItem() {
    const row = rows[current];
    const lit = highlighter(row);
    const notes = parseNotes(row.notes);
    const g = gradeOf(row.n);
    const falsePremise = row.answerable === "no";
    $("item").innerHTML = `
      <div class="title-row">
        <button class="button back" type="button" id="back">All runs</button>
        <h1 tabindex="-1" id="title">${escapeHtml(row.question)}</h1>
        <div class="stepper">
          <button class="button" type="button" id="prev" ${current === 0 ? "disabled" : ""}>Previous</button>
          <span class="num">${row.n} of ${rows.length}</span>
          <button class="button" type="button" id="next" ${current === rows.length - 1 ? "disabled" : ""}>Next</button>
        </div>
      </div>
      <div class="reading">
        <div class="answers">
          <section class="card" aria-labelledby="gold-h">
            <div class="card-head"><h2 id="gold-h">Gold answer</h2>${falsePremise ? '<span class="pill warning">Not answerable as asked</span>' : ""}</div>
            <p class="answer-text">${lit(row.gold)}</p>
            <dl class="kv"><dt>Accepted</dt><dd>${escapeHtml(row.accepted || "—")}</dd></dl>
          </section>
          <section class="card" aria-labelledby="pred-h">
            <div class="card-head"><h2 id="pred-h">Agent's answer</h2></div>
            <p class="answer-text">${row.predicted ? lit(row.predicted) : '<span class="saved">Empty answer</span>'}</p>
          </section>
        </div>
        <section aria-labelledby="notes-h">
          <div class="section-head"><h2 id="notes-h">Research notes</h2><span class="meta num">${notes.length} ${notes.length === 1 ? "source" : "sources"}</span></div>
          ${notes.length ? `<div class="notes">${notes.map((n) => noteHtml(n, lit)).join("")}</div>`
            : '<p class="notes-empty">The agent collected no notes on this run.</p>'}
        </section>
      </div>
      <form class="grade" id="grade" aria-label="Your grades for run ${row.n}" onsubmit="return false">
        ${groupHtml("correctness", "Correctness")}
        ${groupHtml("grounded", "Grounded in the notes")}
        <div class="comment"><label for="comment">Comment</label>
          <textarea id="comment" placeholder="Optional: why, or what the judge might miss">${escapeHtml(g.comment || "")}</textarea></div>
        <div class="grade-foot"><span class="saved" id="saved">${savedText()}</span>
          <button class="button" type="button" id="next-todo">Next to grade</button></div>
      </form>`;
    wireItem();
    $("sheet").scrollTop = 0;
  }

  function wireItem() {
    const row = rows[current];
    $("prev").onclick = () => go(current - 1);
    $("next").onclick = () => go(current + 1);
    $("back").onclick = () => { app.dataset.view = "list"; };
    $("next-todo").onclick = nextTodo;
    for (const group of document.querySelectorAll(".group")) {
      const kind = group.dataset.kind;
      const def = $(`def-${kind}`);
      const defs = Object.fromEntries(data.rubric[kind].map((o) => [o.label, sentence(o.definition)]));
      const pinned = () => defs[gradeOf(row.n)[kind]] || "";
      group.addEventListener("change", (e) => { save(row.n, { [kind]: e.target.value }); def.textContent = pinned(); });
    }
    let timer;
    $("comment").addEventListener("input", (e) => {
      clearTimeout(timer);
      timer = setTimeout(() => save(row.n, { comment: e.target.value }), 300);
    });
    $("comment").addEventListener("blur", (e) => save(row.n, { comment: e.target.value }));
  }

  function go(i, focusTitle = false) {
    if (i < 0 || i >= rows.length) return;
    current = i;
    app.dataset.view = "item";
    renderItem();
    renderQueue();
    if (focusTitle) $("title").focus();
  }

  function nextTodo() {
    for (let k = 1; k <= rows.length; k++) {
      const i = (current + k) % rows.length;
      if (!isDone(rows[i].n)) return go(i, true);
    }
    go(Math.min(current + 1, rows.length - 1), true);
  }

  function renderQueue() {
    const list = $("queue-list");
    const visible = rows.map((r, i) => [r, i]).filter(([r]) => filter === "all" || !isDone(r.n));
    $("count-all").textContent = rows.length;
    $("count-todo").textContent = rows.filter((r) => !isDone(r.n)).length;
    if (!visible.length) {
      list.innerHTML = '<li class="queue-empty">Every run is graded. Download labels.csv to hand them in.</li>';
      return;
    }
    list.innerHTML = visible.map(([r, i]) => {
      const g = gradeOf(r.n);
      const done = isDone(r.n);
      const mark = done ? '<span class="pill done">Graded</span>'
        : isStarted(r.n) ? '<span class="pill half">Started</span>' : '<span class="dot" aria-label="Not graded"></span>';
      const sub = done ? `${NAMES[g.correctness]} · ${NAMES[g.grounded]}` : (r.predicted || "Empty answer");
      return `<li><button type="button" class="queue-row ${done ? "" : "todo"}" data-i="${i}" ${i === current ? 'aria-current="true"' : ""}>
        <span class="queue-n num">${r.n}</span><span class="queue-q">${escapeHtml(r.question)}</span>${mark}
        <span class="queue-sub">${escapeHtml(sub)}</span></button></li>`;
    }).join("");
    for (const b of list.querySelectorAll(".queue-row")) b.onclick = () => go(Number(b.dataset.i), true);
  }

  function renderProgress() {
    const done = rows.filter((r) => isDone(r.n)).length;
    $("progress-text").innerHTML = done === rows.length
      ? `<strong>All ${rows.length}</strong> graded`
      : `<strong>${done}</strong> of ${rows.length} graded`;
    $("progress-fill").style.width = `${(done / rows.length) * 100}%`;
  }

  function download() {
    const cells = (v) => `"${String(v ?? "").replace(/"/g, '""')}"`;
    const head = ["n", "question", "human_correctness", "human_grounded", "comment"];
    const lines = [head.join(",")].concat(rows.map((r) => {
      const g = gradeOf(r.n);
      return [r.n, r.question, g.correctness, g.grounded, g.comment].map(cells).join(",");
    }));
    const blob = new Blob(["﻿" + lines.join("\r\n") + "\r\n"], { type: "text/csv;charset=utf-8" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = "labels.csv";
    document.body.append(a);
    a.click();
    a.remove();
    setTimeout(() => URL.revokeObjectURL(a.href), 1000);
  }

  for (const tab of document.querySelectorAll(".tabs [role=tab]")) {
    tab.onclick = () => {
      filter = tab.dataset.filter;
      for (const t of document.querySelectorAll(".tabs [role=tab]")) t.setAttribute("aria-selected", String(t === tab));
      renderQueue();
    };
  }
  $("download").onclick = download;

  document.addEventListener("keydown", (e) => {
    // Ctrl+Enter (or Cmd+Enter) moves on from anywhere, the comment box included.
    if (e.key === "Enter" && (e.ctrlKey || e.metaKey)) {
      e.preventDefault();
      const comment = $("comment");
      if (comment) save(rows[current].n, { comment: comment.value });
      go(current + 1, true);
      return;
    }
    if (e.target.closest("textarea, input[type=text]") || e.metaKey || e.ctrlKey || e.altKey) return;
    if (e.key === "ArrowRight" || e.key === "j") { e.preventDefault(); go(current + 1); return; }
    if (e.key === "ArrowLeft" || e.key === "k") { e.preventDefault(); go(current - 1); return; }
    for (const [kind, keys] of Object.entries(KEYS)) {
      const i = keys.indexOf(e.key);
      if (i === -1) continue;
      const input = document.querySelectorAll(`input[name=${kind}]`)[i];
      if (input) { input.checked = true; input.dispatchEvent(new Event("change", { bubbles: true })); }
      e.preventDefault();
    }
  });

  renderItem();
  renderQueue();
  renderProgress();
})();
