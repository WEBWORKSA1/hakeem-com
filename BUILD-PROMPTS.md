# Hakeem.com — Phase-wise build prompts

Copy each phase into an AI coding assistant in order. Each phase assumes the previous one is done. The site in this repository is the finished output of these prompts.

---

## Phase 0 — Concept and positioning

> Build **Hakeem.com: "Old remedies, honest evidence."** An evidence-graded reference for herbal and traditional medicine, Unani (Tibb) first, plus Ayurveda, Chinese medicine and Western herbalism.
>
> Why this concept: "hakeem" is the word for a traditional Unani physician across India, Pakistan and the Gulf, so the domain already carries search intent ("hakeem near me", "hakeem medicine", herb names in Urdu/Hindi). Health is a top-tier AdSense niche (roughly $10–25 RPM on Tier-1 traffic). The herbal medicine market was about US$71.5B in 2024 and is growing near 20% a year. India alone has about 7.5 lakh registered AYUSH practitioners who can pay for listings and leads.
>
> The evidence-grading angle is what makes it AdSense-safe: Google restricts unreliable health claims, so every herb shows graded uses, safety and cited sources, and never claims cures.
>
> Revenue engines: AdSense (Auto ads) · consultation leads · paid practitioner listings (Free / $19 Verified / $49 Featured) · sponsorships (Adopt-a-Herb, contest, concern partner, newsletter, video) · reader support · contests that grow the audience.
>
> Avoid trademark issues: use "hakeem" only as a generic descriptive word, claim no rights in it, and publish a disclosure that the site is not affiliated with any person, clinic, manufacturer or brand using the word.

## Phase 1 — Competitive research

> Visit at least 35 leading sites and extract features, forms, content structure, design and monetisation:
> - Evidence references: Examine, NCCIH Herbs at a Glance, MSK About Herbs, Drugs.com Natural Products, MedlinePlus Herbs, NIH ODS, HerbalGram/ABC, NatMed Pro, RxList, WebMD Vitamins, Mayo Clinic, EMA herbal medicines, WHO Traditional Medicine.
> - Traditional medicine: CCRUM, ayush.gov.in, NIUM, Hamdard, Banyan Botanicals, Ayurvedic Institute, Herbal Academy, LearningHerbs, Mountain Rose Herbs, PFAF, botanical.com, American Herbalists Guild, Kew POWO.
> - Lead gen, publishers, donations, contests: Practo, Zocdoc, Healthgrades, Psychology Today, Dr. Axe, Healthline, Medical News Today, Verywell Health, mindbodygreen, Cleveland Clinic, Wikimedia donate, Khan Academy donate, Buy Me a Coffee, Instructables contests.
>
> Output RESEARCH.md: one line per site on what to adopt, then a prioritised feature list. Paraphrase only.

## Phase 2 — Information architecture

> Create this sitemap (static, multi-page, relative links so it runs both at `username.github.io/repo/` and at the custom domain):
> - Home · Herb library (`/herbs/`) + one page per herb · Health concerns (`/concerns/`) + 8 hubs · Interaction checker · Mizaj quiz · Learn (`/learn/`) + 10 guides · Unani glossary · Videos
> - Find a practitioner (lead form) · List your practice · Support · Contests · Careers · Advertise and sponsor
> - About · Editorial policy · How we grade evidence · Contact · Medical disclaimer · Privacy · Cookies · Terms · Trademark and copyright · 404
> - `sitemap.xml`, `robots.txt`, `ads.txt`, `site.webmanifest`
>
> Every page: a top bar reading "Contact, if you are interested in this website / domain name / sponsorship / advertisement / partnership" linked to https://web.works/contact; header with search, theme toggle, mobile menu and a "Find a practitioner" button; footer with newsletter, link columns, disclaimer and trademark line.

## Phase 3 — Design system

