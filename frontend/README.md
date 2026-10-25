# Presentation

React + Vite, deployed on Vercel from `main` ([abel-arizetakehome.vercel.app](https://abel-arizetakehome.vercel.app)). Run from the repository root on Node 22.12+ (`nvm use`):

```sh
npm install
npm run dev              # http://127.0.0.1:5173
npm run build            # -> frontend/dist
npm run test:frontend    # validates both content files
```

Vercel uses the repository root and the checked-in `vercel.json`. The frontend needs no Python and no API keys.

## Content

Two files in `frontend/public/` are loaded at runtime and validated by `src/data.js`:

| File | Feeds | How to change it |
|---|---|---|
| `benchmark.json` | Question-page charts, Methodology (counts, tiers, test list) and the Detailed results table | Generated from `data/benchmark_v2.jsonl` and `results/full-v2-merged.jsonl`: `python3 scripts/export_frontend_metrics.py`. Edit the script to change labels, tier descriptions or exclusions. |
| `fixes.json` | What went wrong and how I fixed it? | Edit by hand. Each entry is `{ "problem", "fix", "links": [{ "title", "url" }] }`. |

Text renders as plain text, and links must be http(s). The prose for the Question, Methodology, Phoenix and Takeaways sections lives in `src/main.jsx`, and the Phoenix screenshots in `public/phoenix/`.

## Judge study page

`judges.html` (`src/judges.jsx`) is a separate page at `/judges`, sent on its own: the judge comparison and human annotation study. It shares `styles.css` with the presentation but none of its content; its screenshots are in `public/annotator/`. Its comparison chapter reads `public/judges.json`, written by `scripts/compare_judges.py`. `vercel.json` and `vite.config.js` route `/judges` and its chapters to it.

## Navigation

The chapter index, the arrow keys, Page Up/Down and Home/End all change chapters. Each chapter has its own path (for example `/detailed-results`), so links and browser back and forward work; `vercel.json` rewrites every path to the app.
