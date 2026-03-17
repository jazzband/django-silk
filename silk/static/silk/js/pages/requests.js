(function () {
  'use strict';

  /* ─── Filter bar toggle ─────────────────────────────────────── */

  function silkFilterToggle() {
    var bar = document.getElementById('silk-filter-bar');
    var btn = document.getElementById('silk-filter-toggle');
    if (!bar) return;
    var isHidden = bar.hasAttribute('hidden');
    if (isHidden) {
      bar.removeAttribute('hidden');
      if (btn) btn.setAttribute('aria-expanded', 'true');
      try { localStorage.setItem('silk-filter-open', '1'); } catch (e) {}
    } else {
      bar.setAttribute('hidden', '');
      if (btn) btn.setAttribute('aria-expanded', 'false');
      try { localStorage.setItem('silk-filter-open', '0'); } catch (e) {}
    }
  }

  /* ─── Time preset ───────────────────────────────────────────── */

  function silkSetSeconds(btn, seconds) {
    var input = document.getElementById('silk-seconds-val');
    if (input) input.value = seconds;
    document.querySelectorAll('.silk-preset-btn').forEach(function (b) {
      b.classList.remove('silk-preset-btn--active');
    });
    if (btn) btn.classList.add('silk-preset-btn--active');
    silkMarkFilterDirty();
  }

  // kept for any legacy references
  function silkFilterPreset(key) {
    silkSetSeconds(null, key);
  }

  /* ─── Method toggle (multi-select) ──────────────────────────── */

  function silkMethodInit() {
    var input = document.getElementById('silk-method-value');
    if (!input) return;
    var value = input.value;
    var selected = [];
    if (value) {
      try {
        var parsed = JSON.parse(value);
        if (Array.isArray(parsed)) {
          selected = parsed.map(function (m) { return m.toUpperCase(); });
        } else if (parsed) {
          selected = [String(parsed).toUpperCase()];
        }
      } catch (e) {
        if (value.trim()) selected = [value.trim().toUpperCase()];
      }
    }
    document.querySelectorAll('.silk-method-btn').forEach(function (btn) {
      var m = (btn.dataset.method || btn.textContent.trim()).toUpperCase();
      btn.classList.toggle('silk-method-btn--active', selected.indexOf(m) !== -1);
    });
  }

  function silkFilterMethod(btn) {
    var input = document.getElementById('silk-method-value');
    btn.classList.toggle('silk-method-btn--active');
    var active = [];
    document.querySelectorAll('.silk-method-btn--active').forEach(function (b) {
      active.push(b.dataset.method || b.textContent.trim());
    });
    if (input) input.value = active.length ? JSON.stringify(active) : '';
    silkMarkFilterDirty();
  }

  /* ─── Dirty state indicator ─────────────────────────────────── */

  function silkMarkFilterDirty() {
    var indicator = document.getElementById('silk-filter-dirty-indicator');
    if (indicator) indicator.classList.add('is-visible');
  }

  /* ─── Custom multi-select ───────────────────────────────────── */

  function silkMsInit(id) {
    var container = document.getElementById(id);
    if (!container) return;
    var hiddenId = container.dataset.hiddenId;
    var hiddenInput = hiddenId ? document.getElementById(hiddenId) : null;
    if (!hiddenInput) return;

    var value = hiddenInput.value;
    var selected = [];
    if (value) {
      try {
        var parsed = JSON.parse(value);
        if (Array.isArray(parsed)) {
          selected = parsed.map(String);
        } else if (parsed) {
          selected = [String(parsed)];
        }
      } catch (e) {
        if (value.trim()) selected = [value.trim()];
      }
    }

    container.querySelectorAll('.silk-ms__option-cb').forEach(function (cb) {
      cb.checked = selected.indexOf(cb.value) !== -1;
    });

    silkMsUpdateDisplay(id);
  }

  function silkMsToggle(id) {
    var container = document.getElementById(id);
    if (!container) return;
    var panel = container.querySelector('.silk-ms__panel');
    if (!panel) return;

    var isHidden = panel.hasAttribute('hidden');

    // Close all open panels first
    document.querySelectorAll('.silk-ms').forEach(function (ms) {
      var p = ms.querySelector('.silk-ms__panel');
      if (p) p.setAttribute('hidden', '');
      ms.classList.remove('is-open');
      var t = ms.querySelector('.silk-ms__trigger');
      if (t) t.setAttribute('aria-expanded', 'false');
    });

    if (isHidden) {
      panel.removeAttribute('hidden');
      container.classList.add('is-open');
      var trigger = container.querySelector('.silk-ms__trigger');
      if (trigger) trigger.setAttribute('aria-expanded', 'true');
      // Auto-focus the search input if present
      var searchInput = panel.querySelector('.silk-ms__search-input');
      if (searchInput) {
        setTimeout(function () { searchInput.focus(); }, 30);
      }
    }
  }

  function silkMsChange(id) {
    silkMsUpdateDisplay(id);
    silkMarkFilterDirty();
  }

  function silkMsUpdateDisplay(id) {
    var container = document.getElementById(id);
    if (!container) return;
    var hiddenId = container.dataset.hiddenId;
    var hiddenInput = hiddenId ? document.getElementById(hiddenId) : null;
    var displayEl = container.querySelector('.silk-ms__display');
    var trigger = container.querySelector('.silk-ms__trigger');

    var checked = [];
    container.querySelectorAll('.silk-ms__option-cb:checked').forEach(function (cb) {
      checked.push(cb.value);
    });

    if (hiddenInput) {
      hiddenInput.value = checked.length ? JSON.stringify(checked) : '';
    }

    if (displayEl) {
      if (checked.length === 0) {
        displayEl.textContent = 'Any';
      } else if (checked.length === 1) {
        displayEl.textContent = checked[0];
      } else {
        displayEl.textContent = checked.length + ' selected';
      }
    }

    if (trigger) {
      if (checked.length > 0) {
        trigger.classList.add('silk-ms__trigger--active');
      } else {
        trigger.classList.remove('silk-ms__trigger--active');
      }
    }
  }

  function silkMsSearch(id, query) {
    var container = document.getElementById(id);
    if (!container) return;
    var q = query.toLowerCase().trim();
    container.querySelectorAll('.silk-ms__option').forEach(function (opt) {
      var val = (opt.dataset.value || '').toLowerCase();
      var label = opt.querySelector('.silk-ms__option-label');
      var text = label ? label.textContent.toLowerCase() : val;
      if (q === '' || text.indexOf(q) !== -1 || val.indexOf(q) !== -1) {
        opt.removeAttribute('hidden');
      } else {
        opt.setAttribute('hidden', '');
      }
    });
  }

  function silkMsClear(id) {
    var container = document.getElementById(id);
    if (!container) return;
    container.querySelectorAll('.silk-ms__option-cb').forEach(function (cb) {
      cb.checked = false;
    });
    var searchInput = container.querySelector('.silk-ms__search-input');
    if (searchInput) {
      searchInput.value = '';
      silkMsSearch(id, '');
    }
    silkMsUpdateDisplay(id);
    silkMarkFilterDirty();
  }

  /* ─── Sort chips ────────────────────────────────────────────── */

  function _getSortList() {
    var input = document.getElementById('silk-sort-criteria');
    if (!input) return [];
    try {
      return JSON.parse(input.value) || [];
    } catch (e) {
      return [];
    }
  }

  function _setSortList(list) {
    var input = document.getElementById('silk-sort-criteria');
    if (input) input.value = JSON.stringify(list);
  }

  function _submitSortForm() {
    var form = document.getElementById('silk-sort-form');
    if (form) form.submit();
  }

  function silkSortToggleDir(btn) {
    var chip = btn.closest('.silk-sort-chip');
    if (!chip) return;
    var field = chip.dataset.field;
    var list = _getSortList();
    list = list.map(function (item) {
      if (item.field === field) {
        return { field: field, dir: item.dir === 'DESC' ? 'ASC' : 'DESC' };
      }
      return item;
    });
    _setSortList(list);
    _submitSortForm();
  }

  function silkSortRemove(btn) {
    var chip = btn.closest('.silk-sort-chip');
    if (!chip) return;
    var field = chip.dataset.field;
    var list = _getSortList().filter(function (item) {
      return item.field !== field;
    });
    _setSortList(list);
    _submitSortForm();
  }

  function silkSortToggleMenu(event) {
    event.stopPropagation();
    var menu = document.getElementById('silk-sort-menu');
    var addBtn = document.getElementById('silk-sort-add-btn');
    if (!menu) return;
    var hidden = menu.hasAttribute('hidden');
    if (hidden) {
      menu.removeAttribute('hidden');
      if (addBtn) addBtn.setAttribute('aria-expanded', 'true');
    } else {
      menu.setAttribute('hidden', '');
      if (addBtn) addBtn.setAttribute('aria-expanded', 'false');
    }
  }

  function silkSortAdd(field, label) {
    var list = _getSortList();
    var exists = list.some(function (item) { return item.field === field; });
    if (!exists) {
      list.push({ field: field, dir: 'DESC' });
      _setSortList(list);
      _submitSortForm();
    }
    var menu = document.getElementById('silk-sort-menu');
    if (menu) menu.setAttribute('hidden', '');
  }

  /* ─── Close menus on outside click ──────────────────────────── */

  document.addEventListener('click', function (e) {
    // Sort menu
    var menu = document.getElementById('silk-sort-menu');
    var addWrapper = document.getElementById('silk-sort-add-wrapper');
    if (menu && !menu.hasAttribute('hidden') && addWrapper && !addWrapper.contains(e.target)) {
      menu.setAttribute('hidden', '');
      var addBtn = document.getElementById('silk-sort-add-btn');
      if (addBtn) addBtn.setAttribute('aria-expanded', 'false');
    }

    // Multi-select panels — close if click is outside any .silk-ms
    var clickedMs = e.target.closest('.silk-ms');
    document.querySelectorAll('.silk-ms').forEach(function (ms) {
      if (ms === clickedMs) return;
      var panel = ms.querySelector('.silk-ms__panel');
      if (panel && !panel.hasAttribute('hidden')) {
        panel.setAttribute('hidden', '');
        ms.classList.remove('is-open');
        var t = ms.querySelector('.silk-ms__trigger');
        if (t) t.setAttribute('aria-expanded', 'false');
      }
    });
  });

  /* ─── Expose helpers to window for inline onclick attributes ── */

  window.silkFilterToggle = silkFilterToggle;
  window.silkSetSeconds = silkSetSeconds;
  window.silkFilterPreset = silkFilterPreset;
  window.silkMethodInit = silkMethodInit;
  window.silkFilterMethod = silkFilterMethod;
  window.silkMarkFilterDirty = silkMarkFilterDirty;
  window.silkMsToggle = silkMsToggle;
  window.silkMsChange = silkMsChange;
  window.silkMsSearch = silkMsSearch;
  window.silkMsClear = silkMsClear;
  window.silkSortToggleDir = silkSortToggleDir;
  window.silkSortRemove = silkSortRemove;
  window.silkSortToggleMenu = silkSortToggleMenu;
  window.silkSortAdd = silkSortAdd;

  /* ─── Init ──────────────────────────────────────────────────── */

  document.addEventListener('DOMContentLoaded', function () {
    if (window.lucide) {
      lucide.createIcons();
    }

    // Restore filter bar open/closed state
    try {
      if (localStorage.getItem('silk-filter-open') === '1') {
        var bar = document.getElementById('silk-filter-bar');
        var btn = document.getElementById('silk-filter-toggle');
        if (bar) {
          bar.removeAttribute('hidden');
          if (btn) btn.setAttribute('aria-expanded', 'true');
        }
      }
    } catch (e) {}

    // Init multi-selects and method buttons from session values
    silkMethodInit();
    silkMsInit('silk-status-ms');
    silkMsInit('silk-path-ms');

    // Mark dirty on number/text input changes within the filter bar
    var filterBar = document.getElementById('silk-filter-bar');
    if (filterBar) {
      filterBar.addEventListener('input', function (e) {
        var t = e.target;
        if (t.type === 'number' || (t.type === 'text' && !t.classList.contains('silk-ms__search-input'))) {
          silkMarkFilterDirty();
        }
      });
    }

    // Clear dirty indicator when filter form is submitted
    var filterForm = document.getElementById('silk-filter-form');
    if (filterForm) {
      filterForm.addEventListener('submit', function () {
        var indicator = document.getElementById('silk-filter-dirty-indicator');
        if (indicator) indicator.classList.remove('is-visible');
      });
    }

    // Reflect current sort + per_page in URL for shareability
    try {
      var sortInput = document.getElementById('silk-sort-criteria');
      var perPageSelect = document.querySelector('select[name="per_page"]');
      if (sortInput || perPageSelect) {
        var params = new URLSearchParams(window.location.search);
        if (sortInput && sortInput.value) {
          params.set('sort_criteria', sortInput.value);
        }
        if (perPageSelect && perPageSelect.value) {
          params.set('per_page', perPageSelect.value);
        }
        var newUrl = window.location.pathname + '?' + params.toString();
        history.replaceState(null, '', newUrl);
      }
    } catch (e) {}
  });

}());