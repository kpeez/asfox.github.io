# extract-prose: notes

Converts prose from the old Pelican site into Markdown for `site/src/content/{news,resources,pages}`, drafts `themes`, copies images and code files.

Re-run: `python3 extract.py` (needs `beautifulsoup4`; reads `typos.json` and `post_subs.json`, writes `extract-log.json`). It overwrites the generated Markdown, so after hand edits to those files, stop re-running it. The four theme files in `src/content/themes/` are hand-written and not produced by the script.

## What was produced

- news: 6 files (`src/content/news/<date>-<old-slug>.md`)
- resources: 11 files (7 tutorials, 4 essays) in `src/content/resources/<old-slug>.md`
- pages: 4 files (`join`, `mission`, `funding`, `cv`)
- themes: 4 files, all `draft: true`
- images: 10 body images + 1 news cover image in `src/assets/content/<slug>/`
- code: 10 files in `public/downloads/code/` (same sub-folders as the old site: `condor_ants/`, `fmristat/`)
- `npx astro sync` passes. Math was render-checked with a throwaway remark-math + rehype-katex run (0 KaTeX errors). A full `astro build` was not possible: `src/pages` and `src/layouts` do not yet render these collections.

## Typos fixed (prose only; code, math, and URLs untouched)

Listed in audit 3.2:
- `recieved` -> received (news: brain-imaging...; pages: funding)
- `nighly` -> nightly (news: CBS13)
- `Psyhchiatry` -> Psychiatry (news: Biological Psychiatry cover, "American Journal of Psyhchiatry")
- `Permision` -> Permission (cv: notice above the publication list)
- `Communicatoins` -> Communications (cv: Chen et al. 2023, Nature Communications)
- `Guildford Press` -> Guilford Press (cv: Davidson, Fox, Kalin 2007)
- Audit also lists `Reseach`, `CHen`, `Transporder`: not in text of my pages. `Transporder` appears only inside a PDF file name in a URL in the CV, left as is. `CHen` is in a publications stub page (not mine).

Other clear typos (not in the audit list), all in `typos.json`:
- cv: `Calrson` -> Carlson (Kamboj et al. 2024); `Feketa` -> Fekete (Kalin et al. 2016, same name is "Fekete" elsewhere in the CV); `adn across` -> and across; `Opportunitvnies` -> Opportunities; `Psychiatrys` -> Psychiatry's (awards list)
- news: `avaialable`, `brian function` -> brain function, `out labs efforts` -> our lab's efforts, `sciece`
- join: `check our my publications` -> check out my publications (audit 3.3)
- funding: "This proposal the Fox lab aims" -> "In this proposal the Fox lab aims"
- essays/tutorials: spelling (`dispite`, `incrase`, `becuase`, `asuming`, `sapce`, `resulotion`, `interst`, `brining`, `sacrice`, `indiference`, `teh`, `relationshp`, `lables`, `irrelavent`, `seperate(ly)`, `triats`, `paramter`, `esitmates`, `carying`, `brodcast`, `Kieth`) and grammar slips (`rst trial` -> first trial: the "fi" ligature was lost; `have and questions`, `look that the correlation`, `with you own data`, `confound lead me`, `you loose a degree`, `allows you use`, `This core components`, `these to variables`, `identical by decent`, `Much what we do` -> Much of what we do, `Fox example` -> For example)
- Dropped apostrophes restored (the old build lost them): didnt, dont, doesnt, isnt, cant, wouldnt, whats, Im, Id, Its easy/funny, what its like, Worsleys, FMRIBs, spearmans, mothers height, subjects' brains, participant's, world's, i-j's, animals', trait's, latitude's, and similar.
- Full list with counts: `extract-log.json` key `typos`.

