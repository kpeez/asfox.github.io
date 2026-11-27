// Emits one static redirect page per old URL, at exactly the old path (e.g. /fox-et-al-2012.html).
import type { APIRoute, GetStaticPaths } from 'astro';
import { legacyRedirects } from '../lib/legacy';
import { SITE } from '../site';

export const getStaticPaths = (async () => {
  const map = await legacyRedirects();
  return [...map.entries()].map(([legacy, to]) => ({ params: { legacy }, props: { to } }));
}) satisfies GetStaticPaths;

const esc = (s: string) => s.replace(/&/g, '&amp;').replace(/"/g, '&quot;').replace(/</g, '&lt;');

export const GET: APIRoute = ({ props }) => {
  const to = esc(props.to as string);
  const abs = esc(new URL(props.to as string, SITE.url).href);
  const html = `<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Moved · ${SITE.name}</title>
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex">
<link rel="canonical" href="${abs}">
<meta http-equiv="refresh" content="0; url=${to}">
<style>body{font:1.0625rem/1.6 system-ui,sans-serif;max-width:40rem;margin:4rem auto;padding:0 1rem;color:#1d1b18;background:#fbfaf7}a{color:#1b4b80}</style>
</head>
<body>
<p>This page has moved to <a href="${to}">${abs}</a>.</p>
</body>
</html>
`;
  return new Response(html, { headers: { 'Content-Type': 'text/html; charset=utf-8' } });
};
