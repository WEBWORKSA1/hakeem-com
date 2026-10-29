# -*- coding: utf-8 -*-
"""Static site generator for Hakeem.com.

Usage:
  python3 _build/build.py              writes the Jekyll source tree into the repository
                                       root; GitHub Pages builds it from the main branch.
  python3 _build/build.py --html DIR   writes the finished HTML site into DIR instead
                                       (for local preview and for checking the Jekyll output).

Edit the data (herbs.py, extras.py) or a page body in pages/, run the script, commit the
result. All internal links are relative, so the output works on any host or path.
"""
import html, json, os, re, sys, datetime
from urllib.parse import quote_plus
from xml.sax.saxutils import escape as xesc

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
sys.path.insert(0, HERE)
from herbs import HERBS, HERB_BY_SLUG, GRADES, QUADRANTS, CLASSES  # noqa: E402
from extras import HUBS, GLOSSARY, VIDEOS, REFS  # noqa: E402

SITE_URL = "https://hakeem.com"
SITE_NAME = "Hakeem.com"
ADSENSE_CLIENT = "ca-pub-6620975821265271"
# Manual ad units: add {"name": "slot-id"} once units are created in AdSense.
# Until then Auto ads places ads and these containers stay empty (nothing rendered).
AD_SLOTS = {}
REVIEWED = "29 October 2026"
REVIEWED_ISO = "2026-10-29"
VERSION = "20261029"
# Pages that never load the ad script: 404 plus the three conversion pages.
NO_ADS = {"404.html", "consult.html", "practitioners.html", "support.html"}

FONTS = ("https://fonts.googleapis.com/css2?family=Alegreya:ital,wght@0,400;0,500;0,700;1,400"
         "&family=Alegreya+Sans:wght@400;500;700&family=Amiri:wght@400;700&display=swap")

NAV = [
    ("herbs/", "Herbs"),
    ("interactions.html", "Interactions"),
    ("mizaj.html", "Mizaj quiz"),
    ("concerns/", "Concerns"),
    ("learn/", "Learn"),
    ("videos.html", "Videos"),
    ("support.html", "Support"),
]

e = html.escape
OUT = []  # (path, title, description) for sitemap/search


def rel_root(path):
    depth = path.count("/")
    return "../" * depth


def canonical(path):
    p = re.sub(r"index\.html$", "", path)
    return SITE_URL + "/" + p


# ---------------------------------------------------------------- fragments
def read_fragment(fp):
    raw = open(fp, encoding="utf-8").read()
    meta, body = {}, raw
    if "\n---\n" in raw:
        head, body = raw.split("\n---\n", 1)
        for line in head.splitlines():
            if ":" in line:
                k, v = line.split(":", 1)
                meta[k.strip()] = v.strip()
    return meta, body


def load_pages():
    pages = []
    base = os.path.join(HERE, "pages")
    for dp, _, files in os.walk(base):
        for f in sorted(files):
            if not f.endswith(".html"):
                continue
            fp = os.path.join(dp, f)
            path = os.path.relpath(fp, base).replace(os.sep, "/")
            meta, body = read_fragment(fp)
            meta["path"] = path
            pages.append((meta, body))
    return pages


def words(htmltext):
    return len(re.sub(r"<[^>]+>", " ", htmltext).split())


# ---------------------------------------------------------------- components
def ad_slot(name):
    slot = AD_SLOTS.get(name)
    if not slot:
        return ""
    return ('<div class="ad-wrap"><div class="ad-label">Advertisement</div>'
            '<ins class="adsbygoogle" style="display:block" data-ad-client="%s" data-ad-slot="%s" '
            'data-ad-format="auto" data-full-width-responsive="true"></ins>'
            '<script>(adsbygoogle=window.adsbygoogle||[]).push({});</script></div>' % (ADSENSE_CLIENT, slot))


def grade_html(g):
    label = GRADES[g][0]
    return ('<span class="grade" data-g="%d" title="%s"><span class="pips" aria-hidden="true">'
            '<i></i><i></i><i></i><i></i></span>%s</span>' % (g, e(GRADES[g][1]), label))


def best_grade(h):
    return max([u[1] for u in h["uses"]] or [0])


def temp_chip(h):
    if not h.get("q"):
        return '<span class="temp-chip"><i></i>Not classed</span>'
    q = QUADRANTS[h["q"]]
    return '<span class="temp-chip" data-q="%s"><i></i>%s</span>' % (h["q"], e(q[2].capitalize()))


def native_line(h):
    for lang, script, roman, rtl in h["names"]:
        if rtl:
            return '<span lang="ur" dir="rtl">%s</span>' % e(script)
    return ""


def label_tile(h, root):
    tags = " ".join(HERB_TAGS.get(h["slug"], []))
    return ('<a class="label" href="{root}herbs/{slug}.html" data-name="{search}" data-trad="{trad}" data-q="{q}" '
            'data-best="{best}" data-tags="{tags}"><span class="l-native">{native}</span><h3>{name}</h3>'
            '<span class="l-latin">{latin}</span><span class="l-use">{use}</span>'
            '<span class="l-foot">{chip}{grade}</span></a>').format(
        root=root, slug=h["slug"], name=e(h["name"]), latin=e(h["latin"]), use=e(h["use"]),
        native=native_line(h), chip=temp_chip(h), grade=grade_html(best_grade(h)),
        search=e((h["name"] + " " + h["latin"] + " " + " ".join(n[2] for n in h["names"])).lower()),
        trad=e("|".join(h["traditions"])), q=h.get("q") or "none", best=best_grade(h), tags=e(tags))


