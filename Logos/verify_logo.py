import numpy as np
from PIL import Image
import os

files = [
    ("logo-icon.png", "Icon", 500, 500),
    ("logo-mark.png", "Mark", 800, 800),
]

for fn, label, w, h in files:
    path = rf"C:\Users\kaino\AppData\Local\Temp\orchestrator\projects\sullivan-technologies\Logos\{fn}"
    img = Image.open(path)
    arr = np.array(img.convert("RGB"))
    print(f"\n=== {label} ({fn}) ===")
    print(f"Dimensions: {img.size} (expected {w}x{h} — {'OK' if img.size==(w,h) else 'MISMATCH'})")

    # Ground color check (top-left corner should be bg #080c14)
    bg = arr[5, 5]
    print(f"Background at (5,5): RGB({bg[0]},{bg[1]},{bg[2]}) — expected ~#080c14 (8,12,20)")

    # Center pixel
    cx, cy = w//2, h//2
    center = arr[cy, cx]
    print(f"Center pixel ({cx},{cy}): RGB({center[0]},{center[1]},{center[2]})")

    # Sample points around the inner hex to detect blue gradient
    blue_samples = []
    # Inner hex center region: probe at several points inside the expected hex area
    # For icon (500): inner hex bounds ~110..390 → probe at (200,200),(250,250),(300,300),(200,300),(300,200)
    # For mark (800): inner hex bounds ~176..624 → probe at (320,320),(400,400),(480,480),(320,480),(480,320)
    if w == 500:
        probes = [(200,200),(250,250),(300,300),(200,300),(300,200),(250,150),(250,350)]
    else:
        probes = [(320,320),(400,400),(480,480),(320,480),(480,320),(400,240),(400,560)]
    for px, py in probes:
        r, g, b = arr[py, px]
        blue_samples.append((px, py, r, g, b))
    print("Blue hex probe samples (points inside inner hex area):")
    for px, py, r, g, b in blue_samples:
        r_val = r/255.0
        g_val = g/255.0
        b_val = b/255.0
        is_blue = (b_val > 0.4) and (b_val > r_val) and (b_val > g_val * 0.8)
        tag = "BLUE" if is_blue else "NOT-BLUE"
        print(f"  ({px:3d},{py:3d}): RGB({r:3d},{g:3d},{b:3d}) {tag}")

    # Check for dark 'st' pixels (bg color) inside blue region — negative space
    dark_count_in_blue = 0
    total_in_blue_probe = 0
    # Scan a sampling grid inside the inner hex region for dark (bg-colored) pixels
    if w == 500:
        x_range = range(115, 385, 4)
        y_range = range(115, 385, 4)
    else:
        x_range = range(180, 620, 6)
        y_range = range(180, 620, 6)
    for py in y_range:
        for px in x_range:
            r, g, b = arr[py, px]
            is_dark = (r < 20 and g < 22 and b < 28)  # near #080c14
            # Is this point inside the blue hex?
            # Test against the inner hex polygon roughly
            if w == 500:
                # inner hex: points 390,250 320,371.24 180,371.24 110,250 180,128.76 320,128.76
                pass  # rough check with simpler bounds
            if is_dark:
                dark_count_in_blue += 1
            total_in_blue_probe += 1
    print(f"Dark pixels (bg-color) in inner-hex scan region: {dark_count_in_blue}")

    # Overall blue pixel count in whole image
    blue_mask = (arr[:,:,2].astype(int) > 60) & (arr[:,:,2] > arr[:,:,0]) & (arr[:,:,2] > arr[:,:,1]*0.7)
    total_blue = int(blue_mask.sum())
    print(f"Total blue-ish pixels in image: {total_blue} ({100*total_blue/(w*h):.1f}%)")

    # Dark 'st' negative-space check: within the blue-filled region, count dark pixels
    # Focus on center band where 'st' lives
    if w == 500:
        st_x = slice(150, 350)
        st_y = slice(150, 350)
    else:
        st_x = slice(240, 560)
        st_y = slice(240, 560)
    st_region = arr[st_y, st_x]
    st_dark_mask = (st_region[:,:,0] < 20) & (st_region[:,:,1] < 22) & (st_region[:,:,2] < 28)
    st_dark_total = int(st_dark_mask.sum())
    st_region_total = st_region.shape[0] * st_region.shape[1]
    print(f"Dark (st-negative-space) pixels in center band: {st_dark_total} / {st_region_total} ({100*st_dark_total/st_region_total:.1f}%)")
    print(f"File size: {os.path.getsize(path):,} bytes")
