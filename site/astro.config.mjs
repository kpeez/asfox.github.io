// @ts-check
import { defineConfig } from 'astro/config';
import tailwindcss from '@tailwindcss/vite';
import sitemap from '@astrojs/sitemap';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import { unified } from '@astrojs/markdown-remark';

// Display math that overflows scrolls inside its own box; make that box keyboard-focusable
// (WCAG 2.1.1, axe "scrollable-region-focusable").
function rehypeFocusableMath() {
  /** @param {any} node a hast node */
  const visit = (node) => {
    if (node.type === 'element') {
      const cls = node.properties?.className;
      if (Array.isArray(cls) && cls.includes('katex-display')) node.properties.tabIndex = 0;
    }
    node.children?.forEach(visit);
    return undefined;
  };
  return visit;
}

export default defineConfig({
  site: 'https://foxlab.ucdavis.edu',
  trailingSlash: 'ignore',
  build: { format: 'directory', inlineStylesheets: 'auto' },
  integrations: [
    // Legacy redirect stubs (*.html) and the 404 page stay out of the sitemap.
    sitemap({ filter: (page) => !page.endsWith('.html') && !page.includes('/404') }),
  ],
  markdown: {
    processor: unified({ remarkPlugins: [remarkMath], rehypePlugins: [rehypeKatex, rehypeFocusableMath] }),
    // The "-default" GitHub themes meet 4.5:1 for their token colors (the older ones do not).
    shikiConfig: { themes: { light: 'github-light-default', dark: 'github-dark-default' } },
  },
  vite: { plugins: [tailwindcss()] },
});
