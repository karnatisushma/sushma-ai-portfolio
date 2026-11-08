(function () {
  var w = window, d = document;
  var root = d.getElementById('root');
  if (!root) return;
  var mm = function (q) { return !!(w.matchMedia && w.matchMedia(q).matches); };
  var reduced = mm('(prefers-reduced-motion: reduce)');
  var fine = mm('(pointer: fine)');
  var $ = function (id) { return d.getElementById(id); };
  var each = function (list, fn) { Array.prototype.forEach.call(list, fn); };
  root.classList.add('is-js');

  /* ---------- sound ---------- */
  var ac = null, soundOn = false, lastBlip = 0;
  function blip(kind) {
    if (!soundOn || !ac) return;
    var now = (w.performance && performance.now()) || Date.now();
    if (kind === 'hover' && now - lastBlip < 80) return;
    lastBlip = now;
    var t = ac.currentTime;
    function tone(type, f0, f1, peak, dur, delay) {
      var o = ac.createOscillator(), g = ac.createGain(), s = t + (delay || 0);
      o.type = type;
      o.frequency.setValueAtTime(f0, s);
      o.frequency.exponentialRampToValueAtTime(f1, s + dur * 0.8);
      g.gain.setValueAtTime(0.0001, s);
      g.gain.exponentialRampToValueAtTime(peak, s + 0.006);
      g.gain.exponentialRampToValueAtTime(0.0001, s + dur);
      o.connect(g); g.connect(ac.destination);
      o.start(s); o.stop(s + dur + 0.02);
    }
    if (kind === 'hover') tone('sine', 2400, 1800, 0.018, 0.05);
    else if (kind === 'click') tone('triangle', 640, 300, 0.05, 0.11);
    else if (kind === 'step') tone('sine', 880, 1320, 0.03, 0.09);
    else if (kind === 'on') { tone('sine', 660, 660, 0.035, 0.09); tone('sine', 990, 990, 0.035, 0.12, 0.08); }
  }
  var snd = $('snd');
  if (snd) snd.addEventListener('click', function () {
    soundOn = !soundOn;
    if (soundOn && !ac) {
      var AC = w.AudioContext || w.webkitAudioContext;
      if (AC) { try { ac = new AC(); } catch (e) { ac = null; } }
    }
    if (ac && ac.state === 'suspended') ac.resume();
    snd.setAttribute('aria-pressed', soundOn ? 'true' : 'false');
    snd.setAttribute('data-cursor', soundOn ? 'Mute' : 'Sound');
    $('sndOn').hidden = !soundOn;
    $('sndOff').style.display = soundOn ? 'none' : 'flex';
    if (soundOn) blip('on');
  });

  /* ---------- reveal + counters ---------- */
  var els = root.querySelectorAll('.rv');
  var counts = root.querySelectorAll('[data-count]');
  function countUp() {
    var start = null, dur = 1600;
    function step(ts) {
      if (start === null) start = ts;
      var k = Math.min(1, (ts - start) / dur), e = 1 - Math.pow(1 - k, 3);
      each(counts, function (c) { c.textContent = Math.round(+c.getAttribute('data-count') * e); });
      if (k < 1) requestAnimationFrame(step);
    }
    requestAnimationFrame(step);
  }
  if ('IntersectionObserver' in w && !reduced) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { if (en.isIntersecting) { en.target.classList.add('in'); io.unobserve(en.target); } });
    }, { threshold: 0.12, rootMargin: '0px 0px -6% 0px' });
    each(els, function (el) { io.observe(el); });
    var metrics = $('metrics');
    if (metrics) {
      each(counts, function (c) { c.textContent = '0'; });
      var mio = new IntersectionObserver(function (en) {
        if (en[0] && en[0].isIntersecting) { countUp(); mio.disconnect(); }
      }, { threshold: 0.35 });
      mio.observe(metrics);
    }
  } else {
    each(els, function (el) { el.classList.add('in'); });
  }

  /* ---------- rotating word ---------- */
  var words = $('words'), wi = 0;
  if (words && !reduced) setInterval(function () {
    wi = (wi + 1) % 4;
    words.style.transform = 'translateY(-' + (wi * 1.2).toFixed(1) + 'em)';
  }, 2600);

  /* ---------- pipeline stepper ---------- */
  var STAGES = [
    ['Ingest the standards', 'Python pipelines break NCERT and US Common Core into curriculum nodes — subject, grade band and learning objective — ready to embed.'],
    ['Embed every objective', 'Gemini embeddings turn each learning objective into a vector, so "fractions in grade 5" can be compared with its counterpart on another board by meaning, not by wording.'],
    ['Match across boards', 'Supabase pgvector runs the semantic search that lines up curriculum nodes across systems and grade bands — the evidence the agent reasons over.'],
    ['Find the gaps', 'A Gemini agent compares what the student has covered against the target board, injects source URLs, and scores each gap with an adaptive percentile model.'],
    ['Trust, then verify', 'Structured JSON output is parsed and validated, and hallucination checks reject anything the retrieved curriculum does not support — inside JWT-authenticated, rate-limited Edge Functions.'],
    ['Hand over a plan', 'Gaps classified Critical, Major or Moderate become a phase-wise bridge timeline with linked study resources — shown in live dashboards and exportable as PDF.']
  ];
  var nodes = root.querySelectorAll('.pnode'), si = 0, picked = false;
  var stitle = $('stitle'), sbody = $('sbody'), spct = $('spct');
  function setStage(i) {
    si = i;
    each(nodes, function (n, k) { n.classList.toggle('on', k === i); n.setAttribute('aria-pressed', k === i ? 'true' : 'false'); });
    each(root.querySelectorAll('.snum'), function (s) { s.textContent = '0' + (i + 1); });
    [stitle, sbody].forEach(function (el) { if (!el) return; el.classList.remove('swap'); void el.offsetWidth; el.classList.add('swap'); });
    if (stitle) stitle.textContent = STAGES[i][0];
    if (sbody) sbody.textContent = STAGES[i][1];
    if (spct) spct.style.width = Math.round(((i + 1) / STAGES.length) * 100) + '%';
  }
  each(nodes, function (n) {
    n.addEventListener('click', function () { picked = true; setStage(+n.getAttribute('data-i')); blip('step'); });
  });
  if (!reduced) setInterval(function () { if (!picked) setStage((si + 1) % STAGES.length); }, 3400);

  /* ---------- scroll progress + timeline ---------- */
  var bar = $('bar'), tl = $('tl'), tlFill = $('tlfill');
  function onScroll() {
    var de = d.documentElement, max = de.scrollHeight - w.innerHeight;
    var p = max > 0 ? (w.scrollY || de.scrollTop) / max : 0;
    if (bar) bar.style.transform = 'scaleX(' + p + ')';
    if (tl && tlFill) {
      var t = 1;
      if (max > 0 && !reduced) {
        var r = tl.getBoundingClientRect();
        t = Math.min(1, Math.max(0, (w.innerHeight * 0.65 - r.top) / r.height));
      }
      tlFill.style.transform = 'scaleY(' + t + ')';
    }
  }
  w.addEventListener('scroll', onScroll, { passive: true });
  w.addEventListener('resize', onScroll);
  onScroll();

  /* ---------- cursor ---------- */
  var dot = $('dot'), ring = $('ring'), hl = $('hl');
  var mx = -100, my = -100, rx = -100, ry = -100, active = false, hovEl = null;
  if (fine && !reduced && dot && ring) {
    d.addEventListener('mousemove', function (e) {
      mx = e.clientX; my = e.clientY;
      if (!active) { active = true; rx = mx; ry = my; root.classList.add('has-cursor'); }
    }, { passive: true });
    (function loop() {
      rx += (mx - rx) * 0.16; ry += (my - ry) * 0.16;
      dot.style.transform = 'translate3d(' + mx + 'px,' + my + 'px,0)';
      ring.style.transform = 'translate3d(' + rx + 'px,' + ry + 'px,0)';
      requestAnimationFrame(loop);
    })();
    d.addEventListener('mouseover', function (e) {
      var t = e.target && e.target.closest ? e.target.closest('a,button,[data-cursor]') : null;
      if (t === hovEl) return;
      hovEl = t;
      ring.classList.toggle('hov', !!t);
      root.classList.toggle('cur-hov', !!t);
      hl.textContent = t ? (t.getAttribute('data-cursor') || '') : '';
      if (t) blip('hover');
    });
    d.addEventListener('mousedown', function () { ring.classList.add('down'); if (hovEl) blip('click'); });
    d.addEventListener('mouseup', function () { ring.classList.remove('down'); });
    d.documentElement.addEventListener('mouseleave', function () { root.classList.add('cur-out'); });
    d.documentElement.addEventListener('mouseenter', function () { root.classList.remove('cur-out'); });
  } else {
    d.addEventListener('mousedown', function (e) {
      if (e.target.closest && e.target.closest('a,button')) blip('click');
    });
  }

  /* ---------- card spotlight + magnetic buttons ---------- */
  each(root.querySelectorAll('.spot'), function (el) {
    el.addEventListener('mousemove', function (e) {
      var r = el.getBoundingClientRect();
      el.style.setProperty('--mx', (e.clientX - r.left) + 'px');
      el.style.setProperty('--my', (e.clientY - r.top) + 'px');
    });
  });
  if (!reduced) each(root.querySelectorAll('[data-mag]'), function (el) {
    el.addEventListener('mousemove', function (e) {
      var r = el.getBoundingClientRect();
      var x = (e.clientX - (r.left + r.width / 2)) * 0.22, y = (e.clientY - (r.top + r.height / 2)) * 0.32;
      el.style.transform = 'translate(' + x.toFixed(1) + 'px,' + y.toFixed(1) + 'px)';
    });
    el.addEventListener('mouseleave', function () { el.style.transform = ''; });
  });

  /* ---------- copy email ---------- */
  var copy = $('copy'), copyl = $('copyl'), ct;
  if (copy) copy.addEventListener('click', function () {
    var done = function () {
      copyl.textContent = 'Copied';
      clearTimeout(ct); ct = setTimeout(function () { copyl.textContent = 'Copy email'; }, 1800);
    };
    try {
      if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText('sushmakarnati14@gmail.com').then(done, function () {});
    } catch (e) {}
  });
})();
