// Collection queries and formatting shared by the pages.
import { getCollection, type CollectionEntry } from 'astro:content';

export type Pub = CollectionEntry<'publications'>;
export type Pres = CollectionEntry<'presentations'>;
export type Person = CollectionEntry<'people'>;

const byDateDesc = (a: { year: number; date?: Date }, b: { year: number; date?: Date }) =>
  b.year - a.year || (b.date?.getTime() ?? 0) - (a.date?.getTime() ?? 0);

export async function getPublications(): Promise<Pub[]> {
  const all = await getCollection('publications');
  return all.sort((a, b) => byDateDesc(a.data, b.data) || a.data.title.localeCompare(b.data.title));
}

export async function getPresentations(): Promise<Pres[]> {
  const all = await getCollection('presentations');
  return all.sort((a, b) => byDateDesc(a.data, b.data) || a.data.title.localeCompare(b.data.title));
}

export async function getPeople() {
  const all = await getCollection('people');
  const sort = (a: Person, b: Person) => a.data.order - b.data.order || a.data.name.localeCompare(b.data.name);
  const current = all.filter((p) => p.data.status === 'current').sort(sort);
  // Alumni: most recent departures first.
  const alumni = all
    .filter((p) => p.data.status === 'alumni')
    .sort((a, b) => (b.data.end ?? '').localeCompare(a.data.end ?? '') || sort(a, b));
  return { all, current, alumni, byId: new Map(all.map((p) => [p.id, p])) };
}

export async function getThemes() {
  return (await getCollection('themes')).sort(
    (a, b) => a.data.order - b.data.order || a.data.title.localeCompare(b.data.title),
  );
}

export async function getNews() {
  return (await getCollection('news')).sort((a, b) => b.data.date.getTime() - a.data.date.getTime());
}

export async function getResources() {
  return (await getCollection('resources')).sort((a, b) => b.data.date.getTime() - a.data.date.getTime());
}

/** Group items by year, newest year first, keeping the incoming order inside each year. */
export function groupByYear<T extends { data: { year: number } }>(items: T[]): [number, T[]][] {
  const map = new Map<number, T[]>();
  for (const it of items) {
    const list = map.get(it.data.year) ?? [];
    list.push(it);
    map.set(it.data.year, list);
  }
  return [...map.entries()].sort((a, b) => b[0] - a[0]);
}

/** Normalize an author string for matching: "Ding X*" -> "ding x". */
export const normName = (s: string) => s.replace(/[*†‡#]/g, '').replace(/\s+/g, ' ').trim().toLowerCase();

/** Split an author list into parts, flagging the ones that are lab members of this entry. */
export function markAuthors(authors: string[], labIds: string[], byId: Map<string, Person>) {
  const names = new Set<string>();
  for (const id of labIds) for (const n of byId.get(id)?.data.citation_names ?? []) names.add(normName(n));
  return authors.map((a) => ({ name: a, lab: names.has(normName(a)) }));
}

const UTC = { timeZone: 'UTC' } as const;
export const fmtDate = (d: Date) =>
  d.toLocaleDateString('en-US', { ...UTC, year: 'numeric', month: 'long', day: 'numeric' });
export const fmtMonth = (d: Date) => d.toLocaleDateString('en-US', { ...UTC, year: 'numeric', month: 'short' });
export const isoDate = (d: Date) => d.toISOString().slice(0, 10);

/** "2018-01" + "2021-06" -> "2018–2021"; current: "Since 2022". */
export function years(start?: string, end?: string, current = false) {
  const s = start?.slice(0, 4);
  const e = end?.slice(0, 4);
  if (current) return s ? `Since ${s}` : '';
  if (s && e) return s === e ? s : `${s}–${e}`;
  return s ?? e ?? '';
}

export const typeLabel = { journal: 'Journal article', chapter: 'Chapter', preprint: 'Preprint' } as const;
export const typePlural = { journal: 'Journal', chapter: 'Chapters', preprint: 'Preprints' } as const;

/** Venue line: "Journal of Neuroscience 44(3):e123" or chapter "In: Eds, Book. Publisher, pp. x". */
export function venueDetail(d: Pub['data']) {
  let vol = '';
  if (d.volume) vol += d.volume;
  if (d.issue) vol += `(${d.issue})`;
  if (d.pages) vol += vol ? `:${d.pages}` : d.type === 'chapter' ? `pp. ${d.pages}` : d.pages;
  return vol;
}

// ---------- BibTeX (built at build time) ----------
const texEscape = (s: string) => s.replace(/([&%$#_])/g, '\\$1');

/** "Fox AS" -> "Fox, A. S."; leaves anything that does not look like "Surname INITIALS" in braces. */
function bibName(raw: string) {
  const s = raw.replace(/[*†‡#]/g, '').trim();
  const m = s.match(/^(.+?)\s+([A-Z]{1,4})$/);
  if (!m) return `{${s}}`;
  return `${m[1]}, ${m[2].split('').map((c) => c + '.').join(' ')}`;
}

export function bibtex(p: Pub) {
  const d = p.data;
  const key = p.id.replace(/[^A-Za-z0-9_-]/g, '');
  const kind = d.type === 'journal' ? 'article' : d.type === 'chapter' ? 'incollection' : 'misc';
  const f: [string, string | undefined][] = [
    ['title', `{${texEscape(d.title)}}`],
    ['author', d.authors.map(bibName).join(' and ')],
    ['year', String(d.year)],
  ];
  if (d.type === 'journal') f.push(['journal', texEscape(d.venue)]);
  if (d.type === 'chapter') {
    f.push(['booktitle', texEscape(d.venue)]);
    if (d.editors) f.push(['editor', texEscape(d.editors)]);
    if (d.publisher) f.push(['publisher', texEscape(d.publisher)]);
  }
  if (d.type === 'preprint') {
    f.push(['howpublished', texEscape(d.venue)]);
    f.push(['note', 'Preprint']);
  }
  f.push(['volume', d.volume], ['number', d.issue], ['pages', d.pages?.replace(/-/g, '--')]);
  if (d.doi) f.push(['doi', d.doi]);
  if (d.url && !d.doi) f.push(['url', d.url]);
  if (d.pmid) f.push(['pmid', d.pmid]);
  const body = f
    .filter(([, v]) => v)
    .map(([k, v]) => `  ${k} = {${v}}`)
    .join(',\n');
  return `@${kind}{${key},\n${body}\n}`;
}

/** Resolve a PDF path: absolute URLs and site paths pass through. */
export const pdfHref = (pdf: string) => (/^(https?:)?\//.test(pdf) ? pdf : `/${pdf.replace(/^\.?\//, '')}`);

/** "Society for Neuroscience" -> "society-for-neuroscience" (filter key). */
export const meetingKey = (m: string) =>
  m
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-|-$/g, '');

/** A filter facet for ListFilter: chips for each option, with counts. */
export interface Facet {
  name: string; // query key and entry data attribute, e.g. "type"
  label: string;
  options: { value: string; label: string; count: number }[];
}
