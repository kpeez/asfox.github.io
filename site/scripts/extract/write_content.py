#!/usr/bin/env python3
"""Write publications/presentations/people content + review.md from entries.json, doi-results.json, people_data.py."""
import datetime, json, os, re, sys, glob
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
import yaml
from PIL import Image, ImageOps
from people_data import P
from parse_entries import slugify, surname, title_word, ROOT   # re-runs parsing (deterministic) and refreshes entries.json
SITE = os.path.abspath(HERE + '/../..')
OUT_PUB, OUT_PRES, OUT_PEOPLE, OUT_IMG = (SITE + '/src/content/publications', SITE + '/src/content/presentations',
                                          SITE + '/src/content/people', SITE + '/src/assets/people')
for d in (OUT_PUB, OUT_PRES, OUT_PEOPLE, OUT_IMG): os.makedirs(d, exist_ok=True)
D = json.load(open(HERE + '/entries.json')); R = json.load(open(HERE + '/doi-results.json'))
LOG = [tuple(x) for x in D['log']]
REV = {k: [] for k in ('doi_miss', 'doi_disagree', 'dates', 'jan1', 'misc', 'ids')}

# ------------------------------------------------------------------ people citation names / lab authors
allauth = set()
for e in D['pubs'] + D['pres']: allauth.update(e['authors'])
cit = {}
for p in P:
    names = sorted({a for a in allauth if a.rstrip('*') in p['cites']}, key=lambda s: (s.endswith('*'), s))
    cit[p['id']] = names
base2id = {}
for p in P:
    for c in p['cites']: base2id[c] = p['id']
def lab_authors(authors):
    out = []
    for a in authors:
        i = base2id.get(a.rstrip('*'))
        if i and i not in out: out.append(i)
    return out

# ------------------------------------------------------------------ publications
CHAP_KW = {'The brain is organized to emote': 'brain-organized', 'Epilogue': 'epilogue', 'On the significance of implicit': 'implicit-communication',
           'The interplay of emotion': 'emotion-cognition', 'The psychological and neurobiological bases': 'dispositional-negativity',
           'Afterword: How are emotions integrated': 'afterword-choice', 'Afterword: When and in what ways': 'afterword-adaptive',
           'Afterword: How are emotions physically': 'afterword-physical-embodiment', 'Afterword: How are emotions embodied in the social': 'afterword-social-world',
           'Afterword: How and why': 'afterword-communication', 'Afterword: What is the role of conscious': 'afterword-awareness',
           'Afterword: How are emotions organized': 'afterword-brain', 'Afterword: What are the dimensions': 'afterword-individual-differences',
           'Afterword: How are emotions, mood': 'afterword-mood-temperament'}
from parse_entries import VENUE_ABBR
used = set()
def uniq(base, title):
    i = base
    if i in used: i = f'{base}-{title_word(title)}'
    n = 2
    while i in used: i = f'{base}-{title_word(title)}-{n}'; n += 1
    used.add(i); return i

def pub_id(e):
    sn = slugify(surname(e['authors'][0])) if not e['authors'][0].startswith('The PRIMatE') else 'primate-de'
    if e['type'] == 'chapter':
        if e['venue'].startswith('The Nature of Emotion'):
            kw = next(v for k, v in CHAP_KW.items() if e['title'].startswith(k))
            return uniq(f'{sn}-{e["year"]}-noe-{kw}', e['title'])
        kw = {'Insights': 'behavioral-inhibition', 'Selecting': 'selecting-anxiety', 'The Central': 'living-without-an-amygdala', 'Neural bases': 'emotion-regulation-handbook'}
        return uniq(f'{sn}-{e["year"]}-' + next(v for k, v in kw.items() if e['title'].startswith(k)), e['title'])
    return uniq(f'{sn}-{e["year"]}-{VENUE_ABBR[e["venue"]]}', e['title'])

