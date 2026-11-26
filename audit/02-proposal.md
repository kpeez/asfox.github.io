# Fox Lab website: proposed reorganization and redesign

This proposal builds on `01-current-site-audit.md`. Each recommendation gives the finding it fixes. Points that need a decision from the PI are listed in §9.

## 0. Summary

1. **Reorganize the content by what it is, not by date.** Today every paper, poster, and person is a dated blog post. Instead, keep papers, people, and news as structured data files, and generate the pages from them.
2. **Make the homepage a lab front door, not a personal page,** and give the site a real menu: Research · People · Publications · News · Resources · Join.
3. **Leaving Pelican is reasonable but not required.** The Pelican source isn't in the repo, so the content must be extracted from the HTML anyway. That removes most of the cost of a stack change. My first choice is **Jekyll with the Greene Lab "Lab Website Template"**, and **Quarto** is a close second. Choose between them with a one-day build of both (§4).
4. **Build to WCAG 2.2 AA from day one.** UC policy and the ADA Title II rule require WCAG 2.1 AA by 2027-04-26 (recheck this date). Today's accessibility scores are 47–67.
5. **Deal with the 585 MB of PDFs.** Link to the DOI or an open-access copy first. Host only files the lab has the right to share, compressed.

---

## 1. Target information architecture

```
/                 Home: who we are (2 sentences), research themes (3–4 cards),
                  latest news (3), recent papers (3), "Join us" call to action
/research/        One section per theme: question, approach, key papers, funding
/people/          Current members (grid), then Alumni with a "now at" line
/people/<name>/   Profile: photo, role, start year, bio, links, their papers
/publications/    One filterable list: Journal articles · Chapters · Preprints
                  Filters: year, type, theme, author. Text search.
/presentations/   Posters and talks (the 69 posters), the same list design
/news/            Press and lab news, newest first
/resources/       Tutorials (7), code (code/ downloads), datasets, tools
/join/            Open roles, what we look for, how to contact
/cv/              PI CV (or a link to a PDF)
/accessibility/   Accessibility statement (required by UC IMT-1300)
404.html, robots.txt, sitemap.xml (absolute URLs), feed.xml
```

Why these sections:
- **The audiences are applicants, collaborators, funders, and press.** NN/g research on academic sites found that applicants want to know the faculty, see authentic images, and use good internal search (`research/design-practices.md` §1).
- **Research gets its own section** because the site has none today. The theme text can start from the funding and mission pages (draft themes are in audit §2.4, pending PI approval).
- **Presentations are separate from Publications.** Today, 69 posters sit beside 109 papers and bury them.
- **Thoughts and tutorials move into Resources.** All seven tutorials date from 2013. Keep them for their value, but stop presenting them as news.
- **No "Participate" page by default.** The lab is mainly a primate lab ("primarily study nonhuman primates", Join page). Add one only if there are human studies that recruit.

### Remove or merge

| What | Count | Action |
|---|---|---|
| Stale duplicate articles | 8 | Delete, and redirect each one to its live twin |
| Live near-duplicates | 2 pairs | Merge into one entry each |
| `drafts/your-post-title.html` | 1 | Delete |
| Author pages | 476 | Delete. Each person's papers appear on their profile and through the publications author filter. |
| Tag and category index pages | — | Replaced by the new sections |
| Citation-stub pages | 178 | Delete as pages. Each becomes an entry in the publications data file, and its old URL redirects to `/publications/#<id>`. Make a detail page only where it adds something: abstract, figure, code, data, or press. |
| Orphan files | 6 PDFs, 27 images, duplicate `code/`, local MathJax tree (17 MB) | Delete |
| Twitter, Instagram, Pinboard, Disqus, Modernizr, jQuery | — | Delete |

---

## 2. Content model: functional units

Store all content as plain text that a grad student can edit in the GitHub web editor. Any of the candidate stacks can read this layout. The structure is the main deliverable, and it is not tied to one tool.

