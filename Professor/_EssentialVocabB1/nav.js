// nav.js 
// — Navigate a set of htmls in a single folder
// ─────────────────────────────────────────────
// To add or activate a unit:
//   1. Add/edit an entry in the UNITS array below
//   2. Set active: true to show it in the nav
//   3. That's it — all pages update automatically
// ─────────────────────────────────────────────
// add these external sources:
// <link rel="stylesheet" href="nav.css">
// <script src="nav.js" defer></script>   not the "defer" attribute

const UNITS = [
  { href: "index.html",            label: "Menu",    title: "index",            active: true },
{ href: "essential-vocab-1.html",  label: "1",  title: "essential-vocab-1",  active: true },
{ href: "essential-vocab-2.html",  label: "2",  title: "essential-vocab-2",  active: true },
{ href: "essential-vocab-3.html",  label: "3",  title: "essential-vocab-3",  active: true },
{ href: "essential-vocab-4.html",  label: "4",  title: "essential-vocab-4",  active: true },
{ href: "essential-vocab-5.html",  label: "5",  title: "essential-vocab-5",  active: true },
{ href: "essential-vocab-6.html",  label: "6",  title: "essential-vocab-6",  active: true },
{ href: "essential-vocab-7.html",  label: "7",  title: "essential-vocab-7",  active: true },
{ href: "essential-vocab-8.html",  label: "8",  title: "essential-vocab-8",  active: true },
{ href: "essential-vocab-9.html",  label: "9",  title: "essential-vocab-9",  active: true },
{ href: "essential-vocab-10.html", label: "10", title: "essential-vocab-10", active: true },
{ href: "essential-vocab-11.html", label: "11", title: "essential-vocab-11", active: true },
{ href: "essential-vocab-12.html", label: "12", title: "essential-vocab-12", active: true },
{ href: "essential-vocab-13.html", label: "13", title: "essential-vocab-13", active: true },
{ href: "essential-vocab-14.html", label: "14", title: "essential-vocab-14", active: true },
];

(function () {
  const currentPage = window.location.pathname.split("/").pop() || "index.html";
  const activeUnits = UNITS.filter(u => u.active);

  // ── BUILD STICKY TOP NAV ─────────────────────────────────
  let navHtml = `<nav>`;
  activeUnits.forEach(unit => {
    const isActive = currentPage === unit.href ? " active" : "";
    const cls = unit.href === "index.html" ? "home" : `unit-link${isActive}`;
    navHtml += `<a href="${unit.href}" class="${cls}" title="${unit.title}">${unit.label}</a>`;
    if (unit.href !== "index.html") navHtml += ``;
  });
    navHtml += `</nav>`;
  document.body.insertAdjacentHTML("afterbegin", navHtml);


})();
