import asyncio
from playwright.async_api import async_playwright

W = r"C:\Users\kaino\AppData\Local\Temp\orchestrator\projects\sullivan-technologies\Logos"
CH = r"C:\Program Files\Google\Chrome\Application\chrome.exe"

ICON_W = 400
ICON_H = 400

ICON_SVG = '''<svg width="400" height="400" viewBox="0 0 400 400" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="sg-i" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#2563eb"/><stop offset="100%" stop-color="#38bdf8"/>
    </linearGradient>
  </defs>
  <rect width="400" height="400" fill="#080c14"/>
  <g stroke="#111827" stroke-width="1.4" opacity="0.5">
    <line x1="28" y1="28" x2="66" y2="28"/><line x1="28" y1="28" x2="28" y2="66"/>
    <line x1="372" y1="28" x2="334" y2="28"/><line x1="372" y1="28" x2="372" y2="66"/>
    <line x1="28" y1="372" x2="66" y2="372"/><line x1="28" y1="372" x2="28" y2="334"/>
    <line x1="372" y1="372" x2="334" y2="372"/><line x1="372" y1="372" x2="372" y2="334"/>
  </g>
  <!-- Hexagon flat-top R=72 centered (200,200) -->
  <polygon points="272,200 236,262.35 164,262.35 128,200 164,137.65 236,137.65"
           fill="url(#sg-i)" stroke="#102a5e" stroke-width="1.4" stroke-linejoin="miter"/>
  <!-- S negative space: flipped S centered (200,200), snug in hex R=72 -->
  <path d="M232,166 L168,166 L168,190 L232,190 L232,214 L168,214 L168,238"
        fill="#080c14" stroke="none"/>
</svg>'''

LOCKUP_SVG = '''<svg width="800" height="300" viewBox="0 0 800 300" xmlns="http://www.w3.org/2000/svg">
  <defs>
    <linearGradient id="sg-lk" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0%" stop-color="#2563eb"/><stop offset="100%" stop-color="#38bdf8"/>
    </linearGradient>
  </defs>
  <rect width="800" height="300" fill="#080c14"/>
  <!-- corner ticks -->
  <g stroke="#111827" stroke-width="1" opacity="0.6">
    <line x1="20" y1="18" x2="70" y2="18"/><line x1="20" y1="18" x2="20" y2="68"/>
    <line x1="780" y1="18" x2="590" y2="18"/><line x1="780" y1="18" x2="780" y2="68"/>
    <line x1="20" y1="282" x2="70" y2="282"/><line x1="20" y1="282" x2="20" y2="232"/>
    <line x1="780" y1="282" x2="590" y2="282"/><line x1="780" y1="282" x2="780" y2="232"/>
  </g>
  <!-- NEGATIVE-SPACE MARK: hexagon (flat-top R=42, centered 110,150) filled with S's blue.
       S drawn on top in bg color -> true negative-space cutout, snug in hex. -->
  <polygon points="152,150 131,192.2 89,192.2 68,150 89,107.8 131,107.8"
           fill="url(#sg-lk)" stroke="#102a5e" stroke-width="1" stroke-linejoin="miter"/>
  <path d="M142,120 L78,120 L78,145 L142,145 L142,170 L78,170 L78,195"
        fill="#080c14" stroke="none"/>
  <!-- WORDMARK: SULLIVAN bold white + TECHNOLOGIES lighter blue, right of mark -->
  <text x="470" y="138" text-anchor="middle"
        font-family="Segoe UI, Arial, sans-serif" font-weight="700"
        font-size="46" letter-spacing="6" fill="#ffffff">SULLIVAN</text>
  <text x="470" y="168" text-anchor="middle"
        font-family="Segoe UI, Arial, sans-serif" font-weight="300"
        font-size="17" letter-spacing="16" fill="#60a5fa">TECHNOLOGIES</text>
  <!-- accent bar + dot (Concept 1) -->
  <rect x="406" y="178" width="128" height="3" rx="1.5" fill="url(#sg-lk)"/>
  <circle cx="534" cy="179.5" r="3.5" fill="#38bdf8"/>
</svg>'''

HTML = """<!DOCTYPE html>
<html lang="en"><head><meta charset="UTF-8"><style>
  html,body{{margin:0;padding:0;background:#080c14;display:flex;align-items:center;justify-content:center;height:100%;width:100%}}
  svg{{display:block}}
</style></head><body>{svg}</body></html>"""

async def main():
    import os
    async with async_playwright() as p:
        b = await p.chromium.launch(executable_path=CH, headless=True,
            args=["--no-sandbox","--disable-gpu","--disable-dev-shm-usage"])

        # icon standalone (centered on its own canvas)
        pg = await b.new_page(viewport={"width":ICON_W,"height":ICON_H})
        await pg.set_content(HTML.format(svg=ICON_SVG), wait_until="networkidle")
        await pg.wait_for_timeout(500)
        await pg.screenshot(path=W+"/logo-icon.png")
        await pg.close()

        # full lockup standalone
        pg = await b.new_page(viewport={"width":800,"height":300})
        await pg.set_content(HTML.format(svg=LOCKUP_SVG), wait_until="networkidle")
        await pg.wait_for_timeout(500)
        await pg.screenshot(path=W+"/logo-lockup.png")
        await pg.close()

        await b.close()
        print("rendered: logo-icon.png, logo-lockup.png (standalone, clean)")

asyncio.run(main())
