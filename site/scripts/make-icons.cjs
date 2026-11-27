// Regenerates public/favicon.svg, favicon.ico (32px PNG inside an ICO), apple-touch-icon.png (180px)
// and og.jpg (1200x630 social card) from the brand data in src/assets/brand/.
// Not part of the build. Needs Playwright (Chromium) and sharp:  node scripts/make-icons.cjs  (from site/)
const {chromium}=require('playwright'); const fs=require('fs');
const path=require('path'); const os=require('os');
const site=path.resolve(__dirname,'..')+'/';
const tmp=fs.mkdtempSync(path.join(os.tmpdir(),'icons-'))+'/';
const mark=JSON.parse(fs.readFileSync(site+'src/assets/brand/brain-mark.json'));
const trace=JSON.parse(fs.readFileSync(site+'src/assets/brand/brain-trace.json'));
const [vx,vy,vw,vh]=mark.viewBox.split(' ').map(Number);
// Square icon: navy rounded tile, mark centered with padding.
function icon(size, radius, sw){
  const pad=vw*0.16; const S=vw+2*pad; const oy=vy-(S-vh)/2;
  return `<svg xmlns="http://www.w3.org/2000/svg" viewBox="${vx-pad} ${oy} ${S} ${S}" width="${size}" height="${size}"><rect x="${vx-pad}" y="${oy}" width="${S}" height="${S}" rx="${S*radius}" fill="#022851"/><g fill="none" stroke="#FFBF00" stroke-width="${sw}" stroke-linecap="round" stroke-linejoin="round"><path d="${mark.outline}"/><path d="${mark.sulci}"/></g></svg>`;
}
fs.writeFileSync(site+'public/favicon.svg', icon(32,0.22,40).replace(/ width="32" height="32"/,''));
(async()=>{
  const b=await chromium.launch(); const p=await b.newPage({deviceScaleFactor:1});
  const shot=async(html,w,h,path)=>{await p.setViewportSize({width:w,height:h});await p.setContent(`<html><body style="margin:0">${html}</body></html>`);await p.screenshot({path,omitBackground:true});};
  await shot(icon(180,0,30),180,180,site+'public/apple-touch-icon.png');
  await shot(icon(32,0.22,44),32,32,tmp+'fav32.png');
  const paths=trace.paths.map(x=>`<path d="${x.d}"/>`).join('');
  const og=`<div style="width:1200px;height:630px;background:#022851 radial-gradient(700px 420px at 80% 50%,rgba(255,255,255,.07),transparent 70%);position:relative;overflow:hidden;font-family:'Newsreader',Georgia,serif;color:#fff">
   <svg viewBox="0 0 ${trace.w} ${trace.h}" style="position:absolute;right:40px;top:95px;width:600px"><g fill="#FFBF00" fill-rule="evenodd">${paths}</g></svg>
   <div style="position:absolute;left:80px;top:170px;width:520px">
    <div style="font:500 22px/1.3 Inter,system-ui,sans-serif;color:rgba(255,255,255,.78)">Department of Psychology · UC Davis</div>
    <div style="font-size:120px;line-height:1;margin-top:18px;font-weight:500;letter-spacing:-2px">Fox Lab</div>
    <div style="font-size:42px;line-height:1.15;margin-top:18px;color:#FFBF00">Translational Affective Neuroscience</div>
   </div></div>`;
  const css=['newsreader/files/newsreader-latin-wght-normal.woff2','inter/files/inter-latin-wght-normal.woff2'].map((f,i)=>`@font-face{font-family:${i?'Inter':'Newsreader'};src:url(data:font/woff2;base64,${fs.readFileSync(site+'node_modules/@fontsource-variable/'+f).toString('base64')}) format('woff2');font-weight:100 900}`).join('');
  await shot(`<style>${css}</style>`+og,1200,630,tmp+'og.png');
  await b.close();
  // ICO wrapper around the 32px PNG
  const png=fs.readFileSync(tmp+'fav32.png');
  const h=Buffer.alloc(22); h.writeUInt16LE(0,0);h.writeUInt16LE(1,2);h.writeUInt16LE(1,4);
  h.writeUInt8(32,6);h.writeUInt8(32,7);h.writeUInt8(0,8);h.writeUInt8(0,9);h.writeUInt16LE(1,10);h.writeUInt16LE(32,12);h.writeUInt32LE(png.length,14);h.writeUInt32LE(22,18);
  fs.writeFileSync(site+'public/favicon.ico',Buffer.concat([h,png]));
  await require('sharp')(tmp+'og.png').jpeg({quality:84,mozjpeg:true}).toFile(site+'public/og.jpg');
})();
