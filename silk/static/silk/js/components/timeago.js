(function () {
  'use strict';

  /**
   * Convert an ISO datetime string to a human-readable relative label.
   * Examples: "just now", "45s ago", "3m ago", "2h ago", "4d ago", "Feb 18"
   */
  function timeAgo(isoString) {
    var date = new Date(isoString);
    if (isNaN(date.getTime())) return null;

    var now = Date.now();
    var diffMs = now - date.getTime();
    var diffSec = Math.floor(diffMs / 1000);

    if (diffSec < 5)   return 'just now';
    if (diffSec < 60)  return diffSec + 's ago';

    var diffMin = Math.floor(diffSec / 60);
    if (diffMin < 60)  return diffMin + 'm ago';

    var diffHr = Math.floor(diffMin / 60);
    if (diffHr < 24)   return diffHr + 'h ago';

    var diffDays = Math.floor(diffHr / 24);
    if (diffDays < 7)  return diffDays + 'd ago';
    if (diffDays < 30) return Math.floor(diffDays / 7) + 'w ago';

    // Older than a month — show short date
    var months = ['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'];
    var label = months[date.getMonth()] + ' ' + date.getDate();
    // Include year if it's not this year
    if (date.getFullYear() !== new Date().getFullYear()) {
      label += ' ' + date.getFullYear();
    }
    return label;
  }

  /**
   * Format an ISO datetime string into a full, readable absolute string
   * used for the title tooltip.
   * Example: "Tue, 18 Feb 2026, 10:14:58"
   */
  function formatAbsolute(isoString) {
    var date = new Date(isoString);
    if (isNaN(date.getTime())) return isoString;
    return date.toLocaleString(undefined, {
      weekday: 'short',
      day: 'numeric',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    });
  }

  /**
   * Find every [data-time] element and:
   *  - set its text content to the relative label
   *  - set its title to the full absolute datetime
   *  - keep the original ISO value in data-time so it stays parseable
   */
  function applyTimeAgo() {
    document.querySelectorAll('[data-time]').forEach(function (el) {
      var iso = el.getAttribute('data-time');
      if (!iso) return;
      var relative = timeAgo(iso);
      if (relative) {
        el.textContent = relative;
      }
      el.setAttribute('title', formatAbsolute(iso));
    });
  }

  document.addEventListener('DOMContentLoaded', applyTimeAgo);
}());
