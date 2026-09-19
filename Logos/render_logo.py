import asyncio, os
from playwright.async_api import async_playwright

LOGO_DIR = r"C:\Users\kaino\AppData\Local\Temp\orchestrator\projects\sullivan-technologies\Logos"
CHROMIUM = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

RENDERS = [
    ("logo-icon.html", "logo-icon.png", 500, 500),
    ("logo-mark-lg.html", "logo-mark.png", 800, 800),
]

async def main():
    async with async_playwright() as pw:
        browser = await pw.chromium.launch(
            executable_path=CHROMIUM,
            args=["--no-sandbox", "--disable-gpu", "--disable-dev-shm-usage"],
            headless=True,
        )
        for html_name, png_name, w, h in RENDERS:
            page = await browser.new_page(viewport={"width": w, "height": h})
            url = "file://" + os.path.join(LOGO_DIR, html_name)
            await page.goto(url, wait_until="networkidle", timeout=15000)
            await page.wait_for_timeout(500)
            out = os.path.join(LOGO_DIR, png_name)
            await page.screenshot(path=out, full_page=False)
            print(f"Wrote {out} ({w}x{h})")
            await page.close()
        await browser.close()

asyncio.run(main())
