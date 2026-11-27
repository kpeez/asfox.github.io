// Content schema for the Fox Lab site.
// Each collection is a folder of small files that can be edited in the GitHub web editor.
// The build fails if a file is missing a required field.
import { defineCollection } from 'astro:content';
import { glob } from 'astro/loaders';
import { z } from 'astro/zod';

const legacy = z.array(z.string()).default([]); // old foxlab.ucdavis.edu paths that redirect here

// One YAML file per paper, chapter, or preprint: src/content/publications/<id>.yaml
const publications = defineCollection({
  loader: glob({ pattern: '**/*.yaml', base: './src/content/publications' }),
  schema: z.object({
    title: z.string(),
    authors: z.array(z.string()).min(1), // as printed: "Fox AS"
    year: z.number().int(),
    date: z.coerce.date().optional(),
    type: z.enum(['journal', 'chapter', 'preprint']),
    venue: z.string(), // journal or book title
    volume: z.string().optional(),
    issue: z.string().optional(),
    pages: z.string().optional(),
    editors: z.string().optional(), // chapters
    publisher: z.string().optional(), // chapters
    doi: z.string().optional(), // bare DOI, e.g. 10.1523/JNEUROSCI.xxxx
    pmid: z.string().optional(),
    url: z.string().url().optional(), // only when there is no DOI
    pdf: z.string().optional(), // path or URL to a PDF the lab keeps
    themes: z.array(z.string()).default([]), // ids from src/content/themes
    lab_authors: z.array(z.string()).default([]), // ids from src/content/people
    featured: z.boolean().default(false),
    legacy,
  }),
});

// One YAML file per poster or talk: src/content/presentations/<id>.yaml
const presentations = defineCollection({
  loader: glob({ pattern: '**/*.yaml', base: './src/content/presentations' }),
  schema: z.object({
    title: z.string(),
    authors: z.array(z.string()).min(1),
    year: z.number().int(),
    date: z.coerce.date().optional(),
    type: z.enum(['poster', 'talk']).default('poster'),
    meeting: z.string(), // e.g. "Society for Neuroscience"
    pdf: z.string().optional(),
    lab_authors: z.array(z.string()).default([]),
    legacy,
  }),
});

// One Markdown file per person; the body is the bio: src/content/people/<id>.md
const people = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/people' }),
  schema: ({ image }) =>
    z.object({
      name: z.string(),
      role: z.string(), // "Principal Investigator", "Graduate Student", ...
      status: z.enum(['current', 'alumni']),
      order: z.number().default(100), // lower sorts first within status
      start: z.string().optional(), // "2022-08"
      end: z.string().optional(),
      now_at: z.string().optional(), // alumni only
      photo: image().optional(),
      photo_alt: z.string().optional(),
      email: z.string().optional(),
      links: z
        .object({
          website: z.string().url().optional(),
          scholar: z.string().url().optional(),
          orcid: z.string().url().optional(),
          github: z.string().url().optional(),
          cv: z.string().optional(),
        })
        .default({}),
      citation_names: z.array(z.string()).default([]), // spellings in author lists, e.g. ["Fox AS"]
      legacy,
    }),
});

// One Markdown file per news item: src/content/news/<yyyy-mm-dd-slug>.md
const news = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/news' }),
  schema: ({ image }) =>
    z.object({
      title: z.string(),
      date: z.coerce.date(),
      summary: z.string(),
      image: image().optional(),
      image_alt: z.string().optional(),
      legacy,
    }),
});

// Long-form tutorials and essays: src/content/resources/<slug>.md (or .mdx)
const resources = defineCollection({
  loader: glob({ pattern: '**/*.{md,mdx}', base: './src/content/resources' }),
  schema: z.object({
    title: z.string(),
    date: z.coerce.date(),
    kind: z.enum(['tutorial', 'essay']),
    summary: z.string(),
    legacy,
  }),
});

// Research themes: src/content/themes/<id>.md, body = longer description
const themes = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/themes' }),
  schema: z.object({
    title: z.string(),
    short: z.string(), // one or two sentences for cards
    order: z.number().default(100),
    grants: z.array(z.string()).default([]),
    draft: z.boolean().default(true), // true until the PI approves the wording
  }),
});

// Free-standing pages (join, mission, funding, CV): src/content/pages/<slug>.md
const pages = defineCollection({
  loader: glob({ pattern: '**/*.md', base: './src/content/pages' }),
  schema: z.object({
    title: z.string(),
    description: z.string(),
    legacy,
  }),
});

export const collections = { publications, presentations, people, news, resources, themes, pages };