> Palette: sage paper `#EEF1EA`, indigo ink `#1F2A44`, saffron `#D99A1E` (primary actions), celadon `#2F6F5E` (links, strong evidence), henna `#9A3324` (cautions). Quadrant colours for temperaments: damwi `#A63D40`, safrawi `#D99A1E`, balghami `#3F7F8F`, saudawi `#3B3355`. Full dark theme via `prefers-color-scheme` and a manual toggle.
>
> Type: Alegreya (headings and long-form reading), Alegreya Sans (UI and body), Amiri for Arabic/Urdu script. Logo: the word حكيم in saffron + "Hakeem.com".
>
> Signature element: a **temperament map** — a four-quadrant SVG (cold↔hot, moist↔dry) with every herb plotted as a dot; hover/tap shows the herb, its temperament and best evidence grade. One orchestrated load animation (dots pop in), nothing else animates on its own. Herb cards are styled as apothecary jar labels (notched corners, inner rule).
>
> Quality floor: responsive to 360px, visible focus, reduced-motion respected, no horizontal scroll, sentence-case copy, no all-caps labels.

## Phase 4 — Content and data model

> Store herbs as data (Python dicts) and generate pages. Each herb: slug, name, Latin name, family, names in Urdu/Arabic/Hindi with transliteration, parts used, forms, traditions, Unani temperament (+ map coordinates), headline use, 3-line summary, "Our take" verdict, uses graded on a five-level scale (Strong / Moderate / Limited / Insufficient / Not supported) with a note each, traditional use per system (labelled as tradition), research paragraph, side effects, who should avoid, interactions keyed to medicine classes with level (avoid / caution / monitor), "do not confuse with", buying tips, verified references (NCCIH, MSK, LiverTox, EMA, MedlinePlus, PubMed/Cochrane).
>
> Launch set (26): black seed, turmeric, ginger, ashwagandha, fenugreek, garlic, cinnamon, licorice, senna, saffron, fennel, holy basil, amla, neem, moringa, chamomile, peppermint, aloe vera, psyllium, green tea, clove, St. John's wort, ginkgo, echinacea, sweet almond, coriander.
>
> Herb page order: names + facts + mini temperament map → byline and review date → summary → our take → evidence table → research → safety box → who should avoid → interactions → traditional use → do not confuse with → buying → sources → disclaimer line. Sidebar: on-this-page, consultation CTA (prefilled herb), Adopt-a-Herb.
>
> Guides (700–1,000 words, original): What is Unani medicine · The four temperaments · Herb–drug interactions · Buying safe herbal products · How to read herbal evidence · Herbs in pregnancy and breastfeeding · Unani vs Ayurveda vs TCM · Kitchen spices evidence check · Hijama (cupping) · Talking to your doctor about herbs.
>
> Concern hubs (8): digestion, heart, blood sugar, mood and sleep, pain, skin and mouth, women's health, colds. Each ranks herbs by evidence and lists red-flag symptoms.
>
> YMYL rules: no cure claims; tradition and evidence always separated; safety visible before benefits; every claim traceable to a cited source; fact-check before publishing.

## Phase 5 — Interactive tools

> 1. **Herb library**: search across English/Latin/Urdu/Hindi names, filters for tradition, temperament, concern and "moderate or strong evidence only", A–Z bar, `?q=` and `?concern=` deep links, empty state with "suggest a herb".
> 2. **Interaction checker**: herbs × 18 medicine classes/situations, results sorted avoid → caution → monitor, note herbs with no documented match ("not proof of safety"), print button, `?h=` prefill from herb pages.
> 3. **Mizaj quiz**: 12 questions scored on two axes, result plotted on the map with a "You" marker; five outcomes (four temperaments + balanced); six-essentials lifestyle tips; traditional balancing herbs linked to their evidence pages; red-flag box; optional email with three separate unticked consents.
> 4. **Site search**: dialog opened by icon or "/" key, fed by a generated `search.json`.

## Phase 6 — Lead generation

> - **Consultation request** (3 steps with progress bar): need (concern, herb, tradition chips, format, city) → context (timing, prescription medicines yes/no, budget band, 300-char note) → contact (first name, email, phone/WhatsApp, preference, required share consent, optional newsletter). Trust row, "what happens next", emergency notice. Prefill from `?concern=` and `?herb=`.
> - **Quick form** on the home page (name, email, concern, tradition, city, consent).
> - **Practitioner listing application** (4 steps): practice → credentials (qualification, institution, regulator, registration no., years, insurance) → profile → contact + plan + code-of-conduct and verification consents. Plan cards above the form.
> - **Advertise/partner enquiry**, **contest entry**, **job application**, **contact**, **newsletter** forms.

