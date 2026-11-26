# Fox Lab website: audit of the current site

Audit date: 2026-11-26. Site: <https://foxlab.ucdavis.edu> (repo `asfox/asfox.github.io`, branch `master`).

All numbers below come from scripts run on the built files, or from Lighthouse, axe-core, and Playwright runs on 9 sample pages, both locally and on the live site. Where a statement is an inference, it says so.

Supporting files:
- `data/inventory.csv`: one row per page (232 rows), with title, category, date, inferred type, word count, and PDF links.
- `screenshots/`: phone (390 px) and desktop (1440 px) captures.
- `research/`: the stack comparison and the design-practice research, with sources.

---

## 1. What the repo is

| Fact | Value |
|---|---|
| Generator | Pelican, with an Octopress-derived Bootstrap theme ("designed by Adrian Artiles, adapted by Drew Fox") |
| What is committed | **Only the built HTML output.** No Markdown, no `pelicanconf.py`, no theme templates. They are not in any of the 50 commits either. |
| Hosting | GitHub Pages, custom domain `foxlab.ucdavis.edu` (CNAME). `asfox.github.io` and `http://` both redirect (301) to it. The live files are byte-identical to `master`. |
| Last build | 2026-09-25 |
| Size | 640 MB working tree. **585 MB of it (91 %) is 125 PDFs.** The git pack is 572 MB. |
| Files | 715 HTML pages, 125 PDFs, 62 images, about 115 theme files |

**Consequence:** the site can't be edited or rebuilt from this repo. Any change to `master` is lost at the next Pelican build from the PI's machine. A redesign must either get the Pelican source from the PI, or rebuild the content from the HTML. Section 7 shows that the HTML can be parsed reliably.

---

## 2. Current information architecture

### 2.1 Navigation

- The top bar has **one link**: an unlabeled house icon to `/`.
- The real menu (cv, news, people, posters, publications, thoughts, tutorials) is **commented out** in the template. There are three abandoned attempts in the HTML, one labeled "co-pilot suggested untested".
- Visitors can reach sections only through a run-in "categories" text list in the homepage sidebar and the footer: `cv (1) news (6) people (9) posters (69) publications (109) thoughts (7) tutorials (7)`.
- `authors.html`, `categories.html`, and `tags.html` are linked from nowhere. `tags.html` is empty, because no page has tags.

### 2.2 Homepage (`index.html`)

From top to bottom:
1. A blue hero (about 550 px tall) with a gold brain line drawing: "FoxLab / Translational Affective Neuroscience".
2. **"about me"**, in the first person ("I am a professor in the Psychology Department…"). The homepage presents the PI personally, not the lab.
3. "recent publications": the 3 newest papers.
4. Six "post" cards, in this order: CBS13 news (2024), NPR (2024), Funding (2022), Biological Psychiatry cover (2021), Mission (2016), Joining (2016).
5. Footer: recent posts (a new member profile shows up here as a "post"), a Twitter timeline that does not render, the categories list, and a DataLab logo.

### 2.3 Content model, as built

Pelican "articles" do every job. A paper, a poster, a person, and a press item are each a dated blog post.

| Inferred type | Pelican category | Live pages | What a page contains |
|---|---|---|---|
| Journal article | publications | 91 | One citation line and a PDF icon (median 37 words) |
| Book chapter | publications | 18 | One citation line (14 are chapters of *The Nature of Emotion*, 2018) |
| Poster / talk | posters | 69 | One citation line. 45 of them have no PDF. |
| Person profile | people | 19 (9 current, 10 former) | Headshot and a short bio |
| News / press | news | 6 (2013–2024) | Short prose with an embed |
| Tutorial | tutorials | 7 (all 2013) | Long code how-tos (up to 6,581 words) |
| Thought | thoughts | 4 essays + mission, joining, funding | Prose |
| CV | cv | 1 | 5,220-word page with its own layout |
| **Total live** | | **218** | |

There are also 476 auto-generated author pages and 8 stale, unlisted duplicate articles (see 3.1).

**82 % of live pages (178 of 218) are one-line citation stubs.** On the category pages, the "Publications" and "Posters" lists show the citations inline and do not link to these stub pages. So most stub pages are reachable only from search engines, the archive, and the "recent posts" box.

### 2.4 Themes in the content (input for a "Research" section)

