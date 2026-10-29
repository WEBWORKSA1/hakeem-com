# -*- coding: utf-8 -*-
"""Render the share image (og.png) and app icons from favicon.svg.

Optional. Needs `pip install playwright` and `python -m playwright install --with-deps chromium`.
Upload the three PNGs to assets/img/; the share-image tags then switch on automatically.
"""
import os
from playwright.sync_api import sync_playwright

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(ROOT, "assets", "img")
svg = open(os.path.join(IMG, "favicon.svg"), encoding="utf-8").read()

OG = """<html><head>
<link href="https://fonts.googleapis.com/css2?family=Alegreya:wght@500&family=Alegreya+Sans:wght@400;700&display=block" rel="stylesheet">
<style>
body{margin:0;width:1200px;height:630px;background:#1F2A44;color:#EEF1EA;display:flex;align-items:center;justify-content:space-between;padding:0 90px;box-sizing:border-box}
h1{font-family:Alegreya,Georgia,serif;font-size:88px;font-weight:500;line-height:1.04;margin:0 0 26px;letter-spacing:-1px}
p{font-family:'Alegreya Sans',Arial,sans-serif;font-size:32px;color:#B9C1D4;margin:0;max-width:640px;line-height:1.3}
.k{font-family:'Alegreya Sans',Arial,sans-serif;font-size:32px;color:#D99A1E;font-weight:700;margin-bottom:26px}
</style></head><body><div><div class="k">Hakeem.com</div><h1>Old remedies,<br>honest evidence.</h1>
<p>Herbal and Unani medicine, graded against modern research.</p></div><div>%s</div></body></html>""" % svg.replace("<svg ", '<svg width="300" height="300" ', 1)

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page(viewport={"width": 1200, "height": 630})
    page.set_content(OG, wait_until="networkidle")
    page.wait_for_timeout(500)
    page.screenshot(path=os.path.join(IMG, "og.png"))
    for n in (192, 512):
        page.set_viewport_size({"width": n, "height": n})
        page.set_content('<html><body style="margin:0">%s</body></html>' % svg.replace("<svg ", '<svg width="%d" height="%d" ' % (n, n), 1))
        page.screenshot(path=os.path.join(IMG, "icon-%d.png" % n), omit_background=True)
    browser.close()
print("Rendered og.png, icon-192.png and icon-512.png")
