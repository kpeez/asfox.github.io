// Site-wide identity and navigation. Content lives in src/content; this file holds only
// labels and the few facts every page repeats (name, contact, affiliation).
export const SITE = {
  name: 'Fox Lab',
  longName: 'The Fox Lab',
  tagline: 'Translational Affective Neuroscience',
  url: 'https://foxlab.ucdavis.edu',
  email: 'dfox@ucdavis.edu',
  department: 'Department of Psychology',
  university: 'University of California, Davis',
  universityUrl: 'https://www.ucdavis.edu/',
  departmentUrl: 'https://psychology.ucdavis.edu/',
  github: 'https://github.com/asfox',
} as const;

export const NAV = [
  { href: '/research/', label: 'Research' },
  { href: '/people/', label: 'People' },
  { href: '/publications/', label: 'Publications' },
  { href: '/presentations/', label: 'Presentations' },
  { href: '/news/', label: 'News' },
  { href: '/resources/', label: 'Resources' },
  { href: '/join/', label: 'Join' },
] as const;
