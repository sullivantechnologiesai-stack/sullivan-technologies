import asyncio, os
from playwright.async_api import async_playwright

LOGO_DIR = r"C:\Users\kaino\AppData\Local\Temp\orchestrator\projects\sullivan-technologies\Logos"

# High-resolution renders: 2000x2000 gives crisp 500px and 120px downscales.
# Browser screenshot captures real transparency (alpha) when body has no background.
RENDERS = [
    ("logo-mark.html", "logo-mark.png", 2000, 2000, 500, 500),
    ("logo-mark.html", "logo-mark-lg.png", 2000, 2000, 800, 800),
]

async def main():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(
            args=["--no-sandbox", "--disable-gpu", "--disable-dev-shm-usage", "--force-color-profile=srgb"],
            headless=True,
        )
        for html_name, png_name, render_w, render_h, final_w, final_h in RENDERS:
            page = await browser.new_page(viewport={"width": render_w, "height": render_h})
            url = "file://" + os.path.join(LOGO_DIR, html_name)
            await page.goto(url, wait_until="networkidle", timeout=20000)
            await page.wait_for_timeout(600)
            out = os.path.join(LOGO_DIR, png_name)
            await page.screenshot(path=out, full_page=False, omit_background=True)
            print(f"Wrote {out} ({render_w}x{render_h}) -> will be used at {final_w}x{final_h}")
            await page.close()
        await browser.close()

asyncio.run(main())
