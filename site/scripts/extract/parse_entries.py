#!/usr/bin/env python3
"""Parse the old Pelican citation lists into intermediate entries.json (+ log.json)."""
import csv, json, os, re, sys, unicodedata, urllib.parse
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from parse_raw import ROOT, parse_li, parse_file
from bs4 import BeautifulSoup

LOG = []          # (kind, id_or_slug, message)
def log(kind, who, msg): LOG.append((kind, who, msg))

inv = list(csv.DictReader(open(ROOT + 'audit/data/inventory.csv')))
pubs_raw = parse_file(ROOT + 'category/publications.html')
posts_raw = parse_file(ROOT + 'category/posters.html')
assert len(pubs_raw) == 109 and len(posts_raw) == 69

def page_info(fn):
    s = BeautifulSoup(open(ROOT + fn, encoding='utf-8').read(), 'html.parser')
    art = s.find('article')
    t = art.find('time')
    return dict(lis=[parse_li(li) for li in art.find_all('li')], date=t['datetime'][:10])

def key(x): return (x['pdf'], x['title'], x['pre'])
pages = {}
for r in inv:
    if r['type'] in ('journal-publication', 'book-chapter', 'conference-poster-talk') and r['in_archive'] == 'Y':
        pages[r['file']] = dict(row=r, **page_info(r['file']))
slug_of = lambda fn: fn[:-5]

def match(raw, types):
    out = {}
    idx = {}
    for i, x in enumerate(raw): idx.setdefault(key(x), []).append(i)
    for fn, p in pages.items():
        if p['row']['type'] in types:
            m = idx[key(p['lis'][0])]
            assert len(m) == 1, fn
            assert m[0] not in out
            out[m[0]] = fn
    assert len(out) == len(raw)
    return out
pub_page = match(pubs_raw, ('journal-publication', 'book-chapter'))
post_page = match(posts_raw, ('conference-poster-talk',))

# ---------------------------------------------------------------- typos
TYPOS = [  # (regex, replacement)
    (r'Emotoin', 'Emotion'), (r'\bCHen\b', 'Chen'), (r'Communicatoins', 'Communications'),
    (r'Psyhchiatry', 'Psychiatry'), (r'Guildford', 'Guilford'), (r'\bGorgans\b', 'Grogans'),
    (r'\bCuapoco\b', 'Chuapoco'), (r'Transporder', 'Transporter'), (r'\b[Bb]io[Aa]rxiv\b', 'bioRxiv'),
    (r'Opportunitvnies', 'Opportunities'), (r'durin gexposure', 'during exposure'),
    (r'\bamygdale\b', 'amygdala'), (r'\bto adn across\b', 'to and across'), (r'\bNeuroimage\b', 'NeuroImage'),
    (r'^The Journal of Neuroscience$', 'Journal of Neuroscience'),
]
def fix(text, who, field):
    for pat, rep in TYPOS:
        new = re.sub(pat, rep, text)
        if new != text:
            m = re.search(pat, text)
            log('typo', who, f'{field}: "{text}" -> "{new}"' if len(text) < 90 else f'{field}: "{m.group(0)}" -> "{rep}" (in: "{text[:70]}...")')
            text = new
    return text

