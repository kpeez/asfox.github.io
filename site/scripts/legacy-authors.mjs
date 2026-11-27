// Writes src/data/legacy-authors.json: the slugs of the old Pelican author pages
// (/author/<slug>.html). The build turns each one into a redirect to /publications/.
// Run from site/:  node scripts/legacy-authors.mjs
import { readdirSync, writeFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';

const authorDir = fileURLToPath(new URL('../../author/', import.meta.url));
const out = fileURLToPath(new URL('../src/data/legacy-authors.json', import.meta.url));

const slugs = readdirSync(authorDir)
  .filter((f) => f.endsWith('.html'))
  .map((f) => f.slice(0, -'.html'.length))
  .sort();

writeFileSync(out, JSON.stringify(slugs, null, 0).replace(/","/g, '",\n"') + '\n');
console.log(`wrote ${slugs.length} author slugs to ${out}`);
