# System one research presentation

From the repository root:

Use Node 24 (`nvm use` with the checked-in `.nvmrc`); Vite requires Node 22.12 or newer.

```sh
npm install
npm run dev
npm run build
npm run test:frontend
```

Vercel: import this repository, use the repository root as the root directory, and keep the checked-in Vercel configuration. The build outputs `frontend/dist`. No Python runtime or API keys are required for this frontend.

## Update the research

Edit `frontend/public/research.json` and rebuild to publish research for everyone. The presentation reads this file automatically; there are no upload or research-download controls. All text uses Times New Roman, with size, regular/bold weight, and italics defining the hierarchy.

The presentation opens with the original question, followed by four sections:

- **When and When Not to Jev** — thesis, motivation, experiment, and conditions being tested.
- **Learnings** — observations with attached links.
- **Challenges & solutions** — explicit problem/solution pairs and evidence.
- **Takeaways** — working or final recommendations with supporting links.

```json
{
  "version": 2,
  "status": "pending",
  "thesis": {
    "body": "The hypothesis being tested.",
    "why": "Why this experiment matters.",
    "when": ["A condition under which Jev is worth testing."],
    "whenNot": ["A condition favoring another approach."],
    "method": "The experimental comparison and controls.",
    "links": [{ "title": "Study design", "url": "https://example.com/study" }]
  },
  "learnings": [{ "title": "A learning", "body": "What the evidence supports.", "links": [] }],
  "challenges": [{ "title": "A challenge", "challenge": "The problem.", "solution": "The fix.", "links": [] }],
  "takeaways": [{ "title": "A takeaway", "body": "A recommendation and its limits.", "links": [] }],
  "sources": []
}
```

Use `pending` while research is in progress, including when implementation learnings are available but a final performance analysis is not. A `ready` file requires at least one learning. All four sections and the sources list are required. Lists support up to 100 entries. Attached links are optional and accept only HTTP(S) URLs. Content renders as plain text. Version 1 files remain supported: findings become learnings and recommendations become takeaways.

The initial section content is grounded in pushed repository commit `440dc8f`, with commit-pinned links beside the observations. It describes implementation and the benchmark plan, not a completed performance comparison. Ongoing local research changes are not automatically published as presentation findings.

## Present

Choose a chapter in the index or use the bottom navigation. Left/right arrows and Page Up/Page Down change chapters when focus is on the presentation; Home/End jump to the first/last chapter. Chapter links use URL fragments and work with browser back/forward. **Present** enters full screen and hides the chapter index; Escape or **Exit presentation** returns. Browsers without full-screen support use a focus view.

Old chapter URLs remain compatible: mechanism/experiment open the thesis, findings/sources open learnings, and practice opens takeaways.