def tmap_svg(points, size=520, mini=False, marker=None):
    pad = 54 if not mini else 34
    cx = cy = size / 2
    sc = (size / 2 - pad) * 0.94
    s = []
    s.append('<svg viewBox="0 0 %d %d" role="img" aria-label="Temperament map: herbs placed from cold to hot and from moist to dry">' % (size, size))
    q = [("saudawi", pad, pad), ("safrawi", cx, pad), ("balghami", pad, cy), ("damwi", cx, cy)]
    for key, x, y in q:
        s.append('<rect x="%.1f" y="%.1f" width="%.1f" height="%.1f" rx="%d" style="fill:var(--q-%s);opacity:.09"/>' % (x, y, cx - pad, cy - pad, 6 if not mini else 3, key))
    s.append('<line class="axis" x1="%d" y1="%d" x2="%d" y2="%d"/>' % (pad, cy, size - pad, cy))
    s.append('<line class="axis" x1="%d" y1="%d" x2="%d" y2="%d"/>' % (cx, pad, cx, size - pad))
    if not mini:
        s.append('<text class="axis-label" x="%d" y="%d" text-anchor="end">Hot</text>' % (size - 2, cy + 4))
        s.append('<text class="axis-label" x="2" y="%d">Cold</text>' % (cy + 4))
        s.append('<text class="axis-label" x="%d" y="%d" text-anchor="middle">Dry</text>' % (cx, pad - 10))
        s.append('<text class="axis-label" x="%d" y="%d" text-anchor="middle">Moist</text>' % (cx, size - pad + 22))
        corner = {"saudawi": (pad, 18, "start"), "safrawi": (size - pad, 18, "end"),
                  "balghami": (pad, size - pad + 22, "start"), "damwi": (size - pad, size - pad + 22, "end")}
        for key, (x, y, anc) in corner.items():
            name, ar, desc, greek = QUADRANTS[key]
            s.append('<text class="q-label" x="%d" y="%d" text-anchor="%s">%s</text>' % (x, y, anc, name))
            s.append('<text class="q-sub" x="%d" y="%d" text-anchor="%s">%s</text>' % (x, y + 20 if y < cy else y + 20, anc, ar))
    else:
        s.append('<text class="axis-label" x="%d" y="%d" text-anchor="end" style="font-size:15px">Hot</text>' % (size - 2, cy + 5))
        s.append('<text class="axis-label" x="2" y="%d" style="font-size:15px">Cold</text>' % (cy + 5))
        s.append('<text class="axis-label" x="%d" y="%d" text-anchor="middle" style="font-size:15px">Dry</text>' % (cx, 22))
        s.append('<text class="axis-label" x="%d" y="%d" text-anchor="middle" style="font-size:15px">Moist</text>' % (cx, size - 10))
    for i, h in enumerate(points):
        px = cx + h["x"] * sc
        py = cy - h["y"] * sc
        right_side = px > size - pad - 60
        tx, anc = (-12, "end") if right_side else (12, "start")
        if mini:
            s.append('<g class="dot on" transform="translate(%.1f %.1f)"><circle r="11" style="fill:var(--q-%s)"/></g>' % (px, py, h["q"]))
        else:
            s.append('<g class="dot" tabindex="0" role="button" data-slug="%s" style="--i:%d" transform="translate(%.1f %.1f)" '
                     'aria-label="%s, %s"><circle r="7.5" style="fill:var(--q-%s)"/><text x="%d" y="4.5" text-anchor="%s">%s</text></g>'
                     % (h["slug"], i, px, py, e(h["name"]), e(h["temp"]), h["q"], tx, anc, e(short_name(h))))
    if marker:
        px = cx + marker[0] * sc
        py = cy - marker[1] * sc
        s.append('<g class="you" id="rMarker" transform="translate(%.1f %.1f)"><circle r="13" style="fill:none;stroke:var(--ink);stroke-width:3"/>'
                 '<circle r="5" style="fill:var(--ink)"/><text x="18" y="5" style="font:700 14px var(--sans);fill:var(--ink)">You</text></g>' % (px, py))
    s.append("</svg>")
    return "".join(s)


def short_name(h):
    return {"Psyllium (Isabgol)": "Psyllium", "Licorice root": "Licorice", "Amla (Indian gooseberry)": "Amla",
            "Holy basil (Tulsi)": "Tulsi", "Sweet almond": "Almond"}.get(h["name"], h["name"])


def mapped_herbs():
    return [h for h in HERBS if h.get("q")]


def tmap_block(root):
    pts = mapped_herbs()
    data = {h["slug"]: {"n": h["name"], "l": h["latin"], "t": h["temp"], "u": h["use"],
                        "g": GRADES[best_grade(h)][0], "q": QUADRANTS[h["q"]][0]} for h in pts}
    return ('<div class="tmap" id="tmap" data-base="%sherbs/">%s<div class="tmap-card" id="tmapCard" aria-live="polite">'
            '<b>Every herb has a temperament.</b> In Unani medicine each remedy is classed as hot or cold, dry or moist. '
            'Tap a dot to see the herb and how strong the modern evidence is.</div>'
            '<p class="tmap-note">Positions are approximate. Classical texts differ, and temperament describes tradition, not proof that a herb works.</p>'
            '<script type="application/json" id="tmapData">%s</script></div>') % (root, tmap_svg(pts), json.dumps(data, ensure_ascii=False))


def grade_scale():
    out = ['<div class="grade-scale">']
    for g in (4, 3, 2, 1):
        out.append('<div>%s<h4>%s</h4><p>%s</p></div>' % (grade_html(g).replace('</span>%s</span>' % GRADES[g][0], '</span></span>'), GRADES[g][0], e(GRADES[g][1])))
    out.append("</div>")
    out.append('<p class="small muted mt1">A fifth label, <b>Not supported</b>, marks uses where good trials found no benefit, such as ginkgo for preventing dementia.</p>')
    return "".join(out)


def newsletter_form(n):
    return ('<form class="js-form" data-subject="Newsletter signup" data-ok="You are on the list. Herb of the Week arrives on Sundays.">'
            '<div class="foot-news"><label class="sr-only" for="nl-%s">Email address</label>'
            '<input id="nl-%s" name="email" type="email" required placeholder="Your email" autocomplete="email">'
            '<input type="hidden" name="list" value="Herb of the Week">'
            '<input class="hp" name="_honey" tabindex="-1" autocomplete="off" aria-hidden="true">'
            '<button class="btn btn-primary btn-small" type="submit">Subscribe</button></div>'
            '<div class="form-msg" role="status"></div></form>') % (n, n)


def herb_options():
    return "".join('<option value="%s">%s</option>' % (e(h["name"]), e(h["name"])) for h in sorted(HERBS, key=lambda x: x["name"]))


def video_card(v):
    return ('<div class="video-item"><div class="video" data-yt="%s" role="button" tabindex="0" aria-label="Play video: %s"></div>'
            '<div class="video-meta"><h3>%s</h3><p>%s. %s</p></div></div>') % (v["id"], e(v["title"]), e(v["title"]), e(v["channel"]), e(v["note"]))


def guides_list(guides, root, limit=None):
    items = guides[:limit] if limit else guides
    out = ['<ul class="guide-list">']
    for m in items:
        out.append('<li><a href="%s%s"><h3>%s</h3><p>%s</p><div class="meta">%s, %d min read</div></a></li>' % (
            root, m["path"], e(m["short"]), e(m["summary"]), e(m.get("category", "Guide")), m["minutes"]))
    out.append("</ul>")
    return "".join(out)