# author-level fixes (applied before splitting: string replace; log each)
PRE_FIX = [
    ('Fox AS Colzato LS', 'Fox AS, Colzato LS', 'missing comma between two authors'),
    ('Dhanesh Sivadasan Bindu DS', 'Sivadasan Bindu DS', 'first name printed in front of surname+initials'),
    ('Naz Taskin N', 'Taskin N', 'first name printed in front of surname+initials'),
    ('David Goertsen D', 'Goertsen D', 'first name printed in front of surname+initials'),
    ('Viktor M. Plattner VM', 'Plattner VM', 'first name printed in front of surname+initials'),
    ('Lillian J. Campos LJ', 'Campos LJ', 'first name printed in front of surname+initials'),
    ('LJ Campos, DPM Tromp, JP Capitanio', 'Campos LJ, Tromp DPM, Capitanio JP', 'initials printed before surname'),
    ('Holley, D., Campos, L. J., Zhang, Y. Z., Capitanio, J. P., & Fox, A. S', 'Holley D, Campos LJ, Zhang YZ, Capitanio JP, Fox AS', 'full-stop style reformatted to "Surname INITIALS"'),
    ('Shelton SE. Fox AS', 'Shelton SE, Fox AS', 'period instead of comma between authors'),
]
TOK_FIX = {  # token-level, evidence in parentheses
    'Calrson EL': ('Carlson EL', 'typo; "Carlson EL" in the same research group papers'),
    'DeYong KA': ('DeYoung KA', 'typo; "DeYoung KA" in the other papers'),
    'Shackman AS': ('Shackman AJ', 'wrong initials; "Shackman AJ" everywhere else'),
    'Goede N': ('Goeden N', 'typo; "Goeden N" in the preprint and other posters'),
    'Goersten D': ('Goertsen D', 'typo; "Goertsen D" in Nature Communications 2023 author list'),
    'Roxa KM': ('Roxas KM', 'typo; "Roxas KM" in the bioRxiv preprint'),
    'Gorgans S': ('Grogans S', 'known typo (audit 3.2)'),
}
AUTH_RE = re.compile(r"^[^\W\d_][\w'’\-\. ]* [A-Z]{1,4}(-[A-Z]{1,3})?\*?( Jr)?$")

def split_authors(a, who):
    a = a.replace('\xa0', ' ')
    a = re.sub(r'\s+', ' ', a).strip()
    a = re.sub(r'\.$', '', a).strip()
    if a.startswith('The PRIMatE Data Exchange'):
        return [a]
    for old, new, why in PRE_FIX:
        if old in a:
            a = a.replace(old, new); log('author', who, f'"{old}" -> "{new}" ({why})')
    a = re.sub(r'(\b[A-Z]{1,4})\. (?=[A-Z][a-z])', r'\1, ', a)
    a = re.sub(r',?\s*&\s*', ', ', a)
    a = re.sub(r',?\s+and\s+', ', ', a)
    toks = [t.strip() for t in a.split(',') if t.strip()]
    out = []
    for t in toks:
        if out and (re.fullmatch(r'[A-Z]{1,4}\*?', t) or t in ('Jr', 'Jr.')):
            out[-1] += ' ' + t.rstrip('.'); continue
        out.append(t)
    res = []
    for t in out:
        if t in TOK_FIX:
            new, why = TOK_FIX[t]; log('author', who, f'"{t}" -> "{new}" ({why})'); t = new
        if not AUTH_RE.match(t): log('REVIEW', who, f'author token does not look like "Surname INITIALS": "{t}"')
        res.append(t)
    return res

def split_pre(pre, who):
    pre = pre.replace('\xa0', ' ')
    m = re.match(r'^(.*?)\s*\((\d{4})\)\.?\s*$', pre)
    assert m, pre
    return split_authors(m.group(1), who), int(m.group(2))

def clean_title(t, who):
    t = re.sub(r'\s+', ' ', t).strip()
    t = re.sub(r'(?<!\.)\.$', '', t)
    return fix(t, who, 'title')

def pdf_path(url, who):
    if not url: return None
    name = url.rsplit('/', 1)[-1]
    if os.path.exists(ROOT + 'publications/' + urllib.parse.unquote(name)):
        return '/publications/' + name
    log('REVIEW', who, f'PDF linked but file missing in publications/: {name}')
    return None

