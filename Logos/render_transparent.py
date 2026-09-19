"""
Render logo-mark.html to a transparent PNG via chroma-key.

Plan:
1. Load logo-mark.html in headless Chromium at 2000x2000 (high-res, no pixelation).
2. After load, force body background to a color NOT present in the logo
   (pure magenta #ff00ff). The logo palette is navy/blues/cyan/white/black -
   magenta does not appear anywhere in the mark.
3. Screenshot full page (omit_background=False so we get a solid background).
4. Close browser.
5. In PIL, replace every pixel that is exactly #ff00ff with full transparent.
6. Save as logo-mark.png (2000x2000) and logo-mark-lg.png (also 2000x2000,
   same source -> identical transparent file; the "lg" name is preserved for
   the 800px display target).
7. Verify: mode is RGBA, corners are fully transparent, content colors intact.
"""
import asyncio, os
from playwright.async_api import async_playwright
from pathlib import Path
from PIL import Image
import numpy as np

LOGO_DIR = Path(r"C:\Users\kaino\AppData\Local\Temp\orchestrator\projects\sullivan-technologies\Logos")
HTML = LOGO_DIR / "logo-mark.html"

MASK_COLOR = (255, 0, 255)  # pure magenta - guaranteed absent from logo palette


async def render():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(
            args=[
                "--no-sandbox",
                "--disable-gpu",
                "--disable-dev-shm-usage",
                "--force-color-profile=srgb",
            ],
            headless=True,
        )
        # 2000x2000 viewport: renders the 500x500 viewBox at 4x, crisp when
        # down-scaled. SVG fills the viewport (width/height 100vw/100vh).
        page = await browser.new_page(viewport={"width": 2000, "height": 2000})
        await page.goto("file://" + str(HTML), wait_until="networkidle", timeout=20000)
        await page.wait_for_timeout(600)
        # Force a solid known mask color behind the logo.
        await page.evaluate("() => { document.body.style.backgroundColor = '#ff00ff'; }")
        await page.wait_for_timeout(200)
        out = LOGO_DIR / "logo-magenta.png"
        await page.screenshot(path=str(out), full_page=False, omit_background=False)
        print(f"Rendered {out} ({os.path.getsize(out):,} bytes)")
        await page.close()
        await browser.close()


def chroma_key(src: Path, dst: Path):
    img = Image.open(src).convert("RGBA")
    arr = np.array(img)
    rgb = arr[..., :3]
    rmask = rgb[..., 0] == MASK_COLOR[0]
    gmask = rgb[..., 1] == MASK_COLOR[1]
    bmask = rgb[..., 2] == MASK_COLOR[2]
    mask = rmask & gmask & bmask
    arr[mask, 3] = 0
    Image.fromarray(arr, "RGBA").save(dst)
    print(f"Chroma-keyed {dst} ({os.path.getsize(dst):,} bytes) -> "
          f"{int(mask.sum()):,} / {mask.size:,} mask pixels = "
          f"{mask.mean()*100:.2f}% replaced with transparent")


def verify(path: Path):
    img = Image.open(path)
    arr = np.array(img)
    print(f"\n=== {path.name} ===")
    print(f"mode : {img.mode}")
    print(f"size : {img.size}")
    print(f"bytes: {path.stat().st_size:,}")
    if arr.ndim == 3 and arr.shape[-1] == 4:
        a = arr[..., 3]
        print(f"ALPHA present.")
        print(f"  corners     : {[tuple(int(x) for x in pt) for pt in [arr[0,0], arr[0,-1], arr[-1,0], arr[-1,-1]]]}")
        print(f"  center      : {tuple(int(x) for x in arr[1000,1000])}")
        print(f"  frac a==0   : {float((a==0).mean()):.4f}")
        print(f"  frac a<250  : {float((a<250).mean()):.4f}")
        opaque = a > 240
        if opaque.any():
            op_rgb = arr[opaque][..., :3]
            dark = (op_rgb[:,0] == 8) & (op_rgb[:,1] == 12) & (op_rgb[:,2] == 20)
            print(f"  opaque dark-fill(8,12,20) frac: {float(dark.mean()):.4f}")
            cyanish = (op_rgb[:,2] > 150) & (op_rgb[:,0] < 100)
            print(f"  opaque cyan-ish frac          : {float(cyanish.mean()):.4f}")
    else:
        print("NO ALPHA CHANNEL")


async def main():
    await render()
    src = LOGO_DIR / "logo-magenta.png"
    chroma_key(src, LOGO_DIR / "logo-mark.png")
    chroma_key(src, LOGO_DIR / "logo-mark-lg.png")
    verify(LOGO_DIR / "logo-mark.png")
    verify(LOGO_DIR / "logo-mark-lg.png")


asyncio.run(main())