def pick_date(e, who):
    ds = sorted(set(d for d in e['page_dates'] if int(d[:4]) == e['year']))
    bad = [d for d in e['page_dates'] if int(d[:4]) != e['year']]
    if bad and not ds:
        REV['dates'].append(f'`{who}`: year {e["year"]} (from the citation) but Pelican page date {", ".join(bad)}; **date omitted**.')
        return None
    if bad: REV['dates'].append(f'`{who}`: merged page(s) with date {", ".join(bad)} disagree with year {e["year"]}; used {ds[0]} from the agreeing page.')
    if ds[0].endswith('-01-01'): REV['jan1'].append(f'`{who}` ({ds[0]})')
    return datetime.date.fromisoformat(ds[0])

pubs = []
for e in D['pubs']:
    pid = pub_id(e); e['id'] = pid
    res = R[e['slugs'][0]]; acc = res['accepted']
    # DOI
    doi = None
    if acc:
        doi = acc['doi']
        if e.get('doi') and e['doi'].lower() != doi.lower():
            REV['misc'].append(f'`{pid}`: DOI printed in old citation ({e["doi"]}) differs from the Crossref match ({doi}); kept the printed DOI.'); doi = e['doi']
        if res['n_acceptable'] > 1: REV['misc'].append(f'`{pid}`: {res["n_acceptable"]} Crossref records passed the thresholds; picked {doi} (page-number match, then title score).')
    elif e.get('doi'):
        doi = e['doi']
    if not acc:
        REV['doi_miss'].append((pid, e, res))
    # ambiguity "V:N"
    if e.get('_ambiguous') and acc:
        n = e['_ambiguous']
        if acc['issue'] == n and (acc['page'] or '').split('-')[0] != n:
            e['issue'] = n; e.pop('pages', None)
            LOG.append(('info', pid, f'"{e["volume"]}:{n}" resolved as volume:issue because Crossref lists issue {n} (pages not printed in the old citation, left empty)'))
    # disagreements with Crossref
    if acc:
        notes = []
        nm = lambda p: re.sub(r'[–-]', '-', p).lower()
        if e.get('volume') and acc['volume'] and e['volume'] != acc['volume']: notes.append(f'volume {e["volume"]} (old) vs {acc["volume"]} (Crossref)')
        if e.get('issue') and acc['issue'] and e['issue'] != acc['issue']: notes.append(f'issue {e["issue"]} vs {acc["issue"]}')
        if e.get('pages') and acc['page'] and nm(e['pages']) != nm(acc['page']):
            a, b = nm(e['pages']).split('-'), nm(acc['page']).split('-')
            abbreviated = len(a) == 2 and len(b) == 2 and a[0] == b[0] and b[1].endswith(a[1]) and len(a[1]) < len(b[1])
            if not abbreviated: notes.append(f'pages {e["pages"]} vs {acc["page"]}')
            else: LOG.append(('info', pid, f'pages "{e["pages"]}" are an abbreviation of Crossref "{acc["page"]}"; kept as printed'))
        if min(acc['years']) != e['year'] and e['year'] not in acc['years']: notes.append(f'year {e["year"]} vs Crossref {acc["years"]}')
        if notes: REV['doi_disagree'].append(f'`{pid}` ({acc["doi"]}): ' + '; '.join(notes))
    d = pick_date(e, pid)
    ent = dict(title=e['title'], authors=e['authors'], year=e['year'])
    if d: ent['date'] = d
    ent['type'] = e['type']; ent['venue'] = e['venue']
    for k in ('volume', 'issue', 'pages', 'editors', 'publisher'):
        if e.get(k): ent[k] = str(e[k])
    if doi: ent['doi'] = doi
    if e['pdf']: ent['pdf'] = e['pdf']
    la = lab_authors(e['authors'])
    ent['lab_authors'] = la
    ent['_year'], ent['_date'] = e['year'], d
    ent['legacy'] = list(e['legacy'])
    pubs.append((pid, ent, e, acc))

