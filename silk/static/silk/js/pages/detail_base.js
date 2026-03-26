document.addEventListener('DOMContentLoaded', function () {
  // Highlight all pre>code blocks
  hljs.highlightAll();

  // Post-process: wrap each line in a span and mark active lines
  document.querySelectorAll('pre[data-active-indices]').forEach(function (pre) {
    var code = pre.querySelector('code');
    if (!code) return;
    var activeIndices;
    try { activeIndices = new Set(JSON.parse(pre.dataset.activeIndices)); } catch (e) { return; }
    if (!activeIndices.size) return;

    var lines = code.innerHTML.split('\n');
    code.innerHTML = lines.map(function (line, i) {
      var cls = activeIndices.has(i) ? ' the-line' : '';
      return '<span class="silk-code-line' + cls + '">' + line + '</span>';
    }).join(''); // no \n joiner — pre preserves whitespace so \n would add blank lines
  });
});