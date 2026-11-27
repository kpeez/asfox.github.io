// Old foxlab.ucdavis.edu URLs and where they now live (keys are output file paths). GitHub Pages cannot send 301s, so each
// old path becomes a small static HTML page that refreshes to the new URL.
import { getCollection } from 'astro:content';
import authorSlugs from '../data/legacy-authors.json';

export async function legacyRedirects(): Promise<Map<string, string>> {
  const map = new Map<string, string>();
  const add = (from: string, to: string) => {
    // "/old.html" is emitted as is; an extensionless "/2013/03/20/slug" becomes "2013/03/20/slug/index.html".
    let path = from.trim().replace(/^\/+/, '').split(/[?#]/)[0];
    if (!path) throw new Error(`empty legacy path for ${to}`);
    if (!/\.html?$/.test(path)) path = path.replace(/\/*$/, '/index.html');
    const prev = map.get(path);
    if (prev && prev !== to) throw new Error(`legacy path "${from}" points to both ${prev} and ${to}`);
    map.set(path, to);
  };

  for (const p of await getCollection('publications')) for (const l of p.data.legacy) add(l, `/publications/#${p.id}`);
  for (const p of await getCollection('presentations')) for (const l of p.data.legacy) add(l, `/presentations/#${p.id}`);
  for (const p of await getCollection('people')) for (const l of p.data.legacy) add(l, `/people/${p.id}/`);
  for (const p of await getCollection('news')) for (const l of p.data.legacy) add(l, `/news/${p.id}/`);
  for (const p of await getCollection('resources')) for (const l of p.data.legacy) add(l, `/resources/${p.id}/`);
  for (const p of await getCollection('pages')) for (const l of p.data.legacy) add(l, `/${p.id}/`);

  // Old index pages.
  const fixed: Record<string, string> = {
    'category/cv.html': '/cv/',
    'category/news.html': '/news/',
    'category/people.html': '/people/',
    'category/posters.html': '/presentations/',
    'category/publications.html': '/publications/',
    'category/thoughts.html': '/resources/#essays',
    'category/tutorials.html': '/resources/#tutorials',
    'archives.html': '/publications/',
    'authors.html': '/people/',
    'categories.html': '/',
    'tags.html': '/',
  };
  for (const [from, to] of Object.entries(fixed)) if (!map.has(from)) add(from, to);
  // The 476 old author pages all go to the publications list.
  for (const slug of authorSlugs as string[]) add(`/author/${slug}.html`, '/publications/');
  return map;
}
