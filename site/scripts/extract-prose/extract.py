#!/usr/bin/env python3
"""Convert the old Pelican pages (prose content) to Markdown for the Astro site.

Usage: python3 extract.py [--old /path/to/old/site] [--site /path/to/site]
Needs beautifulsoup4 (pip install beautifulsoup4).

Owns: site/src/content/{news,resources,pages}/, site/src/assets/content/,
site/public/downloads/code/. Writes log to extract-log.json (next to this script).
Themes are hand-written (see notes.md) and not produced here.
"""
import argparse, json, os, re, shutil, sys
from bs4 import BeautifulSoup, NavigableString, Comment, Tag

HERE = os.path.dirname(os.path.abspath(__file__))
ap = argparse.ArgumentParser()
ap.add_argument('--old', default='/home/user/asfox.github.io')
ap.add_argument('--site', default='/home/user/asfox.github.io/site')
ARGS = ap.parse_args()
OLD, SITE = ARGS.old, ARGS.site
LOG = {'typos': [], 'links_rewritten': [], 'links_left': [], 'images': [], 'videos': [],
       'math': [], 'misc': [], 'pdf_links': 0}

# ---------------------------------------------------------------- typo table
# Applied to prose text nodes only (never code, math, URLs). (pattern, replacement)
TYPOS = [
    # listed in audit 3.2
    (r'\brecieved\b', 'received'),
    (r'\bnighly\b', 'nightly'),
    (r'\bPsyhchiatry\b', 'Psychiatry'),
    (r'\bPermision\b', 'Permission'),
    (r'\bCommunicatoins\b', 'Communications'),
    # other clear misspellings found in the converted pages (spell-check pass)
]
TYPOS_FILE = os.path.join(HERE, 'typos.json')
if os.path.exists(TYPOS_FILE):
    TYPOS += [tuple(x) for x in json.load(open(TYPOS_FILE))]
TYPOS_C = [(re.compile(p), r) for p, r in TYPOS]


def fix_typos(t, slug):
    for rx, rep in TYPOS_C:
        def sub(m, rep=rep):
            LOG['typos'].append([slug, m.group(0), m.expand(rep)])
            return m.expand(rep)
        t = rx.sub(sub, t)
    return t


# ---------------------------------------------------------------- link map
SITE_PATHS = {
    'why-registration-matters-in-big-n-brain-imaging-studies.html': '/resources/why-registration-matters-in-big-n-brain-imaging-studies/',
    'looking-at-co-registered-brains.html': '/resources/looking-at-co-registered-brain-data/',
    '/2013/03/20/looking-at-co-registered-brains': '/resources/looking-at-co-registered-brain-data/',
    '/2013/04/01/python-flipbook-movies': '/resources/python-flipbook-movies/',
    '/2013/05/30/read-nifti-in-fmristat': '/resources/read-nifti-in-fmristat/',
    'fox-lab-mission.html': '/mission/',
    '/joining-the-fox-lab.html': '/join/',
    '/category/publications': '/publications/',
    '/category/publications.html': '/publications/',
    'pub.html': '/publications/',
}


def rewrite_href(href, slug):
    h = href.strip()
    h = h.replace('http://https://', 'https://')
    m = re.match(r'^(?:https?://)?(?:asfox\.github\.io|foxlab\.ucdavis\.edu)(/.*)?$', h)
    key = h
    if m:
        key = (m.group(1) or '/')
    key = key.rstrip('/') if key != '/' else key
    if key in SITE_PATHS:
        new = SITE_PATHS[key]
        LOG['links_rewritten'].append([slug, href, new])
        return new
    if m and key.startswith('/publications/') and key.endswith('.pdf'):
        LOG['pdf_links'] += 1
        return h  # left on the old host until the PDF decision (see notes.md)
    if h.startswith('/downloads/code/'):
        return h
    if h.startswith(('mailto:', '#')):
        return h
    if m:
        LOG['links_left'].append([slug, href, 'old-site link, no new target known'])
        return h
    return h


