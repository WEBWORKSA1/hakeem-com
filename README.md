# Hakeem.com

**Old remedies, honest evidence.** An evidence-graded guide to herbal and traditional medicine (Unani first, plus Ayurveda, Chinese medicine and Western herbalism), monetised with Google AdSense, consultation leads, practitioner listings, sponsorship, reader support and contests.

- Live: https://hakeem.com (GitHub Pages, built from the `main` branch)
- Domain, sponsorship, advertising or partnership enquiries: https://web.works/contact

## What is in the site

| Area | Pages |
|---|---|
| Reference | Home with the temperament map, herb library (26 herb profiles), 8 health-concern hubs, Unani glossary |
| Tools | Herb–drug interaction checker, Mizaj (temperament) quiz, site search |
| Learn | 10 guides, video library (15 vetted videos) |
| Revenue | Find a practitioner (3-step lead form), List your practice (Free / Verified / Featured), Support (one-time and monthly), Contests, Careers, Advertise and sponsor |
| Trust | About, Editorial policy, Evidence method, Medical disclaimer, Privacy, Cookies, Terms, Trademark and copyright, Contact |
| Technical | `sitemap.xml`, `robots.txt`, `ads.txt`, `site.webmanifest`, JSON-LD, Open Graph |

`RESEARCH.md` records the 40 benchmark sites. `BUILD-PROMPTS.md` holds the phase-wise build prompts.

## How it is built

Plain static HTML, one stylesheet (`assets/css/main.css`) and one script (`assets/js/main.js`). The sources live in `_build/`, and a small Python script with no dependencies turns them into a Jekyll source tree that GitHub Pages builds by itself on every push to `main`. No workflow or build server is involved.

```
python3 _build/build.py              # regenerate layouts, page files, data and sitemap in the repo root
python3 _build/build.py --html DIR   # or write the finished HTML into DIR to preview it locally
```

- `_build/herbs.py` — herb data: names, temperament, graded uses, safety, interactions.
- `_build/extras.py` — concern hubs, glossary, videos, verified references.
- `_build/pages/` — page bodies (home, tools, forms, guides, legal pages).
- `_build/build.py` — templates, herb and hub pages, search index, sitemap.

Generated (do not edit by hand): `_layouts/`, `_data/tiles.yml`, `_config.yml`, every `.html` page in the root and in `herbs/`, `concerns/` and `learn/`, plus `sitemap.xml`, `robots.txt`, `ads.txt`, `site.webmanifest`, `assets/search.json` and `assets/js/ix-data.js`. Edit the sources, run the script, commit everything. All internal links are relative, so the output works on any host or path.

## Forms and the private inbox

Every form (consultations, listings, support pledges, contests, jobs, advertising, contact, newsletter, quiz results) is delivered to one private inbox through FormSubmit. The address is never written in the HTML, scripts or this repository; `main.js` assembles it only at the moment a form is sent.

**One-time step:** the first submission from a new domain triggers a FormSubmit activation email to that inbox. Open it and click **Activate** once for hakeem.com.

## Google AdSense

- Publisher ID `ca-pub-6620975821265271`. The loader script and `google-adsense-account` meta tag are on every content page.
- The loader is deliberately left off `404.html`, `consult.html`, `practitioners.html` and `support.html` so ads never sit next to conversion forms.
- `ads.txt` is at the site root. AdSense reads it only from the root of the approved domain, so apply with **hakeem.com** after the domain is connected.
- Auto ads place units automatically. To add manual units, create them in AdSense and put their slot IDs in `AD_SLOTS` in `_build/build.py` (`home-1`, `home-2`, `herb-mid`, `herb-end`, `hub-mid`, `guide-mid`), then rebuild.
- In AdSense, turn on **Privacy & messaging → European regulations** so EEA, UK and Swiss visitors get a Google-certified consent message.

## Publishing on GitHub Pages (free plan)

The repository is public, which the free plan requires. **Settings → Pages → Build and deployment → Deploy from a branch → `main` / (root)**. GitHub rebuilds the site within a minute or two of every push to `main`.

## Custom domain (hakeem.com)

- `CNAME` in the repository root contains `hakeem.com`.
- DNS: `A` records for `@` → `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153`; `CNAME` for `www` → `webworksa1.github.io`.
- In **Settings → Pages**, tick **Enforce HTTPS** once GitHub has issued the certificate.
- After the domain is live: re-activate FormSubmit for it (see above) and submit `https://hakeem.com/sitemap.xml` in Google Search Console.

## Share image and icons (optional)

`og.png`, `icon-192.png` and `icon-512.png` are rendered by `_build/make_images.py` (needs Playwright). Upload them to `assets/img/` and the share-image and touch-icon tags switch on automatically on the next build.

## Trademark note

"Hakeem" is used only as a generic, descriptive word. The site claims no rights in it and states that it is not affiliated with any person, clinic, manufacturer or brand that uses the word. See `trademark.html`.