# ---------------------------------------------------------------- citation tails
def parse_tail(post, who):
    r = dict(volume=None, issue=None, pages=None, doi=None, ambiguous=None)
    s = post.strip()
    m = re.search(r'https?://doi\.org/(\S+)', s)
    if m:
        r['doi'] = m.group(1).rstrip('.'); s = s.replace(m.group(0), '').strip()
        log('info', who, f'DOI printed in the old citation: {r["doi"]}')
    s = re.sub(r'^[.\s]+', '', s); s = re.sub(r'[.\s]+$', '', s)
    if not s: return r
    if re.fullmatch(r'\d{4}', s): log('info', who, f'trailing text "{s}" is only a year; no volume/pages recorded'); return r
    if re.fullmatch(r'\d{1,2} [A-Z][a-z]+', s):
        log('REVIEW', who, f'old citation gives only "{s}" (looks like an online-publication date); no volume/issue/pages recorded'); return r
    m = re.fullmatch(r'(\d+);(\d+)\((\d+)\):\s*(.+)', s)
    if m:
        log('info', who, f'dropped leading "{m.group(1)};" (a day-of-month) from "{s}"')
        r.update(volume=m.group(2), issue=m.group(3), pages=m.group(4)); return finish(r, who, s)
    m = re.fullmatch(r'(\d+)\((\d+)\)', s)
    if m: r.update(volume=m.group(1), issue=m.group(2)); return r
    m = re.fullmatch(r'(\d+)\s*\((\d+)\)\s*:?\s*(.+)', s)
    if m: r.update(volume=m.group(1), issue=m.group(2), pages=m.group(3)); return finish(r, who, s)
    m = re.fullmatch(r'(\d+),\s*(.+)', s)
    if m: r.update(volume=m.group(1), pages=m.group(2)); return finish(r, who, s)
    m = re.fullmatch(r'(\d+):\s*(.+)', s)
    if m:
        r['volume'] = m.group(1); p = m.group(2)
        if re.search(r'[-–]', p) or re.match(r'[a-z]', p) or len(p) >= 5: r['pages'] = p
        else: r['pages'] = p; r['ambiguous'] = p
        return finish(r, who, s)
    if re.fullmatch(r'\d+', s): r['volume'] = s; return finish(r, who, s)
    m = re.fullmatch(r'(?:Advance Online Publication:\s*)?(\d+[-–]\d+)', s)
    if m:
        r['pages'] = m.group(1)
        log('REVIEW', who, f'old citation "{s}": no volume given (advance online / ahead of print); pages recorded as "{m.group(1)}"'); return r
    log('REVIEW', who, f'could not parse volume/pages from "{s}"'); return r

def finish(r, who, s):
    p = r['pages']
    if p and re.fullmatch(r'\d+:\d+', p):
        log('typo', who, f'pages "{p}" -> "{p.replace(":", "-")}" (colon typed instead of hyphen)'); r['pages'] = p.replace(':', '-')
    if r['ambiguous']:
        log('info', who, f'"{s}": single number after volume is ambiguous (issue or article number); recorded as pages, may be re-labelled from Crossref')
    return r