# ---------------------------------------------------------------- math/text
GREEK = {'σ': r'\sigma ', 'α': r'\alpha ', 'β': r'\beta ', 'η': r'\eta ', 'ρ': r'\rho ', 'Ι': 'I', '−': '-'}


def clean_math(m, slug, display=False):
    m = m.strip()
    orig = m
    for k, v in GREEK.items():
        m = m.replace(k, v)
    m = re.sub(r'\\{3,4}(?=\s|$)', r'\\\\', m)          # \\\ and \\\\ were meant as a line break
    m = re.sub(r'^\s*\\\\\s*', '', m)                    # no leading line break
    m = re.sub(r'\s+', ' ', m) if not display else re.sub(r'[ \t]+', ' ', m)
    if m != orig:
        LOG['math'].append([slug, orig, m])
    return m.strip()


MD_ESC = re.compile(r'([\\*_`\[\]<$~|])')


def esc(t):
    return MD_ESC.sub(r'\\\1', t)


INLINE_MATH = re.compile(r'\\\((.+?)\\\)', re.S)
DISPLAY_IN_TEXT = re.compile(r'\$\$(.+?)\$\$', re.S)


def text_to_md(t, slug, typos=True):
    t = t.replace('\xa0', ' ')
    t = re.sub(r'\s+', ' ', t)
    out, pos = [], 0
    for m in INLINE_MATH.finditer(t):
        seg = t[pos:m.start()]
        out.append(esc(fix_typos(seg, slug) if typos else seg))
        out.append('$' + clean_math(m.group(1), slug) + '$')
        pos = m.end()
    seg = t[pos:]
    out.append(esc(fix_typos(seg, slug) if typos else seg))
    return ''.join(out)


# ---------------------------------------------------------------- converter
BLOCK = {'article', 'p', 'div', 'ul', 'ol', 'blockquote', 'pre', 'table', 'figure', 'h1', 'h2', 'h3', 'h4', 'h5',
         'hr', 'iframe', 'video', 'center', 'section', 'li'}