# preprint twin
for pid, ent, e, acc in pubs:
    if acc and acc['doi'] == '10.1038/s41565-023-01419-x':
        ent['legacy'].append('/cuapoco-et-al-bioarxiv-preprint.html')
        LOG.append(('legacy', pid, 'added /cuapoco-et-al-bioarxiv-preprint.html: Crossref lists the bioRxiv preprint 10.1101/2022.01.08.475342 ("Intravenous gene transfer throughout the brain of infant Old World primates using AAV", Chuapoco et al.) as "is-preprint-of" 10.1038/s41565-023-01419-x, which is this Nature Nanotechnology 2023 paper; the preprint is the same work under an earlier title.'))
        REV['misc'].append(f'bioRxiv stale page `cuapoco-et-al-bioarxiv-preprint` treated as the preprint of `{pid}` (Crossref relation is-preprint-of). No separate preprint entry created.')
        break
else:
    REV['misc'].append('bioRxiv stale page cuapoco-et-al-bioarxiv-preprint: could NOT be tied to a live entry; no entry created.')

# featured = 3 newest journal articles
js = sorted([(ent['_year'], (ent['_date'] or datetime.date(ent['_year'], 1, 1)), -i, pid) for i, (pid, ent, e, acc) in enumerate(pubs) if ent['type'] == 'journal'], reverse=True)
featured = {x[3] for x in js[:3]}

def dump(path, data, body=None):
    txt = yaml.safe_dump(data, sort_keys=False, allow_unicode=True, width=10000, default_flow_style=False)
    if body is not None: txt = '---\n' + txt + '---\n\n' + body.strip() + '\n'
    open(path, 'w', encoding='utf-8').write(txt)

for f in glob.glob(OUT_PUB + '/*.yaml') + glob.glob(OUT_PRES + '/*.yaml'): os.remove(f)
for pid, ent, e, acc in pubs:
    ent = {k: v for k, v in ent.items() if not k.startswith('_')}
    ent['featured'] = pid in featured
    ent['lab_authors'] = ent.pop('lab_authors'); leg = ent.pop('legacy'); ent['legacy'] = leg
    ent['themes'] = []
    # keep schema-friendly key order
    order = ['title', 'authors', 'year', 'date', 'type', 'venue', 'volume', 'issue', 'pages', 'editors', 'publisher', 'doi', 'pdf', 'themes', 'lab_authors', 'featured', 'legacy']
    dump(f'{OUT_PUB}/{pid}.yaml', {k: ent[k] for k in order if k in ent})

# ------------------------------------------------------------------ presentations
used.clear()
nprs = 0
for p in D['pres']:
    sn = slugify(surname(p['authors'][0]))
    pid = uniq(f'{sn}-{p["year"]}-{p["acr"]}', p['title']); p['id'] = pid
    d = pick_date(p, pid)
    ent = dict(title=p['title'], authors=p['authors'], year=p['year'])
    if d: ent['date'] = d
    ent.update(type='poster', meeting=p['meeting'])
    if p['pdf']: ent['pdf'] = p['pdf']
    ent['lab_authors'] = lab_authors(p['authors']); ent['legacy'] = p['legacy']
    dump(f'{OUT_PRES}/{pid}.yaml', ent); nprs += 1

# ------------------------------------------------------------------ people
people_ids = []
def make_photo(src, pid):
    im = Image.open(ROOT + 'images/' + src)
    im = ImageOps.exif_transpose(im)
    if im.mode in ('RGBA', 'LA', 'P'):
        im = im.convert('RGBA'); bg = Image.new('RGB', im.size, (255, 255, 255)); bg.paste(im, mask=im.split()[3]); im = bg
    else: im = im.convert('RGB')
    w, h = im.size; m = max(w, h)
    if m > 800:
        s = 800 / m; im = im.resize((round(w * s), round(h * s)), Image.LANCZOS)
    im.save(f'{OUT_IMG}/{pid}.jpg', 'JPEG', quality=85, optimize=True)
    return (w, h), im.size
