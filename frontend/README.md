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
| `benchmark.json` | the charts on the Question page | Generated: `python3 scripts/export_frontend_metrics.py`. Edit the script to change labels, descriptions or exclusions. |
| `research.json` | Methodology, Detailed results, Phoenix, challenges and takeaways | Edit by hand. Each entry is `{ "title", "body", "links": [{ "title", "url" }] }`. Challenges use `challenge` and `solution` instead of `body`. |

Text renders as plain text, and links must be http(s).

## Navigation

The chapter index, the arrow keys, Page Up/Down and Home/End all change chapters. Each chapter has its own URL fragment, so browser back and forward work. **Present** opens full screen without the index.