class Conv:
    def __init__(self, slug, imgdir, md_depth='../../assets/content', head_levels=None, iframe_titles=None):
        self.slug = slug
        self.imgdir = imgdir          # dir name under assets/content
        self.assets = []              # (old image path, new filename)
        self.head_map = head_levels or {}
        self.iframe_titles = iframe_titles or []
        self.code_blocks = []
        self.video_note_used = False
        self.code_lang_hint = 'text'
        self.lang_override = {}
        self.quote_map = {}

    # ---- inline
    def inline(self, node):
        if isinstance(node, Comment):
            return ''
        if isinstance(node, NavigableString):
            return text_to_md(str(node), self.slug)
        n = node.name
        if n in ('script', 'style'):
            return ''
        if n == 'br':
            return '  \n'
        if n in ('em', 'i'):
            return self.wrap('*', node)
        if n in ('strong', 'b'):
            return self.wrap('**', node)
        if n == 'code':
            c = node.get_text()
            fence = '``' if '`' in c else '`'
            return fence + c + fence
        if n in ('sub', 'sup'):
            return f'<{n}>' + ''.join(self.inline(c) for c in node.children) + f'</{n}>'
        if n == 'a':
            if node.find('img') and not node.get_text().strip():
                return ''                      # PDF-icon links (duplicate of the title link)
            href = node.get('href')
            inner = ''.join(self.inline(c) for c in node.children).strip()
            if not href or href.startswith('#') and 'headerlink' in (node.get('class') or []):
                return inner if href else inner
            if 'headerlink' in (node.get('class') or []):
                return ''
            if not inner:
                return ''
            return f'[{inner}]({rewrite_href(href, self.slug)})'
        if n == 'img':
            return self.image(node)
        if n == 'span' or n == 'font':
            return ''.join(self.inline(c) for c in node.children)
        return ''.join(self.inline(c) for c in node.children)

    def wrap(self, mark, node):
        inner = ''.join(self.inline(c) for c in node.children)
        if not inner.strip():
            return inner
        lead = inner[:len(inner) - len(inner.lstrip())]
        trail = inner[len(inner.rstrip()):]
        return f'{lead}{mark}{inner.strip()}{mark}{trail}'

    def image(self, node):
        src = node.get('src', '')
        base = os.path.basename(src)
        alt = (node.get('alt') or node.get('title') or ALT.get(base) or '').strip()
        path = os.path.join(OLD, 'images', base)
        if not os.path.exists(path):
            LOG['misc'].append([self.slug, 'missing image', src])
            return ''
        self.assets.append((path, base))
        LOG['images'].append([self.slug, src, f'{self.imgdir}/{base}'])
        return f'![{esc(alt)}](../../assets/content/{self.imgdir}/{base})'

    # ---- blocks
    def blocks(self, children):
        out, buf = [], ''

        def flush():
            nonlocal buf
            s = buf.strip()
            if s:
                s = re.sub(r'^([-+#>]|\d+[.)]) ', lambda m: '\\' + m.group(0), s)
                out.append(s)
            buf = ''

        for c in children:
            if isinstance(c, Comment):
                continue
            if isinstance(c, Tag) and (c.name in BLOCK or c.name in ('h1',)):
                flush()
                out.extend(self.block(c))
            elif isinstance(c, Tag) and c.name == 'span' and 'videobox' in (c.get('class') or []):
                flush()
                out.extend(self.blocks(c.children))
            else:
                buf += self.inline(c)
        flush()
        return out

    def block(self, n):
        name = n.name
        cls = n.get('class') or []
        if name == 'h1':
            return []
        if name == 'div' and 'meta' in cls:
            return []
        if name == 'div' and 'math' in cls:
            m = n.get_text().strip()
            m = re.sub(r'^\$\$|\$\$$', '', m).strip()
            return ['$$\n' + clean_math(m, self.slug, display=True) + '\n$$']
        if name == 'div' and 'highlight' in cls:
            return [self.fence(n.get_text(), None)]
        if name == 'figure':
            return self.figure(n)
        if name == 'p' and 'fs-3' in cls:
            return ['**' + ''.join(self.inline(c) for c in n.children).strip() + '**']
        if name in ('div', 'center', 'section', 'p', 'article'):
            return self.blocks(n.children)
        if re.fullmatch(r'h[2-6]', name):
            for a in n.find_all('a', class_='headerlink'):
                a.decompose()
            txt = ''.join(self.inline(c) for c in n.children).strip()
            lvl = self.head_map.get(name, int(name[1]))
            txt = re.sub(r'\\?<a id=allCode\\?>', '', txt)
            return ['#' * lvl + ' ' + txt]
        if name == 'hr':
            return []
        if name in ('ul', 'ol'):
            return [self.list(n)]
        if name == 'blockquote':
            inner = self.blocks(n.children)
            body = '\n\n'.join(inner)
            return ['\n'.join(('> ' + l) if l.strip() else '>' for l in body.split('\n'))]
        if name == 'table':
            return [self.table(n)]
        if name == 'iframe':
            return [self.iframe(n)]
        if name == 'video':
            LOG['videos'].append([self.slug, [s.get('src') for s in n.find_all('source')]])
            return ['*(The original video for this tutorial is no longer available.)*']
        if name == 'pre':
            return [self.fence(n.get_text(), None)]
        return self.blocks(n.children)

    def iframe(self, n):
        attrs = dict(n.attrs)
        title = self.iframe_titles.pop(0) if self.iframe_titles else attrs.get('title', '')
        attrs['title'] = title
        order = ['src', 'title', 'width', 'height']
        keys = [k for k in order if k in attrs] + [k for k in attrs if k not in order]
        s = ' '.join(f'{k}="{attrs[k]}"' if attrs[k] != '' else k for k in keys if attrs[k] is not None)
        return f'<iframe {s}></iframe>'

    def list(self, n):
        items = n.find_all('li') if n.get('id') == 'publications' else n.find_all('li', recursive=False)
        ordered = n.name == 'ol'
        lines = []
        for i, li in enumerate(items, 1):
            mark = f'{i}. ' if ordered else '- '
            sub = self.blocks(li.children)
            if not sub:
                continue
            body = '\n\n'.join(sub)
            pad = ' ' * len(mark)
            body_lines = body.split('\n')
            first = body_lines[0]
            rest = [(pad + l) if l.strip() else '' for l in body_lines[1:]]
            lines.append(mark + first + ('\n' + '\n'.join(rest) if rest else ''))
        loose = any('\n\n' in l for l in lines)
        return ('\n\n' if loose else '\n').join(lines)

    def table(self, n):
        rows = []
        aligns = []
        for tr in n.find_all('tr'):
            cells = tr.find_all(['th', 'td'])
            rows.append([''.join(self.inline(c) for c in cell.children).strip().replace('|', '\\|') for cell in cells])
            if not aligns:
                aligns = [(c.get('align') or '') for c in cells]
        head, body = rows[0], rows[1:]
        sep = [{'center': ':---:', 'right': '---:', 'left': ':---'}.get(a, '---') for a in aligns]
        t = ['| ' + ' | '.join(head) + ' |', '| ' + ' | '.join(sep) + ' |']
        t += ['| ' + ' | '.join(r) + ' |' for r in body]
        return '\n'.join(t)

    def figure(self, n):
        cap = n.find('figcaption')
        fname, href, title = None, None, ''
        if cap:
            ts = cap.find('span', class_='liquid-tags-code-title')
            fs = cap.find('span', class_='liquid-tags-code-filename')
            a = cap.find('a')
            href = a['href'] if a else None
            fname = (fs.get_text().strip() if fs else '') or (os.path.basename(href) if href else '')
            title = re.sub(r'\s*codec:utf8\s*', '', ts.get_text() if ts else '').strip()
        # use the real downloadable file as the code body when it exists (identical modulo whitespace)
        code = n.find('pre').get_text()
        rel = None
        if href and href.startswith('/downloads/code/'):
            rel = href[len('/downloads/code/'):]
            src = os.path.join(OLD, 'downloads', 'code', rel)
            if os.path.exists(src):
                body = open(src, newline='').read().replace('\r\n', '\n').replace('\r', '\n')
                if body.strip() != code.strip():
                    LOG['misc'].append([self.slug, 'figure code differs from download', rel])
                code = body
                COPY_CODE.add(rel)
            else:
                LOG['misc'].append([self.slug, 'missing code file', rel])
        ext = os.path.splitext(fname or '')[1]
        lang = {'.py': 'python', '.m': 'matlab', '.sh': 'bash', '.submit': 'text'}.get(ext, 'text')
        head = f'**{title}**' if title else ''
        if fname:
            head += (' — ' if head else '') + (f'`{fname}`')
        if rel:
            head += f' ([download](/downloads/code/{rel}))'
        return [head, self.fence(code, lang)]

    def restore(self, code):
        out = []
        for l in code.split('\n'):
            k = re.sub(r'[\'"]', '', l).strip()
            ind = l[:len(l) - len(l.lstrip())]
            if k in self.quote_map and self.quote_map[k] != l.strip():
                new = ind + self.quote_map[k]
                LOG['misc'].append([self.slug, 'quotes restored in code snippet', [l, new]])
                out.append(new)
            elif k in LINE_FIX:
                new = ind + LINE_FIX[k]
                LOG['misc'].append([self.slug, 'quotes restored in code snippet (manual)', [l, new]])
                out.append(new)
            else:
                out.append(l)
        return '\n'.join(out)

    def fence(self, code, lang):
        code = code.replace('\r\n', '\n').rstrip('\n').lstrip('\n')
        code = '\n'.join(l.rstrip() for l in code.split('\n'))
        if lang is None:
            lang = guess_lang(code, self.slug, len(self.code_blocks), self.lang_override)
            if self.quote_map:
                code = self.restore(code)
        self.code_blocks.append((lang, code[:60]))
        f = '````' if '```' in code else '```'
        return f'{f}{lang}\n{code}\n{f}'