def hubs_list(root):
    out = ['<ul class="guide-list">']
    for hb in HUBS:
        out.append('<li><a href="%sconcerns/%s.html"><h3>%s</h3><p>%s</p><div class="meta">%d herbs reviewed</div></a></li>' % (
            root, hb["slug"], e(hb["title"]), e(hb["blurb"]), len(hb["herbs"])))
    out.append("</ul>")
    return "".join(out)


def ix_tool():
    herbs = "".join('<label><input type="checkbox" name="ixh" value="%s"> %s</label>' % (h["slug"], e(h["name"])) for h in sorted(HERBS, key=lambda x: x["name"]))
    meds = "".join('<label title="%s"><input type="checkbox" name="ixm" value="%s"> %s</label>' % (e(c[2]), c[0], e(c[1])) for c in CLASSES)
    return ('<div class="ix-tool"><div class="ix-pick"><h3>1. Herbs and supplements</h3>%s</div>'
            '<div class="ix-pick"><h3>2. Medicines and situations</h3>%s</div></div>') % (herbs, meds)


HERB_TAGS = {}
for hb in HUBS:
    for slug, _ in hb["herbs"]:
        HERB_TAGS.setdefault(slug, []).append(hb["slug"])


def concern_options():
    return "".join('<option value="%s">%s</option>' % (hb["slug"], e(hb["title"])) for hb in HUBS)


# ---------------------------------------------------------------- layout
def jsonld(obj):
    return '<script type="application/ld+json">%s</script>' % json.dumps(obj, ensure_ascii=False)


def breadcrumb_ld(trail):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [
        {"@type": "ListItem", "position": i + 1, "name": n, "item": SITE_URL + "/" + p} for i, (n, p) in enumerate(trail)]}


ADS_TAG = ('<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=%s" '
           'crossorigin="anonymous"></script>' % ADSENSE_CLIENT)
PAGES = []  # every page: path, layout name, front-matter values, content


def nav_html(root):
    nav = "".join('<li><a href="%s%s">%s</a></li>' % (root, href, label) for href, label in NAV)
    return nav + ('<li class="menu-cta"><a href="%scontests.html">Contests</a></li><li class="menu-cta">'
                  '<a class="btn btn-primary" href="%sconsult.html">Find a practitioner</a></li>' % (root, root))


def png_tags(root):
    # Share image and touch icon are PNGs rendered by make_images.py; tags appear only when the files exist.
    return ('\n<meta property="og:image" content="%s/assets/img/og.png">\n<meta name="twitter:card" content="summary_large_image">'
            '\n<link rel="apple-touch-icon" href="%sassets/img/icon-192.png">' % (SITE_URL, root))


def layout(path, title, desc, body, ld=None, ogtype="website", cls="", kind="default", fields=None):
    """Register a page. body is the page content (for herb and hub pages, fields fill the layout instead)."""
    full_title = title if title.endswith(SITE_NAME) else "%s | %s" % (title, SITE_NAME)
    PAGES.append({"path": path, "kind": kind, "content": body, "fields": fields or {},
                  "base": {"v_root": rel_root(path), "v_t": e(full_title), "v_d": e(desc), "v_c": canonical(path),
                           "v_ogt": ogtype, "v_ld": "".join(jsonld(x) for x in (ld or [])), "v_cls": cls},
                  "noads": path in NO_ADS, "is404": path == "404.html"})
    OUT.append((path, title, desc))


def render_html(pg, has_png):
    """The finished page, exactly as GitHub Pages renders it from the Jekyll tree."""
    b, f = pg["base"], pg["fields"]
    if pg["kind"] == "herb":
        body = HERB_TPL.format(root="../", reviewed=REVIEWED, ad1=ad_slot("herb-mid"), ad2=ad_slot("herb-end"),
                               related="".join(TILES[s] for s in f["rel"]), **{k: v for k, v in f.items() if k != "rel"})
    elif pg["kind"] == "hub":
        body = HUB_TPL.format(root="../", ad=ad_slot("hub-mid"), **f)
    elif pg["kind"] == "guide":
        body = GUIDE_TPL.format(root="../", reviewed=REVIEWED, body=pg["content"], **f)
    else:
        body = pg["content"]
    root = b["v_root"]
    return TEMPLATE.format(
        root=root, title=b["v_t"], desc=b["v_d"], canonical=b["v_c"], ogtype=b["v_ogt"], fonts=FONTS,
        ver=VERSION, ads="" if pg["noads"] else ADS_TAG, ld=b["v_ld"], cls=b["v_cls"], nav=nav_html(root), body=body,
        year=datetime.date.today().year, newsletter=newsletter_form("f"), client=ADSENSE_CLIENT,
        png=png_tags(root) if has_png else "", base=BASE_SCRIPT if pg["is404"] else "")


# 404.html is served for missing paths at any depth, so it resolves links from the site root at runtime.
BASE_SCRIPT = ("\n<script>(function(){var p=location.pathname.split('/'),b=/github\\.io$/.test(location.hostname)&&p[1]?'/'+p[1]+'/':'/';"
               "document.write('<base href=\"'+b+'\">')})();</script>\n<meta name=\"robots\" content=\"noindex\">")