There is no Research page. The mission (2016) and the funding page (2022) describe these lines of work (my grouping, to be confirmed by the PI):
- Primate anxious temperament and behavioral inhibition across development (R01 MH121735)
- Uncertain-threat anticipation: computational models, fMRI, and experience sampling (R21 MH129851, R01 MH131264)
- Cell-type-specific viral tools for primates (U01 MH128336, with Gradinaru)
- Gut-to-brain circuits and Parkinson-like phenotypes (ASAP)

---

## 3. Content and data quality

### 3.1 Duplicates and stale pages
- **8 published pages are in no index or sitemap, but they still exist and can be indexed.** They are:
  - `ander-et-al-molecular-psychiatry-2025` (twin of `-2026`)
  - two copies of the Biological Psychiatry cover news item (`foxs-…`, `fox-lab-featured-…`)
  - `campos-drzewiecki-fox-…-2024` (twin of `-2025`)
  - `holley-fox-…-2022` (twin of `-2025`)
  - `davidson-et-al-2006` (twin of `-2007`)
  - `shackman-et-al-2016` (twin of `…-2017-2017`)
  - `cuapoco-et-al-bioarxiv-preprint`
- **Live near-duplicates:**
  - `oler-tromp-et-al-2016` and `oler-tromp-et-al-bsf-2017-2017` (same paper, same PDF)
  - the two Campos SoBP 2022 pages
- **`drafts/your-post-title.html` is live.** It is the stock Octopress demo from 2012 and contains broken scripts.

### 3.2 Names, slugs, and typos
- **18 slugs repeat the year,** for example `hur-et-al-bbs-2019-2019`.
- **Slug typos:** `emotoin`, `shackma`, `lapte`, `gorgans` (Grogans), `cuapoco` (Chuapoco), `bioarxiv`, `principle-investigator`.
- **Text typos:** "recieved", "Reseach", "nighly", "CHen", "Communicatoins", "Psyhchiatry", "Guildford", "Permision", "Transporder".
- **Four pages have a date that disagrees with the year in the title.** For example, `fox-cns-2018` is dated 2014.
- **Venue names are spelled more than one way:** "Neuroimage" vs "NeuroImage", and "Journal of Neuroscience" vs "The Journal of Neuroscience".
- **Author names are fragmented across 476 author pages.** Kalin alone has 8 variants (`kalin-nh`, `and-kalin-nh`, `nh`, `kalin`…). Fox appears as `fox-as` and `drew-fox`. 15 pages have one-token slugs such as `d`, `hc`, and `se`. Every author page shows the PI's "about me" text, not that author's papers.

### 3.3 Out-of-date facts
- The PI is "Associate Professor" on the People page and bio, but "2026 – present Professor" on the CV.
- Profiles still describe former members as current. For example, Rani Purewal is an "incoming graduate student", and Lillian Campos is a "Graduate Student" although she has defended.
- The lab photo is from July 2022, but members who joined in 2024 and 2025 are listed.
- The "Joining" text (2016) says "check our my publications".
- No page shows a "last updated" date.

### 3.4 Assets
- **PDFs:**
  - 35 PDFs are larger than 5 MB, and 16 are larger than 10 MB. The largest is a 34 MB SfN 2024 poster.
  - Many of the article PDFs appear to be publisher versions (not checked one by one). The publications page says "Permision to use these files is granted for personal use only. Please do not distribute", but serves them publicly. (This is a rights question, not a finding of a violation. See the proposal, §5.)
- **Orphan files:** 6 PDFs (including a 30.5 MB "UCLA publication packet"), 27 images, a duplicate `code/` folder, and an unused 17 MB local MathJax 3 tree.
- **Missing files:** both tutorial videos (`video/t1.mp4`) and `tomorrow.css`.
- **Hard-coded domain:** 3,387 links point to `https://asfox.github.io/…`. Each one costs an extra redirect, and a local build pulls production files.

---

## 4. Technical debt

| Area | Finding |
|---|---|
| CSS/JS | Bootstrap 5.0.0-**beta1**, with class names from Bootstrap 2 and 3 mixed in. jQuery 2.1.4 (probably unused), Modernizr 2.8.3, and Twitter `widgets.js` loaded twice per page. About 1.4 MB per page before any content images. |
| Dead integrations | Twitter timeline (throws `hydrateRoot is not a function` on every page), plus Instagram, Pinboard, GitHub, and Disqus scripts (commented out but still shipped) |
| Broken links | **3,197 broken internal link instances** across 21 targets. 99.7 % are on author pages, where relative "Read on →" links resolve under `/author/`. |
| SEO metadata | `canonical href=""` on 479 pages and a relative canonical on the rest. No Open Graph, no JSON-LD, no Google Scholar `citation_*` tags. `sitemap.xml` uses relative URLs, which the sitemap protocol does not allow. No `robots.txt`, no `404.html`, no RSS. |
| Analytics | None at all |
| Old templates | 58 pages use an older template with no nav |