# ---------------------------------------------------------------- publications
VENUE_ABBR = {
 'Nature Chemical Biology': 'natchembio', 'Molecular Psychiatry': 'molpsych', 'Social Cognitive and Affective Neuroscience': 'scan',
 'Journal of Neuroscience': 'jneurosci', 'American Journal of Psychiatry': 'ajp', 'Nature Reviews Neuroscience': 'nrn',
 'Computational Psychiatry': 'compsych', 'Cognitive, Affective, & Behavioral Neuroscience': 'cabn', 'Translational Psychiatry': 'translpsych',
 'Psychoneuroendocrinology': 'pne', 'Proceedings of the National Academy of Sciences': 'pnas', 'PLoS One': 'plosone',
 'Nature Communications': 'natcomm', 'Neuroscience & Biobehavioral Reviews': 'nbr', 'Current Research in Neurobiology': 'crn',
 'Nature Nanotechnology': 'natnano', 'Oxford Open Neuroscience': 'oxopenneuro', 'Neuron': 'neuron', 'Psychological Science': 'psychsci',
 'Molecular Therapy': 'moltherapy', 'NeuroImage': 'neuroimage', 'Biological Psychiatry': 'biolpsych',
 'Biological Psychiatry: Cognitive Neuroscience and Neuroimaging': 'bpcnni', 'Progress in Brain Research': 'pbr', 'Neuroscience': 'neuroscience',
 'Neuroscience Letters': 'neurosciletters', 'Emotion': 'emotion', 'Behavioral and Brain Sciences': 'bbs', 'Scientific Reports': 'scirep',
 'Trends in Cognitive Sciences': 'tics', 'Human Brain Mapping': 'hbm', 'Brain Structure and Function': 'bsf', 'Psychological Bulletin': 'psychbull',
 'Journal of Experimental Psychopathology': 'jep', 'Trends in Neurosciences': 'tins', 'Neuropsychopharmacology': 'npp',
 'Journal of Cognitive Neuroscience': 'jocn', 'Cerebral Cortex': 'cercor', 'Nature': 'nature',
}
STOP = set('the a an of in on and for to with from by is are how what when why at as or its their into between'.split())
def slugify(s): return re.sub(r'[^a-z0-9]+', '-', unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode().lower()).strip('-')
def surname(a):
    a = a.rstrip('*'); a = re.sub(r' Jr$', '', a)
    return re.sub(r' [A-Z]{1,4}$', '', a)
def title_word(t, skip=()):
    for w in re.findall(r"[A-Za-z]+", t):
        if w.lower() not in STOP and w.lower() not in skip and len(w) > 2: return w.lower()
    return 'x'

CHAPTERS = {  # category index -> (book/venue, editors, publisher, pages, series-note)
}
def chapter_meta(i, x, who):
    em, post = x['em'], x['post']
    if i == 3:  # Campos 2025
        m = re.fullmatch(r'\.\s*(.*?)\.\s*(Blackford JU & Milad M) \(Eds\.\)', post)
        return dict(venue='New discoveries in the brain sciences of fear and anxiety: from basic to clinical neuroscience (Springer Series in Behavioral Neuroscience)',
                    editors='Blackford JU & Milad M', publisher='Springer', pages=None,
                    note='publisher "Springer" taken from the series name "Springer Series in Behavioral Neuroscience"; no pages printed')
    if i == 4:  # Holley 2025
        return dict(venue='Neurobehavioral individual differences - A transdisciplinary approach to advancing clinical science',
                    editors='Latzman RD & Patrick CJ', publisher='Springer, Cham', pages='85–111', note='')
    if 49 <= i <= 62:
        return dict(venue='The Nature of Emotion: Fundamental questions (2nd edition)', editors='Fox AS, Lapate RC, Shackman AJ & Davidson RJ',
                    publisher='Oxford University Press', pages=None, note='')
    if i == 70:
        return dict(venue='Living without an amygdala', editors='Amaral DG, Bauman M & Adolphs R', publisher='Guilford Press', pages=None, note='')
    if i == 101:
        return dict(venue='Handbook of Emotion Regulation', editors='Gross and Gotlib', publisher='Guilford Press', pages=None,
                    note='editors kept as printed ("Gross and Gotlib"); the printed publisher "Guildford Press" corrected to Guilford')
    raise ValueError(i)
CHAPTER_IDX = set([3, 4, 70, 101] + list(range(49, 63)))

