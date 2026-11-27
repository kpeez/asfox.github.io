# Regenerates src/assets/brand/brain-trace.json, the vector brain used in the home hero,
# by tracing the gold line drawing in the old site's images/heroBack_UC.jpg.
#
# Not part of the build. Needs Pillow, numpy and potracer:
#   python3 -m venv /tmp/trace && /tmp/trace/bin/pip install pillow numpy potracer
#   /tmp/trace/bin/python scripts/trace-brain.py      (run from site/)
#
# Method: crop the large brain, upscale 4x, take R-B as a "gold" signal (the blue
# background is about -70), blur slightly, threshold at -48, trace with potrace,
# group hole contours with their outer contour, and write compact relative paths
# in half-pixel units, sorted left to right (the hero draws them in that order).
import json
from pathlib import Path

import numpy as np
import potrace
from PIL import Image, ImageFilter

SRC = Path(__file__).resolve().parents[2] / 'images' / 'heroBack_UC.jpg'
OUT = Path(__file__).resolve().parents[1] / 'src' / 'assets' / 'brand' / 'brain-trace.json'
X0, Y0, X1, Y1 = 650, 485, 1195, 905  # crop around the large brain
S = 4  # upscale factor before tracing
THRESHOLD, TURDSIZE, BLUR, OPTTOL = -48, 60, 1.2, 0.8
Q = 2 / S  # output unit = half a source pixel

im = Image.open(SRC).convert('RGB').crop((X0, Y0, X1, Y1))
im = im.resize(((X1 - X0) * S, (Y1 - Y0) * S), Image.LANCZOS)
a = np.asarray(im).astype(float)
g = Image.fromarray(np.clip(a[..., 0] - a[..., 2] + 128, 0, 255).astype('uint8'))
g = np.asarray(g.filter(ImageFilter.GaussianBlur(BLUR))).astype(float) - 128
mask = g > THRESHOLD

curves = list(potrace.Bitmap(~mask).trace(turdsize=TURDSIZE, alphamax=1.0, opticurve=True, opttolerance=OPTTOL))


def q(p):
    return round(p.x * Q), round(p.y * Q)


def emit(curve):
    cur = q(curve.start_point)
    s = [f'M{cur[0]} {cur[1]}']
    for seg in curve.segments:
        if seg.is_corner:
            for p in (q(seg.c), q(seg.end_point)):
                s.append(f'l{p[0] - cur[0]} {p[1] - cur[1]}')
                cur = p
        else:
            c1, c2, e = q(seg.c1), q(seg.c2), q(seg.end_point)
            s.append(f'c{c1[0] - cur[0]} {c1[1] - cur[1]} {c2[0] - cur[0]} {c2[1] - cur[1]} {e[0] - cur[0]} {e[1] - cur[1]}')
            cur = e
    s.append('z')
    return ''.join(s).replace(' -', '-')


def poly(curve):
    return [(curve.start_point.x, curve.start_point.y)] + [(sg.end_point.x, sg.end_point.y) for sg in curve.segments]


def area(pts):
    return 0.5 * sum(pts[i][0] * pts[i - 1][1] - pts[i - 1][0] * pts[i][1] for i in range(len(pts)))


def bbox(pts):
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    return min(xs), min(ys), max(xs), max(ys)


info = [(c, poly(c), area(poly(c))) for c in curves]
outer_sign = np.sign(max((i[2] for i in info), key=abs))
groups = [{'b': bbox(p), 'a': abs(ar), 'd': [emit(c)]} for c, p, ar in info if np.sign(ar) == outer_sign]
for c, p, ar in info:
    if np.sign(ar) != outer_sign:
        b = bbox(p)
        parents = [gr for gr in groups if gr['b'][0] <= b[0] and gr['b'][1] <= b[1] and gr['b'][2] >= b[2] and gr['b'][3] >= b[3]]
        min(parents, key=lambda gr: gr['a'])['d'].append(emit(c))

groups.sort(key=lambda gr: gr['b'][0])
out = {
    'w': (X1 - X0) * 2,
    'h': (Y1 - Y0) * 2,
    'paths': [{'d': ''.join(gr['d']), 'x': round(gr['b'][0] * Q)} for gr in groups],
}
OUT.write_text(json.dumps(out, separators=(',', ':')))
print(f'{len(groups)} paths, {OUT.stat().st_size} bytes -> {OUT}')
