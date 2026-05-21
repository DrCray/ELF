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
{ href: "advanced-vocab-01.html",  label: "1",  title: "advanced-vocab-01",  active: true },
{ href: "advanced-vocab-02.html",  label: "2",  title: "advanced-vocab-02",  active: true },
{ href: "advanced-vocab-03.html",  label: "3",  title: "advanced-vocab-03",  active: true },
{ href: "advanced-vocab-04.html",  label: "4",  title: "advanced-vocab-04",  active: true },
{ href: "advanced-vocab-05.html",  label: "5",  title: "advanced-vocab-05",  active: true },
{ href: "advanced-vocab-06.html",  label: "6",  title: "advanced-vocab-06",  active: true },
{ href: "advanced-vocab-07.html",  label: "7",  title: "advanced-vocab-07",  active: true },
{ href: "advanced-vocab-08.html",  label: "8",  title: "advanced-vocab-08",  active: true },
{ href: "advanced-vocab-09.html",  label: "9",  title: "advanced-vocab-09",  active: true },
{ href: "advanced-vocab-10.html",  label: "10", title: "advanced-vocab-10",  active: true },
{ href: "advanced-vocab-11.html",  label: "11", title: "advanced-vocab-11",  active: true },
{ href: "advanced-vocab-12.html",  label: "12", title: "advanced-vocab-12",  active: true },
{ href: "advanced-vocab-13.html",  label: "13", title: "advanced-vocab-13",  active: true },
{ href: "advanced-vocab-14.html",  label: "14", title: "advanced-vocab-14",  active: true },
{ href: "advanced-vocab-15.html",  label: "15", title: "advanced-vocab-15",  active: true },
{ href: "advanced-vocab-16.html",  label: "16", title: "advanced-vocab-16",  active: true },
{ href: "advanced-vocab-17.html",  label: "17", title: "advanced-vocab-17",  active: true },
{ href: "advanced-vocab-18.html",  label: "18", title: "advanced-vocab-18",  active: true },
{ href: "advanced-vocab-19.html",  label: "19", title: "advanced-vocab-19",  active: true },
{ href: "advanced-vocab-20.html",  label: "20", title: "advanced-vocab-20",  active: true },
{ href: "advanced-vocab-21.html",  label: "21", title: "advanced-vocab-21",  active: true },
{ href: "advanced-vocab-22.html",  label: "22", title: "advanced-vocab-22",  active: true },
{ href: "advanced-vocab-23.html",  label: "23", title: "advanced-vocab-23",  active: true },
{ href: "advanced-vocab-24.html",  label: "24", title: "advanced-vocab-24",  active: true },
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