entries = []
for i, x in enumerate(pubs_raw):
    fn = pub_page[i]; slug = slug_of(fn); who = slug
    pg = pages[fn]
    authors, year = split_pre(x['pre'], who)
    if x['title'] == 'Brain Structure and Function':   # the -bsf-2017 page has title and venue swapped
        title = None
    else:
        title = clean_title(x['title'], who)
    e = dict(src='pub', idx=i, slugs=[slug], page_dates=[pg['date']], authors=authors, year=year, title=title,
             pdf=pdf_path(x['pdf'], who), legacy=['/' + slug + '.html'])
    if i in CHAPTER_IDX:
        e['type'] = 'chapter'
        cm = chapter_meta(i, x, who)
        e.update(venue=fix(cm['venue'], who, 'venue'), editors=cm['editors'], publisher=cm['publisher'])
        if cm['pages']: e['pages'] = cm['pages']
        if cm['note']: log('info', who, 'chapter: ' + cm['note'])
        if i == 101: log('typo', who, 'publisher: "Guildford Press" -> "Guilford Press"')
    else:
        e['type'] = 'journal'
        venue = x['em']
        if not venue:
            venue = 'Brain Structure and Function'; log('info', who, 'old page has title and venue swapped (title printed as "Brain Structure and Function", no venue); merged with its twin')
        venue = fix(re.sub(r'\s+', ' ', venue).strip(), who, 'venue')
        e['venue'] = venue
        t = parse_tail(x['post'], who)
        for k in ('volume', 'issue', 'pages', 'doi'):
            if t[k]: e[k] = t[k]
        if t['ambiguous']: e['_ambiguous'] = t['ambiguous']
    entries.append(e)

# --- merge near-duplicate: oler-tromp (2016 full citation, 2017 broken-title page)
ia = next(k for k, e in enumerate(entries) if e['slugs'] == ['oler-tromp-et-al-2016'])
ib = next(k for k, e in enumerate(entries) if e['slugs'] == ['oler-tromp-et-al-bsf-2017-2017'])
A, B = entries[ia], entries[ib]
assert A['authors'] == B['authors'] and A['pdf'] == B['pdf'] and A['volume'] == B['volume'] == '222'
A['slugs'] += B['slugs']; A['legacy'] += B['legacy']; A['page_dates'] += B['page_dates']
A['year'] = 2017
log('merge', 'oler-tromp', 'oler-tromp-et-al-2016 (year printed 2016, full title) + oler-tromp-et-al-bsf-2017-2017 (year printed 2017, title field holds only the journal name, no venue): same authors, same PDF, 222(1):21-39. '
    'Merged into one entry with the full title; both legacy paths kept. Year set to 2017 because the volume/issue (222(1), January 2017) is the print year; the two pages disagree (2016 vs 2017) and Crossref is checked as well (see DOI section).')
del entries[ib]

# --- stale twins -> legacy
def add_legacy(live_slug, stale_slug, why):
    for e in entries:
        if live_slug in e['slugs']:
            e['legacy'].append('/' + stale_slug + '.html'); log('legacy', live_slug, f'added /{stale_slug}.html ({why})'); return
    raise KeyError(live_slug)
add_legacy('ander-et-al-molecular-psychiatry-2026', 'ander-et-al-molecular-psychiatry-2025', 'stale twin; same title/PDF, printed year 2025 vs live 2026')
add_legacy('campos-drzewiecki-fox-springer-series-in-behavioral-neuroscience-new-discoveries-in-the-brain-sciences-of-fear-and-anxiety-from-basic-to-clinical-neuroscience-2025',
           'campos-drzewiecki-fox-springer-series-in-behavioral-neuroscience-new-discoveries-in-the-brain-sciences-of-fear-and-anxiety-from-basic-to-clinical-neuroscience-2024', 'stale twin; printed year 2024 vs live 2025')
add_legacy('holley-fox-neurobehavioral-individual-differences-2025', 'holley-fox-neurobehavioral-individual-differences-2022', 'stale twin; "In Press" 2022 vs live 2025')
add_legacy('davidson-et-al-2007', 'davidson-et-al-2006', 'stale twin; printed year 2006 vs live 2007')
add_legacy('shackman-et-al-molecular-psychiatry-2017-2017', 'shackman-et-al-2016', 'stale twin; same title/PDF, printed year 2016 vs live 2017')