COPY_CODE = set()

# alt text for images that had none (descriptive only, no new claims)
ALT = {
    'sos.png': 'Example result plot from the Self-Other Game',
    'sogame-01.png': 'Illustration of step 1 of the Self-Other Game algorithm',
    'sogame-02.png': 'Illustration of step 2 of the Self-Other Game algorithm',
    'sogame-03.png': 'Illustration of step 3 of the Self-Other Game algorithm',
    'sogame-04.png': 'Illustration of step 4 of the Self-Other Game algorithm',
    'multipleSubjectResolution.png': 'Grids from multiple subjects with different offsets, shown in an upsampled standard space',
}

# snippet lines (quote-stripped) that do not occur verbatim in the full script
LINE_FIX = {
    'img = nib.load(file.nii)': "img = nib.load('file.nii')",
    'img2 = nib.load(file2.nii)': "img2 = nib.load('file2.nii')",
    'axHist2d.set_xlabel(File1.nii, fontsize=16)': "axHist2d.set_xlabel('File1.nii', fontsize=16)",
    'axHist2d.set_ylabel(File2.nii, fontsize=16)': "axHist2d.set_ylabel('File2.nii', fontsize=16)",
    'axHistx.set_title(File1.nii, fontsize=10)': "axHistx.set_title('File1.nii', fontsize=10)",
    'axHisty.set_ylabel(File2.nii, fontsize=10, rotation=-90, verticalalignment=top, horizontalalignment=center )': "axHisty.set_ylabel('File2.nii', fontsize=10, rotation=-90, verticalalignment='top', horizontalalignment='center' )",
    'mainFig.canvas.set_window_title( (File1 vs. File2) )': "mainFig.canvas.set_window_title( ('File1' + ' vs. ' + 'File2') )",
}

