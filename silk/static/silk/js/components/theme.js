(function () {
  'use strict';

  var STORAGE_KEY = 'silk-theme';
  var ROOT_ID     = 'silk-root';

  var SCHEMES = [
    { value: 'light',         label: 'Light',         icon: 'sun' },
    { value: 'dark',          label: 'Dark',           icon: 'moon' },
    { value: 'midnight',      label: 'Midnight',       icon: 'moon-star' },
    { value: 'high-contrast', label: 'High Contrast',  icon: 'contrast' },
  ];

  /* ─── Core helpers ───────────────────────────────────────────── */

  function applyScheme(scheme) {
    var root = document.getElementById(ROOT_ID);
    if (root) root.setAttribute('data-theme', scheme);
  }

  function getSaved() {
    try {
      var v = localStorage.getItem(STORAGE_KEY);
      // backward-compat: old 'dark'/'light' strings are valid scheme values
      return v || 'light';
    } catch (e) { return 'light'; }
  }

  function save(scheme) {
    try { localStorage.setItem(STORAGE_KEY, scheme); } catch (e) {}
  }

  function getActive() {
    var root = document.getElementById(ROOT_ID);
    return root ? root.getAttribute('data-theme') || 'light' : 'light';
  }

  /* ─── Nav picker UI ─────────────────────────────────────────── */

  function updatePickerLabel(scheme) {
    var meta = SCHEMES.find(function (s) { return s.value === scheme; })
            || SCHEMES[0];
    var label = document.getElementById('silk-scheme-label');
    var icon  = document.getElementById('silk-scheme-icon');
    if (label) label.textContent = meta.label;
    if (icon) {
      icon.setAttribute('data-lucide', meta.icon);
      if (window.lucide) lucide.createIcons();
    }
    // Mark active option in dropdown
    document.querySelectorAll('.silk-scheme-option').forEach(function (btn) {
      btn.classList.toggle('is-active', btn.dataset.scheme === scheme);
    });
  }

  function openPicker() {
    var menu = document.getElementById('silk-scheme-menu');
    var btn  = document.getElementById('silk-scheme-btn');
    if (!menu) return;
    menu.removeAttribute('hidden');
    if (btn) btn.setAttribute('aria-expanded', 'true');
  }

  function closePicker() {
    var menu = document.getElementById('silk-scheme-menu');
    var btn  = document.getElementById('silk-scheme-btn');
    if (!menu) return;
    menu.setAttribute('hidden', '');
    if (btn) btn.setAttribute('aria-expanded', 'false');
  }

  function isPickerOpen() {
    var menu = document.getElementById('silk-scheme-menu');
    return menu && !menu.hasAttribute('hidden');
  }

  /* ─── Apply saved theme immediately (before paint) ──────────── */
  applyScheme(getSaved());

  /* ─── DOMContentLoaded init ─────────────────────────────────── */
  document.addEventListener('DOMContentLoaded', function () {
    var saved = getSaved();
    applyScheme(saved);
    updatePickerLabel(saved);

    // Toggle open/close on picker button
    var btn = document.getElementById('silk-scheme-btn');
    if (btn) {
      btn.addEventListener('click', function (e) {
        e.stopPropagation();
        isPickerOpen() ? closePicker() : openPicker();
      });
    }

    // Select scheme from dropdown
    document.querySelectorAll('.silk-scheme-option').forEach(function (opt) {
      opt.addEventListener('click', function () {
        var scheme = this.dataset.scheme;
        applyScheme(scheme);
        save(scheme);
        updatePickerLabel(scheme);
        closePicker();
        document.dispatchEvent(new CustomEvent('silk-scheme-changed', { detail: scheme }));
      });
    });

    // Close on outside click
    document.addEventListener('click', function (e) {
      var picker = document.getElementById('silk-scheme-picker');
      if (picker && !picker.contains(e.target)) closePicker();
    });

    if (window.lucide) lucide.createIcons();
  });

  /* ─── Expose for settings page ─────────────────────────────── */
  window.silkApplyScheme = function (scheme) {
    applyScheme(scheme);
    save(scheme);
    updatePickerLabel(scheme);
    document.dispatchEvent(new CustomEvent('silk-scheme-changed', { detail: scheme }));
  };

  window.silkGetActiveScheme = getActive;
  window.silkSchemes = SCHEMES;

}());