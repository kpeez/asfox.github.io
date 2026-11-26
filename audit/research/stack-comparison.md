# Static-site stack options for the Fox Lab website (foxlab.ucdavis.edu)

Research date / "today": 2026-11-26. All sources accessed 2026-11-26 unless noted.
Convention: **[unverified]** = I could not confirm from a primary source (official docs, repo page/feed, package registry, the site itself). Where a date is derived from a GitHub Atom feed, PyPI, RubyGems, or npm, that is a primary registry/repo record.

Method limits (be aware): GitHub REST API and `gh` were blocked in this session, so repo activity comes from github.com HTML pages and `.atom` feeds, which do give full timestamps. The GitHub release *pages* only show "day month" without year; I used the Atom/registry dates instead. UC Davis web pages (sitefarm.ucdavis.edu, lsit.ucdavis.edu, communicationsguide.ucdavis.edu) returned HTTP 403 to my fetcher, so all UC Davis policy statements below come from search-result snippets and are **[unverified]** until someone reads the pages. I did not build a prototype in any stack; "learning curve" and "accessibility" judgments are my assessment, not measurements.

## 0. What the current site is (observed)

- foxlab.ucdavis.edu footer: "Powered by Pelican. Originally designed by Adrian Artiles and adapted by Drew Fox." Categories: cv, news, people, posters, publications, thoughts, tutorials. Twitter embed still on home page. No UC Davis logo, Regents copyright line, or accessibility statement visible in the text extraction (visual-only branding can't be ruled out).
- The repo's built output has one HTML page per paper, poster, person and news item (flat URLs like `/fox-et-al-pnas-2015.html`). Whatever stack is chosen, **preserving these URLs (or 301-style redirect stubs) matters** because papers and posters are linked from CVs, Google Scholar, and press pages. GitHub Pages cannot send real 301s; use meta-refresh stubs or keep the permalink pattern.

## 1. Comparison table

| | (a) Pelican + new theme | (b) Jekyll + Greene Lab template | (c) Jekyll al-folio | (d) Hugo + HugoBlox | (e) Quarto website | (f) Astro (+ scholar templates) | (g) Eleventy |
|---|---|---|---|---|---|---|---|
| Language / toolchain | Python (4.12.0 needs Python >= 3.11, Docutils 0.22+) | Ruby + Jekyll; citations step is Python (Manubot) run in CI; local preview via Docker/Ruby | Ruby + Jekyll, plugin gems (v1.x); Docker supported | Go binary (Hugo Extended) + Node (README: "Requires Hugo Extended & Node.js"); Hugo Modules need Go | One binary (Quarto, bundles Pandoc/Deno); Jupyter/R only needed if executing code | Node.js (Astro 7.x; GitHub action default Node 24) | Node.js (docs: Node 18+, even releases recommended) |
| Install pain for scientists | Low (pip) | Medium locally (Ruby/Docker); **low if they only edit on github.com and let Actions build** | Medium (Ruby/Docker) | Medium-high (Hugo + Go + Node, module system) | Low (installer) | Medium (Node, npm, config in JS/TS) | Medium (Node, JS data files) |
| Publications model | Markdown articles per paper today; BibTeX via `pelican-pybtex` (MIT, 1.0.2, 2026-03-06) or other plugins (most are abandoned: pelican-bib 2018, pelican-publications 2015) | `_data/sources*.yaml`: one `id: doi:...` line per paper; Manubot builds `citations.yaml`. Also ORCID/PubMed/Google Scholar (SerpAPI key) "metasources". Extra fields: `type`, `description`, `image`, `buttons`, `tags`, `repo` | BibTeX file via jekyll-scholar (`al_folio_core`); citation-count badges via `al_citations` | One page bundle (folder + `index.md` + optional `cite.bib`) per paper; authors as slugs into `data/authors/*.yaml`; BibTeX import via `academic import` CLI or Ownable VS Code ext. | No native BibTeX *publications page*. Options: `bibliography:` + `nocite: @*` (renders a CSL list; no per-item PDF buttons), or YAML-backed **listing** with custom EJS template (arbitrary fields, e.g. `pdf:`), or community scripts converting .bib to .qmd | Templates differ: astro-scholar (`src/data/publications.bib`), scholar-lite (`citations.bib`, buttons for PDF/code/video) | No academic template found; plugins `eleventy-plugin-bibtex`/`-citations` exist; one lab site (hoglelab) keeps publications in `_data` [unverified details] |
| DOI/ORCID auto-citation | No (manual or BibTeX) | **Yes, native** (DOI, PMID/PMCID, arXiv, ISBN, URL; ORCID metasource) | Partial: BibTeX in; Scholar citation counts via workflow | No auto fetch in the free docs I read | No native; community scripts (e.g. ADS/ORCID to qmd) | No native | No native |
| People model | Per-person Markdown file (as now) | `_members/*.md` per person (front matter: role, bio, links); docs page for team not retrieved | `_data` people page (profile-oriented; lab-roster fit not verified) | `data/authors/*.yaml` + author pages; lab "Research Group" themes exist separately | Listing of `people/*.qmd` or YAML | `authors.json`/team collection (themes) | Roll your own |
| GH Pages deploy | Official reusable workflow `getpelican/pelican/.github/workflows/github_pages.yml`; CNAME via `EXTRA_PATH_METADATA` | Template ships Actions + PR previews; built-in GH Pages Jekyll is pinned at 3.10.0 (pages.github.com/versions, 2025-08-13) so Actions-based builds are the norm | Actions `deploy.yml` | Actions workflow; Hugo Blox docs say free hosting on GH Pages/Netlify/Vercel/CF Pages | `quarto-dev/quarto-actions` (setup@v2, publish@v2) or render to `docs/`; CNAME file at project root | Official `withastro/action@v6` + `deploy-pages@v5`; `public/CNAME` | Static `_site`; generic Actions |
| Maintenance (primary, dated) | Pelican 4.12.0 on 2026-04-20; 4.11.0 2025-01-15 (+post0 2025-10-30); commits 2026-11-09. **Themes stale**: Papyrus last commit 2023-10-27, Flex 2025-06-04, Elegant only dependabot merge 2026-05-11 (real work 2022-23) | Template v1.4.1 on 2026-11-11 (also 1.4.0 2026-08-03 security fix; 1.3.9 2026-06-02; 1.3.8 2025-11-17; 1.3.7 2025-07-30). Jekyll itself: last gem 4.4.1 on 2025-01-29, but repo commits through 2026-10-13 | al-folio v1.0 2026-06-02, v1.1 2026-07-30, v1.2 2026-08-09, v0.16.3 2026-01-20; repo commits 2026-11-23 (bot-only recently). 16.4k stars, 4 maintainers | `HugoBlox/kit`: modules/blox v0.12.0 2026-04-02, v0.11.0 2026-01-02; main-branch feed last entry 2026-05-27 (so quiet since then [feed may be incomplete]); Hugo itself v0.170.1 2026-11-17 | Quarto "Latest" tag v1.11.9 (30 Oct; year not shown on page, 2026 inferred); feed also lists v1.12.0-1.12.3 (2026-11-02..17) unmarked; poldracklab.org is built with quarto-1.11.9 | Astro 7.4.13 on 2026-11-18; 7.0 on 2026-06-22. Templates: astro-scholar v0.6.1 2026-06-10 (32 stars, MIT); scholar-lite last commit 2025-12-26 (license **not stated** on its theme page) | Eleventy 3.1.8 on 2026-11-03; v4 alpha.12 2026-11-19; rebranded "Build Awesome" under Font Awesome, Mar 2026 |
| Learning curve for non-devs | Medium: Markdown + metadata header; theme edits need Jinja/HTML/CSS | **Lowest of the SSGs for this use case**: add a line of YAML for a paper, a Markdown file for a person; docs + PR preview | Medium; heavy config, many options | Medium-high; breaking-change history, config sprawl | Low-medium: Markdown/YAML; custom listing needs EJS once | Medium-high: need to understand components/collections | High: build everything yourself |
| Math / code blocks | Plugins (render_math) / Pygments | MathJax (via Jekyll Spaceship; v1.3.9 notes upgrade MathJax) + code blocks | MathJax via `al_math`, code highlight, Jupyter embeds | KaTeX/MathJax supported by Blox [details unverified] | MathJax default (`$`, `$$`); 140+ highlight languages; executable code | MDX; astro-scholar commit "remove LaTeX markdown configuration and blog" (2026-04-08) suggests math is not a given | DIY |
| Lock-in / migration risk | Lowest (Markdown, stays put) but you own the theme | Low: Markdown + YAML; but template-specific Liquid includes/components | Medium: custom plugin ecosystem; v2.0 will drop legacy Bootstrap markup | **High** historically (see section 3) | Low-medium: Markdown/YAML; Quarto-specific shortcodes | Low-medium (Markdown/MDX); per-template schemas | Low (Markdown) but project-specific glue code |
| License | AGPL-3.0 (Pelican) [license not re-checked this session; unverified] | BSD-3-Clause (repo page) | MIT (repo page) | MIT (HugoBlox/kit LICENSE; trademark held by Lore Labs) | MIT [unverified this session] | astro-scholar MIT; scholar-lite unstated | MIT [unverified this session] |

## 2. Notes per option

### (a) Stay on Pelican with a modern theme
- Pelican is healthy: 4.12.0 (2026-04-20) bumped minimums to Python 3.11, Docutils 0.22+, Sphinx 9.0+; commits as recent as 2026-11-09 (RSS guid fix, category-folder fixes).
- The weakness is the **theme ecosystem**: search surfaced Papyrus, Pelican-Blue, Alchemy, Atom; of those I checked, Papyrus last commit was 2023-10-27, Flex 2025-06-04, Elegant's last substantive work is 2022-23. No theme I found targets labs (people, publications, alumni). So "modern theme" realistically means writing/adapting one in Jinja. WCAG compliance of any of them is unverified.
- Publications: `pelican-pybtex` is the only publications plugin I found with a 2026 release (1.0.2, 2026-03-06, MIT, built on pybtex 0.26.1 released 2026-04-03). It populates a Jinja `publications` variable from a .bib file: workable, but a single-maintainer plugin. Older plugins (pelican-bib 2018, pelican-publications 2015, pelican-bibtex-reader 2023 AGPL) should be avoided.
- Zero content migration; lowest risk to existing URLs. Cost is paid in theme work.

### (b) Jekyll + Greene Lab `lab-website-template`
- Repo: BSD-3-Clause, 582 stars/450 forks, 188 commits, 6 open issues (page snapshot). Releases are frequent and recent (v1.4.1 2026-11-11 updating Docker image, Ruby in workflows, all gems; v1.4.0 2026-08-03 fixing a GitHub Actions security vulnerability; v1.3.9 removed polyfill.io dependency).
- Model: you put identifiers in `_data/sources*.yaml`; the "cite" process (Manubot, Python) generates `citations.yaml` (never hand-edit). Filename prefix selects plugin: `sources*`, `orcid*` (docs recommend ORCID as most reliable), `pubmed*` (docs call it "brittle"), `google-scholar*` (needs a SerpAPI key). Manual fields override: `title, authors, publisher, date, link`; rich fields `type, description (Markdown), image, buttons, tags, repo`. Results are cached; delete `_cite/.cache` to refresh.
- **Fit gap for the Fox Lab**: ~90 posters, book chapters and conference abstracts have no DOI. They must be entered with explicit fields (title/authors/date/buttons-with-PDF-link). The docs say there is no dedicated PDF field; use `buttons`. This is fine but means roughly half the corpus is manual either way.
- Team pages from Markdown (docs for the exact member schema/alumni handling were not retrievable: that page 404'd; verify). Blog with tags; MathJax via Jekyll Spaceship; "automatic pull request previews" is a feature (valuable for grad-student/PI review).
- Risks: Jekyll core release cadence is slow (4.4.1 on 2025-01-29, nothing since on RubyGems; repo commits continue, e.g. "soft deprecate old rubies" 2026-09-17), the template depends on a Manubot/Python+Ruby+Docker combination, and it is maintained by one lab (Greene Lab) with no stated support promise.

### (c) Jekyll al-folio
- 16.4k stars, MIT, 13.0k forks. v1.0 (2026-06-02) turned al-folio into "a thin starter, not a theme" with runtime features in separately versioned plugin gems; v1.1 2026-07-30; v1.2 2026-08-09. Legacy Bootstrap markup is opt-in and "removed in v2.0" (page statement). An upgrade skill/`al_folio_upgrade` exists for old forks. In other words, **a major architectural change landed 5 months ago**; settling period.
- Publications from BibTeX are its strength (jekyll-scholar); Scholar citation badges via workflow. It is designed for an individual researcher's homepage; a 20-person roster with alumni and 190 PDFs is possible but not its native shape (people page is `_data`-driven; no lab-oriented docs seen). It has news, projects, books, teachings collections and MathJax/Jupyter support.
- A real neuroscience lab example: UCSF Decision Lab (Jekyll, UCSF template + al-folio code).

### (d) Hugo + HugoBlox (formerly Wowchemy, formerly Academic) - honest assessment
- License: MIT for the framework (`HugoBlox/kit` LICENSE; copyright and the "HugoBlox" trademark held by Lore Labs). Site says "MIT-licensed and free forever", unlimited sites, self-host anywhere.
- Pricing (hugoblox.com/pricing): open-source tier $0; the paid tiers are for the **Hugo Chat AI** product: Plus $12/mo ($108/yr), Pro $25/mo ($240/yr), Max $60/mo, Team $32/seat/mo (annual). The framework itself is free on every tier. The README also says "Pro" adds "visual editing, AI automations, BibTeX import, and priority support", while the docs I read describe BibTeX import via free `pip install academic` + `academic import` and a VS Code extension (Ownable). **Whether BibTeX import is free or paywalled in the current offering is unverified**; the `academic` PyPI package's last release is 0.11.2 on 2023-11-26 (stale), and CLI syntax differs between doc pages.
- Breaking-change history (verified from the docs/blog sources I could read, not from a single changelog): Academic -> Wowchemy (c. 2020) -> Hugo Blox Builder; repo/module renames (v0.11.0 migration page; core module now `blox-tailwind`, earlier `wowchemy/v5` paths); a Bootstrap-to-Tailwind move for 2026 (vendor's own page); upgrade docs say migrations must be applied release-by-release and recommend a full backup; Hugo forum threads ("Wowchemy site stopped working") report sites breaking on Hugo updates; an ex-user post (glls.github.io, 2026-03-23) cites repeated renames, theme breaks on new Hugo, and an open-core focus on paid products. That post is opinion, but consistent with the docs. I found **no 2026-dated changelog** enumerating v5-to-current breaking changes.
- Activity: kit repo 2,275 commits, 9.8k stars; module releases 2026-01-02 and 2026-04-02; main-branch feed's newest entry 2026-05-27. Weekly upgrade bot + CLI exist. Needs Hugo Extended, Node, Go (modules).
- Verdict: free and capable, but for scientists with no web dev, the **update treadmill is the main risk**. Note: Gallant Lab (UC Berkeley) uses plain Hugo with a custom design, not HugoBlox.

### (e) Quarto website
- One installer, Markdown + YAML. Fox Lab's *tutorials* (nifti, ANTs, fmristat posts) are exactly Quarto's strength: code blocks with highlighting (140+ languages), optional executed notebooks (use `freeze` to avoid needing Python in CI), MathJax by default.
- Publications: YAML-listing + custom EJS template is the officially supported path to a Pubs page with PDF buttons (items can carry arbitrary fields; custom listings need classes for sorting/filtering; raw HTML blocks don't process Markdown). Doc caveats: the escaping note in the docs reads reversed vs. standard EJS; examples are correct. No native DOI/ORCID fetch; you would add a small script (Python + Crossref/ORCID) or a community converter to emit YAML from a .bib. Quarto's citeproc `nocite: @*` can render a plain formatted bibliography from the .bib with CSL.
- Deploy: `quarto-dev/quarto-actions/publish@v2` to gh-pages after one local `quarto publish gh-pages`; need CNAME at project root; Pages source must be switched to the gh-pages branch for user sites.
- Maintenance: Posit-backed, very active (v1.11.9 tagged Latest 30 Oct; 1.12.x tags seen 2026-11-02..17). Real labs: Poldrack Lab (confirmed `quarto-1.11.9` meta generator) and NeuroMH Lab ("Built with Quarto" footer).
- Cost: someone must write the listing template once (~1 day); after that, edits are YAML.

### (f) Astro
- Astro is very active (7.4.13 on 2026-11-18; monthly minors; 7.0 on 2026-06-22 with Vite 8 and Rust compiler) and has a first-class GitHub Pages guide (needs `site`/`base`, `public/CNAME`).
- Academic templates exist but are small and single-author: astro-scholar (MIT, 32 stars, 107 commits, v0.6.1 2026-06-10, BibTeX in `src/data/publications.bib`, team via `authors.json`, GH Pages workflow with PR previews; LaTeX config removed 2026-04-08), scholar-lite (BibTeX + Team collection + Pagefind search, Astro 6/Tailwind 4, last commit 2025-12-26, license unstated), academic-portfolio-astro, Space Lab [none individually vetted]. Major version churn is quick (v5, v6, v7 in under two years: v7 and v6 existence per astro.build/blog; v5 dates unverified).
- Fit: best-in-class performance and flexibility, but the audience (scientists, not developers) must tolerate a Node/JS stack and component syntax; the template bus-factor is 1.

### (g) Eleventy
- Mature, minimalist, data-file friendly, but: March 2026 rebrand to "Build Awesome" by Font Awesome (official 11ty blog; community reaction mixed; details of subsequent plans unverified); v3.1.8 stable and v4 still alpha (2026-11-19). "Build Awesome Pro" is paid but, per the announcement, not required.
- No maintained academic/lab template found; you'd write the data pipeline and layouts yourself. Not recommended for this team.

## 3. Hosting

- **GitHub Pages limits** (docs.github.com, Pages limits page): published site <= 1 GB; repo recommended <= 1 GB; soft 100 GB/month bandwidth; deployments time out at 10 min; soft 10 builds/hour (does not apply to custom Actions workflows). Not for commercial/SaaS. 190 PDFs: check total size; if > ~500 MB, host PDFs elsewhere (e.g. university Box/Drive links are fragile) or use a CDN.
- **Cloudflare Pages (free)**: 20,000 files/site, 25 MiB max per asset, 500 builds/month, 100 custom domains (docs). No statement found on bandwidth limits, nor about merging into Workers (the page only points large multi-site users to Workers) [Workers-migration claim unverified].
- **Netlify**: pricing page shows the free plan with a 300-credit limit, 20 credits per GB; whether credits reset monthly and what happens at the cap were not stated in what I could retrieve. Treat as unverified. The older "100 GB/month free" model should not be assumed.
- Recommendation: stay on GitHub Pages (already working, custom-domain CNAME already in repo, Actions build). Cloudflare Pages is the fallback if repo size/limits bite.
- **UC Davis [all unverified; UC Davis pages 403'd to my fetcher]**: search snippets say SiteFarm (Drupal 10-based) is the campus-recommended CMS built to UC Davis web/accessibility/brand standards; hosting is free to units; campus IT guidance prefers lab sites as a section under the department's SiteFarm site; policy 310-70 reportedly requires the UC Davis logo, a Regents copyright notice and WCAG 2 Level AA for UC Davis-hosted sites. Observations that corroborate Regents-notice practice at sister campuses: Gallant Lab (UC Berkeley, footer credits the Regents of the University of California) and UCSF Decision Lab ("(c) 2026 The Regents of the University of California", Accessibility/Privacy/Terms links). **Action for the PI: ask the Psychology department web/IT contact whether a GitHub-Pages-hosted site at foxlab.ucdavis.edu needs a Regents copyright line, accessibility statement, or SiteFarm migration.** The domain is already ucdavis.edu, which is helpful.

## 4. Exemplary lab sites (observed 2026-11-26)

Only structural/text observations; I could not evaluate visual design from text extraction.

| Lab | Stack (evidence) | What stands out |
|---|---|---|
| Poldrack Lab, Stanford (poldracklab.org) | Quarto 1.11.9 (meta generator tag) | Neuroscience/psychology flagship lab on Quarto; Bootstrap-based; shows Quarto is fine for a big lab |
| Gallant Lab, UC Berkeley (gallantlab.org) | Hugo, custom design (footer "Built with Hugo", source gallantlab/gallantlab.github.io; fonts Source Serif 4/Inter/JetBrains Mono) | Nav: News, Publications, Brain Viewers, People, Data, Code, Learn, Blog, Join us; open-source tool showcase and interactive viewer; footer has Regents credit, lab address, "last updated" date. Same UC system, so a good brand reference |
| Greene Lab, Penn (greenelab.com) | lab-website-template (footer "Built with Lab Website Template") | Highlights cards (Research/Tools/Team), Research/Tools/Team/Blog/Contact nav, ORCID/Scholar/GitHub icons |
| Decision Lab, UCSF (decisionlab.ucsf.edu) | Jekyll: ucsf_jekyll_basic + al-folio code (footer) | News/Team/Papers nav; institutional footer with Accessibility, Privacy, Terms and Regents copyright; open-source on GitHub |
| NeuroMH Lab, Maastricht (neuromh-lab.github.io) | Quarto ("Built with Quarto" footer) | Home, About, People, Research, Publications, Teaching, Join Us; "Latest" news feed with DOI links; publications generated from a YAML file via Quarto listings (per search result, not verified on the page) |
| Kording Lab (kordinglab.com) | Hand-written static HTML + Bootstrap 3.4.1 + MathJax (script tags) | Shows a no-SSG, math-capable site; also the failure mode: old Bootstrap 3 |
| Gershman CCN Lab, Harvard (gershmanlab.com) | Static Bootstrap page (meta generator "Bootply") | Minimal hand-built page |
| AffCom Lab, U. Kansas | Quarto (per a search result; page fetch failed; unverified) | Listed as a research-lab Quarto example (people, publication, blog listing) |

Not verified: Cognition, Motion & Neuroscience Lab, Hamburg (Hugo "Research Group theme" per search), and the Hogle Lab (Eleventy per its GitHub README snippet).

## 5. Ranked recommendation

Criteria weights: (1) a grad student can add a paper/person by editing one file; (2) publications from BibTeX/YAML with PDF links; (3) maintained now and likely to be in 2 years; (4) low churn/lock-in; (5) free GitHub Pages + Actions.

1. **Jekyll + Greene Lab lab-website-template (first choice, conditional on a 1-day spike).** Best fit to the stated workflow: YAML/ID-per-paper, Markdown-per-person, news/blog, PR previews, Actions deploy, actively released (latest 2026-11-11), MathJax, BSD-3. Mitigations: (i) use only the GitHub web editor + Actions so no one installs Ruby; (ii) pre-fill posters/chapters as full manual entries (title, authors, date, `buttons` PDF link) and let DOIs auto-resolve for the ~100 journal papers; (iii) pin the template release; (iv) keep content in Markdown/YAML so exit is cheap. Residual risks: Jekyll's slow core release cadence; reliance on Manubot network calls in CI; single-lab maintainership.
2. **Quarto website (close second; best if tutorials/code are the priority and the lab is Python/R-native).** One tool, one language, YAML listings, MathJax and code blocks first-class, strong 2026 maintenance (Posit), proven by Poldrack lab. Cost: write the custom EJS publications/people listing template once, and a small Python script (Crossref/ORCID/BibTeX -> YAML) for DOI auto-citation.
3. **Stay on Pelican with a custom theme (lowest-risk/lowest-change fallback).** Choose this if the lab values zero content migration and stable URLs above UX. Pelican is actively maintained, but you will own the theme (no good lab theme exists) and the BibTeX plugin is single-maintainer.
4. **al-folio** (good for the PI's personal page; v1.x re-architecture is only 5 months old; less lab-roster-native).
5. **Astro** (excellent engine, but JS toolchain + tiny single-author templates; revisit if you have a developer).
6. **Hugo + HugoBlox** (free MIT code but rename/breaking-change history, Tailwind migration in 2026, open-core product focus, unclear BibTeX-import licensing; highest maintenance risk for non-developers).
7. **Eleventy / Build Awesome** (no academic template; 2026 rebrand uncertainty).

## 6. Risks and open items

- No prototype built: before committing, port ~10 papers (journal + poster + book chapter), 3 people (current/alumni), 1 tutorial with code and math into (b) and (e) and test: edit-one-file flow, PDF links, URL preservation, Lighthouse/axe accessibility.
- UC Davis web policy (brand, accessibility, Regents copyright, SiteFarm expectations) is **unverified**; check with department IT before launch.
- Accessibility/performance defaults of every option are unverified by me; all produce static HTML, but theme-level WCAG conformance must be tested (campus policy reportedly targets WCAG 2 AA [unverified]).
- Staleness traps: the `academic` HugoBlox CLI (last PyPI release 2023-11-26), Pelican plugins from 2015-2018, Astro themes with one maintainer and no license (scholar-lite).
- GitHub Pages cannot do server redirects; keep slugs or add meta-refresh stubs.
- Twitter embed on the current home page is likely dead/obsolete; replace with news feed.
- Release-date caveat: Quarto "Latest" tag date year not shown on the page; 2026 inferred from feeds and poldracklab.org's generator tag. HugoBlox main-branch feed ends 2026-05-27, which might be a feed limitation.
- Eleventy rebrand details beyond the official post, and any "Cloudflare Pages merging into Workers" or Netlify credit rules: unverified.

## 7. Sources (all accessed 2026-11-26)

Pelican / Python
- https://github.com/getpelican/pelican/releases ; https://pypi.org/pypi/pelican/json (4.12.0 2026-04-20; 4.11.0.post0 2025-10-30; 4.11.0 2025-01-15)
- https://github.com/getpelican/pelican/commits/main.atom (commits to 2026-11-09)
- https://docs.getpelican.com/en/latest/tips.html (GitHub Pages workflow, CNAME)
- https://pypi.org/pypi/pelican-pybtex/json ; /pelican-bib/json ; /pelican-publications/json ; /pelican-bibtex-reader/json ; /pybtex/json ; /academic/json (via PyPI JSON)
- https://github.com/alexandrevicenzi/Flex/commits/master.atom ; https://github.com/Pelican-Elegant/elegant/commits/master.atom ; https://github.com/pelican-themes/papyrus/commits/main.atom
- Plugin search results: https://github.com/vene/pelican-bibtex , https://github.com/scheunemann/pelican-bib , https://pypi.org/project/pelican-pybtex

Jekyll / templates
- https://rubygems.org/api/v1/versions/jekyll.json (4.4.1 2025-01-29) ; https://github.com/jekyll/jekyll/releases ; https://github.com/jekyll/jekyll/commits/master.atom
- https://pages.github.com/versions/ (Jekyll 3.10.0, github-pages gem 232, 2025-08-13)
- https://github.com/greenelab/lab-website-template ; .../releases.atom ; .../commits/main.atom
- https://greene-lab.gitbook.io/lab-website-template-docs/ ; https://greene-lab.gitbook.io/lab-website-template-docs/basics/citations.md
- https://github.com/alshedivat/al-folio ; .../releases.atom ; .../commits/main.atom ; .../blob/main/README.md

Hugo / HugoBlox
- https://github.com/HugoBlox/hugo-blox-builder (redirects to HugoBlox/kit) ; .../releases.atom ; .../commits/main.atom
- https://hugoblox.com/pricing ; https://hugoblox.com/docs/guide/building/publications
- https://glls.github.io/posts/goodbye-hugo-blox (2026-03-23; opinion)
- https://docs.hugoblox.com/guides/upgrade/migrations/v0-11-0-migration ; https://discourse.gohugo.io/t/wowchemy-site-stopped-working-academic-theme/50237 (via search results; pages not fully fetched)
- https://github.com/gohugoio/hugo/releases.atom (v0.170.1 2026-11-17)

Quarto
- https://github.com/quarto-dev/quarto-cli/releases/latest ; .../releases.atom
- https://quarto.org/docs/websites/website-listings.html ; https://quarto.org/docs/websites/website-listings-custom.html
- https://quarto.org/docs/publishing/github-pages.html ; https://quarto.org/docs/authoring/citations.html ; https://quarto.org/docs/authoring/markdown-basics.html
- Community how-tos (search results only): https://drganghe.github.io/notes/generate-publications-listing.html , https://github.com/drganghe/quarto-academic-website-template , https://jebyrnes.github.io/bibtex_2_website_qmds

Astro
- https://registry.npmjs.org/astro (via `npm view astro`: latest 7.4.13, 2026-11-18) ; https://astro.build/blog/ ; https://docs.astro.build/en/guides/deploy/github/
- https://astro.build/themes/details/astro-scholar/ ; https://github.com/shravanngoswamii/astro-scholar (+ commits atom) ; https://astro.build/themes/details/scholar-lite/ ; https://github.com/fjd2004711/scholar-lite commits atom

Eleventy
- npm registry via `npm view @11ty/eleventy` (3.1.8 2026-11-03; 4.0.0-alpha.12 2026-11-19) ; https://www.11ty.dev/docs/ ; https://www.11ty.dev/blog/build-awesome/
- Search-result commentary (secondary): byteiota.com, hamatti.org/posts/au-revoir-eleventy, disassociated.com

Hosting
- https://docs.github.com/en/pages/getting-started-with-github-pages/github-pages-limits
- https://developers.cloudflare.com/pages/platform/limits/
- https://www.netlify.com/pricing/ (partial)
- UC Davis (secondary, search snippets only; primary pages returned 403): https://sitefarm.ucdavis.edu/join , https://lsit.ucdavis.edu/our-services/websites-and-web-hosting , https://biology.ucdavis.edu/node/9676 , https://sitefarm.ucdavis.edu/blog/use-campus-policy-as-checklist-while-subtheming , https://communicationsguide.ucdavis.edu/departments/web

Exemplar sites
- https://foxlab.ucdavis.edu ; https://www.poldracklab.org ; https://gallantlab.org ; https://greenelab.com ; https://decisionlab.ucsf.edu ; https://neuromh-lab.github.io ; https://kordinglab.com ; https://gershmanlab.com