## Phase 7 — Monetisation

> - **AdSense**: in every page `<head>` except 404 and the three conversion pages (consult, practitioners, support):
>   `<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-6620975821265271" crossorigin="anonymous"></script>` plus `<meta name="google-adsense-account" content="ca-pub-6620975821265271">`. `ads.txt`: `google.com, pub-6620975821265271, DIRECT, f08c47fec0942fa0`. Use Auto ads now; optional labelled manual slots (home ×2, herb mid/end, hub, guide) render only once slot IDs are configured. Never place ads inside safety boxes or beside form buttons.
> - **Support**: one-time/monthly toggle, presets with impact lines ($10/25/50/100; $5/10/20/50 monthly), fund selector (running costs, reviews, outreach, hiring, prize pool), supporter wall opt-in, pledge → secure payment link by email, honest "not tax-deductible" note, allocation bars, supporter tiers.
> - **Sponsorship**: Adopt-a-Herb, contest sponsor, concern partner, newsletter, video series, featured directory listings; guardrails (no editorial influence; no sponsoring a herb you sell).
> - **Contests**: photo, story and monthly quiz; tiered cash prizes; live countdown to quarter end; judging criteria; official rules (no purchase necessary, eligibility, rights, privacy).
> - **Careers**: medical reviewers, Unani/Ayurveda writers, research editor, translators, video producer, community manager, partnerships lead, volunteers.

## Phase 8 — Trust, compliance and private contact routing

> - Pages: About, Editorial policy (sources, process, corrections, advertising, AI use), Evidence method, Medical disclaimer, Privacy (AdSense cookie disclosure, opt-out links, consent for EEA/UK/CH, rights under GDPR/PIPEDA/Law 25), Cookies, Terms, Trademark and copyright disclosure.
> - **Only one inbox receives every form**, and the address must never appear in HTML, JS strings, JSON or the repo. Store it XOR-encoded and reversed in JS, assemble it only at send time, and post forms as JSON to the FormSubmit AJAX endpoint. A "write us an email" link builds the `mailto:` on click. Verify with a grep across the repo before every deploy.

## Phase 9 — SEO and performance

> Titles and descriptions per page, canonical URLs on the custom domain, Open Graph and Twitter cards with a 1200×630 image, JSON-LD (WebSite + SearchAction, Organization, MedicalWebPage with lastReviewed and DietarySupplement, Article, BreadcrumbList), generated sitemap and robots, YouTube facades (thumbnail until click, privacy-enhanced embeds), no frameworks, one CSS and one JS file, lazy assets.

## Phase 10 — QA and deployment

> - Build with `python3 _build/build.py`. Run a link checker, an address-leak grep, and headless browser tests: library filters, checker results, quiz completion and marker, multi-step validation and submission, donation toggle, countdown, search, theme, AdSense presence/absence, top banner on every page.
> - Screenshot desktop and 390px mobile, light and dark.
> - Push to `WEBWORKSA1/hakeem-com` (public, free plan). Generate a Jekyll source tree (layouts, page files with front matter, data) so GitHub Pages builds the site natively from `main` / root with no workflow; add `CNAME` for the custom domain.
> - Custom domain: add `CNAME` with `hakeem.com`, set DNS, enforce HTTPS, then apply to AdSense with hakeem.com.

## Phase 11 — Growth roadmap (expandable)

> 1. Add 10 herbs a month (hibiscus, rose, cumin, ajwain, triphala, giloy, shilajit, valerian, kalonji oil blends, honey) with the same template.
> 2. Recruit and display named medical reviewers on each page.
> 3. Urdu and Hindi translations (`/ur/`, `/hi/`) with `hreflang`.
> 4. Open the live directory city by city once 10+ verified practitioners are listed.
> 5. Weekly Herb of the Week newsletter and lead magnets (printable interaction chart, six-essentials chart).
> 6. Monthly herb quiz and seasonal contests; publish winners' galleries.
> 7. Replace pledges with instant checkout (Stripe or PayPal payment links) when accounts are ready.
> 8. Create manual AdSense units and add their slot IDs in `_build/build.py`.
