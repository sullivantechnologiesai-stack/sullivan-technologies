"""
Render the SAME transparent logo at 500x500 on two backgrounds to prove the
background-mismatch issue is resolved:

1. navy (#0f172a)  - the page header / footer color
2. white (#ffffff)  - the page content section color

Both renders use the SAME transparent logo-mark.png. If the logo's dark
hexagon fill used to "not match" on light sections, this proves it now blends
cleanly because the background is transparent.
"""
import asyncio, os
from playwright.async_api import async_playwright
from pathlib import Path
from PIL import Image
import numpy as np

LOGO_DIR = Path(r"C:\Users\kaino\AppData\Local\Temp\orchestrator\projects\sullivan-technologies\Logos")
LOGO = LOGO_DIR / "logo-mark.png"

OUT_DIR = Path(r"C:\Users\kaino\Desktop")
NAVY = "#0f172a"
WHITE = "#ffffff"


def make_html(bg_hex):
    return f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8">
<style>
html,body{{margin:0;padding:0;background:{bg_hex};display:flex;align-items:center;justify-content:center;height:100%;}}
img{{display:block;}}
</style></head>
<body>
<img src="file://{LOGO}" width="200" height="200" alt="logo">
</body></html>"""


async def render(bg_hex, name):
    html = make_html(bg_hex)
    out = OUT_DIR / name
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(
            args=["--no-sandbox","--disable-gpu","--disable-dev-shm-usage","--force-color-profile=srgb"],
            headless=True,
        )
        page = await browser.new_page(viewport={"width":500,"height":500})
        await page.set_content(html)
        await page.wait_for_timeout(400)
        await page.screenshot(path=str(out), full_page=False, omit_background=True)
        print(f"Wrote {out}")
        await page.close()
        await browser.close()
    return out


async def main():
    await render(NAVY, "logo-on-navy.png")
    await render(WHITE, "logo-on-white.png")


asyncio.run(main())

for name, bg in [("logo-on-navy.png", NAVY), ("logo-on-white.png", WHITE)]:
    p = OUT_DIR / name
    img = Image.open(p)
    arr = np.array(img)
    print(f"\n=== {name} ===")
    print(f"  mode={img.mode} size={img.size} bytes={p.stat().st_size:,}")
    # sample corners (should be pure background color, fully opaque)
    corners = [tuple(int(x) for x in arr[0,0]), tuple(int(x) for x in arr[0,-1]),
               tuple(int(x) for x in arr[-1,0]), tuple(int(x) for x in arr[-1,-1])]
    rounded = [tuple(round(c/10)*10 for c in pt[:3]) for pt in corners]
    print(f"  corners (rounded to 10): {rounded}")
    print(f"  center pixel: {tuple(int(x) for x in arr[250,250])}")
    print(f"  background should be {bg}")