Left as written although they look wrong (uncertain, PI to confirm):
- mission: "will lead us to a better understand humanity" (probably "better understand humanity" or "a better understanding of humanity")
- how-much-is-a-dollar: "playing ... participant in of our experiments" (probably "in one of"), "ratio of the two others", "Step 3 ... centered around 0 ~50% of the time"
- what-is-a-genetic-correlation: "$\eta$ is ???" (the author's own unresolved note), "variance attributed to the environment in this mode" (model?), "think about source of the correlation"
- news CBS13: "other scientists are doing help those that are suffering"; cover item: "Much of this which began during Fox's time"
- cv: author formatting in Chen et al. 2023 looks duplicated ("Viktor M. Plattner VM, Lillian J. Campos LJ, ... Dhanesh Sivadasan Bindu DS, ... David Goertsen D"); kept exactly.
- "Fox & Shackman" in the cover item's list: link file name says 2017, text says Neuroscience Letters 2019; kept.

## Math

- MathJax `\( \)` -> `$ $`; `div.math` `$$..$$` -> display `$$` blocks on their own lines (also inside blockquotes). Literal dollar signs in prose are escaped as `\$`.
- Fixes (all in `extract-log.json` key `math`): `\\\` and `\\\\` row separators (an artifact of the old build) -> `\\`; a leading `\\` removed from the last display block of the dollar essay; Greek capital iota in `Ι_n` -> `I_n`; Unicode `σ` -> `\sigma`; Unicode minus `−` -> `-`.
- The "Self-Other Game" box (`(\$0-\$10)`) had been turned into broken math spans by the old build; restored to `($0-$10)`.
- `what-is-a-genetic-correlation`: the source had `\(rho_g\)` and `\(rho_e\)` (backslash missing); written as `$\rho_g$` and `$\rho_e$`.
- `\begin{align}` is used in one display block; KaTeX accepts it in display mode.

## Links

Rewritten to new paths (12):
- `/category/publications`, `https://foxlab.ucdavis.edu/category/publications.html`, `pub.html` -> `/publications/` (news x3, join, ask-for-help; `pub.html` is not a page I could find, treated as the publications list because the link text is "monkeys")
- `fox-lab-mission.html` -> `/mission/`; `/joining-the-fox-lab.html` -> `/join/` (assumes the pages collection is routed at `/mission/` and `/join/`, `/funding/`, `/cv/`; change if layouts use other paths)
- `why-registration-matters-in-big-n-brain-imaging-studies.html` -> `/resources/why-registration-matters-in-big-n-brain-imaging-studies/`
- `looking-at-co-registered-brains.html` and `https://asfox.github.io/2013/03/20/looking-at-co-registered-brains/` -> `/resources/looking-at-co-registered-brain-data/` (the old link used a different slug than the page)
- `https://asfox.github.io/2013/04/01/python-flipbook-movies` -> `/resources/python-flipbook-movies/`
- `http://https://asfox.github.io/2013/05/30/read-nifti-in-fmristat/` (broken double scheme in the old multistatic page) -> `/resources/read-nifti-in-fmristat/`
- `/downloads/code/...` links kept as is; the files now exist at `public/downloads/code/`.
- Heading anchors: the viz tutorial's `#allCode` link now points to `#all-the-code` (the old heading was `<a id=allCode>All the code!` written as broken text; now plain heading "All the code!").

Left as is:
- 119 links to PDFs on the old host (`https://asfox.github.io/publications/<file>.pdf`): 109 in the CV publication list, the rest in news, the cover item list, and two tutorials. They still resolve only while the old site is up. Decision needed on PDF hosting (proposal section 5); then do a search-and-replace on `https://asfox.github.io/publications/`.
- External links (NIH RePORTER, news sites, fmriStat, ANTS, etc.) unchanged, including `http://` ones.
- `mailto:` links (fox.drew@gmail.com, troakes@gmail.com) kept as in the old pages.
- The old "Disqus" comment placeholder and `<!--more-->` markers were dropped.

## Legacy paths

- Every page: `/<old-slug>.html`.
- Cover item: also `/fox-lab-featured-on-cover-of-biological-psychiatry.html` and `/foxs-work-featured-on-cover-of-biological-psychiatry.html` (the stale duplicates; their text was identical except for the title).
- Octopress date permalinks that other old pages link to: `/2013/03/20/looking-at-co-registered-brains` (on looking-at-co-registered-brain-data), `/2013/04/01/python-flipbook-movies`, `/2013/05/30/read-nifti-in-fmristat`. Entered without a trailing slash. Other tutorials: no date permalink was linked anywhere, none added (add `/2013/03/19/running-ants-on-condor` style paths only if the real old URLs are known).
- pages: `join` <- `/joining-the-fox-lab.html`, `mission` <- `/fox-lab-mission.html`, `funding` <- `/current-funding-in-the-fox-lab.html`, `cv` <- `/resumecv.html`.

## Missing media

- Videos: both `<video>` tags pointed to `video/t1.mp4` (not in the repository; audit 3.4). Removed in `looking-at-co-registered-brain-data` and `python-flipbook-movies`; each now has the italic note "(The original video for this tutorial is no longer available.)". The poster image `images/compareAlignment_movie.png` was not used.
- All other images referenced by my pages exist in the old `images/` folder and were copied.
- Images that had no alt text (essay figures) got a neutral description; see `ALT` in `extract.py`.
- Embeds: the KCRW and YouTube iframes are kept as raw HTML with a descriptive `title`. The YouTube one already had the generic title "YouTube video player"; replaced by the name of the CBS13 feature. Obsolete attributes (`frameborder`, `scrolling`, `seamless`) were kept as in the original.

## Code blocks

- The code shown in each tutorial figure is the real downloadable file (checked identical to the embedded text apart from trailing whitespace), with a line "title, file name, download link" above the fenced block. Languages: `.py` python, `.m` matlab, `.sh` bash, `.submit` text (Condor submit file; no highlighter).
- Unlabeled snippets: shell commands -> `bash`, Python -> `python`; the Condor DAG snippet -> `text`.
- Quotes were lost in the short Python snippets of the "Visualizing the correlation of two volumes" tutorial (`facecolor=white`, `nib.load(file.nii)`...). Restored from the full script on the same page; 20 lines, listed in `extract-log.json` (`misc`). One command had a missing hyphen (`-fx 0 fy 0`), now `-fx 0 -fy 0`.
- Text that said to download "with the link on the top right" now says the link is above the code (3 places: multistatic, fmristat, viz tutorial).
- Not fixed (inside code, original text): comment typos such as "Threhold", "isnt", "tempalte", "housekeping".
- The old `code/` folder and `downloads/code/` folder are identical; every file in them is linked from a tutorial (none orphaned).

## Layout / structure choices (for the layout worker)

- The cover news item has the image both as the `image` frontmatter field and inline in the body (as in the old page). Drop one if the layout shows `image` at the top.
- Headings: body headings start at `##` (the page title is the `<h1>`); essays with h2+h4 became `##`/`###`; the mission page's h4 sections became `##`.
- The CV keeps the old order (Positions, Awards, Committees, Talks, Teaching, Training, Skills, Professional Experience, Publications). All 209 list items are present (109 publications). The PDF-icon links next to each publication were dropped (they duplicated the title link). In the positions list, the multi-space gap after the date range became ": ".
- Co-first-author asterisks in the cover item's reading list ("Oler*, Fox*, et al.") had been turned into accidental italics by the old build; written as literal `\*`.

## Out-of-date or inconsistent facts in the source (not changed)

- CV: "Positions and Education" says Professor (2026 - present), but "Professional Experience" still says "2016 - Present, Associate Professor". Also "Society for Neuroscience, 2016, Nano-Symposium (Upcoming; Session Chair)" is stale. Awards list repeats "Hertz Foundation Research Fellowship" and the 2005/2006 NSF Honorable Mentions as in the source. "Fox & Shackman, Neuroscience Letters" year differs between the file name (2017) and text (2019).
- Funding page dated 2022-06-27 ("most recent grants"); no later update.
- Join page (2016): says the lab is looking for team members; no date handling.
- Essays and tutorials are 2013 posts; they use first person and an informal tone (emoticons kept).

## Themes (drafts)

`anxious-temperament`, `uncertain-threat`, `viral-tools`, `gut-brain-parkinsons`, all `draft: true`, with order 1 to 4. Text only paraphrases the funding page (and, for the wireless-optogenetic pilot, the same page). Grant numbers exactly as on the funding page: R01 MH121735; R21 MH129851 and R01 MH131264; U01 MH128336; ASAP-020495.
- The phrase "anxious temperament" is in the theme title (from the audit's grouping) but does not appear in the funding or mission text; the body uses only "behavioral inhibition" and "dispositional anxiety" from the sources.
- The pilot funded by the UC Davis Behavioral Health Center of Excellence has no grant number, so it is described in the body of the first theme and not listed in `grants`.
- Theme ids are what `publications[].themes` should use.
