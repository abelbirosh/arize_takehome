import { defineConfig } from 'vite';
import { fileURLToPath } from 'node:url';

const page = name => fileURLToPath(new URL(`frontend/${name}.html`, import.meta.url));
// /judges and its chapters serve the judge study page, as vercel.json rewrites them.
const judgesRoute = {
  name: 'judges-route',
  configureServer(server) {
    server.middlewares.use((req, _res, next) => {
      if (/^\/judges(\/[\w-]*)?\/?(\?.*)?$/.test(req.url)) req.url = '/judges.html';
      next();
    });
  },
};
// Two pages: the presentation (index) and the judge study (judges), sent separately.
export default defineConfig({
  root: 'frontend',
  plugins: [judgesRoute],
  build: { outDir: 'dist', rollupOptions: { input: { index: page('index'), judges: page('judges') } } },
});
