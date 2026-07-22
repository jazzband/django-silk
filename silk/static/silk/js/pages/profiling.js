(function () {
  'use strict';

  /* ─── Filter bar toggle ──────────────────────────────────────── */

  function silkFilterToggle() {
    var bar = document.getElementById('silk-filter-bar');
    var btn = document.getElementById('silk-filter-toggle');
    if (!bar) return;
    var isHidden = bar.hasAttribute('hidden');
    if (isHidden) {
      bar.removeAttribute('hidden');
      if (btn) btn.setAttribute('aria-expanded', 'true');
      try { localStorage.setItem('silk-profiling-filter-open', '1'); } catch (e) {}
    } else {
      bar.setAttribute('hidden', '');
      if (btn) btn.setAttribute('aria-expanded', 'false');
      try { localStorage.setItem('silk-profiling-filter-open', '0'); } catch (e) {}
    }
  }

  /* ─── Time preset ────────────────────────────────────────────── */

  function silkFilterPreset(key) {
    var input = document.getElementById('silk-time-preset-val');
    if (input) {
      input.value = key;
    }
    document.querySelectorAll('.silk-preset-btn').forEach(function (btn) {
      btn.classList.remove('silk-preset-btn--active');
    });
    if (event && event.target) {
      event.target.classList.add('silk-preset-btn--active');
    }
  }

  /* ─── Expose globals ─────────────────────────────────────────── */

  window.silkFilterToggle = silkFilterToggle;
  window.silkFilterPreset = silkFilterPreset;

  /* ─── Init ───────────────────────────────────────────────────── */

  document.addEventListener('DOMContentLoaded', function () {
    if (window.lucide) {
      lucide.createIcons();
    }

    // Restore filter bar open/closed state
    try {
      if (localStorage.getItem('silk-profiling-filter-open') === '1') {
        var bar = document.getElementById('silk-filter-bar');
        var btn = document.getElementById('silk-filter-toggle');
        if (bar) {
          bar.removeAttribute('hidden');
          if (btn) btn.setAttribute('aria-expanded', 'true');
        }
      }
    } catch (e) {}

    // Reflect current per_page (show) in browser URL for shareability.
    try {
      var perPageSelect = document.querySelector('select[name="show"]');
      if (perPageSelect && perPageSelect.value) {
        var params = new URLSearchParams(window.location.search);
        params.set('show', perPageSelect.value);
        history.replaceState(null, '', window.location.pathname + '?' + params.toString());
      }
    } catch (e) {}
  });

}());
