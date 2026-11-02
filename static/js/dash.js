/* Oakbound Trust Bank: signed-in app interactions. No dependencies. */
(function () {
  "use strict";
  var doc = document;
  var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var fine = window.matchMedia && window.matchMedia("(hover: hover) and (pointer: fine)").matches;
  var $$ = function (s, c) { return Array.prototype.slice.call((c || doc).querySelectorAll(s)); };

  /* ---------- 3D tilt with moving glare (one element at a time, one rAF) ---------- */
  if (fine && !reduce) {
    var active = null, tick = false, ev = null;
    var apply = function () {
      tick = false; if (!active || !ev) return;
      var r = active.getBoundingClientRect(), x = (ev.clientX - r.left) / r.width, y = (ev.clientY - r.top) / r.height, max = parseFloat(active.getAttribute("data-tilt")) || 7;
      active.style.setProperty("--ry", ((x - 0.5) * 2 * max).toFixed(2) + "deg");
      active.style.setProperty("--rx", ((0.5 - y) * 2 * max).toFixed(2) + "deg");
      active.style.setProperty("--gx", (x * 100).toFixed(1) + "%"); active.style.setProperty("--gy", (y * 100).toFixed(1) + "%");
    };
    doc.addEventListener("pointermove", function (e) {
      var t = e.target.closest ? e.target.closest("[data-tilt]") : null;
      if (t !== active) { if (active) { active.classList.remove("live"); active.style.setProperty("--rx", "0deg"); active.style.setProperty("--ry", "0deg"); } active = t; if (active) active.classList.add("live"); }
      ev = e; if (active && !tick) { tick = true; requestAnimationFrame(apply); }
    }, { passive: true });
    doc.addEventListener("pointerleave", function () { if (active) { active.classList.remove("live"); active.style.setProperty("--rx", "0deg"); active.style.setProperty("--ry", "0deg"); active = null; } });
  }

  /* ---------- count-up numbers (text is already final, so no-JS is fine) ---------- */
  var fmt = new Intl.NumberFormat("en-US", { minimumFractionDigits: 2, maximumFractionDigits: 2 });
  function countUp(el) {
    var raw = el.textContent.trim(), m = raw.match(/^([^\d-]*)(-?[\d,]+(?:\.\d+)?)(.*)$/);
    if (!m) return;
    var pre = m[1], target = parseFloat(m[2].replace(/,/g, "")), post = m[3], dec = /\./.test(m[2]), t0 = performance.now(), dur = 1100;
    if (!isFinite(target) || target === 0) return;
    (function step(now) {
      var p = Math.min(1, (now - t0) / dur), e = 1 - Math.pow(1 - p, 4), v = target * e;
      el.textContent = pre + (dec ? fmt.format(v) : Math.round(v).toLocaleString("en-US")) + post;
      if (p < 1) requestAnimationFrame(step); else el.textContent = raw;
    })(t0);
  }
  var counters = $$("[data-count]");
  if (counters.length) {
    if (reduce || !("IntersectionObserver" in window)) { /* leave final values */ }
    else { var io = new IntersectionObserver(function (es) { es.forEach(function (e) { if (e.isIntersecting) { countUp(e.target); io.unobserve(e.target); } }); }, { threshold: 0.4 }); counters.forEach(function (c) { io.observe(c); }); }
  }

  /* ---------- donut chart from real balances ---------- */
  $$("[data-donut]").forEach(function (box) {
    var vals = box.getAttribute("data-donut").split(",").map(function (v) { return Math.max(0, parseFloat(v) || 0); });
    var total = vals.reduce(function (a, b) { return a + b; }, 0), circs = $$("circle[data-seg]", box), C = 2 * Math.PI * 70, off = 0;
    circs.forEach(function (c, i) {
      var share = total ? vals[i] / total : 0, len = Math.max(0, share * C - (share > 0 ? 8 : 0));
      c.setAttribute("stroke-dashoffset", String(-off)); c.style.strokeDasharray = "0 " + C;
      (function (cc, l) { setTimeout(function () { cc.style.strokeDasharray = l + " " + (C - l); }, 120); })(c, len);
      off += share * C;
    });
  });

  /* ---------- greeting by time of day ---------- */
  var g = doc.querySelector("[data-greet]");
  if (g) { var h = new Date().getHours(); g.textContent = h < 5 ? "Good evening" : h < 12 ? "Good morning" : h < 18 ? "Good afternoon" : "Good evening"; }

  /* ---------- Bootstrap-compatible modal (no Bootstrap needed) ---------- */
  var backdrop = null;
  function openModal(m) { if (!m) return; backdrop = doc.createElement("div"); backdrop.className = "modal-backdrop-glass"; backdrop.addEventListener("click", closeModal); m.parentNode.insertBefore(backdrop, m); m.classList.add("show"); m.removeAttribute("aria-hidden"); doc.body.classList.add("modal-open"); var i = m.querySelector("input"); if (i) setTimeout(function () { i.focus(); }, 60); }
  function closeModal() { $$(".modal.show").forEach(function (m) { m.classList.remove("show"); m.setAttribute("aria-hidden", "true"); }); if (backdrop) { backdrop.remove(); backdrop = null; } doc.body.classList.remove("modal-open"); }
  doc.addEventListener("click", function (e) {
    var t = e.target.closest ? e.target.closest("[data-bs-toggle='modal']") : null;
    if (t) { e.preventDefault(); openModal(doc.querySelector(t.getAttribute("data-bs-target"))); return; }
    if (e.target.closest && e.target.closest("[data-bs-dismiss='modal']")) { e.preventDefault(); closeModal(); }
    else if (e.target.classList && e.target.classList.contains("modal")) closeModal();
  });
  doc.addEventListener("keydown", function (e) { if (e.key === "Escape") closeModal(); });

  /* ---------- receipt: print, copy, share, barcode ---------- */
  $$("[data-print]").forEach(function (b) { b.addEventListener("click", function () { window.print(); }); });
  $$("[data-copy]").forEach(function (b) {
    b.addEventListener("click", function () {
      var el = doc.querySelector(b.getAttribute("data-copy")); if (!el) return; var text = el.textContent.trim();
      var done = function () { b.classList.add("ok"); setTimeout(function () { b.classList.remove("ok"); }, 1400); };
      if (navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(text).then(done, function () {});
      else { var r = doc.createRange(); r.selectNodeContents(el); var sel = window.getSelection(); sel.removeAllRanges(); sel.addRange(r); try { doc.execCommand("copy"); done(); } catch (e) {} }
    });
  });
  $$("[data-share]").forEach(function (b) {
    if (!navigator.share) { b.style.display = "none"; return; }
    b.addEventListener("click", function () { navigator.share({ title: "Transfer receipt", text: b.getAttribute("data-share-text") || "" }).catch(function () {}); });
  });
  $$("svg[data-barcode]").forEach(function (svg) {
    var str = svg.getAttribute("data-barcode") || "oakbound", seed = 2166136261, i;
    for (i = 0; i < str.length; i++) { seed = Math.imul(seed ^ str.charCodeAt(i), 16777619) >>> 0; }
    var rnd = function () { seed = (Math.imul(seed, 1664525) + 1013904223) >>> 0; return seed / 4294967296; };
    var x = 0, NS = "http://www.w3.org/2000/svg";
    while (x < 236) { var w = 1 + Math.floor(rnd() * 3.4), gap = 1 + Math.floor(rnd() * 2.6), r = doc.createElementNS(NS, "rect"); r.setAttribute("x", x); r.setAttribute("y", 0); r.setAttribute("width", w); r.setAttribute("height", 44); svg.appendChild(r); x += w + gap; }
  });
  (function () {
    var b = doc.getElementById("mb-menu"), sheet = doc.getElementById("mb-sheet"); if (!b || !sheet) return;
    var set = function (open) { sheet.hidden = !open; b.setAttribute("aria-expanded", String(open)); b.setAttribute("aria-label", open ? "Close menu" : "Open menu"); b.classList.toggle("open", open); };
    b.addEventListener("click", function (e) { e.stopPropagation(); set(sheet.hidden); });
    doc.addEventListener("click", function (e) { if (!sheet.hidden && !sheet.contains(e.target)) set(false); });
    doc.addEventListener("keydown", function (e) { if (e.key === "Escape") set(false); });
  })();
})();
