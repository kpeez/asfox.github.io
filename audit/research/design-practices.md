# Design research: UC Davis Fox Lab website (foxlab.ucdavis.edu)

Compiled 2026-11-26. All URLs accessed 2026-11-26.
Tags: [V] = read from the cited page this session. [S] = search-result snippet or secondary source only. [U] = unverified, from memory, or could not fetch. [Inf] = my inference or judgment.
Several UC Davis brand pages (communicationsguide.ucdavis.edu, marketingtoolbox, samc, uecomm, foa, caes) returned HTTP 403 to the fetch tool, so brand details rest on search snippets. Confirm them against the live brand guide before launch.

---

## 0. Compliance and brand constraints (read first)

### 0.1 Legal and policy
- DOJ ADA Title II web rule (April 2024) requires WCAG 2.1 Level AA. [V] https://www.ada.gov/resources/2024-03-08-web-rule/
- An Interim Final Rule of April 20, 2026 extended the dates. [V] https://www.ada.gov/resources/2024-03-08-web-rule/ ; Federal Register notice (snippet only [S]): https://www.federalregister.gov/documents/2026/04/20/2026-07663/extension-of-compliance-dates-for-nondiscrimination-on-the-basis-of-disability-accessibility-of-web
  - Entities serving 50,000+ people: April 26, 2027 (was April 24, 2026).
  - Entities under 50,000 and special districts: April 26, 2028.
  - One law-firm summary says April 27, 2027; ada.gov and the Federal Register say April 26. Use April 26.
  - DOJ said it expects to hold these dates unless it issues an NPRM or extends again. [S] Recheck before publishing.
- UC is treated as a large public entity, so April 26, 2027 applies. [V] https://digitalaccessibility.ucop.edu/frequently-asked-questions/
- UC policy IMT-1300 requires WCAG 2.1 AA for websites, documents (PDF, Word, etc.) and third-party content under UC contract. [V FAQ] same URL.
  - FAQ dates: March 17, 2026 (IMT-1300 compliance), April 26, 2027 (Title II), May 11, 2027 (Section 504).
  - Preexisting-content exceptions key off creation dates (April 24, 2026 for IMT-1300). Exceptions last two years and need renewal.
  - Other UC pages give conflicting "effective" dates (March 17 vs April 24, 2026). [S] Check the policy text (policy.ucop.edu) before quoting a date in an accessibility statement.
  - Every website should have an accessibility statement (FAQ 22). Department sites, including password-protected areas, must meet 2.1 AA. [V]
  - Archived-content exception needs all four conditions (created before the date, kept only for reference, in a clearly identified archive, unaltered). Do not rely on it for live lab pages. [V]
- UC Davis states it follows WCAG 2.1 AA. [S] https://accessibility.ucdavis.edu/digital ; https://cee.ucdavis.edu/digital-accessibility

