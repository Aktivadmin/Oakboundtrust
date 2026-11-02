/* Oakbound Trust Bank: motion layer. Vanilla JS, no dependencies.
   Built to be cheap: one rAF per frame, no layout reads in loops, nothing runs off-screen.
   With no JS or with "reduce motion" the page is still fully usable. */
(function () {
  "use strict";
  var doc = document, root = doc.documentElement;
  var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  var fine = window.matchMedia && window.matchMedia("(hover: hover) and (pointer: fine)").matches;
  var lowEnd = (navigator.hardwareConcurrency || 8) <= 4 || (navigator.deviceMemory || 8) <= 4;
  var $ = function (s, c) { return (c || doc).querySelector(s); };
  var $$ = function (s, c) { return Array.prototype.slice.call((c || doc).querySelectorAll(s)); };
  var clamp = function (v, a, b) { return Math.min(b, Math.max(a, v)); };
  var ease = function (t) { return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2; };
  var seen = false;
  try { seen = sessionStorage.getItem("ob-loaded") === "1"; } catch (e) {}

  /* ---------- loader (once per visit, short) ---------- */
  var loader = $(".ob-loader");
  function finishLoader() {
    if (!loader) return;
    loader.classList.add("done");
    doc.body.classList.remove("ob-lock");
    var l = loader; loader = null;
    setTimeout(function () { if (l.parentNode) l.parentNode.removeChild(l); }, 1000);
    try { sessionStorage.setItem("ob-loaded", "1"); } catch (e) {}
  }
  if (loader) {
    if (seen || reduce) { finishLoader(); }
    else {
      doc.body.classList.add("ob-lock");
      var cnt = $(".count", loader), bar = $(".bar i", loader), t0 = performance.now(), dur = 900;
      (function tick(now) {
        if (!loader) return;
        var p = clamp((now - t0) / dur, 0, 1), e = 1 - Math.pow(1 - p, 3);
        if (cnt) cnt.textContent = String(Math.round(e * 100)).padStart(3, "0") + "%";
        if (bar) bar.style.transform = "scaleX(" + e + ")";
        if (p < 1) requestAnimationFrame(tick); else setTimeout(finishLoader, 120);
      })(t0);
      setTimeout(finishLoader, 2500);
    }
  }

  /* ---------- scroll: header state (batched) ---------- */
  var header = $(".ob-header"), scrollTick = false, hooks = [];
  function onScroll() {
    if (scrollTick) return; scrollTick = true;
    requestAnimationFrame(function () {
      scrollTick = false;
      if (header) header.classList.toggle("scrolled", window.scrollY > 24);
      for (var i = 0; i < hooks.length; i++) hooks[i]();
    });
  }
  window.addEventListener("scroll", onScroll, { passive: true });
  window.addEventListener("resize", onScroll);
  onScroll();

  /* ---------- mobile drawer ---------- */
  var burger = $(".ob-burger"), drawer = $(".ob-drawer");
  if (burger && drawer) {
    burger.addEventListener("click", function () {
      var open = drawer.classList.toggle("open");
      burger.setAttribute("aria-expanded", open ? "true" : "false");
      doc.body.classList.toggle("ob-lock", open);
    });
    $$("a", drawer).forEach(function (a) { a.addEventListener("click", function () { drawer.classList.remove("open"); burger.setAttribute("aria-expanded", "false"); doc.body.classList.remove("ob-lock"); }); });
  }

  /* ---------- reveal on scroll ---------- */
  var revealEls = $$("[data-reveal]");
  if ("IntersectionObserver" in window && !reduce) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) { if (en.isIntersecting) { en.target.classList.add("in"); io.unobserve(en.target); } });
    }, { threshold: 0.1, rootMargin: "0px 0px -5% 0px" });
    revealEls.forEach(function (el) { io.observe(el); });
  } else { revealEls.forEach(function (el) { el.classList.add("in"); }); }

  /* ---------- pointer: spotlight + dot (one rAF, one rect read) ---------- */
  var cursor = $(".ob-cursor");
  if (fine && !reduce) {
    var px = 0, py = 0, cx = 0, cy = 0, moved = false, running = false, spotEl = null;
    var frame = function () {
      cx += (px - cx) * 0.22; cy += (py - cy) * 0.22;
      if (cursor) cursor.style.transform = "translate3d(" + cx + "px," + cy + "px,0)";
      if (spotEl) {
        var r = spotEl.getBoundingClientRect();
        spotEl.style.setProperty("--mx", (px - r.left) + "px"); spotEl.style.setProperty("--my", (py - r.top) + "px");
      }
      if (Math.abs(px - cx) > 0.3 || Math.abs(py - cy) > 0.3 || moved) { moved = false; requestAnimationFrame(frame); } else running = false;
    };
    window.addEventListener("pointermove", function (e) {
      px = e.clientX; py = e.clientY; moved = true;
      if (cursor) cursor.style.opacity = "1";
      spotEl = e.target.closest ? e.target.closest("[data-spot]") : null;
      if (!running) { running = true; requestAnimationFrame(frame); }
    }, { passive: true });
    if (cursor) doc.addEventListener("pointerover", function (e) { cursor.classList.toggle("big", !!(e.target.closest && e.target.closest("a, button, summary, .ob-tab, input, textarea, select"))); }, { passive: true });
  }

  /* ---------- vault scene: scroll drives wheel, door, text (direct writes, only when changed) ---------- */
  var hero = $("[data-vault]");
  if (hero && !reduce) {
    var vault = $(".vault", hero), door = $(".door", hero), wheel = $("#vWheel", hero), inner = $(".opening .in", hero), copy = $(".copy", hero);
    var last = -1;
    hooks.push(function () {
      var r = hero.getBoundingClientRect(), vh = window.innerHeight;
      if (r.bottom < -50 || r.top > vh) return;                      // off-screen: do nothing
      var p = clamp(-r.top / (r.height - vh), 0, 1);
      if (Math.abs(p - last) < 0.0015) return; last = p;
      var turn = ease(clamp(p / 0.42, 0, 1)), swing = ease(clamp((p - 0.42) / 0.3, 0, 1)), txt = clamp((p - 0.62) / 0.25, 0, 1);
      var rise = ease(clamp(p / 0.3, 0, 1)), zoom = ease(clamp((p - 0.3) / 0.6, 0, 1)), out = clamp(p / 0.28, 0, 1);
      wheel.setAttribute("transform", "rotate(" + (turn * 540).toFixed(1) + " 300 300)");
      door.style.transform = "rotateY(" + (-swing * 108).toFixed(1) + "deg)";
      door.style.opacity = String(1 - clamp((p - 0.78) / 0.2, 0, 0.7));
      inner.style.opacity = txt.toFixed(3); inner.style.transform = "translate3d(0," + ((1 - txt) * 18).toFixed(1) + "px,0)";
      vault.style.transform = "translate3d(0," + ((1 - rise) * 52).toFixed(2) + "vh,0) scale(" + (0.8 + rise * 0.2 + zoom * 0.22).toFixed(4) + ")";
      copy.style.opacity = (1 - out).toFixed(3);
      copy.style.transform = "translate3d(0," + (-out * 90).toFixed(1) + "px,0) scale(" + (1 - out * 0.06).toFixed(4) + ")";
    });
  }

  /* ---------- gold motes: few, paused off-screen or when the tab is hidden ---------- */
  $$("canvas[data-motes]").forEach(function (cv) {
    if (reduce || lowEnd || window.innerWidth < 720) return;
    var ctx = cv.getContext("2d"), W, H, dots = [], n = 28, dpr = Math.min(window.devicePixelRatio || 1, 1.5), visible = true;
    function size() { W = cv.clientWidth; H = cv.clientHeight; cv.width = W * dpr; cv.height = H * dpr; ctx.setTransform(dpr, 0, 0, dpr, 0, 0); }
    size(); window.addEventListener("resize", size);
    for (var i = 0; i < n; i++) dots.push({ x: Math.random(), y: Math.random(), r: Math.random() * 1.6 + 0.4, s: Math.random() * 0.0035 + 0.0008, a: Math.random() * 0.55 + 0.2, p: Math.random() * 6.28 });
    new IntersectionObserver(function (e) { visible = e[0].isIntersecting; }).observe(cv);
    (function loop(t) {
      if (visible && !doc.hidden) {
        ctx.clearRect(0, 0, W, H);
        for (var k = 0; k < dots.length; k++) {
          var d = dots[k]; d.y -= d.s; if (d.y < -0.02) { d.y = 1.02; d.x = Math.random(); }
          ctx.globalAlpha = d.a * (0.5 + 0.5 * Math.sin(t * 0.002 + d.p));
          ctx.fillStyle = "#e6c77c"; ctx.beginPath(); ctx.arc((d.x + Math.sin(t * 0.0004 + d.p) * 0.012) * W, d.y * H, d.r, 0, 6.283); ctx.fill();
        }
      }
      requestAnimationFrame(loop);
    })(0);
  });

  /* ---------- parallax: only elements near the viewport ---------- */
  var par = $$("[data-par]");
  if (par.length && !reduce && !lowEnd) {
    var near = new Set();
    var pio = new IntersectionObserver(function (es) { es.forEach(function (e) { if (e.isIntersecting) near.add(e.target); else near.delete(e.target); }); }, { rootMargin: "20% 0px" });
    par.forEach(function (el) { pio.observe(el); });
    hooks.push(function () { near.forEach(function (el) { var r = el.getBoundingClientRect(), c = r.top + r.height / 2 - window.innerHeight / 2; el.style.transform = "translate3d(0," + (c * parseFloat(el.getAttribute("data-par")) * -1).toFixed(1) + "px,0)"; }); });
  }

  /* ---------- tabs ---------- */
  $$("[data-tabs]").forEach(function (box) {
    var tabs = $$("[role=tab]", box), panels = $$("[role=tabpanel]", box);
    function pick(i) { tabs.forEach(function (t, k) { t.setAttribute("aria-selected", k === i ? "true" : "false"); }); panels.forEach(function (p, k) { p.classList.toggle("on", k === i); }); }
    tabs.forEach(function (t, i) { t.addEventListener("click", function () { pick(i); }); t.addEventListener("mouseenter", function () { if (fine) pick(i); }); });
    pick(0);
  });

  /* ---------- live filter (help centre) ---------- */
  $$("[data-filter]").forEach(function (input) {
    var items = $$(input.getAttribute("data-filter"));
    input.addEventListener("input", function () {
      var q = input.value.trim().toLowerCase();
      items.forEach(function (el) { el.style.display = !q || el.textContent.toLowerCase().indexOf(q) > -1 ? "" : "none"; });
    });
  });

  /* ---------- toasts auto-dismiss ---------- */
  $$("[data-toast]").forEach(function (t) { setTimeout(function () { t.style.transition = "opacity .5s"; t.style.opacity = "0"; setTimeout(function () { t.remove(); }, 600); }, 6500); });
})();
