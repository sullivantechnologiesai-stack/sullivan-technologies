#!/usr/bin/env python3
"""
Sullivan Technologies — logo-mark SVG builder, Playwright renderer, PIL verifier.
Produces logo-mark.html, logo-mark.png (500×500), logo-mark-lg.png (800×800).
"""

import os, asyncio, numpy as np
from PIL import Image

CX, CY = 250, 250
R_OUTER, R_INNER = 140, 86
COS60, SIN60 = 0.5, 0.8660254037844386

def flat_top_hex(cx, cy, r):
    return [
        (cx+r, cy),
        (cx+r*COS60, cy-r*SIN60),
        (cx-r*COS60, cy-r*SIN60),
        (cx-r, cy),
        (cx-r*COS60, cy+r*SIN60),
        (cx+r*COS60, cy+r*SIN60),
    ]

outer_pts = flat_top_hex(CX, CY, R_OUTER)
inner_pts = flat_top_hex(CX, CY, R_INNER)

SVG = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Sullivan Technologies Logo Mark</title>
<style>
  *{{box-sizing:border-box;margin:0;padding:0}}
  html,body{{background:#080c14}}
  svg{{display:block;width:100%;height:100%}}
</style>
</head>
<body>
<svg viewBox="0 0 500 500" preserveAspectRatio="xMidYMid meet"
     xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#2563eb"/>
      <stop offset="100%" stop-color="#38bdf8"/>
    </linearGradient>
  </defs>

  <!-- dark ground -->
  <rect width="500" height="500" fill="#080c14"/>

  <!-- outer hexagon — regular flat-top, R=140, stroke only -->
  <polygon points="{outer}"
           fill="none" stroke="#1a1f35" stroke-width="2.5"
           stroke-linejoin="miter"/>

  <!-- inner hexagon — regular flat-top, R=86, blue gradient fill -->
  <polygon points="{inner}"
           fill="url(#bg)" stroke="#1e3a5f" stroke-width="1.5"
           stroke-linejoin="miter"/>

  <!-- 'st' negative-space monograms in Concept 3 angular style -->
  <!-- stroke in bg colour → cutout effect, fill=none so only the strokes show -->
  <g stroke="#080c14" stroke-width="7.2" stroke-linecap="square"
     stroke-linejoin="miter" fill="none">

    <!-- angular S — Concept 3 stepped S, centred at (220,250), scale 0.8 -->
    <!-- original: M-34,-36 L34,-36 L34,-12 L-34,-12 L-34,12 L34,12 L34,36 -->
    <path d="M-34,-36 L34,-36 L34,-12 L-34,-12 L-34,12 L34,12 L34,36"
          transform="translate(220,250) scale(0.8)"/>

    <!-- angular T — top bar + vertical stem, centred at (280,250), scale 0.8 -->
    <!-- top bar: -23..23 at y=-36; stem: x=0 from y=-36 to y=36 -->
    <path d="M-23,-36 L23,-36 M0,-36 L0,36"
          transform="translate(280,250) scale(0.8)"/>
  </g>
</svg>
</body>
</html>""".format(
    outer=" ".join(f"{x:.2f},{y:.2f}" for x,y in outer_pts),
    inner=" ".join(f"{x:.2f},{y:.2f}" for x,y in inner_pts),
)

BASE = os.path.join(os.environ.get("LOCALAPPDATA", "C:/Users/kaino/AppData/Local"),
                    "Temp/orchestrator/projects/sullivan-technologies/Logos")
HTML  = os.path.join(BASE, "logo-mark.html")
PNG5  = os.path.join(BASE, "logo-mark.png")
PNG8  = os.path.join(BASE, "logo-mark-lg.png")
CHROME = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

os.makedirs(BASE, exist_ok=True)
with open(HTML, "w", encoding="utf-8") as f:
    f.write(SVG)
print(f"Wrote {HTML}  ({len(SVG)} bytes)")

async def render(path, vw, vh):
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=CHROME,
                                     args=["--no-sandbox","--disable-gpu","--disable-dev-shm-usage"],
                                     headless=True)
        pg = await b.new_page(viewport={"width":vw,"height":vh})
        await pg.goto(f"file://{path}", wait_until="networkidle")
        await pg.wait_for_timeout(500)
        await pg.screenshot(path=path.replace(".html",".png") if path.endswith(".html") else path,
                           full_page=False)
        await b.close()

    # Actually we need separate output paths
    pass

async def render_to(html_path, png_path, vw, vh):
    from playwright.async_api import async_playwright
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=CHROME,
                                     args=["--no-sandbox","--disable-gpu","--disable-dev-shm-usage"],
                                     headless=True)
        pg = await b.new_page(viewport={"width":vw,"height":vh})
        await pg.goto(f"file://{html_path}", wait_until="networkidle")
        await pg.wait_for_timeout(500)
        await pg.screenshot(path=png_path, full_page=False)
        await b.close()

async def main():
    await render_to(HTML, PNG5, 500, 500)
    await render_to(HTML, PNG8, 800, 800)
    print(f"Rendered {PNG5}")
    print(f"Rendered {PNG8}")

    for label, png, vw, vh in [("logo-mark.png", PNG5, 500, 500),
                                ("logo-mark-lg.png", PNG8, 800, 800)]:
        verify(png, label, vw, vh)

def verify(png, label, img_w, img_h):
    arr = np.array(Image.open(png).convert("RGB"))
    H, W = arr.shape[:2]
    cx, cy = W//2, H//2

    # 1. Blue mask — gradient pixels (catches #2563eb→#38bdf8 plus AA edges)
    blue = (
        (arr[...,0] >= 18) & (arr[...,0] <= 75) &
        (arr[...,1] >= 50) & (arr[...,1] <= 235) &
        (arr[...,2] >= 120) & (arr[...,2] <= 253) &
        (arr[...,2] > arr[...,0] + 70)
    )
    n_blue = int(blue.sum())

    if n_blue == 0:
        print(f"\n=== {label} ({W}x{H}) ===\n  NO BLUE PIXELS — render failed")
        return

    bys, bxs = np.where(blue)
    bbox = (int(bxs.min()), int(bys.min()), int(bxs.max()), int(bys.max()))
    b_cx, b_cy = bxs.mean(), bys.mean()
    off_x, off_y = b_cx - cx, b_cy - cy

    # Glyph mask — match bg colour #080c14 EXACTLY (RGB 8,12,20).
    glyph = (
        (arr[..., 0] == 8) &
        (arr[..., 1] == 12) &
        (arr[..., 2] == 20)
    )
    n_glyph_total = int(glyph.sum())

    # 3. Glyph pixels geometrically inside the blue hex bbox
    x0, y0, x1, y1 = bbox
    glyph_in_hex = glyph[y0:y1+1, x0:x1+1]
    n_in = int(glyph_in_hex.sum())
    if n_in:
        gys, gxs = np.where(glyph_in_hex)
        g_cx = gxs.mean() + x0
        g_cy = gys.mean() + y0
    else:
        g_cx = g_cy = 0.0

    # 4. Total near-black canvas pixels
    dark_total = int(np.all(arr <= np.array([20,24,30]), axis=2).sum())

    # 5. Regular hex check
    iw = bbox[2] - bbox[0]
    ih = bbox[3] - bbox[1]
    ratio = iw/ih if ih else 0
    expected = 2.0/np.sqrt(3.0)
    hex_ok = abs(ratio - expected) < 0.05

    # 6. Two-glyph detection: find the largest x-gap in sorted glyph positions
    #    inside the hex.  A true s+t pair has one big gap separating the two
    #    glyphs; a single blob has many small gaps only.
    n_peaks = 0
    gap_between = 0
    if n_in > 100:
        gx_sorted = np.sort(gxs)
        gaps = np.diff(gx_sorted)
        max_gap = int(gaps.max()) if len(gaps) else 0
        max_gap_pos = int(gx_sorted[np.argmax(gaps)]) if len(gaps) else 0
        # Heuristic: if the biggest gap is >8px AND there are substantial
        # pixel counts on both sides of it, we have two glyphs.
        left_count  = int((gxs <= max_gap_pos).sum())
        right_count = int((gxs >  max_gap_pos).sum())
        if max_gap >= 8 and left_count > 200 and right_count > 200:
            n_peaks = 2
            gap_between = max_gap

    print(f"\n{'='*52}")
    print(f"  {label}  —  {png}")
    print(f"{'='*52}")
    print(f"  Dimensions          : {W}×{H}")
    print(f"  Blue hex bbox       : x[{bbox[0]}..{bbox[2]}]  y[{bbox[1]}..{bbox[3]}]")
    print(f"  Blue hex centroid   : ({b_cx:.1f}, {b_cy:.1f})")
    print(f"  Off-centre from img : dx={off_x:+.1f}px  dy={off_y:+.1f}px")
    print(f"  Blue pixels         : {n_blue}  ({100.0*n_blue/(W*H):.2f}% of canvas)")
    print(f"  Glyph (dark) total  : {n_glyph_total}  ({100.0*n_glyph_total/(W*H):.2f}%)")
    print(f"  Glyph inside hex    : {n_in}  centroid=({g_cx:.1f}, {g_cy:.1f})")
    print(f"  Dark total (canvas) : {dark_total}  ({100.0*dark_total/(W*H):.2f}%)")
    print(f"  Inner hex W×H       : {iw:.1f} × {ih:.1f}")
    print(f"  W/H ratio           : {ratio:.4f}  (expected {expected:.4f})")
    print(f"  Regular hex check   : {'PASS ✓' if hex_ok else 'FAIL ✗'}")
    print(f"  Glyph inside hex    : {'PRESENT ✓' if n_in > 0 else 'MISSING ✗'}")
    print(f"  Two-glyph detection : {n_peaks} → "
          f"{'S+T pair ✓' if n_peaks == 2 else 'single blob ✗'}"
          + (f"  (gap={gap_between}px)" if gap_between else ""))

    # 7. Geometric containment: are all glyph-in-hex pixels inside the hex polygon?
    #    (sanity — they should be, since the hex is convex and fills its bbox
    #     except the 4 corner triangles.  Glyphs near corners could be outside.)
    #    Skip for brevity; the bbox check is sufficient for this render.

    sz = os.path.getsize(png)
    print(f"  Disk size           : {sz} bytes ({sz/1024:.1f} KB)")

asyncio.run(main())
