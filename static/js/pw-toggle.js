/* Adds a show/hide (eye) button to every password field. Self-contained: injects its own styles. */
(function () {
  "use strict";
  var css = ".ob-pw{position:relative;display:block;width:100%}.ob-pw>input{width:100%;padding-right:50px!important;box-sizing:border-box}" +
    ".ob-pw>.ob-pw-btn{position:absolute!important;top:50%!important;right:10px!important;left:auto!important;transform:translateY(-50%)!important;width:34px!important;height:34px!important;min-width:0!important;margin:0!important;padding:0!important;border:0!important;border-radius:50%!important;background:transparent!important;box-shadow:none!important;color:inherit!important;opacity:.62;cursor:pointer;display:grid!important;place-items:center;transition:opacity .2s,background .2s}" +
    ".ob-pw>.ob-pw-btn:hover,.ob-pw>.ob-pw-btn:focus-visible{opacity:1;background:rgba(127,127,127,.22)!important;outline:0}.ob-pw-btn svg{width:20px;height:20px;fill:none;stroke:currentColor;stroke-width:1.8;stroke-linecap:round;stroke-linejoin:round;pointer-events:none;display:block;flex:none}" +
    ".ob-pw-btn .off{display:none}.ob-pw-btn[aria-pressed=true] .on{display:none}.ob-pw-btn[aria-pressed=true] .off{display:block}";
  var st = document.createElement("style"); st.textContent = css; document.head.appendChild(st);
  var EYE = '<svg class="on" viewBox="0 0 24 24" aria-hidden="true"><path d="M2 12s3.6-7 10-7 10 7 10 7-3.6 7-10 7S2 12 2 12z"/><circle cx="12" cy="12" r="3"/></svg>' +
            '<svg class="off" viewBox="0 0 24 24" aria-hidden="true"><path d="M3 3l18 18"/><path d="M10.6 5.1A10.7 10.7 0 0 1 12 5c6.4 0 10 7 10 7a17.6 17.6 0 0 1-3.2 4.2M6.6 6.7C3.7 8.6 2 12 2 12s3.6 7 10 7c1.7 0 3.2-.4 4.5-1"/><path d="M9.9 9.9a3 3 0 0 0 4.2 4.2"/></svg>';
  function enhance(input) {
    if (input.getAttribute("data-pw")) return; input.setAttribute("data-pw", "1");
    var wrap = document.createElement("span"); wrap.className = "ob-pw";
    input.parentNode.insertBefore(wrap, input); wrap.appendChild(input);
    var b = document.createElement("button"); b.type = "button"; b.className = "ob-pw-btn"; b.setAttribute("aria-label", "Show password"); b.setAttribute("aria-pressed", "false"); b.innerHTML = EYE;
    b.addEventListener("click", function () {
      var show = input.type === "password", s = input.selectionStart, e = input.selectionEnd;
      input.type = show ? "text" : "password"; b.setAttribute("aria-pressed", show ? "true" : "false"); b.setAttribute("aria-label", show ? "Hide password" : "Show password");
      input.focus(); try { input.setSelectionRange(s, e); } catch (x) {}
    });
    wrap.appendChild(b);
    var form = input.form; if (form) form.addEventListener("submit", function () { if (input.type === "text" && input.getAttribute("data-pw")) { /* leave as typed */ } });
  }
  function run() { Array.prototype.forEach.call(document.querySelectorAll("input[type=password]"), enhance); }
  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", run); else run();
  if ("MutationObserver" in window) new MutationObserver(run).observe(document.documentElement, { childList: true, subtree: true });
})();
