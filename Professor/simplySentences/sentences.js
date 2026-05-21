/* ============================================================
   sentences.js — Simply Sentences shared JavaScript
   All pages in the Simply Sentences series link to this file.
   ============================================================ */

(function () {
  'use strict';

  /* ----------------------------------------------------------
     1. SCROLL PROGRESS BAR
     Injects a thin progress bar just below the sticky nav.
     ---------------------------------------------------------- */
  function initScrollProgress() {
    const bar = document.getElementById('scroll-progress');
    if (!bar) return;

    function updateBar() {
      const scrollTop    = window.scrollY || document.documentElement.scrollTop;
      const docHeight    = document.documentElement.scrollHeight - window.innerHeight;
      const pct          = docHeight > 0 ? (scrollTop / docHeight) * 100 : 0;
      bar.style.width    = pct + '%';
    }

    window.addEventListener('scroll', updateBar, { passive: true });
    updateBar();
  }


  /* ----------------------------------------------------------
     2. DYNAMIC NAV HEIGHT
     The nav has no fixed height — it wraps freely on mobile.
     This function measures the rendered nav height and sets
     body padding-top to match, recalculating on resize so
     content is never hidden behind the nav at any screen width.
     ---------------------------------------------------------- */
  function initDynamicNavHeight() {
    const nav = document.querySelector('.site-nav');
    if (!nav) return;

    function setBodyPad() {
      const h = nav.getBoundingClientRect().height;
      document.body.style.paddingTop = h + 'px';

      // Also shift the scroll-progress bar to sit flush below the nav
      const bar = document.getElementById('scroll-progress');
      if (bar) bar.style.top = h + 'px';
    }

    setBodyPad();
    window.addEventListener('resize', setBodyPad, { passive: true });

    // Run once more after fonts are loaded, since Nunito can shift layout
    if (document.fonts && document.fonts.ready) {
      document.fonts.ready.then(setBodyPad);
    }
  }


  /* ----------------------------------------------------------
     3. ACTIVE NAV LINK
     Adds the .active class to the nav link whose href matches
     the current page filename.
     ---------------------------------------------------------- */
  function initActiveNav() {
    const currentPage = window.location.pathname.split('/').pop() || 'index.html';
    document.querySelectorAll('.nav-links a').forEach(function (a) {
      const linkPage = a.getAttribute('href').split('/').pop();
      if (linkPage === currentPage) {
        a.classList.add('active');
        a.setAttribute('aria-current', 'page');
      }
    });
  }


  /* ----------------------------------------------------------
     4. SMOOTH ANCHOR OFFSET
     When a #hash link is clicked, offset the scroll position
     so the sticky nav doesn't cover the target heading.
     Reads the live nav height so it works at any screen width.
     ---------------------------------------------------------- */
  function initAnchorOffset() {
    function navHeight() {
      const nav = document.querySelector('.site-nav');
      return nav ? nav.getBoundingClientRect().height + 8 : 64;
    }

    document.querySelectorAll('a[href^="#"]').forEach(function (a) {
      a.addEventListener('click', function (e) {
        const id     = a.getAttribute('href').slice(1);
        const target = document.getElementById(id);
        if (!target) return;
        e.preventDefault();
        const top = target.getBoundingClientRect().top + window.scrollY - navHeight();
        window.scrollTo({ top: top, behavior: 'smooth' });
      });
    });

    if (window.location.hash) {
      window.addEventListener('load', function () {
        const id     = window.location.hash.slice(1);
        const target = document.getElementById(id);
        if (!target) return;
        setTimeout(function () {
          const top = target.getBoundingClientRect().top + window.scrollY - navHeight();
          window.scrollTo({ top: top, behavior: 'smooth' });
        }, 150);
      });
    }
  }


  /* ----------------------------------------------------------
     5. ANNOTATION LEGEND AUTO-BUILD
     If a <div class="annotation-legend"> exists on the page,
     and it is empty, automatically populate it from the
     highlight classes actually used on that page.
     ---------------------------------------------------------- */
  const LEGEND_LABELS = {
    'hl-subject':      'Subject',
    'hl-verb':         'Verb',
    'hl-direct-obj':   'Direct Object',
    'hl-indirect-obj': 'Indirect Object',
    'hl-prep':         'Prep. Phrase',
    'hl-verbal':       'Verbal Phrase',
    'hl-conjunction':  'Conjunction',
    'hl-note':         'Note / Highlight',
  };

  function initAnnotationLegend() {
    const legend = document.querySelector('.annotation-legend');
    if (!legend || legend.children.length > 0) return; // already populated

    // Find which hl- classes are actually used on this page
    const usedClasses = new Set();
    document.querySelectorAll('[class]').forEach(function (el) {
      el.classList.forEach(function (cls) {
        if (cls.startsWith('hl-') && LEGEND_LABELS[cls]) {
          usedClasses.add(cls);
        }
      });
    });

    // Build legend items in the defined order
    Object.keys(LEGEND_LABELS).forEach(function (cls) {
      if (!usedClasses.has(cls)) return;
      const item    = document.createElement('span');
      item.className = 'legend-item';

      const swatch  = document.createElement('span');
      swatch.className = 'legend-swatch ' + cls;
      // Swatch background comes from the CSS variable via the hl- class styling
      // We need to apply the background directly since the swatch doesn't contain text
      const styles  = getComputedStyle(document.documentElement);
      const varName = '--hl-' + cls.replace('hl-', '');
      const bg      = styles.getPropertyValue(varName).trim();
      swatch.style.background = bg || '#ddd';

      const label   = document.createElement('span');
      label.textContent = LEGEND_LABELS[cls];

      item.appendChild(swatch);
      item.appendChild(label);
      legend.appendChild(item);
    });
  }


  /* ----------------------------------------------------------
     6. EXAMPLE TOGGLES  [ more … | close ]
     Any .toggle-btn controls the .example-overflow that
     immediately follows it inside the same .sentence-group.
     ---------------------------------------------------------- */
  function initExampleToggles() {
    document.querySelectorAll('.toggle-btn').forEach(function (btn) {
      btn.addEventListener('click', function () {
        const overflow = btn.parentElement.querySelector('.example-overflow');
        if (!overflow) return;
        const isOpen = overflow.classList.toggle('open');
        btn.textContent = isOpen ? '[ close ]' : '[ more … ]';
      });
    });
  }


  /* ----------------------------------------------------------
     7. INIT — run everything on DOMContentLoaded
     ---------------------------------------------------------- */
  document.addEventListener('DOMContentLoaded', function () {
    initScrollProgress();
    initDynamicNavHeight();
    initActiveNav();
    initAnchorOffset();
    initAnnotationLegend();
    initExampleToggles();
  });

}());
