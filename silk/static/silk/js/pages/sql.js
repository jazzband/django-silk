$(document).ready(function () {
  document.querySelectorAll(".data-row").forEach((rowElement) => {
    let sqlDetailUrl = rowElement.dataset.sqlDetailUrl;
    rowElement.addEventListener("click", (e) => {
      switch (e.button) {
        case 0:
          window.location = sqlDetailUrl;
          break;
        case 1:
          window.open(sqlDetailUrl);
          break;
        default:
          break;
      }
    });
  });
});

// N+1 pattern expand / collapse
document.addEventListener('DOMContentLoaded', function () {
  document.querySelectorAll('.silk-n1-row').forEach(function (btn) {
    btn.addEventListener('click', function () {
      var pattern = this.closest('.silk-n1-pattern');
      var body = pattern.querySelector('.silk-n1-body');
      var expanded = this.getAttribute('aria-expanded') === 'true';

      if (expanded) {
        body.hidden = true;
        this.setAttribute('aria-expanded', 'false');
      } else {
        body.hidden = false;
        this.setAttribute('aria-expanded', 'true');
        // Syntax-highlight on first open
        var code = body.querySelector('code:not(.hljs)');
        if (code && window.hljs) {
          hljs.highlightElement(code);
        }
      }

      // Flip chevron
      var chevron = this.querySelector('[data-lucide]');
      if (chevron) {
        chevron.setAttribute('data-lucide', expanded ? 'chevron-down' : 'chevron-up');
        if (window.lucide) lucide.createIcons();
      }
    });
  });
});