```
_data/publications.yaml   # or .bib — one entry per paper/chapter/preprint
_data/presentations.yaml  # posters & talks
_data/people.yaml         # or one Markdown file per person
_data/themes.yaml         # research themes; papers tag into them
_data/funding.yaml
news/YYYY-MM-DD-slug.md
resources/tutorials/*.md  # code blocks, MathJax where needed
pages/{join,cv,accessibility}.md
```

One publication entry looks like this. With the Greene Lab template, the DOI alone fills in the rest:

```yaml
- id: grogans2024jneurosci
  doi: 10.1523/JNEUROSCI.xxxx-xx.2024      # placeholder; looked up via Crossref, then checked
  type: journal            # journal | chapter | preprint
  themes: [uncertain-threat]
  lab_authors: [fox]       # links to people/; bolded in the list
  pdf: null                # only if the lab may host it (see §5)
  links: {pubmed: , code: , data: , press: }
```

One person entry:

```yaml
- id: kyle-puhger
  name: Kyle Puhger
  role: Postdoctoral Scholar
  status: current          # current | alumni
  start: 2022-08
  end:
  now_at:                  # alumni only
  photo: people/kyle-puhger.webp   # 800 px source, resized at build
  links: {orcid: , scholar: , github: }
  bio: >-
    …
```

These fields fix specific audit findings:
- `status` and `now_at` fix the stale "is a graduate student" profiles.
- `lab_authors` replaces the 476 fragmented author pages.
- `doi` lets the build pull consistent titles and venues. That fixes the 18 doubled-year slugs and the "Neuroimage"/"NeuroImage" variants at the source.

### Migration path from the current HTML

1. A script turns `data/inventory.csv` plus each page's citation text into draft YAML.
2. A second pass looks up DOIs through Crossref by title and year. Matches below a confidence threshold go to a review list. Do not accept a DOI without a check.
3. The PI or a lab member checks the review list, together with the typo list in audit §3.2.
4. Map every old URL to its new place. Generate redirect stubs, because GitHub Pages can't send server-side 301s.
5. The build fails if any old URL from `sitemap.xml` has no redirect.

---

## 3. UI and visual design

Direction: **calm, typographic, fast.** Keep the existing identity, the gold brain line art on deep blue. It is distinctive and already close to UC Davis Aggie Blue `#022851` and Gold `#FFBF00` (the brand values were found only in search snippets; confirm them with UC Davis Strategic Communications).

**Layout**
- A sticky header with the lab wordmark and 6 text links. It turns into a disclosure menu below about 720 px.
- A short hero (no more than 40 vh) with one sentence and the brain mark. Content starts above the fold on a phone.
- Body column at most 68ch wide. Profile and publication lists are full width.

**Type and color**
- System font stack. Proxima Nova, the UC Davis brand font, has an unconfirmed web license outside SiteFarm.
- Body text 17–18 px, line height about 1.55, and one modular scale for headings.
- Color tokens defined on `:root`, with a dark-mode override.
- Gold is an accent on blue only. Gold on white fails text contrast.
- All text must reach 4.5:1 contrast. That replaces today's `#428bca` link blue (3.6:1) and `#b3b3b1` grey dates (2.1:1).

**Components**
- **Publication list:**
  - Grouped by year, with filter chips (type, theme, lab author) and a text filter.
  - Each entry has buttons for DOI · PubMed · PDF · Code · Data · Cite (BibTeX).
  - The full list renders as plain HTML. The filters are a progressive enhancement of about 5 KB of JS, so the list works without JS.
- **People grid:** square photos (WebP, `srcset` at 200/400/800 px), name, role, and a link to the profile. Alumni appear as a compact list with a "now at" line.
- **Theme cards on the home and research pages:** an image, a 2-line summary, and a link to the papers for that theme.
- **Code blocks:** `overflow-x: auto` inside the block, so the page itself never scrolls sideways. That fixes the 1,338 px tutorial overflow.

