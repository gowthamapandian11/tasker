/**
 * main.js — Task Tracker client-side scripts
 *
 * Features:
 *  1. Auto-dismiss flash messages after 4 seconds
 *  2. Confirm dialog before deleting a task or member
 *  3. Highlight the active navigation link based on current URL
 *  4. Animate dashboard stat cards on load
 */

document.addEventListener("DOMContentLoaded", function () {

  // ── 1. Auto-dismiss flash messages ──────────────────────────────────────
  const flashes = document.querySelectorAll(".flash");
  flashes.forEach(function (flash) {
    setTimeout(function () {
      flash.style.transition = "opacity 0.5s ease, transform 0.5s ease";
      flash.style.opacity    = "0";
      flash.style.transform  = "translateX(120%)";
      setTimeout(function () { flash.remove(); }, 500);
    }, 4000);
  });


  // ── 2. Confirm delete dialogs ────────────────────────────────────────────
  document.querySelectorAll("form[data-confirm]").forEach(function (form) {
    form.addEventListener("submit", function (e) {
      const message = form.getAttribute("data-confirm") || "Are you sure?";
      if (!confirm(message)) {
        e.preventDefault();
      }
    });
  });


  // ── 3. Active navigation link (managed server-side in base.html) ─────────



  // ── 4. Animate stat card values (count-up effect) ────────────────────────
  document.querySelectorAll(".stat-value[data-target]").forEach(function (el) {
    const target   = parseInt(el.getAttribute("data-target"), 10);
    const duration = 800; // ms
    const steps    = 30;
    const step     = Math.ceil(target / steps);
    let   current  = 0;

    const interval = setInterval(function () {
      current = Math.min(current + step, target);
      el.textContent = current;
      if (current >= target) clearInterval(interval);
    }, duration / steps);
  });

});