TEMPLATE = """<!doctype html>
<html lang="en" data-root="{root}">
<head>
<meta charset="utf-8">{base}
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<link rel="canonical" href="{canonical}">
<meta property="og:type" content="{ogtype}">
<meta property="og:site_name" content="Hakeem.com">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{canonical}">{png}
<meta name="theme-color" content="#1F2A44">
<meta name="google-adsense-account" content="{client}">
<link rel="icon" href="{root}assets/img/favicon.svg" type="image/svg+xml">
<link rel="manifest" href="{root}site.webmanifest">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="{fonts}">
<link rel="stylesheet" href="{root}assets/css/main.css?v={ver}">
<script>try{{var t=localStorage.getItem('hk-theme');if(t)document.documentElement.setAttribute('data-theme',t)}}catch(e){{}}</script>
{ads}
{ld}
</head>
<body class="{cls}">
<a class="skip" href="#main">Skip to content</a>
<div class="interest"><a href="https://web.works/contact" target="_blank" rel="noopener"><b>Contact,</b> if you are interested in this website / domain name / sponsorship / advertisement / partnership</a></div>
<header class="site-header">
 <div class="wrap nav">
  <a class="brand" href="{root}index.html" aria-label="Hakeem.com home"><span class="brand-mark" lang="ar" aria-hidden="true">حكيم</span><span class="brand-name">Hakeem<span>.com</span></span></a>
  <nav aria-label="Main"><ul class="menu" id="menu">{nav}</ul></nav>
  <div class="nav-tools">
   <button class="icon-btn" id="searchBtn" type="button" aria-label="Search herbs and guides"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg></button>
   <button class="icon-btn" id="themeBtn" type="button" aria-label="Switch light or dark theme"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M21 12.8A9 9 0 1 1 11.2 3a7 7 0 0 0 9.8 9.8z"/></svg></button>
   <button class="icon-btn burger" id="burger" type="button" aria-label="Open menu" aria-expanded="false" aria-controls="menu"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><path d="M4 7h16M4 12h16M4 17h16"/></svg></button>
   <a class="btn btn-primary btn-small btn-cta" href="{root}consult.html">Find a practitioner</a>
  </div>
 </div>
</header>
<main id="main">
{body}
</main>
<footer class="site-footer">
 <div class="wrap">
  <div class="foot-grid">
   <div class="foot-brand">
    <a class="brand" href="{root}index.html"><span class="brand-mark" lang="ar" aria-hidden="true">حكيم</span><span class="brand-name" style="color:#fff">Hakeem<span style="color:#A9B2C6">.com</span></span></a>
    <p>Traditional herbal medicine, checked against modern evidence. Free to read, funded by readers, sponsors and advertising.</p>
    <p class="small" style="margin-bottom:4px">Herb of the Week, every Sunday:</p>
    {newsletter}
   </div>
   <div><h4>Explore</h4><ul>
    <li><a href="{root}herbs/">Herb library</a></li><li><a href="{root}concerns/">Health concerns</a></li><li><a href="{root}interactions.html">Interaction checker</a></li>
    <li><a href="{root}mizaj.html">Mizaj quiz</a></li><li><a href="{root}glossary.html">Unani glossary</a></li><li><a href="{root}videos.html">Videos</a></li></ul></div>
   <div><h4>Learn</h4><ul>
    <li><a href="{root}learn/what-is-unani-medicine.html">What is Unani medicine?</a></li><li><a href="{root}learn/four-temperaments-explained.html">The four temperaments</a></li>
    <li><a href="{root}learn/herb-drug-interactions.html">Herb–drug interactions</a></li><li><a href="{root}learn/buying-safe-herbal-products.html">Buying safe products</a></li><li><a href="{root}learn/">All guides</a></li></ul></div>
   <div><h4>Get involved</h4><ul>
    <li><a href="{root}consult.html">Find a practitioner</a></li><li><a href="{root}practitioners.html">List your practice</a></li><li><a href="{root}support.html">Support Hakeem.com</a></li>
    <li><a href="{root}contests.html">Contests and prizes</a></li><li><a href="{root}careers.html">Careers</a></li><li><a href="{root}advertise.html">Advertise and sponsor</a></li></ul></div>
   <div><h4>About</h4><ul>
    <li><a href="{root}about.html">About us</a></li><li><a href="{root}editorial-policy.html">Editorial policy</a></li><li><a href="{root}evidence-method.html">How we grade evidence</a></li>
    <li><a href="{root}contact.html">Contact</a></li><li><a href="{root}disclaimer.html">Medical disclaimer</a></li><li><a href="{root}privacy.html">Privacy policy</a></li>
    <li><a href="{root}cookies.html">Cookie policy</a></li><li><a href="{root}terms.html">Terms of use</a></li><li><a href="{root}trademark.html">Trademark and copyright</a></li></ul></div>
  </div>
  <div class="foot-legal">
   <span>&copy; <span class="year">{year}</span> Hakeem.com. Educational information only, not medical advice. In an emergency call your local emergency number.</span>
   <span>"Hakeem" is used as a descriptive word. Not affiliated with any person, clinic or brand of that name. <a href="{root}trademark.html">Disclosure</a></span>
  </div>
 </div>
</footer>
<div class="search-dlg" id="searchDlg" role="dialog" aria-modal="true" aria-label="Search">
 <div class="search-box">
  <label class="sr-only" for="searchInput">Search herbs, concerns and guides</label>
  <input id="searchInput" type="search" placeholder="Search herbs, concerns and guides" autocomplete="off">
  <ul class="search-res" id="searchRes"></ul>
  <p class="small muted mb0" style="margin-top:10px">Press <span class="kbd">Esc</span> to close.</p>
 </div>
</div>
<div class="cookie" id="cookie" role="region" aria-label="Cookie notice">
 <b>Cookies on Hakeem.com</b>
 <p class="mb0">We use cookies for essential features, and our advertising partner Google uses cookies to show and measure ads. <a href="{root}cookies.html">Cookie policy</a></p>
 <div class="btns"><button class="btn btn-ink btn-small" data-cookie="all" type="button">Accept</button><button class="btn btn-line btn-small" data-cookie="essential" type="button">Essential only</button></div>
</div>
<script src="{root}assets/js/main.js?v={ver}" defer></script>
</body>
</html>
"""