for f in glob.glob(OUT_PEOPLE + '/*.md'): os.remove(f)
photo_log = []
for p in P:
    sz = make_photo(p['img'], p['id']); photo_log.append((p['id'], p['img'], sz))
    fm = dict(name=p['name'], role=p['role'], status=p['status'], order=p['order'], start=p['start'])
    if p.get('now_at'): fm['now_at'] = p['now_at']
    fm['photo'] = f'../../assets/people/{p["id"]}.jpg'; fm['photo_alt'] = p['name']
    if p.get('email'): fm['email'] = p['email']
    if p.get('links'): fm['links'] = p['links']
    fm['citation_names'] = cit[p['id']]
    fm['legacy'] = ['/' + p['src'] + '.html']
    dump(f'{OUT_PEOPLE}/{p["id"]}.md', fm, p['bio'])

# ------------------------------------------------------------------ review.md
def sect(title): return f'\n## {title}\n\n'
L = ['# Migration review log (publications, presentations, people)\n',
     'Generated by `site/scripts/extract/write_content.py` from `parse_entries.py`, `doi_lookup.py`, `people_data.py`. Re-running is deterministic (Crossref responses are cached in `crossref-cache.json`).\n']
n_j = sum(1 for _, ent, _, _ in pubs if ent['type'] == 'journal'); n_c = len(pubs) - n_j
n_doi = sum(1 for pid, ent, e, acc in pubs if 'doi' in ent)
n_look = sum(1 for _ in pubs)
L.append(sect('1. Counts') + f'- publications: {len(pubs)} files ({n_j} journal, {n_c} chapter) = 109 live citations (91 journal + 18 chapters) minus 1 merged near-duplicate (Oler/Tromp BSF).\n'
         f'- presentations: {nprs} files = 69 live posters minus 1 merged near-duplicate (Campos SoBP 2022).\n- people: {len(P)} ({sum(p["status"]=="current" for p in P)} current, {sum(p["status"]=="alumni" for p in P)} alumni).\n'
         f'- DOIs: {n_doi} of {len(pubs)} publication entries have a DOI ({sum(1 for pid,ent,e,acc in pubs if acc)} accepted from Crossref by the threshold rule, {n_doi - sum(1 for pid,ent,e,acc in pubs if acc)} copied from the old citation text). '
         f'Journal articles: {sum(1 for pid,ent,e,acc in pubs if ent["type"]=="journal" and "doi" in ent)}/{n_j}; chapters: {sum(1 for pid,ent,e,acc in pubs if ent["type"]=="chapter" and "doi" in ent)}/{n_c}.\n'
         f'- featured: {", ".join(sorted(featured))}.\n- No preprint entries: the only preprint page (bioRxiv) is a stale page with a live published twin.\n')
L.append(sect('2. Merges of near-duplicates') + '\n'.join('- ' + m for k, w, m in LOG if k == 'merge') + '\n')
L.append(sect('3. Stale pages added to `legacy` of the live twin') + '\n'.join(f'- `{w}`: {m}' for k, w, m in LOG if k == 'legacy') + '\n'
         '\nThe two stale "cover of Biological Psychiatry" pages (`foxs-work-featured-on-cover-of-biological-psychiatry`, `fox-lab-featured-on-cover-of-biological-psychiatry`) are news items, not publications or presentations; they were left to whoever owns news.\n')
L.append(sect('4. Typo fixes and normalizations') + '\n'.join(f'- `{w}`: {m}' for k, w, m in LOG if k in ('typo',)) + '\n')
L.append('\nTypos from the audit list (3.2) that were **not present in any citation text** and so needed no edit: "Emotoin" (only in the page slug `heller-et-al-emotoin-2019`), "Psyhchiatry" (only on the stale cover news pages), "Cuapoco" / "bioarxiv" (slugs only; the stale preprint page reads "Chuapoco" and "BioArxiv" in its text, and no entry is created for it), "Transporder" (only inside the PDF file name `theSerotoninTransporderGenotype...pdf`; the file name is unchanged because the `pdf` path must match the file on disk), "Guildford" (fixed, in the Davidson chapter publisher), "Gorgans" (fixed, poster author), "CHen" (only on the CV page). Typos found by reading all titles and fixed beyond the audit list: "Opportunitvnies", "durin gexposure", "amygdale", "to adn across". A possible typo left alone: "5-HTTP S-Carriers" in the Fox SoBP 2007 poster title (probably 5-HTTLPR or 5-HTT).\n')
L.append(sect('5. Author-list repairs') + '\n'.join(f'- `{w}`: {m}' for k, w, m in LOG if k == 'author') + '\n')
L.append(sect('6. Meeting names (presentations) normalized') + 'The old lines read e.g. "Meeting for the Society of Biological Psychiatry", "Presented at the Society for Neuroscience Conference in 2022.", "Society for Neuroscience meeting". The `meeting` field holds the society/meeting name only (the year is in `year`). Every change:\n\n' +
         '\n'.join(f'- `{w}`: {m}' for k, w, m in LOG if k == 'meeting') + '\n\nNote: "Human Brain Mapping meeting" became "Organization for Human Brain Mapping" and "Cognitive Neuroscience Meeting"/"Society for Biological Psychiatry Meeting" were mapped to the society names; these are my identifications of the meetings (PDF names such as `foxAS_CNS_2011_reprint.pdf` support the CNS one), please confirm. No poster text says "talk", so all 68 are type `poster`.\n')
