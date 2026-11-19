/* Progressive enhancement only. Every page is complete and readable without this file. */
(function () {
  var root = document.documentElement;
  var reduce = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
  var darkQuery = window.matchMedia('(prefers-color-scheme: dark)');

  /* Theme toggle, remembered. The saved choice is applied by an inline script in <head>. */
  function currentTheme() {
    var t = root.getAttribute('data-theme');
    if (t === 'dark' || t === 'light') return t;
    return darkQuery.matches ? 'dark' : 'light';
  }
  function syncToggles() {
    var dark = currentTheme() === 'dark';
    document.querySelectorAll('[data-theme-toggle]').forEach(function (b) {
      b.setAttribute('aria-pressed', String(dark));
    });
  }
  document.querySelectorAll('[data-theme-toggle]').forEach(function (b) {
    b.hidden = false;
    b.addEventListener('click', function () {
      var next = currentTheme() === 'dark' ? 'light' : 'dark';
      root.setAttribute('data-theme', next);
      try { localStorage.setItem('theme', next); } catch (e) {}
      syncToggles();
    });
  });
  syncToggles();
  if (darkQuery.addEventListener) darkQuery.addEventListener('change', syncToggles);

  /* Value chain: loads showing the break, and mends when the reader first scrolls
     or presses the button. The first view stays still, so nothing moves until the
     reader acts. Reduced motion and no JavaScript both show it mended. */
  document.querySelectorAll('[data-vc]').forEach(function (fig) {
    var btn = fig.parentNode.querySelector('[data-vc-replay]');
    var status = fig.parentNode.querySelector('[data-vc-status]');
    function set(mended, announce) {
      fig.setAttribute('data-state', mended ? 'mended' : 'broken');
      if (btn) btn.textContent = mended ? 'Show the break' : 'Mend the chain';
      if (status && announce) {
        status.textContent = mended
          ? 'Chain repaired. Value now reaches realise value and renew.'
          : 'Chain shown broken between adopt and realise value.';
      }
    }
    if (btn) {
      btn.hidden = false;
      btn.addEventListener('click', function () {
        set(fig.getAttribute('data-state') !== 'mended', true);
      });
    }
    if (reduce) { set(true, false); return; }
    set(false, false);
    var onScroll = function () {
      if (window.scrollY < 40) return;
      window.removeEventListener('scroll', onScroll);
      if (fig.getAttribute('data-state') !== 'mended') set(true, false);
    };
    window.addEventListener('scroll', onScroll, { passive: true });
  });

  /* Headline figures count up once when first seen. The real value is in the HTML. */
  var counters = document.querySelectorAll('[data-count]');
  if (!reduce && 'IntersectionObserver' in window && counters.length) {
    var run = function (el) {
      var to = +el.getAttribute('data-count');
      var pre = el.getAttribute('data-prefix') || '';
      var suf = el.getAttribute('data-suffix') || '';
      var start = null;
      function frame(t) {
        if (!start) start = t;
        var k = Math.min((t - start) / 900, 1);
        var e = 1 - Math.pow(1 - k, 3);
        el.textContent = pre + Math.round(to * e).toLocaleString('en-GB') + suf;
        if (k < 1) requestAnimationFrame(frame);
      }
      requestAnimationFrame(frame);
    };
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { run(en.target); io.unobserve(en.target); }
      });
    }, { threshold: 0.6 });
    counters.forEach(function (c) { io.observe(c); });
  }

  /* Filter case studies by skill. Without JavaScript every card shows. */
  var filter = document.querySelector('[data-filter]');
  if (filter) {
    var cards = document.querySelectorAll('[data-skill-card]');
    var status = document.querySelector('[data-filter-status]');
    filter.hidden = false;
    filter.addEventListener('click', function (e) {
      var b = e.target.closest('button');
      if (!b) return;
      filter.querySelectorAll('button').forEach(function (x) {
        x.setAttribute('aria-pressed', String(x === b));
      });
      var key = b.getAttribute('data-skill');
      var shown = 0;
      cards.forEach(function (c) {
        var show = key === 'all' || c.getAttribute('data-skill-card') === key;
        c.hidden = !show;
        if (show) shown++;
      });
      var name = b.getAttribute('data-name');
      status.textContent = key === 'all'
        ? 'Showing all ' + shown + ' case studies'
        : 'Showing ' + shown + ' case ' + (shown === 1 ? 'study' : 'studies') + ' in ' + name;
    });
  }

  /* How I work: the workflow line draws once when the section comes into view,
     and each step comes forward as the line reaches it. */
  var flow = document.querySelector('[data-flow]');
  if (flow && !reduce && 'IntersectionObserver' in window) {
    var steps = Array.prototype.slice.call(flow.children);
    flow.classList.add('is-pending');
    flow.style.setProperty('--p', '0');
    var flowIO = new IntersectionObserver(function (entries) {
      if (!entries[0].isIntersecting) return;
      flowIO.disconnect();
      var vertical = getComputedStyle(flow).gridTemplateColumns.split(' ').length === 1;
      var size = vertical ? flow.offsetHeight : flow.offsetWidth;
      var marks = steps.map(function (li) { return (vertical ? li.offsetTop : li.offsetLeft) / size; });
      var start = null;
      function frame(t) {
        if (!start) start = t;
        var p = Math.min((t - start) / 3000, 1);
        flow.style.setProperty('--p', p.toFixed(3));
        steps.forEach(function (li, i) { if (p >= marks[i]) li.classList.add('is-active'); });
        if (p < 1) { requestAnimationFrame(frame); } else { flow.classList.remove('is-pending'); }
      }
      requestAnimationFrame(frame);
    }, { threshold: 0.4 });
    flowIO.observe(flow);
  }

  /* Back to top: shown once the reader is past the first screen. */
  var toTop = document.querySelector('[data-to-top]');
  if (toTop) {
    var topTick = false;
    window.addEventListener('scroll', function () {
      if (topTick) return;
      topTick = true;
      requestAnimationFrame(function () {
        toTop.classList.toggle('is-visible', window.scrollY > window.innerHeight * 0.8);
        topTick = false;
      });
    }, { passive: true });
  }

  /* Reading progress on case studies. Measured only once the reader scrolls,
     so loading the page never forces a full layout. */
  var bar = document.querySelector('[data-progress]');
  if (bar) {
    var ticking = false;
    var update = function () {
      var max = document.documentElement.scrollHeight - window.innerHeight;
      bar.style.transform = 'scaleX(' + (max > 0 ? Math.min(window.scrollY / max, 1) : 0) + ')';
      ticking = false;
    };
    window.addEventListener('scroll', function () {
      if (!ticking) { ticking = true; requestAnimationFrame(update); }
    }, { passive: true });
  }
})();
