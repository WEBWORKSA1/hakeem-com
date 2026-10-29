/* Hakeem.com — site script (no dependencies) */
(function () {
  'use strict';
  var $ = function (s, c) { return (c || document).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || document).querySelectorAll(s)); };
  var ROOT = document.documentElement.getAttribute('data-root') || '';
  function store(k, v) { try { if (v === undefined) return localStorage.getItem(k); localStorage.setItem(k, v); } catch (e) { return null; } }
  function esc(s) { return String(s).replace(/[&<>"']/g, function (c) { return { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]; }); }
  var params = new URLSearchParams(location.search);

  /* ---------- Private inbox routing: the address is assembled only at send time ---------- */
  var _k = [122, 120, 116, 57, 123, 126, 118, 122, 112, 87, 38, 118, 100, 124, 101, 120, 96, 117, 114, 96];
  function inbox() { return String.fromCharCode.apply(null, _k.map(function (c) { return c ^ 23; })).split('').reverse().join(''); }
  function endpoint() { return 'https://formsubmit.co/ajax/' + inbox(); }
  $$('[data-mail]').forEach(function (a) {
    a.addEventListener('click', function (e) {
      e.preventDefault();
      location.href = 'mailto:' + inbox() + '?subject=' + encodeURIComponent(a.getAttribute('data-mail') || 'Enquiry from Hakeem.com');
    });
  });

  /* ---------- Theme ---------- */
  var tb = $('#themeBtn');
  if (tb) tb.addEventListener('click', function () {
    var root = document.documentElement;
    var cur = root.getAttribute('data-theme');
    if (!cur) cur = matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
    var next = cur === 'dark' ? 'light' : 'dark';
    root.setAttribute('data-theme', next); store('hk-theme', next);
  });

  /* ---------- Navigation ---------- */
  var here = location.pathname.replace(/index\.html$/, '');
  $$('#menu a').forEach(function (a) {
    var u = new URL(a.getAttribute('href'), location.href).pathname.replace(/index\.html$/, '');
    if (u.length > 1 && (here === u || (u.slice(-1) === '/' && here.indexOf(u) === 0))) a.setAttribute('aria-current', 'page');
  });
  var bg = $('#burger'), menu = $('#menu');
  if (bg && menu) bg.addEventListener('click', function () { var o = menu.classList.toggle('open'); bg.setAttribute('aria-expanded', o); });

  /* ---------- Year + cookie notice ---------- */
  $$('.year').forEach(function (el) { el.textContent = new Date().getFullYear(); });
  var ck = $('#cookie');
  if (ck && !store('hk-cookie')) ck.classList.add('show');
  $$('[data-cookie]').forEach(function (b) { b.addEventListener('click', function () { store('hk-cookie', b.getAttribute('data-cookie')); ck.classList.remove('show'); }); });

  /* ---------- Search ---------- */
  var dlg = $('#searchDlg'), si = $('#searchInput'), sr = $('#searchRes'), index = null, sel = -1;
  function openSearch() {
    dlg.classList.add('open'); si.value = ''; sr.innerHTML = ''; setTimeout(function () { si.focus(); }, 30);
    if (!index) fetch(ROOT + 'assets/search.json').then(function (r) { return r.json(); }).then(function (d) { index = d; }).catch(function () { index = []; });
  }
  function closeSearch() { dlg.classList.remove('open'); }
  if (dlg) {
    $('#searchBtn').addEventListener('click', openSearch);
    dlg.addEventListener('click', function (e) { if (e.target === dlg) closeSearch(); });
    document.addEventListener('keydown', function (e) {
      if (e.key === 'Escape') closeSearch();
      if (e.key === '/' && !/input|textarea|select/i.test(document.activeElement.tagName)) { e.preventDefault(); openSearch(); }
    });
    si.addEventListener('input', function () {
      var q = si.value.trim().toLowerCase(); sel = -1;
      if (!q || !index) { sr.innerHTML = ''; return; }
      var hits = index.filter(function (it) { return (it.t + ' ' + it.s).toLowerCase().indexOf(q) > -1; }).slice(0, 12);
      sr.innerHTML = hits.length ? hits.map(function (it) {
        return '<li><a href="' + ROOT + esc(it.u) + '">' + esc(it.t) + '<small>' + esc(it.k) + '</small></a></li>';
      }).join('') : '<li class="muted" style="padding:10px 12px">No match. Try a Latin, Urdu or Hindi name, or browse the <a href="' + ROOT + 'herbs/">herb library</a>.</li>';
    });
    si.addEventListener('keydown', function (e) {
      var links = $$('a', sr); if (!links.length) return;
      if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
        e.preventDefault(); sel = (sel + (e.key === 'ArrowDown' ? 1 : -1) + links.length) % links.length;
        links.forEach(function (l, i) { l.classList.toggle('sel', i === sel); });
      } else if (e.key === 'Enter') { e.preventDefault(); location.href = links[Math.max(0, sel)].href; }
    });
  }

  /* ---------- Hero search (herb library) ---------- */
  var hs = $('#heroSearch');
  if (hs) hs.addEventListener('submit', function (e) {
    e.preventDefault(); var q = $('input', hs).value.trim();
    location.href = ROOT + 'herbs/' + (q ? '?q=' + encodeURIComponent(q) : '');
  });

  /* ---------- Prefill forms from links ---------- */
  ['herb', 'concern', 'topic', 'role', 'contest', 'plan', 'fund'].forEach(function (k) {
    var v = params.get(k); if (!v) return;
    $$('[data-prefill="' + k + '"]').forEach(function (el) {
      if (el.tagName === 'SELECT') { $$('option', el).forEach(function (o) { if (o.value === v || o.textContent === v) el.value = o.value; }); }
      else if (el.type === 'radio') { if (el.value === v) el.checked = true; }
      else if (!el.value) el.value = v;
    });
  });

  /* ---------- Forms (sent through a private relay) ---------- */
  $$('form.js-form').forEach(function (f) {
    f.addEventListener('submit', function (e) {
      e.preventDefault();
      var msg = $('.form-msg', f);
      var hp = f.querySelector('[name=_honey]');
      if (hp && hp.value) return;
      if (!f.checkValidity()) { f.reportValidity(); return; }
      var btn = $('button[type=submit]', f), old = btn ? btn.textContent : '';
      if (btn) { btn.disabled = true; btn.textContent = 'Sending…'; }
      var data = {};
      new FormData(f).forEach(function (v, k) { if (k !== '_honey') data[k] = data[k] ? data[k] + ', ' + v : v; });
      data._subject = (f.getAttribute('data-subject') || 'Hakeem.com form') + ' — ' + (data.name || data.first_name || data.email || '');
      data._template = 'table'; data._captcha = 'false'; data.page = location.href;
      fetch(endpoint(), { method: 'POST', headers: { 'Content-Type': 'application/json', 'Accept': 'application/json' }, body: JSON.stringify(data) })
        .then(function (r) { if (!r.ok) throw new Error('send'); return r.json().catch(function () { return {}; }); })
        .then(function () {
          if (msg) { msg.className = 'form-msg ok'; msg.textContent = f.getAttribute('data-ok') || 'Sent. We reply within two working days.'; }
          f.reset(); resetSteps(f);
          var after = f.getAttribute('data-after'); if (after && window[after]) window[after](data);
        })
        .catch(function () {
          if (msg) { msg.className = 'form-msg err'; msg.textContent = 'Your message did not send. Check your connection and press the button again.'; }
        })
        .then(function () { if (btn) { btn.disabled = false; btn.textContent = old; } });
    });
  });

  /* ---------- Multi-step forms ---------- */
  function resetSteps(f) {
    var st = $$('.step', f); if (!st.length) return;
    st.forEach(function (s, i) { s.classList.toggle('active', i === 0); });
    $$('.steps-ind span', f).forEach(function (s, i) { s.classList.toggle('on', i === 0); });
  }
  $$('form.multistep').forEach(function (f) {
    var steps = $$('.step', f), ind = $$('.steps-ind span', f), i = 0;
    function go(n) {
      if (n > i) {
        var bad = $$('input,select,textarea', steps[i]).filter(function (x) { return !x.checkValidity(); });
        if (bad.length) { bad[0].reportValidity(); return; }
      }
      i = Math.max(0, Math.min(steps.length - 1, n));
      steps.forEach(function (s, k) { s.classList.toggle('active', k === i); });
      ind.forEach(function (s, k) { s.classList.toggle('on', k <= i); });
      var first = $('input:not([type=hidden]),select,textarea', steps[i]); if (first) first.focus({ preventScroll: true });
      f.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
    }
    $$('[data-next]', f).forEach(function (b) { b.addEventListener('click', function () { go(i + 1); }); });
    $$('[data-prev]', f).forEach(function (b) { b.addEventListener('click', function () { go(i - 1); }); });
  });

  /* ---------- YouTube facades ---------- */
  $$('.video[data-yt]').forEach(function (v) {
    var id = v.getAttribute('data-yt');
    v.innerHTML = '<img loading="lazy" alt="" src="https://i.ytimg.com/vi/' + id + '/hqdefault.jpg"><div class="play"><span>▶</span></div>';
    function play() {
      v.innerHTML = '<iframe src="https://www.youtube-nocookie.com/embed/' + id + '?autoplay=1&rel=0" title="' + esc(v.getAttribute('aria-label') || 'Video') + '" allow="accelerometer;autoplay;clipboard-write;encrypted-media;gyroscope;picture-in-picture" allowfullscreen></iframe>';
    }
    v.addEventListener('click', play, { once: true });
    v.addEventListener('keydown', function (e) { if (e.key === 'Enter' || e.key === ' ') { e.preventDefault(); play(); } });
  });

  /* ---------- Temperament map ---------- */
  var tmap = $('#tmap');
  if (tmap) {
    var td = {}; try { td = JSON.parse($('#tmapData').textContent); } catch (e) { }
    var card = $('#tmapCard'), base = tmap.getAttribute('data-base');
    var dots = $$('.dot', tmap);
    function show(d) {
      var s = d.getAttribute('data-slug'), h = td[s]; if (!h) return;
      dots.forEach(function (x) { x.classList.toggle('on', x === d); });
      card.innerHTML = '<b>' + esc(h.n) + '</b> <i class="muted">' + esc(h.l) + '</i><br>' + esc(h.q) + ': ' + esc(h.t) +
        '. Best evidence: <b>' + esc(h.g) + '</b> (' + esc(h.u.toLowerCase()) + '). <a href="' + base + s + '.html">Read the profile</a>';
    }
    dots.forEach(function (d) {
      d.addEventListener('mouseenter', function () { show(d); });
      d.addEventListener('focus', function () { show(d); });
      d.addEventListener('click', function () { show(d); });
      d.addEventListener('keydown', function (e) { if (e.key === 'Enter') location.href = base + d.getAttribute('data-slug') + '.html'; });
    });
  }

  /* ---------- Herb library filters ---------- */
  var lib = $('#labels');
  if (lib) {
    var tiles = $$('.label', lib), q = $('#libSearch'), conc = $('#libConcern'), count = $('#libCount'), empty = $('#libEmpty');
    var state = { trad: 'all', temp: 'all', ev: false, letter: '' };
    function apply() {
      var text = (q.value || '').trim().toLowerCase(), c = conc.value, n = 0;
      tiles.forEach(function (t) {
        var ok = (!text || t.getAttribute('data-name').indexOf(text) > -1) &&
          (state.trad === 'all' || t.getAttribute('data-trad').split('|').indexOf(state.trad) > -1) &&
          (state.temp === 'all' || t.getAttribute('data-q') === state.temp) &&
          (!state.ev || +t.getAttribute('data-best') >= 3) &&
          (!c || t.getAttribute('data-tags').split(' ').indexOf(c) > -1) &&
          (!state.letter || t.querySelector('h3').textContent.charAt(0).toUpperCase() === state.letter);
        t.hidden = !ok; if (ok) n++;
      });
      count.textContent = n + (n === 1 ? ' herb' : ' herbs');
      empty.hidden = n > 0;
    }
    $$('[data-filter]').forEach(function (b) {
      b.addEventListener('click', function () {
        var k = b.getAttribute('data-filter'), v = b.getAttribute('data-value');
        if (k === 'ev') { state.ev = !state.ev; b.setAttribute('aria-pressed', state.ev); }
        else { state[k] = v; $$('[data-filter="' + k + '"]').forEach(function (x) { x.setAttribute('aria-pressed', x === b); }); }
        apply();
      });
    });
    $$('.az a').forEach(function (a) {
      a.addEventListener('click', function (e) {
        e.preventDefault(); var L = a.getAttribute('data-letter');
        state.letter = state.letter === L ? '' : L;
        $$('.az a').forEach(function (x) { x.style.background = x.getAttribute('data-letter') === state.letter ? 'var(--saffron-soft)' : ''; });
        apply();
      });
    });
    var reset = $('#libReset');
    if (reset) reset.addEventListener('click', function () {
      q.value = ''; conc.value = ''; state = { trad: 'all', temp: 'all', ev: false, letter: '' };
      $$('[data-filter]').forEach(function (x) { x.setAttribute('aria-pressed', x.getAttribute('data-value') === 'all'); });
      $$('.az a').forEach(function (x) { x.style.background = ''; });
      apply();
    });
    q.addEventListener('input', apply); conc.addEventListener('change', apply);
    if (params.get('q')) q.value = params.get('q');
    if (params.get('concern')) conc.value = params.get('concern');
    apply();
  }

  /* ---------- Interaction checker ---------- */
  var ixOut = $('#ixResults');
  if (ixOut && window.HK_IX) {
    var D = window.HK_IX, order = { avoid: 0, caution: 1, monitor: 2 }, names = { avoid: 'Avoid', caution: 'Use caution', monitor: 'Monitor' };
    if (params.get('h')) { var pre = $('input[name=ixh][value="' + params.get('h') + '"]'); if (pre) pre.checked = true; }
    function run() {
      var hs = $$('input[name=ixh]:checked').map(function (x) { return x.value; });
      var ms = $$('input[name=ixm]:checked').map(function (x) { return x.value; });
      if (!hs.length || !ms.length) {
        ixOut.innerHTML = '<div class="empty">Tick at least one herb and one medicine or situation to see results.</div>'; return;
      }
      var res = [];
      hs.forEach(function (h) {
        D.herbs[h].ix.forEach(function (it) { if (ms.indexOf(it[0]) > -1) res.push({ h: h, c: it[0], l: it[1], n: it[2] }); });
      });
      res.sort(function (a, b) { return order[a.l] - order[b.l]; });
      var none = [];
      hs.forEach(function (h) { if (!res.some(function (r) { return r.h === h; })) none.push(D.herbs[h].n); });
      var htmlOut = '<h3>' + res.length + (res.length === 1 ? ' interaction' : ' interactions') + ' found</h3>';
      htmlOut += res.map(function (r) {
        return '<div class="ix-item" data-level="' + r.l + '"><h4>' + esc(D.herbs[r.h].n) + ' + ' + esc(D.classes[r.c][0]) +
          '<span class="lvl lvl-' + r.l + '">' + names[r.l] + '</span></h4><p>' + esc(r.n) + '</p></div>';
      }).join('');
      if (none.length) htmlOut += '<p class="muted">No documented interaction in our data for: ' + esc(none.join(', ')) + '. That is not proof of safety; ask your pharmacist.</p>';
      htmlOut += '<p class="small muted">Generated ' + new Date().toLocaleDateString() + '. Take this list to your pharmacist or doctor. <button class="btn btn-line btn-small no-print" type="button" onclick="window.print()">Print</button></p>';
      ixOut.innerHTML = htmlOut;
    }
    $$('input[name=ixh],input[name=ixm]').forEach(function (x) { x.addEventListener('change', run); });
    var clr = $('#ixClear'); if (clr) clr.addEventListener('click', function () { $$('input[name=ixh],input[name=ixm]').forEach(function (x) { x.checked = false; }); run(); });
    run();
  }

  /* ---------- Mizaj quiz ---------- */
  var quiz = $('#quiz');
  if (quiz) {
    var Q = JSON.parse($('#quizData').textContent);
    var qs = $$('.quiz-q', quiz), bar = $('.quiz-progress i', quiz), idx = 0, H = 0, Dd = 0, maxH = 0, maxD = 0, hist = [];
    Q.questions.forEach(function (q) {
      maxH += Math.max.apply(null, q.o.map(function (o) { return Math.abs(o[1]); }));
      maxD += Math.max.apply(null, q.o.map(function (o) { return Math.abs(o[2]); }));
    });
    function showQ(n) {
      qs.forEach(function (x, i) { x.classList.toggle('active', i === n); });
      bar.style.width = (n / qs.length * 100) + '%';
      var back = $('#quizBack'); if (back) back.hidden = n === 0;
    }
    qs.forEach(function (qel, qi) {
      $$('button[data-o]', qel).forEach(function (b) {
        b.addEventListener('click', function () {
          var o = Q.questions[qi].o[+b.getAttribute('data-o')];
          hist[qi] = [o[1], o[2]];
          idx = qi + 1;
          if (idx < qs.length) showQ(idx); else finish();
        });
      });
    });
    var back = $('#quizBack');
    if (back) back.addEventListener('click', function () { if (idx > 0) { idx--; showQ(idx); } });
    function finish() {
      H = 0; Dd = 0; hist.forEach(function (p) { if (p) { H += p[0]; Dd += p[1]; } });
      var x = Math.max(-1, Math.min(1, H / (maxH * 0.55))), y = Math.max(-1, Math.min(1, Dd / (maxD * 0.55)));
      var key = (Math.abs(x) < 0.15 && Math.abs(y) < 0.15) ? 'mutadil' : (x >= 0 ? (y >= 0 ? 'safrawi' : 'damwi') : (y >= 0 ? 'saudawi' : 'balghami'));
      var R = Q.results[key];
      quiz.hidden = true;
      var out = $('#quizResult'); out.hidden = false;
      $('#rName').textContent = R.name; $('#rAr').textContent = R.ar; $('#rQual').textContent = R.qual;
      $('#rTraits').textContent = R.traits; $('#rTend').textContent = R.tend;
      $('#rTips').innerHTML = R.tips.map(function (t) { return '<li><b>' + esc(t[0]) + '.</b> ' + esc(t[1]) + '</li>'; }).join('');
      $('#rHerbs').innerHTML = R.herbs.map(function (s) { return '<a class="chip" href="' + ROOT + 'herbs/' + s[0] + '.html">' + esc(s[1]) + '</a>'; }).join(' ');
      var hid = $('#rField'); if (hid) hid.value = R.name + ' (' + R.qual + '); hot/cold ' + x.toFixed(2) + ', dry/moist ' + y.toFixed(2);
      var mk = $('#rMarker');
      if (mk) { var sc = 0.94 * (260 - 54); mk.setAttribute('transform', 'translate(' + (260 + x * sc).toFixed(1) + ' ' + (260 - y * sc).toFixed(1) + ')'); }
      bar.style.width = '100%';
      out.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
    var again = $('#quizAgain');
    if (again) again.addEventListener('click', function () { hist = []; idx = 0; quiz.hidden = false; $('#quizResult').hidden = true; showQ(0); quiz.scrollIntoView({ block: 'start' }); });
    showQ(0);
  }

  /* ---------- Support / donations ---------- */
  var don = $('#donate');
  if (don) {
    var freq = 'once', amt = 25;
    var presets = { once: [[10, 'Covers one month of hosting and tools'], [25, 'Pays for a source check of one herb profile'], [50, 'Funds a new guide, researched and reviewed'], [100, 'Adds a prize to next season’s contest']],
      monthly: [[5, 'Keeps the interaction checker updated'], [10, 'Funds a monthly safety review of herb profiles'], [20, 'Supports translation into Urdu and Hindi'], [50, 'Helps us hire a licensed medical reviewer']] };
    var amtWrap = $('#amounts'), imp = $('#impact'), amtIn = $('#amtInput'), freqIn = $('#freqInput'), sumEl = $('#donSummary');
    function draw() {
      amtWrap.innerHTML = presets[freq].map(function (p) {
        return '<label class="choice"><input type="radio" name="preset" value="' + p[0] + '"' + (p[0] === amt ? ' checked' : '') + '><span>$' + p[0] + (freq === 'monthly' ? '/mo' : '') + '</span></label>';
      }).join('');
      $$('input[name=preset]', amtWrap).forEach(function (r) { r.addEventListener('change', function () { amt = +r.value; amtIn.value = amt; upd(); }); });
      upd();
    }
    function upd() {
      var p = presets[freq].filter(function (x) { return x[0] === amt; })[0];
      imp.textContent = p ? p[1] + '.' : 'Every amount goes to running and improving Hakeem.com.';
      freqIn.value = freq === 'monthly' ? 'Monthly' : 'One-time';
      sumEl.textContent = '$' + (amt || 0) + (freq === 'monthly' ? ' per month' : ' one-time');
    }
    $$('[data-freq]').forEach(function (b) {
      b.addEventListener('click', function () {
        freq = b.getAttribute('data-freq'); amt = freq === 'monthly' ? 10 : 25; amtIn.value = amt;
        $$('[data-freq]').forEach(function (x) { x.setAttribute('aria-pressed', x === b); }); draw();
      });
    });
    amtIn.addEventListener('input', function () { amt = Math.max(1, Math.round(+amtIn.value || 0)); $$('input[name=preset]', amtWrap).forEach(function (r) { r.checked = +r.value === amt; }); upd(); });
    draw();
  }

  /* ---------- Contest countdown: season closes at the end of the current quarter (UTC) ---------- */
  var cd = $$('[data-countdown]');
  if (cd.length) {
    var now = new Date(), qEnd = new Date(Date.UTC(now.getUTCFullYear(), Math.floor(now.getUTCMonth() / 3) * 3 + 3, 0, 23, 59, 59));
    if (qEnd - now < 7 * 864e5) qEnd = new Date(Date.UTC(now.getUTCFullYear(), Math.floor(now.getUTCMonth() / 3) * 3 + 6, 0, 23, 59, 59));
    $$('[data-close-date]').forEach(function (el) { el.textContent = qEnd.toLocaleDateString(undefined, { day: 'numeric', month: 'long', year: 'numeric', timeZone: 'UTC' }) + ', 23:59 UTC'; });
    (function tick() {
      var ms = Math.max(0, qEnd - new Date());
      var d = Math.floor(ms / 864e5), h = Math.floor(ms % 864e5 / 36e5), m = Math.floor(ms % 36e5 / 6e4), s = Math.floor(ms % 6e4 / 1e3);
      var txt = d + 'd ' + (h < 10 ? '0' : '') + h + 'h ' + (m < 10 ? '0' : '') + m + 'm ' + (s < 10 ? '0' : '') + s + 's';
      cd.forEach(function (el) { el.textContent = txt; });
      setTimeout(tick, 1000);
    })();
  }

  /* ---------- Character counters ---------- */
  $$('textarea[maxlength]').forEach(function (t) {
    var c = document.createElement('div'); c.className = 'hint'; t.parentNode.appendChild(c);
    function u() { c.textContent = t.value.length + ' / ' + t.getAttribute('maxlength') + ' characters'; }
    t.addEventListener('input', u); u();
  });
})();