# ---------------------------------------------------------------- herb pages
def herb_page(h):
    path = "herbs/%s.html" % h["slug"]
    root = rel_root(path)
    names = "".join('<li><span>%s</span><b %s>%s</b>%s</li>' % (
        e(lang), 'class="ar" dir="rtl" lang="ur"' if rtl else "", e(script),
        (" <i class='muted'>(%s)</i>" % e(roman)) if roman and roman != script else "") for lang, script, roman, rtl in h["names"])
    if h.get("q"):
        qn = QUADRANTS[h["q"]]
        mini = ('<div class="mini-map"><h4>Temperament (mizaj)</h4>%s<p><b>%s</b>: %s. %s</p></div>'
                % (tmap_svg([h], size=220, mini=True), qn[0], e(h["temp"]), "Classical texts differ."))
    else:
        mini = '<div class="mini-map"><h4>Temperament (mizaj)</h4><p>%s.</p></div>' % e(h["temp"])
    uses = "".join('<tr><td><b>%s</b></td><td>%s</td><td>%s</td></tr>' % (e(u[0]), grade_html(u[1]), e(u[2])) for u in h["uses"])
    trad = "".join('<h3>%s</h3><p>%s</p>' % (e(k), e(v)) for k, v in h["traditional"].items())
    safety = "".join("<li>%s</li>" % e(x) for x in h["safety"])
    avoid = "".join("<li>%s</li>" % e(x) for x in h["avoid"])
    cls_names = {c[0]: c[1] for c in CLASSES}
    lvl_name = {"avoid": "Avoid", "caution": "Use caution", "monitor": "Monitor"}
    if h["ix"]:
        ix = "".join('<div class="ix-item" data-level="%s"><h4>%s<span class="lvl lvl-%s">%s</span></h4><p>%s</p></div>' % (
            lvl, e(cls_names[k]), lvl, lvl_name[lvl], e(note)) for k, lvl, note in h["ix"])
    else:
        ix = '<p>No significant interactions are well documented at food amounts. Tell your pharmacist about any supplement you take.</p>'
    refs = REFS.get(h["slug"], [])
    refs_html = "".join('<li><a href="%s" rel="noopener" target="_blank">%s</a></li>' % (e(u), e(t)) for t, u in refs)
    refs_html += '<li>Hakeem.com editorial review of traditional Unani and Ayurvedic sources and the references above.</li>'
    related = [x for x in HERBS if x["slug"] != h["slug"] and set(HERB_TAGS.get(x["slug"], [])) & set(HERB_TAGS.get(h["slug"], []))][:4]
    hub_links = ", ".join('<a href="%sconcerns/%s.html">%s</a>' % (root, s, e(HUB_BY_SLUG[s]["title"])) for s in HERB_TAGS.get(h["slug"], []))
    fields = dict(name=e(h["name"]), name_l=e(h["name"].split(" (")[0].lower() if not h["name"].startswith("St.") else h["name"]),
                  name_q=quote_plus(h["name"]), latin=e(h["latin"]), names=names, family=e(h["family"]), parts=e(h["parts"]),
                  forms=e(h["forms"]), trads=e(", ".join(h["traditions"])), best=grade_html(best_grade(h)),
                  hubs=('<dt>Concerns</dt><dd>%s</dd>' % hub_links) if hub_links else "", mini=mini,
                  summary=e(h["summary"]), verdict=e(h["verdict"]), uses=uses, research=e(h["research"]), safety=safety,
                  avoid=avoid, ix=ix, slug=h["slug"], trad=trad, confuse=e(h["confuse"]), buying=e(h["buying"]),
                  refs=refs_html, rel=[x["slug"] for x in related])
    ld = [{
        "@context": "https://schema.org", "@type": "MedicalWebPage", "name": "%s (%s): uses, evidence and safety" % (h["name"], h["latin"]),
        "url": canonical(path), "lastReviewed": REVIEWED_ISO, "inLanguage": "en", "audience": {"@type": "Patient"},
        "about": {"@type": "DietarySupplement", "name": h["name"], "alternateName": [n[2] for n in h["names"] if n[2]],
                  "nonProprietaryName": h["latin"]},
        "publisher": {"@type": "Organization", "name": SITE_NAME, "url": SITE_URL}},
        breadcrumb_ld([("Home", ""), ("Herb library", "herbs/"), (h["name"], path)])]
    desc = "%s (%s): what the evidence says, safety, medicine interactions and traditional Unani and Ayurvedic use." % (h["name"], h["latin"])
    layout(path, "%s: uses, evidence and safety" % h["name"], desc[:158], "", ld=ld, ogtype="article", kind="herb", fields=fields)


HERB_TPL = """<article>
<section class="page-hero" style="padding-bottom:36px">
 <div class="wrap">
  <nav class="crumbs" aria-label="Breadcrumb"><a href="{root}index.html">Home</a> / <a href="{root}herbs/">Herb library</a> / {name}</nav>
  <div class="herb-head">
   <div>
    <h1>{name}</h1>
    <p class="latin">{latin}</p>
    <ul class="names">{names}</ul>
    <dl class="facts">
     <dt>Plant family</dt><dd>{family}</dd>
     <dt>Parts used</dt><dd>{parts}</dd>
     <dt>Common forms</dt><dd>{forms}</dd>
     <dt>Traditions</dt><dd>{trads}</dd>
     <dt>Best evidence</dt><dd>{best}</dd>
     {hubs}
    </dl>
   </div>
   {mini}
  </div>
 </div>
</section>
<section style="padding-top:36px">
 <div class="wrap article">
  <div class="prose">
   <div class="reviewed"><span>By <b>Hakeem.com Editorial Team</b></span><span>Reviewed against cited sources <b>{reviewed}</b></span><span><a href="{root}evidence-method.html">How we grade evidence</a></span></div>
   <p class="summary">{summary}</p>
   <div class="note"><b>Our take.</b> {verdict}</div>
   <h2 id="evidence">What the evidence says</h2>
   <table class="ev-table"><thead><tr><th>Use</th><th>Evidence</th><th>What we found</th></tr></thead><tbody>{uses}</tbody></table>
   <p>{research}</p>
   {ad1}
   <h2 id="safety">Safety and who should avoid it</h2>
   <div class="caution"><h3>Side effects and cautions</h3><ul>{safety}</ul></div>
   <h3>Who should avoid it or ask first</h3>
   <ul>{avoid}</ul>
   <h2 id="interactions">Medicine interactions</h2>
   {ix}
   <p><a href="{root}interactions.html?h={slug}">Check {name_l} against your medicines</a></p>
   <h2 id="tradition">Traditional use</h2>
   <p class="muted" style="font-family:var(--sans);font-size:1rem">How each tradition has used this plant. Traditional use describes history, not proof that it works.</p>
   {trad}
   <h2 id="confuse">Do not confuse with</h2>
   <p>{confuse}</p>
   <h2 id="buying">Buying and quality</h2>
   <p>{buying} See our <a href="{root}learn/buying-safe-herbal-products.html">guide to buying safe herbal products</a>.</p>
   <h2 id="refs">Sources</h2>
   <ol class="refs">{refs}</ol>
   {ad2}
   <p class="small muted" style="font-family:var(--sans)">This page is for education and does not replace advice from your doctor, pharmacist or a qualified practitioner. Spotted an error? <a href="{root}contact.html?topic=Correction">Tell us</a>.</p>
  </div>
  <aside>
   <div class="aside-sticky">
    <div class="aside-box toc"><h3>On this page</h3><ol>
     <li><a href="#evidence">Evidence</a></li><li><a href="#safety">Safety</a></li><li><a href="#interactions">Interactions</a></li>
     <li><a href="#tradition">Traditional use</a></li><li><a href="#confuse">Do not confuse with</a></li><li><a href="#buying">Buying</a></li><li><a href="#refs">Sources</a></li></ol></div>
    <div class="aside-box"><h3>Ask a practitioner about {name_l}</h3><p class="small muted">Get matched with a qualified practitioner who can check it against your health and medicines.</p>
     <a class="btn btn-primary btn-small" href="{root}consult.html?herb={name_q}">Request a consultation</a></div>
    <div class="aside-box"><h3>Adopt this herb</h3><p class="small muted">Sponsors fund the upkeep of a herb page and get a credit line. No influence over content.</p>
     <a href="{root}advertise.html#adopt">Adopt {name_l}</a></div>
   </div>
  </aside>
 </div>
</section>
</article>
<section class="band section-tight">
 <div class="wrap">
  <div class="section-head"><h2>Related herbs</h2></div>
  <div class="labels">{related}</div>
 </div>
</section>
"""