L.append(sect('7. Dates dropped or adjusted (Pelican page date vs citation year)') + ('\n'.join('- ' + x for x in REV['dates']) or '- none') + '\n'
         f'\nThe audit mentions 4 mismatches; among the 177 live citation pages only one disagrees (the other mismatches belong to stale pages that have no entry). '
         f'\n**Placeholder-looking dates:** {len(REV["jan1"])} entries keep a `date` of the form YYYY-01-01 because the Pelican page date agrees with the year, but a 1 January date is probably a placeholder, not the real publication date: ' + ', '.join(REV['jan1']) + '. Consider dropping `date` for these, or sort by year only.\n')
L.append(sect('8. DOIs not accepted (journal articles and chapters)') + 'Rule: normalized title similarity >= 0.92 AND Crossref year within +-1 AND first-author surname match (and a journal/book-chapter record type). Two queries per item at most (`query.bibliographic`, then `query.title`+`query.author`). Best candidates shown as `DOI (title score, Crossref years, author match, type)`.\n\n')
for pid, e, res in REV['doi_miss']:
    L.append(f'- `{pid}` ({e["year"]}, {e["type"]}): "{e["title"]}"\n')
    for c in res['candidates']:
        L.append(f'    - {c["doi"]} ({c["ts"]}, {c["years"]}, author {"yes" if c["author_match"] else "no"} [{c["first_author_cr"]}], {c["type"]}): "{c["title"][:110]}"\n')
L.append(sect('9. Accepted DOIs whose Crossref bibliographic data disagrees with the old citation') + 'The old text was kept (not overwritten) so the PI can decide. Probable typos in the old text are marked.\n\n' + '\n'.join('- ' + x for x in REV['doi_disagree']) + '\n')
L.append(sect('10. Other items needing a human look') + '\n'.join('- ' + x for x in REV['misc']) + '\n' + '\n'.join(f'- `{w}`: {m}' for k, w, m in LOG if k == 'REVIEW') + '\n\n'
         '**Old citation oddities left as printed** (no source to correct them from): author name variants such as "Davidson R"/"Davidson RJ", "Kalin N"/"Kalin NH", "Man K-NM"/"Man KNM"/"Man NKM", "Ores KS"/"Ores Walsh KS"/"Ores-Walsh KS", "Lemay EP"/"LeMay EP", "Chuapoco M/ME/MR", "Shaya T" (probably Shay TF), "Pine P" (probably Pine DS), "Fox SE" (Chu SoBP 2019, not the PI); titles that probably lost a question mark ("Afterword: How are emotions integrated into choice" and the other chapter titles in The Nature of Emotion); "Biological Psychiatry"/Neuron/PNAS volume-page values listed in section 9.\n'
         '\nNo `pmid` or `url` was added. `themes` left empty everywhere.\n')