# ---------------------------------------------------------------- presentations
MEETINGS = [  # (regex on em, canonical name, id acronym)
    (r"Biological Psychiatry", 'Society of Biological Psychiatry', 'sobp'),
    (r"Society (for|of) Neuroscience", 'Society for Neuroscience', 'sfn'),
    (r"^Society for Neuroscience$", 'Society for Neuroscience', 'sfn'),
    (r"Cognitive Neuroscience (Society|Meeting)", 'Cognitive Neuroscience Society', 'cns'),
    (r"Human Brain Mapping", 'Organization for Human Brain Mapping', 'hbm'),
    (r"International Primatological", 'International Primatological Society', 'ips'),
    (r"International Society of Psychoneuroendocrinology", 'International Society of Psychoneuroendocrinology', 'ispne'),
    (r"Society for Neuroeconomics", 'Society for Neuroeconomics', 'sne'),
    (r"New York Academy of Sciences meeting on Behavioral Epigenetics", 'New York Academy of Sciences meeting on Behavioral Epigenetics', 'nyas'),
    (r"New York Academy of Sciences meeting, Linking", 'New York Academy of Sciences meeting: Linking Affect to Action: Critical Contributions of the Orbitofrontal Cortex', 'nyas'),
    (r"Society for Nuclear Medicine", 'Society for Nuclear Medicine', 'snm'),
    (r"Medical Imaging Conference", 'Medical Imaging Conference', 'mic'),
    (r"Mechanisms of Learning", 'Sixth Annual Mechanisms of Learning Forum', 'mol'),
    (r"Aligning Science Across Parkinson", "Aligning Science Across Parkinson's", 'asap'),
]
def meeting_of(em, who):
    for pat, name, acr in MEETINGS:
        if re.search(pat, em):
            if name != em: log('meeting', who, f'"{em}" -> "{name}"')
            return name, acr
    raise ValueError(em)

pres = []
for i, x in enumerate(posts_raw):
    fn = post_page[i]; slug = slug_of(fn); who = slug
    authors, year = split_pre(x['pre'], who)
    meeting, acr = meeting_of(x['em'], who)
    title = clean_title(x['title'], who)
    pres.append(dict(src='post', idx=i, slugs=[slug], page_dates=[pages[fn]['date']], authors=authors, year=year, title=title, meeting=meeting,
                     acr=acr, type='poster', pdf=pdf_path(x['pdf'], who), legacy=['/' + slug + '.html']))
# merge Campos SoBP 2022
pa = next(p for p in pres if p['slugs'] == ['campos-et-al-society-of-biological-psychiatry-meeting-2022'])
pb = next(p for p in pres if p['slugs'] == ['lillian-jcampos-society-of-biological-psychiatry-2022'])
assert pa['title'] == pb['title'] and pa['year'] == pb['year'] == 2022
log('merge', 'campos-sobp-2022', f'{pa["slugs"][0]} (authors incl. Tromp DPM, no PDF) + {pb["slugs"][0]} (authors without Tromp DPM, with PDF). The authors differ; the PDF itself (publications/Campos_SoBP_2022.pdf, pdftotext page 1) lists Lillian J. Campos, Carly M. Drzewiecki, Do P.M. Tromp, John P. Capitanio, Andrew S. Fox, so the longer list was kept. PDF kept; both legacy paths kept.')
assert pa['authors'] == ['Campos LJ', 'Drzewiecki CM', 'Tromp DPM', 'Capitanio JP', 'Fox AS']
pa['pdf'] = pa['pdf'] or pb['pdf']; pa['slugs'] += pb['slugs']; pa['legacy'] += pb['legacy']; pa['page_dates'] += pb['page_dates']
pres.remove(pb)

json.dump(dict(pubs=entries, pres=pres, log=LOG), open(HERE + '/entries.json', 'w'), indent=1, ensure_ascii=False)
print(len(entries), 'publications', len(pres), 'presentations', len(LOG), 'log lines')