---

## 5. Measured quality (Lighthouse 12, axe-core, Playwright)

| Page | Perf (phone) | Perf (desktop) | Accessibility | SEO | LCP (phone) | Page weight |
|---|---|---|---|---|---|---|
| Home | 77 (live: 83) | 99 | **47** | 82 | 4.2 s | 1.3 MB |
| People | 67 | 77 | 54 | 75 | **29.0 s** | **17.3 MB** |
| Profile (kyle-puhger) | 67 (live: 73) | 90 | 67 | 83 | 11.9 s | 2.4 MB |
| CV | 76 | 98 | 55 | 75 | 4.2 s | 1.0 MB |
| Archives | 77 | 98 | 61 | 75 | 4.2 s | 1.1 MB |
| Publication stub | 73 | 99 | 61 | 83 | 5.1 s | 1.0 MB |

The table shows local runs on an uncompressed server, with live values where they were measured. Lighthouse simulates a slow 4G connection. Each value is one run, so scores can vary by a few points.

### 5.1 Ranked issues, by effect on users
1. **No usable navigation** on any of the 715 pages.
2. **People page weighs 17 MB:**
   - `ShawnKamboj.png` is 5.3 MB but displays at about 135 px.
   - Four other headshots and the lab photo are 1.5–2.4 MB each.
   - Lighthouse estimates 16 MB of savings.
3. **Color contrast fails on every page:**
   - Link blue `#428bca` on white is 3.6:1, and the grey dates `#b3b3b1` are 2.1:1. WCAG AA needs 4.5:1.
   - The archives page has 671 failing nodes.
4. **Images lack alt text:** 7,304 of 8,540 `<img>` (86 %) have no `alt`. Most are the repeated PDF icon and the social icons.
5. **Links lack accessible names:** 4–7 per page, and 99 on the CV.
6. **The Twitter embed is broken everywhere:** it adds 190–330 KB and console errors, and shows nothing.
7. **Mobile layout breaks:**
   - Tutorial code blocks make pages 1,338 px wide on a 390 px phone.
   - The People page overflows by 11 px.
   - Tap targets are smaller than 24 px on every page.
8. **Structure:** no `<main>`, no skip link, headings skip levels on all pages, and category pages have no `<h1>`.

What passes:
- Every page has `lang="en"` and a viewport meta tag.
- HTTPS is valid.
- No mixed content.
- Keyboard focus is visible.
- Total Blocking Time is 0 ms.
- CLS is about 0.

### 5.2 Compliance context
- The US DOJ ADA Title II rule requires **WCAG 2.1 AA** for public universities. On 2026-04-20, an interim final rule moved the date for large entities to **2027-04-26**.
- UC policy IMT-1300 requires WCAG 2.1 AA for websites and PDFs, and an accessibility statement.
- The current site would not pass (accessibility scores 47–67, with contrast, alt-text, and name failures on every page).
- Sources are in `research/design-practices.md`. Recheck the dates before you rely on them, because DOJ has moved them once already.

---

## 6. Screenshots

- `screenshots/index.390.png`: the phone homepage. The only nav is the house icon, and content starts below a large hero.
- `screenshots/grogans-et-al-journal-of-neuroscience-2024.1440.png`: a typical publication page, a single citation in a big card.
- `screenshots/running-ants.390.png`: a tutorial with horizontal overflow on a phone.

---

## 7. What can be reused

- **Structured content can be extracted reliably.** The inventory script matched all 218 live pages to a category, with 0 ambiguous matches. The only unmatched page is the stale bioRxiv page. The citations sampled follow one pattern (`Authors (Year). Title. Journal. vol(issue):pages`). A full parse will still need a manual review list. That makes an automated export to `publications.yml` / BibTeX feasible, with DOI lookup as a second pass.
- **The brand identity is worth keeping:** gold brain line art on deep blue, close to UC Davis Aggie Blue and Gold.
- **Tutorials and the mission text are real, distinctive content.**