**Restraint rules** (adapted from Anthropic's `frontend-design` skill guide, see `research/design-practices.md` §5):
- No gradient washes.
- No fade-in on every section.
- No identical rounded-card grids for everything.
- Honor `prefers-reduced-motion`.
- Make the one bold choice the brain mark and the blue band.

**Performance budget:** HTML and CSS under 50 KB, JS under 30 KB, and an LCP image under 150 KB on each page. These limits are my judgment, set well inside web.dev's 170 KB critical-path guidance. On the People page alone this cuts about 16 MB.

**Accessibility floor (WCAG 2.2 AA):**
- `<main>`, a skip link, and one `<h1>` per page with no skipped heading levels.
- Alt text required by the data schema: the build fails if a photo has no `alt`.
- Tap targets of at least 24 px.
- Visible focus that the sticky header doesn't hide.
- PDFs hosted by the lab must also be accessible. This is a strong reason to link out rather than host.

**Metadata:**
- Absolute canonical URLs.
- Open Graph tags.
- JSON-LD for `Organization`, `Person`, and `ScholarlyArticle`. This gives no rich-result gain, but it is cheap.
- Google Scholar `citation_*` tags only on detail pages that host full text.

---

## 4. Stack recommendation

Ranking for this lab: maintainers are scientists who should be able to add a paper or a person by editing one file, and hosting is free on GitHub Pages. Full table and sources: `research/stack-comparison.md`.

| Rank | Stack | Why | Main risk |
|---|---|---|---|
| **1** | **Jekyll + Greene Lab Lab Website Template** (v1.4.1, 2026-11-11, BSD-3) | Built for labs: team, research, and blog sections. A paper is one `id: doi:…` line, with ORCID/PubMed import. A person is one Markdown file. PR preview sites and an Actions deploy are included. Nobody has to install Ruby if edits go through GitHub. | Jekyll core releases are slow (last gem 2025-01). The template is maintained by one lab. 69 posters and 18 chapters have no DOI and need manual fields. |
| **2** | **Quarto website** | Fits the lab's Python habits (the PI leads a Python User Group). Best for the code tutorials: notebooks render directly, with MathJax built in. Used by poldracklab.org. Backed by Posit. | No built-in publications page. It needs a custom listing template over YAML and a small DOI-lookup script. |
| 3 | Stay on Pelican with a new custom theme | Python, and the toolchain the PI already knows | No maintained lab theme exists. The publications page and theme would be all custom work. Without the source, there is no migration advantage. |
| — | al-folio, Hugo/HugoBlox, Astro, Eleventy | Not recommended. al-folio is built for one person's homepage, not a lab roster, and its v1 restructure is recent. HugoBlox has had repeated renames and breaking changes. Astro and Eleventy have no maintained lab template, so the build would be bespoke and harder for non-developers. | |

**Hosting:** stay on GitHub Pages and deploy with GitHub Actions. Keep the `foxlab.ucdavis.edu` CNAME. Limits: 1 GB site and 100 GB/month bandwidth (soft). Moving the PDFs out (§5) removes the only size risk. Cloudflare Pages is the fallback if the site ever needs server-side redirects.

**Settle it with a one-day spike, not opinion.** Port 10 papers (including 2 posters and 1 chapter), 3 people (1 alumnus), and 1 tutorial into options 1 and 2. Score each one on:
1. Can a grad student add a paper through the GitHub web UI alone?
2. Are the old URLs kept through redirects?
3. axe: 0 violations on the sample pages.
4. Lighthouse mobile performance of at least 95.
5. Build time and failure modes in Actions.

**Continuous integration (either stack):**
- `lychee` link check, run weekly and on each PR.
- `pa11y-ci` with axe over the sitemap, run on each PR.
- Image resizing at build time.
- Schema validation of the YAML files.

---

## 5. PDFs and copyright

The site serves 125 PDFs (585 MB). About 100 are journal articles or chapters, and many appear to be publisher versions (not checked one by one). They sit under a notice that says "personal use only. Please do not distribute". The proposal:
1. **Each paper links first to the DOI**, then to a free copy: PMC, eScholarship, or a preprint. Under the UC open-access policy, a UC-authored accepted manuscript can go to eScholarship. Check each journal's terms in Sherpa Romeo.
2. **Host only lab-owned files:** posters, slides, and accepted manuscripts where the publisher allows it. Compress posters with Ghostscript (target under 5 MB; the largest today is 34 MB).
3. **UC IMT-1300 includes PDFs in its WCAG requirement,** so each hosted PDF also needs tags and alt text. That is another reason to host fewer.
4. Keep the full PDF archive out of the website repo, for example in lab storage. Git history keeps the 572 MB pack regardless. A new repo, or a new branch with fresh history, would drop it. That is a decision for the PI.

This is not legal advice. Confirm with the UC Davis Library's scholarly-communication office.

---

## 6. Phased plan

| Phase | Work | Output |
|---|---|---|
| 0. Decide | Answer the questions in §9. Get the Pelican source if it exists. | Decisions logged |
| 1. Extract | Script from HTML or source to YAML/Markdown. Crossref DOI pass. Human review list. Typo fixes. | `_data/*.yaml`, `news/`, `resources/`, URL map |
| 2. Spike | Port the 10/3/1 sample to the top 2 stacks and score them (§4). | Pick one stack |
| 3. Build | Templates, design tokens, publication filter, people grid, research pages, CI (lychee, pa11y, schema). | Preview site from a PR |
| 4. Review | The PI and lab review the preview. Keyboard and screen-reader pass. Phone check. | Sign-off |
| 5. Cut over | Deploy to Pages on the same domain. Redirect stubs for all 218 live URLs and the 8 stale ones. Submit the sitemap to Search Console. | Live site |
| 6. Maintain | README "how to add a paper or person". PR template. Weekly link-check issue. | Lasting process |

Phases 1 and 2 are mostly scripted. Phase 3 is the bulk of the work.

---

## 7. Acceptance checks for the new site

These are the outside measures that show the redesign worked. Use the same tools as in the audit, so the before and after compare directly.

| Check | Today | Target |
|---|---|---|
| axe violations, sample pages | 20–671 nodes per page | 0 |
| Lighthouse accessibility | 47–67 | 100 |
| Lighthouse mobile performance | 67–83 | ≥ 95 |
| People page weight | 17.3 MB | < 1 MB |
| Broken internal links | 3,197 | 0 (lychee in CI) |
| Old URLs that resolve (redirect or page) | — | 226 of 226 |
| Pages with a visible nav | 0 of 715 | all |
| Valid sitemap, robots.txt, 404, canonical | no | yes |

---

## 8. What this proposal does not decide

- **Research theme text and images** come from the PI. §2.4 of the audit is only a draft grouping.
- **Final colors and logo use** need UC Davis brand guidance. The official brand pages returned 403 to the research agent.
- **Whether to add analytics.** Plausible, Umami, and GoatCounter are cookieless options. No UC Davis requirement was found. The simplest choice is none.

---

## 9. Decisions needed from you or the PI

1. **Does the PI have the Pelican source** (Markdown and `pelicanconf.py`)? If yes, extraction is easier, but the recommendation does not change.
2. **Lab site or PI site?** The homepage is currently first person. Recommendation: lab site, with the PI on `/people/andrew-fox/` and `/cv/`.
3. **Stack:** approve the one-day spike of Greene Lab template vs Quarto, or name a preference now. For example, Quarto if the PI wants tutorials written as notebooks.
4. **PDFs:** approve "link out first, host only lab-owned files".
5. **History:** keep the 572 MB git history, or start the new site in a new repo or branch with fresh history?
6. **Who maintains it** after launch? This sets how much the README and CI must carry.
7. **Does any human study recruit participants?** If yes, add a Participate page.
