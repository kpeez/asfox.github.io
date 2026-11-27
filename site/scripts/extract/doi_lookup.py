#!/usr/bin/env python3
"""Crossref DOI lookup for journal articles and chapters. Cached in crossref-cache.json.
Acceptance: normalized title similarity >= 0.92 AND Crossref year within +-1 AND first-author surname matches."""
import json, os, re, sys, time, unicodedata, html, urllib.parse
import requests
from difflib import SequenceMatcher
HERE = os.path.dirname(os.path.abspath(__file__))
CACHE_F = HERE + '/crossref-cache.json'
HDR = {'User-Agent': 'foxlab-site-migration/0.1 (mailto:none)'}
cache = json.load(open(CACHE_F)) if os.path.exists(CACHE_F) else {}
last = [0.0]
SEL = 'DOI,title,subtitle,issued,published-print,published-online,author,type,volume,issue,page,container-title,relation'

def get(url):
    if url in cache: return cache[url]
    wait = 0.25 - (time.time() - last[0])
    if wait > 0: time.sleep(wait)
    for attempt in range(4):
        try:
            r = requests.get(url, headers=HDR, timeout=30)
            last[0] = time.time()
            if r.status_code == 200:
                cache[url] = r.json(); json.dump(cache, open(CACHE_F, 'w'), indent=0); return cache[url]
            if r.status_code in (429, 503): time.sleep(2 + attempt * 3); continue
            print('HTTP', r.status_code, url); cache[url] = {'error': r.status_code}; return cache[url]
        except requests.RequestException as ex:
            print('ERR', ex); time.sleep(3)
    return {'error': 'unreachable'}

def norm(s):
    s = html.unescape(re.sub(r'<[^>]+>', '', s or ''))
    s = unicodedata.normalize('NFKD', s).encode('ascii', 'ignore').decode().lower()
    return re.sub(r'[^a-z0-9]+', '', s)
def sim(a, b): return SequenceMatcher(None, norm(a), norm(b)).ratio()
def surname(a):
    a = a.rstrip('*'); a = re.sub(r' Jr$', '', a); return re.sub(r' [A-Z]{1,4}(-[A-Z]{1,3})?$', '', a)
def years(it):
    ys = set()
    for k in ('issued', 'published-print', 'published-online'):
        try: ys.add(it[k]['date-parts'][0][0])
        except Exception: pass
    return ys
def cand_info(it, e):
    titles = [(it.get('title') or [''])[0]]
    if it.get('subtitle'): titles.append(titles[0] + ' ' + it['subtitle'][0])
    ts = max(sim(e['title'], t) for t in titles)
    ys = [y for y in years(it) if y is not None]
    ydiff = min([abs(y - e['year']) for y in ys], default=99)
    first = e['authors'][0]
    au = it.get('author') or []
    if first.startswith('The PRIMatE'):
        am = bool(au) and 'primate' in norm(au[0].get('name', '') + au[0].get('family', ''))
    else:
        sn = norm(surname(first)); am = False
        if au:
            fam = norm(au[0].get('family', '') or au[0].get('name', ''))
            am = bool(fam) and (fam == sn or fam.endswith(sn) or sn.endswith(fam))
    pg = (it.get('page') or '').split('-')[0].strip().lower()
    ours = re.split(r'[-–]', e.get('pages') or '')[0].strip().lower()
    page_match = bool(pg) and bool(ours) and pg == ours
    return dict(page_match=page_match, doi=it['DOI'], title=titles[0], ts=round(ts, 3), years=sorted(ys), ydiff=ydiff, author_match=am,
                first_author_cr=(au[0].get('family') or au[0].get('name') or '') if au else '', type=it.get('type'),
                volume=it.get('volume'), issue=it.get('issue'), page=it.get('page'), relation=it.get('relation'))
OKTYPES = {'journal-article', 'book-chapter', 'book-part', 'reference-entry', 'proceedings-article'}

def lookup(e):
    first = e['authors'][0] if not e['authors'][0].startswith('The PRIMatE') else 'PRIMatE Data Exchange'
    q = f"{e['title']} {surname(first) if first != 'PRIMatE Data Exchange' else first} {e['year']}"
    urls = [f"https://api.crossref.org/works?query.bibliographic={urllib.parse.quote(q)}&rows=3&select={SEL}",
            f"https://api.crossref.org/works?query.title={urllib.parse.quote(e['title'])}&query.author={urllib.parse.quote(surname(first))}&rows=3&select={SEL}"]
    cands = []; tried = 0
    for u in urls:
        d = get(u); tried += 1
        if 'error' in d: continue
        for it in d['message']['items']:
            ci = cand_info(it, e)
            if ci['doi'] not in [c['doi'] for c in cands]: cands.append(ci)
        ok = [c for c in cands if c['ts'] >= 0.92 and c['ydiff'] <= 1 and c['author_match'] and c['type'] in OKTYPES]
        if ok: break
    ok = [c for c in cands if c['ts'] >= 0.92 and c['ydiff'] <= 1 and c['author_match'] and c['type'] in OKTYPES]
    ok.sort(key=lambda c: (not c['page_match'], -c['ts'], c['ydiff']))
    cands.sort(key=lambda c: -c['ts'])
    return dict(accepted=ok[0] if ok else None, candidates=cands[:3], n_acceptable=len(ok))

if __name__ == '__main__':
    d = json.load(open(HERE + '/entries.json'))
    res = {}
    for i, e in enumerate(d['pubs']):
        key = e['slugs'][0]
        res[key] = lookup(e)
        a = res[key]['accepted']
        print(i, key[:50], 'OK ' + a['doi'] if a else 'MISS', res[key]['candidates'][0]['ts'] if res[key]['candidates'] else '')
    json.dump(res, open(HERE + '/doi-results.json', 'w'), indent=1, ensure_ascii=False)