HUB_BY_SLUG = {hb["slug"]: hb for hb in HUBS}


def hub_page(hb):
    path = "concerns/%s.html" % hb["slug"]
    root = rel_root(path)
    rows = []
    for slug, note in sorted(hb["herbs"], key=lambda x: -max([u[1] for u in HERB_BY_SLUG[x[0]]["uses"]])):
        h = HERB_BY_SLUG[slug]
        g = max([u[1] for u in h["uses"]])
        rows.append('<tr><td><a href="%sherbs/%s.html"><b>%s</b></a><br><i class="muted">%s</i></td><td>%s</td><td>%s</td></tr>' % (
            root, slug, e(h["name"]), e(h["latin"]), grade_html(g), e(note)))
    red = "".join("<li>%s</li>" % e(x) for x in hb["redflags"])
    fields = dict(title=e(hb["title"]), title_l=e(hb["title"].lower()), intro=e(hb["intro"]), rows="".join(rows), red=red,
                  advice=e(hb["advice"]), slug=hb["slug"])
    layout(path, "%s: herbs and the evidence" % hb["title"], hb["blurb"][:158], "",
           ld=[breadcrumb_ld([("Home", ""), ("Health concerns", "concerns/"), (hb["title"], path)])], kind="hub", fields=fields)


HUB_TPL = """<section class="page-hero"><div class="wrap">
 <nav class="crumbs" aria-label="Breadcrumb"><a href="{root}index.html">Home</a> / <a href="{root}concerns/">Health concerns</a> / {title}</nav>
 <h1>{title}</h1><p class="lead">{intro}</p></div></section>
<section><div class="wrap article"><div class="prose">
 <h2 class="mt0">Herbs reviewed for {title_l}</h2>
 <table class="ev-table"><thead><tr><th>Herb</th><th>Best evidence</th><th>For this concern</th></tr></thead><tbody>{rows}</tbody></table>
 {ad}
 <h2>See a doctor first if you have</h2>
 <div class="caution"><ul>{red}</ul></div>
 <h2>How to use this page</h2>
 <p>{advice}</p>
 <p>Evidence grades describe the strongest use we found for each herb, as explained in <a href="{root}evidence-method.html">our method</a>. Open a herb page for its full safety profile before trying it.</p>
</div><aside><div class="aside-sticky"><div class="aside-box"><h3>Want a personal plan?</h3><p class="small muted">A qualified practitioner can look at your history and medicines.</p><a class="btn btn-primary btn-small" href="{root}consult.html?concern={slug}">Request a consultation</a></div>
 <div class="aside-box"><h3>Check interactions</h3><p class="small muted">Taking prescription medicines? Check before you add any herb.</p><a href="{root}interactions.html">Open the checker</a></div></div></aside></div></section>
"""


# ---------------------------------------------------------------- blocks
def render_blocks(body, root, guides):
    featured = ["black-seed", "turmeric", "ginger", "ashwagandha", "psyllium", "garlic", "saffron", "peppermint"]
    blocks = {
        "tmap": lambda: tmap_block(root),
        "tmap:quiz": lambda: tmap_svg([], marker=(0, 0)),
        "labels:featured": lambda: '<div class="labels">%s</div>' % "".join(label_tile(HERB_BY_SLUG[s], root) for s in featured),
        "labels:all": lambda: '<div class="labels" id="labels">%s</div>' % "".join(label_tile(h, root) for h in sorted(HERBS, key=lambda x: x["name"])),
        "grade_scale": grade_scale,
        "guides:all": lambda: guides_list(guides, root),
        "guides:home": lambda: guides_list(guides, root, 6),
        "hubs": lambda: hubs_list(root),
        "videos:all": lambda: '<div class="grid g3">%s</div>' % "".join(video_card(v) for v in VIDEOS),
        "videos:home": lambda: '<div class="grid g3">%s</div>' % "".join(video_card(v) for v in VIDEOS[:3]),
        "herb_options": herb_options,
        "concern_options": concern_options,
        "ix_tool": ix_tool,
        "newsletter": lambda: newsletter_form("b"),
        "glossary": glossary_html,
        "az": lambda: az_bar(),
        "herb_count": lambda: str(len(HERBS)),
        "guide_count": lambda: str(len(guides)),
        "ad:home-1": lambda: ad_slot("home-1"),
        "ad:home-2": lambda: ad_slot("home-2"),
        "ad:guide-mid": lambda: ad_slot("guide-mid"),
        "reviewed": lambda: REVIEWED,
        "mapped_count": lambda: str(len(mapped_herbs())),
    }

    def rep(m):
        key = m.group(1)
        return blocks[key]() if key in blocks else m.group(0)
    body = re.sub(r"\{\{block:([a-z_:\-0-9]+)\}\}", rep, body)
    return body.replace("{{root}}", root)


def az_bar():
    letters = {h["name"][0].upper() for h in HERBS}
    out = []
    for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
        out.append('<a href="#" data-letter="%s">%s</a>' % (c, c) if c in letters else '<span aria-hidden="true">%s</span>' % c)
    return '<nav class="az" aria-label="Browse herbs A to Z">%s</nav>' % "".join(out)


def glossary_html():
    out = ['<dl class="glossary">']
    for term, ar, meaning in sorted(GLOSSARY, key=lambda x: x[0].lower()):
        anchor = re.sub(r"[^a-z0-9]+", "-", term.lower()).strip("-")
        out.append('<div class="g-item" id="%s"><dt><b>%s</b> %s</dt><dd>%s</dd></div>' % (
            anchor, e(term), ('<span class="ar" dir="rtl" lang="ur">%s</span>' % e(ar)) if ar else "", meaning))
    out.append("</dl>")
    return "".join(out)


# ---------------------------------------------------------------- guides
def guide_fields(meta, body, root, guides):
    path = meta["path"]
    others = [g for g in guides if g["path"] != path][:4]
    other_html = "".join('<li><a href="%s%s">%s</a></li>' % (root, g["path"], e(g["short"])) for g in others)
    heads = re.findall(r'<h2 id="([^"]+)">([^<]+)</h2>', body)
    toc = "".join('<li><a href="#%s">%s</a></li>' % (a, t) for a, t in heads)
    return dict(cat=e(meta.get("category", "Guide")), title=e(meta["title"]), summary=e(meta["summary"]),
                minutes=str(meta["minutes"]), others=other_html,
                toc=('<div class="aside-box toc"><h3>On this page</h3><ol>%s</ol></div>' % toc) if toc else "")


