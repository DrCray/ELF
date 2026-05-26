/*
To use this single page navigatin system,
you need h2 headings at each navigation point.
  <h2> Section 1 </h2>
  <h2> Section 2 </h2> ...

  also add this top menu division to your page.
     <div id="top"></div>
*/


document.addEventListener("DOMContentLoaded", () => {
    if ("scrollRestoration" in history) {
        history.scrollRestoration = "manual";
    }

    window.scrollTo(0, 0);

    const headings = [...document.querySelectorAll("h2")];
    if (!headings.length) return;

    const slugify = (str) =>
    str
    .toLowerCase()
    .trim()
    .replace(/[^\w\s-]/g, "")
    .replace(/\s+/g, "-")
    .replace(/-+/g, "-");

    const usedIds = new Set();

    headings.forEach((h2, index) => {
        let id = h2.id || slugify(h2.textContent || `section-${index + 1}`);
        const base = id;
        let n = 2;

        while (usedIds.has(id) || document.getElementById(id)) {
            id = `${base}-${n++}`;
        }

        h2.id = id;
        usedIds.add(id);
    });

    const navWrap = document.createElement("details");
    navWrap.className = "h2-nav-wrap";
    navWrap.open = true;

    const summary = document.createElement("summary");
    summary.textContent = "Page sections";
    navWrap.appendChild(summary);

    const nav = document.createElement("nav");
    nav.className = "h2-nav";

    headings.forEach((h2) => {
        const a = document.createElement("a");
        a.href = `#${h2.id}`;
        a.textContent = h2.textContent.trim();
        nav.appendChild(a);
    });

    navWrap.appendChild(nav);

    const firstHeading = headings[0];
    firstHeading.parentNode.insertBefore(navWrap, firstHeading);

    headings.forEach((h2, index) => {
        const controls = document.createElement("div");
        controls.className = "h2-controls";

        const prevId = headings[index - 1]?.id || headings[0].id;
        const nextId = headings[index + 1]?.id || headings[headings.length - 1].id;

        controls.innerHTML = `
        <a class="h2-btn" href="#top">Top menu</a>
        <a class="h2-btn" href="#${prevId}">Previous section</a>
        <a class="h2-btn" href="#${nextId}">Next section</a>
        `;

        h2.insertAdjacentElement("afterend", controls);
    });
});
