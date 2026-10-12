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

## Load the research

Edit `frontend/public/research.json` and rebuild to publish research for everyone. The interface's **Load research** button previews a JSON file locally for the current browser session; it does not upload or publish anything. Download template returns the hosted research file.

```json
{
  "version": 1,
  "status": "ready",
  "findings": [
    { "title": "Your measured finding", "body": "Evidence, scope, and limitations." }
  ],
  "recommendations": [
    { "title": "When to use it", "body": "Your evidence-backed recommendation." }
  ],
  "sources": [
    { "title": "Source title", "url": "https://example.com/research" }
  ]
}
```

Use `pending` while research is in progress. A `ready` file requires at least one finding. All three lists are required; each supports up to 100 entries. Sources accept only HTTP(S) URLs. Imports are capped at 2 MB. Content renders as plain text, not HTML. Pending sections never display fabricated benchmark values.

## Present

Choose a chapter in the index or use the bottom navigation. Left/right arrows and Page Up/Page Down change chapters when focus is on the presentation; Home/End jump to the first/last chapter. Chapter links use URL fragments and work with browser back/forward. **Present** enters full screen and hides the chapter index; Escape or **Exit presentation** returns. Browsers without full-screen support use a focus view.

The initial mechanism and experiment copy describes the repository implementation and provisional benchmark plan. Replace it as the final presentation structure develops; it is not a claim about measured results.