GUIDE_TPL = """<article>
<section class="page-hero"><div class="wrap"><div style="max-width:780px">
 <nav class="crumbs" aria-label="Breadcrumb"><a href="{root}index.html">Home</a> / <a href="{root}learn/">Learn</a> / {cat}</nav>
 <h1>{title}</h1><p class="lead">{summary}</p></div></div></section>
<section style="padding-top:30px"><div class="wrap article">
 <div class="prose">
  <div class="reviewed"><span>By <b>Hakeem.com Editorial Team</b></span><span>Reviewed <b>{reviewed}</b></span><span>{minutes} min read</span></div>
  {body}
  <hr>
  <p class="small muted" style="font-family:var(--sans)">Educational information only. It does not replace advice from your doctor, pharmacist or a qualified practitioner. <a href="{root}editorial-policy.html">Editorial policy</a>. Spotted an error? <a href="{root}contact.html?topic=Correction">Tell us</a>.</p>
 </div>
 <aside><div class="aside-sticky">
  {toc}
  <div class="aside-box"><h3>Talk it through</h3><p class="small muted">Get matched with a qualified practitioner.</p><a class="btn btn-primary btn-small" href="{root}consult.html">Request a consultation</a></div>
  <div class="aside-box"><h3>More guides</h3><ul class="plain-list" style="font-size:.97rem">{others}</ul></div>
 </div></aside>
</div></section>
</article>"""


# ---------------------------------------------------------------- output
def write(base, path, content):
    out = os.path.join(base, path)
    os.makedirs(os.path.dirname(out), exist_ok=True)
    with open(out, "w", encoding="utf-8") as fh:
        fh.write(content)


TILES = {}  # herb card HTML as used on herb pages (root "../"), shared through _data/tiles.yml

# Liquid stand-ins used when turning the Python templates into Jekyll layouts.
SPECIAL = {
    "@content": "{{ content }}",
    "@year": '{{ site.time | date: "%Y" }}',
    "@ads": "{% unless page.v_noads %}" + ADS_TAG + "{% endunless %}",
    "@base": "{% if page.v_base %}" + BASE_SCRIPT + "{% endif %}",
    "@png": ('{% assign hk_png = site.static_files | where: "path", "/assets/img/og.png" | first %}{% if hk_png %}'
             + png_tags("{{ page.v_root }}") + "{% endif %}"),
    "@related": "{% for s in page.v_rel %}{{ site.data.tiles[s] }}{% endfor %}",
}


def S(key):
    return "\x00%s\x00" % key


def liquidize(text):
    literal = re.sub(r"\x00[^\x00]+\x00", "", text)
    if "{{" in literal or "{%" in literal:
        raise SystemExit("Template text contains Liquid-like braces; escape them before building.")
    return re.sub(r"\x00([^\x00]+)\x00", lambda m: SPECIAL.get(m.group(1)) or "{{ page.%s }}" % m.group(1), text)


def yq(v):
    """YAML single-quoted scalar: no backslash escapes, quotes doubled."""
    if any(ch in v for ch in "\n\r") or any(ord(ch) in (0x85, 0x2028, 0x2029, 0xFEFF) for ch in v):
        raise SystemExit("Line break inside a front matter value: %r" % v[:60])
    return "'" + v.replace("'", "''") + "'"


def front_matter(d):
    lines = ["---"]
    for k, v in d.items():
        if isinstance(v, bool):
            lines.append("%s: %s" % (k, "true" if v else "false"))
        elif isinstance(v, list):
            lines.append("%s: [%s]" % (k, ", ".join(yq(x) for x in v)))
        elif k == "layout":
            lines.append("layout: %s" % v)
        else:
            lines.append("%s: %s" % (k, yq(v)))
    lines.append("---")
    return "\n".join(lines) + "\n"


def raw(text):
    if "{% endraw" in text:
        raise SystemExit("Page body contains an endraw tag.")
    return "{% raw %}" + text + "{% endraw %}"


def jekyll_layouts():
    default = TEMPLATE.format(
        root=S("v_root"), title=S("v_t"), desc=S("v_d"), canonical=S("v_c"), ogtype=S("v_ogt"), fonts=FONTS, ver=VERSION,
        ads=S("@ads"), ld=S("v_ld"), cls=S("v_cls"), nav=nav_html(S("v_root")), body=S("@content"), year=S("@year"),
        newsletter=newsletter_form("f"), client=ADSENSE_CLIENT, png=S("@png"), base=S("@base"))
    sub = "---\nlayout: default\n---\n"
    herb_keys = ["name", "name_l", "name_q", "latin", "names", "family", "parts", "forms", "trads", "best", "hubs", "mini",
                 "summary", "verdict", "uses", "research", "safety", "avoid", "ix", "slug", "trad", "confuse", "buying", "refs"]
    herb = HERB_TPL.format(root="../", reviewed=REVIEWED, ad1=ad_slot("herb-mid"), ad2=ad_slot("herb-end"),
                           related=S("@related"), **{k: S("v_" + k) for k in herb_keys})
    hub = HUB_TPL.format(root="../", ad=ad_slot("hub-mid"),
                         **{k: S("v_" + k) for k in ["title", "title_l", "intro", "rows", "red", "advice", "slug"]})
    guide = GUIDE_TPL.format(root="../", reviewed=REVIEWED, body=S("@content"),
                             **{k: S("v_" + k) for k in ["cat", "title", "summary", "minutes", "others", "toc"]})
    return {"default": liquidize(default), "herb": sub + liquidize(herb), "hub": sub + liquidize(hub), "guide": sub + liquidize(guide)}


def page_source(pg):
    fm = {"layout": pg["kind"]}
    fm.update(pg["base"])
    if pg["noads"]:
        fm["v_noads"] = True
    if pg["is404"]:
        fm["v_base"] = True
    for k, v in pg["fields"].items():
        fm["v_" + k] = v
    body = raw(pg["content"]) if pg["kind"] in ("default", "guide") else ""
    return front_matter(fm) + body


CONFIG = """# GitHub Pages builds this site from the main branch with its built-in Jekyll.
# The page files, layouts and data here are generated by _build/build.py:
# edit _build/herbs.py, _build/extras.py or _build/pages/, run the script and commit the result.
title: Hakeem.com
url: https://hakeem.com
exclude:
  - README.md
  - RESEARCH.md
  - BUILD-PROMPTS.md
"""


