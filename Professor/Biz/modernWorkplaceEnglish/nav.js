// nav.js — Modern Workplace English
// ─────────────────────────────────────────────
// To add or activate a unit:
//   1. Add/edit an entry in the UNITS array below
//   2. Set active: true to show it in the nav
//   3. That's it — all pages update automatically
// ─────────────────────────────────────────────

const UNITS = [
  { href: "unit01.html", label: "Unit 1", title: "The Breakroom",       active: true  },
  { href: "unit02.html", label: "Unit 2", title: "Big News",             active: true  },
  { href: "unit03.html", label: "Unit 3", title: "The Job Posting",      active: true  },
  { href: "unit04.html", label: "Unit 4", title: "The Team Meeting",     active: true  },
  { href: "unit05.html", label: "Unit 5", title: "Working from Home",    active: true },
  { href: "unit06.html", label: "Unit 6", title: "The Difficult Client", active: true },
  { href: "unit07.html", label: "Unit 7", title: "Parker's Last Day",    active: true },
];

(function () {
  const currentPage = window.location.pathname.split("/").pop() || "index.html";
  const activeUnits = UNITS.filter(u => u.active);

  // ── BUILD STICKY TOP NAV ─────────────────────────────────
  let navHtml = `<nav><a class="home" href="index.html">Modern Workplace English</a>`;

  activeUnits.forEach(unit => {
    const isActive = currentPage === unit.href ? " active" : "";
    navHtml += `<span class="sep">›</span><a href="${unit.href}" class="unit-link${isActive}" title="${unit.title}">${unit.label}</a>`;
  });

  navHtml += `</nav>`;
  document.body.insertAdjacentHTML("afterbegin", navHtml);

  // ── REMOVE ANY HARDCODED .page-nav ───────────────────────
  document.querySelectorAll(".page-nav").forEach(el => el.remove());

})();