SHELL_START = re.compile(r'^(fslmerge|fslview|drawASlice|createAntsDag|condor_|go_ants|go_shapeUpdate|python |more |ls |cd )')


def guess_lang(code, slug, idx, override):
    first = code.split('\n')[0].strip()
    if (slug, idx) in override:
        return override[(slug, idx)]
    if SHELL_START.match(first):
        return 'bash'
    if re.match(r'^(PARENT|JOB|VARS|Executable)\b', first) or re.match(r'^(PARENT|Job)\b', first):
        return 'text'
    if re.match(r'^(import |from |def |mainFig|axHist|# |x_data|y_data|H, |nullfmt|myTicks|img|x_in|y_in|x_thr|y_fil|y = |x = |mainFig|plt)', first) or 'nib.' in code or 'axHist' in code:
        return 'python'
    return 'text'


# ---------------------------------------------------------------- helpers
def load_article(slug):
    s = BeautifulSoup(open(os.path.join(OLD, slug + '.html'), encoding='utf-8').read(), 'html.parser')
    a = s.find('div', class_='my_junk') or s.find('article')
    for t in a.find_all('script'):
        if not (t.get('type') or '').startswith('math'):
            t.decompose()
    t = a.find('time')
    date = t['datetime'][:10] if t else None
    title = a.find('h1').get_text().strip()
    return a, title, date


def q(s):
    return json.dumps(s, ensure_ascii=False)