def build(html_dir=None):
    pages = load_pages()
    guides = []
    for meta, body in pages:
        if meta.get("kind") == "guide":
            meta["minutes"] = max(3, round(words(body) / 220))
            meta.setdefault("short", meta["title"])
            guides.append(meta)
    guides.sort(key=lambda m: int(m.get("order", 99)))
    for h in HERBS:
        TILES[h["slug"]] = label_tile(h, "../")

    for meta, body in pages:
        path = meta["path"]
        root = rel_root(path)
        b = render_blocks(body, root, guides)
        ld, kind, fields = [], "default", None
        if meta.get("kind") == "guide":
            kind, fields = "guide", guide_fields(meta, b, root, guides)
            ld = [{"@context": "https://schema.org", "@type": "Article", "headline": meta["title"], "description": meta["summary"],
                   "dateModified": REVIEWED_ISO, "datePublished": REVIEWED_ISO, "author": {"@type": "Organization", "name": "Hakeem.com Editorial Team"},
                   "publisher": {"@type": "Organization", "name": SITE_NAME, "url": SITE_URL}, "mainEntityOfPage": canonical(path)},
                  breadcrumb_ld([("Home", ""), ("Learn", "learn/"), (meta["title"], path)])]
            ogtype = "article"
        else:
            ogtype = "website"
        if path == "index.html":
            ld = [{"@context": "https://schema.org", "@type": "WebSite", "name": SITE_NAME, "url": SITE_URL + "/",
                   "potentialAction": {"@type": "SearchAction", "target": SITE_URL + "/herbs/?q={search_term_string}",
                                       "query-input": "required name=search_term_string"}},
                  {"@context": "https://schema.org", "@type": "Organization", "name": SITE_NAME, "url": SITE_URL,
                   "logo": SITE_URL + "/assets/img/favicon.svg"}]
        layout(path, meta["title"], meta.get("description", meta.get("summary", "")), b, ld=ld, ogtype=ogtype,
               cls=meta.get("class", ""), kind=kind, fields=fields)

    for h in HERBS:
        herb_page(h)
    for hb in HUBS:
        hub_page(hb)

    base = html_dir or ROOT
    files = {}
    # interaction data for the checker
    ixd = {"herbs": {h["slug"]: {"n": h["name"], "ix": [[k, l, n] for k, l, n in h["ix"]]} for h in HERBS},
           "classes": {c[0]: [c[1], c[2]] for c in CLASSES}}
    files["assets/js/ix-data.js"] = "window.HK_IX=%s;\n" % json.dumps(ixd, ensure_ascii=False)

    # search index
    idx = []
    for h in HERBS:
        idx.append({"t": h["name"], "s": h["latin"] + " " + " ".join(n[2] for n in h["names"]), "u": "herbs/%s.html" % h["slug"], "k": "Herb"})
    for hb in HUBS:
        idx.append({"t": hb["title"], "s": hb["blurb"], "u": "concerns/%s.html" % hb["slug"], "k": "Concern"})
    for g in guides:
        idx.append({"t": g["title"], "s": g["summary"], "u": g["path"], "k": "Guide"})
    for p, t, d in OUT:
        if not p.startswith(("herbs/", "concerns/", "learn/")) and p not in ("404.html",):
            idx.append({"t": t, "s": d, "u": p.replace("index.html", ""), "k": "Page"})
    files["assets/search.json"] = json.dumps(idx, ensure_ascii=False)

    # sitemap, robots, ads.txt, manifest
    urls = sorted({p for p, _, _ in OUT if p != "404.html"})
    sm = ['<?xml version="1.0" encoding="UTF-8"?>', '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for p in urls:
        pri = "1.0" if p == "index.html" else ("0.8" if p.startswith(("herbs/", "concerns/", "learn/")) else "0.6")
        sm.append("<url><loc>%s</loc><lastmod>%s</lastmod><priority>%s</priority></url>" % (xesc(canonical(p)), REVIEWED_ISO, pri))
    sm.append("</urlset>")
    files["sitemap.xml"] = "\n".join(sm) + "\n"
    files["robots.txt"] = "User-agent: *\nAllow: /\n\nSitemap: %s/sitemap.xml\n" % SITE_URL
    files["ads.txt"] = "google.com, pub-6620975821265271, DIRECT, f08c47fec0942fa0\n"
    files["site.webmanifest"] = json.dumps({
        "name": "Hakeem.com", "short_name": "Hakeem", "start_url": "./", "display": "standalone",
        "background_color": "#EEF1EA", "theme_color": "#1F2A44",
        "icons": [{"src": "assets/img/favicon.svg", "sizes": "any", "type": "image/svg+xml"}]}, indent=1)
    for p, c in files.items():
        write(base, p, c)

    if html_dir:
        has_png = os.path.exists(os.path.join(ROOT, "assets", "img", "og.png"))
        for pg in PAGES:
            write(html_dir, pg["path"], render_html(pg, has_png))
        for sub in ("assets/css", "assets/js", "assets/img"):
            src = os.path.join(ROOT, sub)
            for f in os.listdir(src):
                if f not in ("ix-data.js",) and os.path.isfile(os.path.join(src, f)):
                    with open(os.path.join(src, f), "rb") as a:
                        os.makedirs(os.path.join(html_dir, sub), exist_ok=True)
                        with open(os.path.join(html_dir, sub, f), "wb") as b:
                            b.write(a.read())
        if os.path.exists(os.path.join(ROOT, "CNAME")):
            write(html_dir, "CNAME", open(os.path.join(ROOT, "CNAME")).read())
        where = html_dir
    else:
        for name, src in jekyll_layouts().items():
            write(ROOT, "_layouts/%s.html" % name, src)
        write(ROOT, "_data/tiles.yml", "".join("%s: %s\n" % (k, yq(v)) for k, v in TILES.items()))
        write(ROOT, "_config.yml", CONFIG)
        for pg in PAGES:
            write(ROOT, pg["path"], page_source(pg))
        stale = os.path.join(ROOT, ".nojekyll")
        if os.path.exists(stale):  # .nojekyll would switch off the Jekyll build on GitHub Pages
            os.remove(stale)
        where = "the Jekyll source tree"
    print("Built %d pages (%d herbs, %d concern hubs, %d guides) into %s." % (len(OUT), len(HERBS), len(HUBS), len(guides), where))


if __name__ == "__main__":
    if len(sys.argv) == 3 and sys.argv[1] == "--html":
        build(os.path.abspath(sys.argv[2]))
    else:
        build()