**A1. Target WCAG 2.2 AA.** It adds nine criteria and drops only 4.1.1 Parsing, so it also meets 2.1 AA. [V] https://www.w3.org/WAI/standards-guidelines/wcag/new-in-22/
- New AA items: 2.4.11 Focus Not Obscured (Minimum), 2.5.7 Dragging Movements, 2.5.8 Target Size (Minimum), 3.3.8 Accessible Authentication (Minimum). New A items: 3.2.6 Consistent Help, 3.3.7 Redundant Entry.
- Target size: at least 24x24 CSS px, unless a 24px circle around the target touches no other target (plus inline/equivalent/user-agent exceptions). [V] https://www.w3.org/WAI/WCAG22/Understanding/target-size-minimum.html
- Contrast: text 4.5:1; large text (18pt, or 14pt bold) 3:1; ratios are not rounded. [V] https://www.w3.org/WAI/WCAG22/Understanding/contrast-minimum.html
- Non-text contrast (1.4.11) is 3:1 for UI components and graphics. [U: only implied on the page fetched; confirm at https://www.w3.org/WAI/WCAG22/Understanding/non-text-contrast.html]

**A2.** Add an accessibility statement page with a feedback contact, linked from the footer. Source: UC FAQ item 22 [V].

**A3.** Any PDF the lab authors and hosts must be accessible (tagged) under IMT-1300. Prefer HTML for lab-authored documents (rotation guide, participant info). Whether merely linking to publisher PDFs avoids the duty is [U]; ask the campus ADA coordinator.

### 0.2 UC Davis brand
- Aggie Blue #022851 (RGB 2/40/81); Aggie Gold #FFBF00 (RGB 255/191/0). [S, several UC Davis unit pages agree] https://communicationsguide.ucdavis.edu/brand-guide/colors (403 to fetcher); https://samc.ucdavis.edu/brand-guide/colors
- Spirit-mark guidance: gold on dark/blue, blue on light/gold. Approved logo colors: blue, gold, black, white. [S] https://communicationsguide.ucdavis.edu/ucd-mark
- Secondary palette: a campus-designated set exists but units publish different subsets. [S] Do not invent hex values; take the official list from the brand guide. A UE Comm page references an "Accessible Color Combinations Guide" PDF. [S] https://uecomm.ucdavis.edu/toolbox/colors
- Fonts: Proxima Nova is the primary sans, available by default on SiteFarm and usable on other ucdavis.edu sites; official set is Proxima Nova, Ryman Eco, Freight Text; Berkeley is retired. Fallback Arial/Helvetica (Aptos also listed by UC Davis Health). [S] https://communicationsguide.ucdavis.edu/brand-guide/fonts ; https://health.ucdavis.edu/graphic-standards/brand-and-fonts/
- Logos: units use official Unit Signatures made by Repro Graphics; never recreate UC Davis marks or add words to the wordmark. [S] https://communicationsguide.ucdavis.edu/brand-guide/logos/unit-signatures ; https://communicationsguide.ucdavis.edu/brand-guide/logos . One snippet says departments may use own lockups [S, ambiguous]; ask Repro Graphics.

**B1.** Use Aggie Blue as the ink/header color and Gold only as an accent on dark blue. Gold on white fails text contrast, so never use it for text on light backgrounds. Compute every pair with a script before shipping.

**B2.** Use a system stack by default (`system-ui, -apple-system, "Segoe UI", Arial, sans-serif`). Add Proxima Nova only if licensed for the host (github.io vs ucdavis.edu is [U]). Also helps the performance budget.

**B3.** Put the UC Davis identity in header/footer using a downloaded official signature; do not draw it. Ask the brand office about a lab-level signature.

---

## 1. Information architecture

- NN/g: prospective students, high school through PhD, want to know about the professors they will learn from; parents read faculty pages too. [V] https://www.nngroup.com/videos/university-faculty-pages/
- NN/g Top 10 university-site guidelines [V] https://www.nngroup.com/articles/university-sites/ : identify the institution on every page; authentic images, not stock; useful About page with plain summary and key facts; easy program browsing; findable application steps and deadlines; test journeys with about five users; do not be too "cool" (flashy content reduces trust); expect external search and provide solid internal search.
- A "more than half of prospective students miss programs" statistic appears only on a vendor page. [S, not verified at NN/g] Not relied on.

Audience needs below are my synthesis [Inf]; I found no primary source specific to lab sites:
- Prospective grad students/postdocs: current research, whether the PI is recruiting, how to apply (programs, deadlines), lab culture, recent outputs, alumni destinations.
- RAs/undergrads: how to join, time expectation, contact.
- Collaborators: publications, methods, data/code, contact.
- Funders/press: plain-language summary, news, funding acknowledgments, media contact.
- Participants: who runs studies, what is involved, safety, compensation, eligibility, how to sign up, IRB contact. Write in plain language, separate from academic pages.

**C1. Nav (7 items max):** Research, People, Publications, News, Join, Participate, Contact. Keep Participate separate from Join so the audiences do not collide. Provide site search (header link or box). Contact may move to the footer plus Join if crowded.

**C2. Templates:**
1. Home: one-sentence plain-language mission, 3 research themes with images, "recruiting" banner only when true (with expiry date), latest 3 news, 3 recent papers, UC Davis signature.
2. Research theme: question, why it matters (lay summary), methods (primate and human neuroimaging, behavior), key papers, people, funding.
3. Person profile: photo, role, short bio, interests, links (ORCID, Scholar, email), that person's publications. Alumni use the same page with a "Now at" line.
4. Publications list (section 2).
5. News: dated posts with tags, plain language, link to the paper.
6. Join: sections for grad students, postdocs, RAs/undergrads; how to apply and what to include.
7. Participate: eligibility, what happens, compensation, risks, contact. Recruitment wording needs IRB approval [U].
8. Accessibility statement and privacy page.

---

## 2. Publication-list UX

**D1. Layout.** Group by year, descending, as default. Filters: year, type (journal, preprint, review, chapter), theme/topic, author. Add text search over title, authors, journal. Render the full list as HTML and enhance with JS so it works without JS. Mark preprints visibly. [Inf]

**D2. Per-entry fields.** Authors (lab members marked), year, title, journal/volume/pages, DOI link, PubMed link, preprint link, open-access link (see D4), code/data link (OSF, GitHub, OpenNeuro), and a BibTeX/RIS cite option. Generate from one data file (section 4). [Inf]

**D3. Citation style.** One consistent style throughout; offer BibTeX download for the whole list and per paper. [Inf]

**D4. Copyright.**
- Publisher PDFs are generally not ours to host. Host the author accepted manuscript only where the publisher's policy allows; otherwise link to a repository copy (eScholarship, PMC, bioRxiv/PsyArXiv). Label links "Open-access version" and name the version. [Inf]
- UC's Presidential Open Access Policy (Oct 2015) covers non-Senate authors including postdocs and requires deposit of a copy in eScholarship; copyright stays with authors. [S] https://escholarship.org/uc/ucd/ucoapolicies ; https://osc.universityofcalifornia.edu/for-authors/open-access-policy/policy-faq/
- Sources say "final version"; whether that means accepted manuscript was not settled. [U] Policy text: https://osc.universityofcalifornia.edu/open-access-at-uc/open-access-policy/policy-text/presidential/
- Check each journal's self-archiving rules, e.g. Sherpa Romeo. [U, not fetched] https://v2.sherpa.ac.uk/romeo/

**D5. Google Scholar.** Scholar indexes per-paper pages, not list pages: "Each paper must have its own unique URL." List pages only help crawlers find paper URLs. [V] https://scholar.google.com/intl/en/scholar/inclusion.html
- Required Highwire tags: citation_title, citation_author (one tag per author, no affiliations), citation_publication_date. A page missing any is treated as having no tags.
- citation_pdf_url must be absolute and in the same subdirectory as the abstract page. Optional: citation_journal_title, volume, issue, firstpage, lastpage, issn.
- Tags go only on pages that actually offer the paper (abstract page or full text). If the lab only links out to publishers, Scholar already indexes the publisher version, so lab per-paper pages add little. [Inf]
- citation_doi is a common Highwire tag but is not on the Scholar page fetched. [U]

**D6. Structured data.**
- schema.org ScholarlyArticle: Thing > CreativeWork > Article > ScholarlyArticle; use author, datePublished, isPartOf, sameAs (DOI URL), identifier. [V] https://schema.org/ScholarlyArticle
- Google's Article rich result accepts only Article, NewsArticle, BlogPosting; ScholarlyArticle is not named. For internal author profile pages Google recommends profile-page markup. [V] https://developers.google.com/search/docs/appearance/structured-data/article
- Add JSON-LD: ScholarlyArticle on per-paper pages (if any), Person (sameAs ORCID, Scholar) on profiles, Organization for the lab. Expect no rich-result gain; it helps machine readers. [Inf]

---

## 3. Visual design, performance, privacy

**E1. Typography.** Body 16-18px, line-height about 1.5-1.6, measure 60-75 characters (`max-width: 65ch`). WCAG 1.4.8 (AAA) caps lines at 80 characters, asks for line spacing of at least 1.5 and no full justification, and 200% resize without horizontal scroll. [V] https://www.w3.org/WAI/WCAG22/Understanding/visual-presentation.html
- Modular scale around 1.2-1.25 with `clamp()` for headings; rem units. [Inf]
- GOV.UK typography page returned 404 when fetched. [U] Find the current URL under https://design-system.service.gov.uk/ if wanted.

**E2. Color and dark mode.** Tokens on `:root` (ink, paper, accent, link, border); redefine under `@media (prefers-color-scheme: dark)`. Verify each pair at 4.5:1 text and 3:1 UI. Visible focus ring that sticky headers cannot cover (2.4.11). Never use color alone for status. [Inf, grounded in A1]

**E3. Images.** `srcset`/`sizes` for resolution switching; `<picture>` for format or art direction. [V] https://web.dev/learn/images/responsive-images
- Also: width/height attributes (avoid layout shift), `loading="lazy"` below the fold, never lazy-load the LCP image. [U: not on the page fetched; see https://web.dev/articles/optimize-lcp]
- Alt text: describe the finding for brain figures; `alt=""` for decorative. People photos: consistent crop, about 400px max, AVIF/WebP with JPEG fallback. [Inf]

**E4. Performance.** Core Web Vitals "good" at the 75th percentile, mobile and desktop; all three must pass: LCP at most 2.5 s, INP at most 200 ms, CLS at most 0.1. [V] https://web.dev/articles/vitals
- Budgets: web.dev suggests starting points of TTI under 5 s on slow 3G and under 170 KB critical-path resources, enforced with Lighthouse CI. [V] https://web.dev/articles/performance-budgets-101
- Suggested lab-site budget: HTML+CSS under 50 KB, JS under 30 KB (filter/search only), at most 1 font file, hero image under 150 KB. These numbers are my judgment [Inf].

**E5. Minimal JS.** Static HTML; JS only for publication filter/search and optional theme toggle. No carousels or autoplay. Honor `prefers-reduced-motion`. [Inf]

**E6. Modern but not flashy.** NN/g: avoid "too cool", use authentic images [V, URL in section 1]. In practice: whitespace, restrained palette (blue plus one accent), real lab photos and figures, left-aligned text, strong headings. [Inf]

**E7. Analytics.** Universal Analytics was retired in July 2023 (campus migration to GA4). [S] https://websites.ucr.edu/google-analytics
- Plausible: no cookies, no persistent visitor identifiers, daily-rotating hash, raw IP not stored. [V] https://plausible.io/data-policy ; hosted is paid (about $9/mo [S]); Community Edition self-hostable (AGPL).
- Umami (self-hostable) and GoatCounter (donation-supported) are cookieless. [S, vendor-adjacent blogs] https://www.github.com/spekulatius/awesome-privacy-friendly-web-analytics
- Server-log tools (GoAccess) need logs that GitHub Pages does not provide. DNS blockers may block analytics script domains, causing undercounts. [S]
- I found no UC Davis-wide analytics requirement. [S] SiteFarm has a GA training page: https://sitefarm.ucdavis.edu/training/managers/google-analytics . Ask the UC Davis privacy office before adding any third-party script, and state what is collected on a privacy page.
- Keep third-party scripts off the participant-recruitment pages. [Inf] If analytics is not needed, add none.

---

## 4. Content maintenance

**F1. Single source of truth.** Structured data files, not hand-edited HTML: `people.yml` (name, role, years, photo, links, ORCID, status current/alumni), `publications.yml` or `.bib` keyed by DOI, `news/*.md`, `research.yml`. Generate pages, nav and per-person publication lists from them. Validate schema in CI (fail on missing DOI/year/authors). Crossref/PubMed lookup by DOI cuts typos. [Inf; APIs not fetched]

**F2. Alumni.** Keep alumni profiles (name, role, years, "Now at"); do not delete. Honor removal requests for photos and contact details. [Inf]

**F3. Currency.** Visible "Last updated" on Home, People, Join. Quarterly review reminder. Give "recruiting" and study-status fields an expiry date in the data so stale claims disappear automatically. [Inf]

**F4. Link checking (lychee).** `lycheeverse/lychee-action@v2`, scheduled run plus on PR; `fail: false` on the schedule and open an issue from `./lychee/out.md` via peter-evans/create-issue-from-file; cache with `--cache --max-cache-age 1d`; pin the action to a SHA with Dependabot. [V] https://github.com/lycheeverse/lychee-action
- Many publisher sites return 403 to bots; handle with lychee's accept/exclude options [U: exact flags; see lychee docs]. DOI links should be checked for redirects.

**F5. Accessibility CI (pa11y-ci).** `.pa11yci(.json/.js)` with `urls` and `defaults`; `runners` = `htmlcs` (default), `axe`, or both; `--sitemap` tests every URL; exit code 2 means failures. [V] https://github.com/pa11y/pa11y-ci
- Run both runners against the built site, in light and dark mode. [Inf]
- Automated tools catch only part of the issues. Add a manual checklist: keyboard-only pass, 200% zoom, screen-reader spot check, reduced motion. [Inf]

**F6. Images in CI.** Convert/resize at build time (sharp, Eleventy Image, Hugo processing, depending on generator); fail the build on oversized images or missing alt. [U: depends on site generator]

---

## 5. Anthropic frontend-design skill

Source: https://github.com/anthropics/skills/blob/main/skills/frontend-design/SKILL.md [V]. Key rules:
- Make deliberate, brief-specific choices. Plan first (4-6 named hex colors, type roles, layout sketch), review the plan for "generic default" tells, then build.
- Type: one or two clearly distinct families; clear scale; line length under 80 characters; serif needs slightly more line height.
- Avoid tells: accenting one headline word, all-caps labels, needless labels above content, 01/02/03 markers on non-sequences, middle-dot meta strings, arrows on every link, identical rounded cards with soft gray shadows, gradient washes, fade-and-slide on every section.
- Motion: sparing; one orchestrated moment beats many effects.
- "Spend your boldness in one place"; keep the rest quiet.
- Quality floor without announcing it: responsive, visible keyboard focus, reduced motion honored, accessible color.
- Write real copy; plain verbs, sentence case, active voice.

Fit here: adopt restraint, the type scale, the line-length cap, the quality floor and real copy. The skill says to follow a brief that pins a visual direction. For a ucdavis.edu lab, the UC Davis brand is that pinned direction, so apply the distinctiveness to layout and imagery, not brand colors or logo. [Inf]

---

## Open items before launch
1. Get the official UC Davis brand pages (colors, fonts, unit signatures, secondary palette); fetcher got 403. Contact Repro Graphics/brand office about a lab signature.
2. Confirm Proxima Nova web license for non-SiteFarm hosting.
3. Confirm IMT-1300 dates in policy text; ask the campus ADA coordinator about hosted publisher PDFs.
4. Confirm WCAG 1.4.11 text and web.dev LCP-image guidance ([U] items).
5. Ask UC Davis privacy whether analytics is required or restricted.
6. Check publisher self-archiving policies per paper and the UC OA policy's version wording.
7. DOJ dates could move again; recheck ada.gov before publishing the accessibility statement.