def write(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    open(path, 'w', encoding='utf-8').write(text)


def copy_assets(conv):
    for src, base in conv.assets:
        dst = os.path.join(SITE, 'src/assets/content', conv.imgdir, base)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copyfile(src, dst)


def finish_md(blocks):
    # collapse blank-line runs only outside fenced code blocks (code must stay byte-for-byte)
    parts = [b if b.lstrip().startswith('```') else re.sub(r'\n{3,}', '\n\n', b) for b in blocks if b.strip()]
    return '\n\n'.join(parts).strip() + '\n'


def frontmatter(d):
    lines = ['---']
    for k, v in d.items():
        if isinstance(v, list):
            if not v:
                lines.append(f'{k}: []')
            else:
                lines.append(f'{k}:')
                lines += [f'  - {q(x)}' for x in v]
        elif isinstance(v, (int, float, bool)):
            lines.append(f'{k}: {str(v).lower() if isinstance(v, bool) else v}')
        elif k == 'date':
            lines.append(f'{k}: {v}')
        else:
            lines.append(f'{k}: {q(v)}')
    lines.append('---')
    return '\n'.join(lines) + '\n\n'


# ---------------------------------------------------------------- content definitions
NEWS = [
    dict(old='researchers-discover-the-brain-origins-of-variation-in-pathological-anxiety',
         slug='researchers-discover-the-brain-origins-of-variation-in-pathological-anxiety',
         summary='New findings from nonhuman primates suggest that an overactive core circuit in the brain, and its interaction with other specialized circuits, accounts for the variability in symptoms shown by patients with severe anxiety.'),
    dict(old='featured-in-isgtw', slug='featured-in-isgtw',
         summary='Some of my research was recently featured in international science grid this week (iSGTW), an international weekly online publication that covers distributed computing and the research it enables.'),
    dict(old='brain-imaging-shows-how-children-inherit-their-parents-anxiety',
         slug='brain-imaging-shows-how-children-inherit-their-parents-anxiety',
         summary='Our study aimed at understanding the mechanisms by which the risk of developing anxiety and depression is passed from parents to children received attention from the press.'),
    dict(old='fox-work-featured-on-cover-of-biological-psychiatry',
         slug='fox-work-featured-on-cover-of-biological-psychiatry',
         summary='Work from Fox was shown on the cover of the Biological Psychiatry special issue on Pediatric Anxiety Disorders.',
         legacy_extra=['/fox-lab-featured-on-cover-of-biological-psychiatry.html',
                       '/foxs-work-featured-on-cover-of-biological-psychiatry.html'],
         image=('BiologicalPsychiatry_04012021_cover.tif.jpg', 'Cover of the April 1, 2021 issue of Biological Psychiatry')),
    dict(old='fox-work-featured-on-nprs-second-opinion', slug='fox-work-featured-on-nprs-second-opinion',
         summary='Work from the Fox Lab was featured on NPR. This brief news feature focuses on our recent paper published in Computational Psychiatry.',
         iframe_titles=['KCRW Second Opinion: Waiting for test results to come back']),
    dict(old='fox-work-featured-on-the-cbs13-news', slug='fox-work-featured-on-the-cbs13-news',
         summary='Work from the Fox Lab was featured on the nightly news. This brief news feature focuses on our recent paper published in the American Journal of Psychiatry.',
         iframe_titles=['CBS13 News: UC Davis study aims to find link between how your cells contribute to anxiety, depression']),
]

TUTORIALS = [
    dict(slug='looking-at-co-registered-brain-data',
         summary='How to tell whether co-registration of brain images worked, by merging subjects into one file and viewing them as a flipbook-style movie in fslview.',
         legacy_extra=['/2013/03/20/looking-at-co-registered-brains']),
    dict(slug='python-flipbook-movies',
         summary='A short python script that writes out a flipbook movie of one slice from many subjects, used to check registration.',
         legacy_extra=['/2013/04/01/python-flipbook-movies']),
    dict(slug='running-ants-on-condor',
         summary='A walkthrough of creating a study-specific MRI template with ANTS on a Condor cluster, using bash scripts that build a DAG file.'),
    dict(slug='what-is-a-genetic-correlation',
         summary='An explanation of the genetic correlation: how the correlation between two traits can be split into genetic and environmental parts, and how heritability and bivariate heritability are estimated.'),
    dict(slug='including-voxelwise-covariates-with-multistatic',
         summary='Introduces multistatic.m, a MATLAB function that adds a voxelwise covariate to the multistat mixed-effects model, with the pluses and minuses from practical, statistical, and computing perspectives.'),
    dict(slug='read-nifti-in-fmristat',
         summary='Modified fmriStat files that use the SurfStat libraries so fmriStat can read and write NIFTI files.',
         legacy_extra=['/2013/05/30/read-nifti-in-fmristat']),
    dict(slug='visualizing-the-correlation-of-two-volumes',
         summary='Python code that plots a 2D histogram of the voxelwise relationship between two brain volumes, with a walkthrough of how it works.'),
]
ESSAYS = [
    dict(slug='ask-for-help',
         summary='Asking for help can be surprisingly difficult, and the amygdala may play a role in everyday situations like this.'),
    dict(slug='how-much-is-a-dollar-to-a-stranger-worth-to-you',
         summary='Describes the Self-Other Game, a revealed-preference dictator game that estimates how much a dollar to a stranger is worth to you, and the algorithm behind it.'),
    dict(slug='where-do-i-feel',
         summary='A proof-of-principle map of electrodermal activity matched to location, from wearing a wireless skin-conductance sensor for a few days.'),
    dict(slug='why-registration-matters-in-big-n-brain-imaging-studies',
         summary='An argument that careful inter-subject registration still matters as the N of an imaging study grows, and may even allow sub-voxel resolution in standard space.'),
]

PAGES = [
    dict(old='joining-the-fox-lab', slug='join', title='Joining the Fox Lab',
         description='The Fox Lab is often looking for undergraduate, graduate, and post-doctoral team members; email Drew to start a conversation.',
         legacy=['/joining-the-fox-lab.html']),
    dict(old='fox-lab-mission', slug='mission', title='Fox Lab Mission',
         description='The Fox Lab studies the neurobiology of affective style, guided by principles of innovation, integration, and collaboration.',
         legacy=['/fox-lab-mission.html']),
    dict(old='current-funding-in-the-fox-lab', slug='funding', title='Current Funding in the Fox Lab',
         description="Some of the most recent grants for the lab's ongoing projects, from NIH, Aligning Science Across Parkinson's, and UC Davis.",
         legacy=['/current-funding-in-the-fox-lab.html']),
]

# a few snippets whose quotes were lost by the old build; restored from the full script on the same page
QUOTE_FIX = {
    'visualizing-the-correlation-of-two-volumes': 'plotImage2Image_2dHist.py',
}


def restore_quotes(snippet_html_text_lines, full_code):
    """Return {stripped-of-quotes line: original line} from the full script."""
    m = {}
    for l in full_code.split('\n'):
        k = re.sub(r'[\'"]', '', l).strip()
        if k and k not in m:
            m[k] = l.strip()
    return m


def pre_fix_html(slug, html):
    # currency like (\$0-\$10) was mangled into math spans by the old build
    html = html.replace('(\\<span class="math">\\(0-\\\\)</span>10)', '($0-$10)')
    return html


# ---------------------------------------------------------------- run
def run_news():
    for it in NEWS:
        a, title, date = load_article(it['old'])
        conv = Conv(it['slug'], 'news/' + it['slug'], iframe_titles=list(it.get('iframe_titles', [])))
        # drop the "<!--more-->" paragraph wrappers etc. (comments ignored)
        blocks = conv.blocks(a.children)
        md = post_fix(it['slug'], finish_md(blocks))
        fm = {'title': title, 'date': date, 'summary': it['summary']}
        legacy = ['/' + it['old'] + '.html'] + it.get('legacy_extra', [])
        if 'image' in it:
            base, alt = it['image']
            path = os.path.join(OLD, 'images', base)
            conv.assets.append((path, base))
            fm['image'] = f'../../assets/content/news/{it["slug"]}/{base}'
            fm['image_alt'] = alt
        fm['legacy'] = legacy
        copy_assets(conv)
        write(os.path.join(SITE, f'src/content/news/{date}-{it["slug"]}.md'), frontmatter(fm) + md)


def run_resources(items, kind):
    for it in items:
        a, title, date = load_article(it['slug'])
        html = pre_fix_html(it['slug'], str(a))
        a = BeautifulSoup(html, 'html.parser')
        heads = sorted({int(t.name[1]) for t in a.find_all(re.compile(r'^h[2-6]$'))})
        head_map = {f'h{h}': 2 + i for i, h in enumerate(heads)}
        conv = Conv(it['slug'], it['slug'], head_levels=head_map)
        if it['slug'] in QUOTE_FIX:
            full = open(os.path.join(OLD, 'downloads', 'code', QUOTE_FIX[it['slug']])).read()
            conv.quote_map = restore_quotes(None, full)
        blocks = conv.blocks(a.children)
        md = finish_md(blocks)
        md = post_fix(it['slug'], md)
        copy_assets(conv)
        fm = {'title': fix_typos(title, it['slug']), 'date': date, 'kind': kind, 'summary': it['summary'],
              'legacy': ['/' + it['slug'] + '.html'] + it.get('legacy_extra', [])}
        write(os.path.join(SITE, f'src/content/resources/{it["slug"]}.md'), frontmatter(fm) + md)


def post_fix(slug, md):
    """Slug-specific wording fixes after conversion (all logged)."""
    subs = POST_SUBS.get(slug, [])
    for old, new in subs:
        if old not in md:
            LOG['misc'].append([slug, 'post-fix pattern not found', old])
            continue
        md = md.replace(old, new)
        LOG['misc'].append([slug, 'post-fix', f'{old!r} -> {new!r}'])
    return md


POST_SUBS = {}
_ps = os.path.join(HERE, 'post_subs.json')
if os.path.exists(_ps):
    POST_SUBS = json.load(open(_ps))


def run_pages():
    for it in PAGES:
        a, title, date = load_article(it['old'])
        if it['slug'] == 'funding':
            h = re.sub(r'\.\s*\n\s{4,}(NIH:|Aligning Science|UC Davis Behavioral)', r'.<br/>\1', str(a))
            a = BeautifulSoup(h, 'html.parser')
        conv = Conv(it['slug'], 'pages/' + it['slug'],
                    head_levels={'h4': 2, 'h2': 2})
        blocks = conv.blocks(a.children)
        md = post_fix(it['slug'], finish_md(blocks))
        fm = {'title': title, 'description': it['description'], 'legacy': it['legacy']}
        write(os.path.join(SITE, f'src/content/pages/{it["slug"]}.md'), frontmatter(fm) + md)
    run_cv()


def run_cv():
    s = BeautifulSoup(open(os.path.join(OLD, 'resumecv.html'), encoding='utf-8').read(), 'html.parser')
    art = s.find('article')
    for t in art.find_all(['script', 'style']):
        t.decompose()
    html = str(art)
    html = re.sub(r'(\d{4} – (?:present|\d{4}))\s{2,}', r'\1: ', html, flags=re.I)
    html = html.replace('Professor\nUniversity of California, Davis', 'Professor<br/>University of California, Davis')
    art = BeautifulSoup(html, 'html.parser')
    conv = Conv('cv', 'pages/cv', head_levels={'h2': 2})
    blocks = conv.blocks(art.children)
    md = finish_md(blocks)
    md = post_fix('cv', md)
    fm = {'title': 'Resume/CV',
          'description': 'Curriculum vitae of Andrew S. Fox: positions, awards, committees, talks, teaching, skills, and publications.',
          'legacy': ['/resumecv.html']}
    write(os.path.join(SITE, 'src/content/pages/cv.md'), frontmatter(fm) + md)
    n_li = len(art.find('ul', id='publications').find_all('li'))
    LOG['misc'].append(['cv', 'publication entries in source', n_li])


def copy_code():
    for rel in sorted(COPY_CODE):
        src = os.path.join(OLD, 'downloads', 'code', rel)
        dst = os.path.join(SITE, 'public/downloads/code', rel)
        os.makedirs(os.path.dirname(dst), exist_ok=True)
        shutil.copyfile(src, dst)
    # also copy any code file in the old tree not referenced (none expected); log
    root = os.path.join(OLD, 'downloads', 'code')
    allf = {os.path.relpath(os.path.join(d, f), root) for d, _, fs in os.walk(root) for f in fs}
    LOG['misc'].append(['code', 'old code files not linked from any page', sorted(allf - COPY_CODE)])


if __name__ == '__main__':
    run_news()
    run_resources(TUTORIALS, 'tutorial')
    run_resources(ESSAYS, 'essay')
    run_pages()
    copy_code()
    json.dump(LOG, open(os.path.join(HERE, 'extract-log.json'), 'w'), indent=1, ensure_ascii=False)
    print({k: (len(v) if isinstance(v, list) else v) for k, v in LOG.items()})
