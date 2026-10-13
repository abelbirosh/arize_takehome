# Presentation

React + Vite, deployed on Vercel from `main` ([arizetakehome.vercel.app](https://arizetakehome.vercel.app)). Run from the repository root on Node 22.12+ (`nvm use`):

```sh
npm install
npm run dev              # http://127.0.0.1:5173
npm run build            # -> frontend/dist
npm run test:frontend    # validates both content files
```

Vercel uses the repository root and the checked-in `vercel.json`. The frontend needs no Python and no API keys.

## Content

Both files in `frontend/public/` are loaded at runtime and validated by `src/research.js`:

| File | Feeds | How to change it |
|---|---|---|
| `benchmark.json` | Question-page charts, Methodology (counts, tiers, test list) and the Detailed results table | Generated from `data/benchmark_v2.jsonl` and `results/full-v2-merged.jsonl`: `python3 scripts/export_frontend_metrics.py`. Edit the script to change labels, tier descriptions or exclusions. |
| `research.json` | The problem/fix list and takeaways | Edit by hand. Entries are `{ "title", "body", "links": [{ "title", "url" }] }`; problem/fix entries are `{ "challenge", "solution", "links" }`. |

Text renders as plain text, and links must be http(s).

## Navigation

The chapter index, the arrow keys, Page Up/Down and Home/End all change chapters. Each chapter has its own path (for example `/detailed-results`), so links and browser back and forward work; old `#chapter` links redirect to the path.