L.append(sect('11. Info lines from the parser') + '\n'.join(f'- `{w}`: {m}' for k, w, m in LOG if k == 'info') + '\n')
L.append(sect('12. People') + '''- Source: `category/people.html` + the 19 profile pages. Current (9): Fox, Sharma, Puhger, Kamboj, Scott, Varga, Purewal, Chavez, Okhan. Alumni (10): Drzewiecki, Koh, Chu, Holley, Campos, Drwecki, Zhang, Queen, Imai, Marcil.
- Role typo fixed: "Junior Reseach Specialist" -> "Junior Research Specialist". PI role: the profile has no role line; set to "Principal Investigator" (old slug/title "Principle Investigator" is a typo).
- Alumni bios rewritten in third person/past tense from the profile text plus the one-line "former member" notes on the people page. Words fixed: "carreer", "Psycholgy", "recieved", "Reseach", "Tensorflow" -> "TensorFlow". Nothing was added except "Lillian defended her PhD" (people page: "Lillian just defended her PhD!!!").
- `end` is empty for everyone: the old site has no end dates. Alumni `order` is therefore: staff/postdocs (Drzewiecki 20, Koh 21, Chu 22), grad students (Holley 23, Campos 24), then visiting faculty/undergraduates (30-34), newest start first within each group. Change if the PI knows end dates.
- `now_at` filled only where the old people page states it (Chu, Marcil, Imai, Holley, Drwecki, Queen, Zhang, Drzewiecki). Campos and Koh: empty (not stated). The people page wording was kept ("Master's degree student..." etc.).
- Rani Purewal: old profile says "incoming graduate student" (written in 2022; she is on the 2024 SfN poster). Bio changed to "joined the Fox lab as a graduate student" without claiming anything new.
- Mesude Okhan: profile says she "joined the Fox Lab in 2024" but the "Joined the Foxlab" line says September 2025; `start` follows the "Joined" line (2025-09), bio text kept verbatim. PI to confirm.
- Jeetu Sharma: bio changed from "has joined us from MIT" to "joined the lab from MIT". Photo file on the old site is `jitendra_sharma.jpg`; Crossref lists "Sharma J" on Ding et al. 2026 as Jitendra Sharma (alongside Campos, Kamboj, Fox), so `Sharma J` is mapped to jeetu-sharma. Name "Jeetu" kept as on the old site.
- Kyle Puhger: dropped the first-person sentence ("Check out my Google Scholar, follow me on Twitter, and connect with me on LinkedIn!"); kept the Google Scholar link in `links.scholar`. Twitter (https://twitter.com/kpeez_) and LinkedIn (https://www.linkedin.com/in/kyle-puhger/) have no field in the schema and were not carried over.
- PI: bio kept verbatim ("Associate Professor"), but `resumecv.html` lists "2026 - present Professor" (and another line still says Associate Professor): **PI must confirm the title**. Links: scholar and GitHub as linked from the old homepage, email `dfox@ucdavis.edu` as shown in the old footer. `links.cv` left empty (the new CV path is not known to me). Headshot: `images/headshot_2025.jpg`, confirmed as the image used on `principle-investigator.html` and on the people page.
- Erin Scott: "interested in working developing tools" -> "interested in developing tools".
- citation_names are the exact strings found in author lists. People with no appearance in any citation have an empty list: Puhger, Chavez, Okhan, Koh, Drwecki, Queen, Imai, Marcil. Matches made by surname + initials only (not exact full names): "Scott E" (Erin Scott, poster with Fox/Tian lab authors), "Zhang YZ" (Yizi Zhang, Holley 2019 posters), "Chu AMF" (Amanda Chu), "Sharma J" (verified above). "Fox AS" also matches `andrew-fox` for all entries; "Fox SE" does not.
- Photos: resized to max 800 px on the long side (never upscaled), JPEG q85, EXIF orientation applied; images with transparency were flattened onto white. Source -> output sizes: ''' + '; '.join(f'{i}: {s[0]}x{s[1]} -> {t[0]}x{t[1]}' for i, _, (s, t) in photo_log) + '\n')
open(HERE + '/review.md', 'w', encoding='utf-8').write(''.join(L))
print('pubs', len(pubs), 'pres', nprs, 'people', len(P), 'doi', n_doi)
