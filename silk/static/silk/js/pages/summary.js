(function () {
  'use strict';

  /* ── CSS variable reader ──────────────────────────────────── */
  /* Must read from #silk-root — that's where data-theme is set  */
  function css(v) {
    var root = document.getElementById('silk-root') || document.documentElement;
    return getComputedStyle(root).getPropertyValue(v).trim();
  }

  /* ── Shared floating tooltip ─────────────────────────────── */
  var _tip = null;
  function getTip() {
    if (!_tip) {
      _tip = d3.select('body').append('div').attr('class', 'silk-d3-tip');
    }
    return _tip;
  }
  function tipShow(evt, html) {
    getTip().style('opacity', 1).html(html)
      .style('left', (evt.pageX + 14) + 'px')
      .style('top',  (evt.pageY - 36) + 'px');
  }
  function tipHide() { getTip().style('opacity', 0); }

  /* ── Performance color by ms value ──────────────────────── */
  function perfColor(ms) {
    if (ms >= 1000) return css('--silk-perf-very-bad');
    if (ms >= 500)  return css('--silk-perf-bad');
    if (ms >= 200)  return css('--silk-perf-ok');
    if (ms >= 100)  return css('--silk-perf-good');
    return css('--silk-perf-very-good');
  }

  /* ── SVG setup helper ────────────────────────────────────── */
  function setupSvg(el, margin, fixedHeight) {
    var parentW = el.parentElement
      ? el.parentElement.getBoundingClientRect().width
      : 400;
    var w = Math.max(parentW - margin.left - margin.right, 80);
    var h = fixedHeight - margin.top - margin.bottom;
    d3.select(el)
      .attr('width',  parentW)
      .attr('height', fixedHeight);
    return { w: w, h: h };
  }

  /* ── Empty state helper ──────────────────────────────────── */
  function emptyState(el, msg, height) {
    d3.select(el)
      .attr('width', '100%')
      .attr('height', height || 80);
    d3.select(el).append('text')
      .attr('x', '50%').attr('y', '50%')
      .attr('text-anchor', 'middle')
      .attr('dominant-baseline', 'middle')
      .attr('fill', css('--silk-text-muted'))
      .attr('font-size', '12px')
      .text(msg || 'No data');
  }

  /* ════════════════════════════════════════════════════════════
     Chart 1 — Request Activity (area + line + dots)
     ════════════════════════════════════════════════════════════ */
  function renderActivity(el, timeline) {
    d3.select(el).selectAll('*').remove();
    if (!timeline || timeline.length === 0) { emptyState(el, 'No request data', 140); return; }

    var m = { top: 20, right: 20, bottom: 36, left: 42 };
    var d = setupSvg(el, m, 160);
    var g = d3.select(el).append('g')
      .attr('transform', 'translate(' + m.left + ',' + m.top + ')');

    var parse = d3.isoParse;
    var data = timeline.map(function (r) { return { t: parse(r.t), n: r.count }; })
      .filter(function (r) { return r.t; });
    if (data.length === 0) { emptyState(el, 'No data', 140); return; }

    var accent     = css('--silk-chart-accent')  || '#4f46e5';
    var gridColor  = css('--silk-border');
    var textColor  = css('--silk-text-secondary');
    var surfColor  = css('--silk-surface');

    /* expand domain when only 1 data point so the scale isn't degenerate */
    var ext = d3.extent(data, function (r) { return r.t; });
    if (ext[0].getTime() === ext[1].getTime()) {
      var pad = 3600000; // ± 1 h
      ext = [new Date(ext[0].getTime() - pad), new Date(ext[1].getTime() + pad)];
    }
    var xSc = d3.scaleTime().domain(ext).range([0, d.w]);
    var yMax = d3.max(data, function (r) { return r.n; }) || 1;
    var ySc = d3.scaleLinear().domain([0, yMax * 1.25]).range([d.h, 0]);

    /* gradient fill */
    var defs   = d3.select(el).append('defs');
    var fillId = 'act-fill-' + el.id;
    var lg = defs.append('linearGradient').attr('id', fillId)
      .attr('x1', '0%').attr('x2', '0%').attr('y1', '0%').attr('y2', '100%');
    lg.append('stop').attr('offset', '0%').attr('stop-color', accent).attr('stop-opacity', '0.35');
    lg.append('stop').attr('offset', '100%').attr('stop-color', accent).attr('stop-opacity', '0.02');

    /* grid */
    g.append('g')
      .call(d3.axisLeft(ySc).ticks(3).tickSize(-d.w).tickFormat(''))
      .call(function (a) {
        a.select('.domain').remove();
        a.selectAll('line').attr('stroke', gridColor).attr('stroke-dasharray', '3,3').attr('opacity', 0.5);
      });

    /* axes */
    var axC = css('--silk-border');
    g.append('g')
      .call(d3.axisLeft(ySc).ticks(3).tickFormat(d3.format('d')))
      .call(function (a) {
        a.select('.domain').attr('stroke', axC);
        a.selectAll('text').attr('fill', textColor).attr('font-size', '11px');
        a.selectAll('line').attr('stroke', axC);
      });
    g.append('g').attr('transform', 'translate(0,' + d.h + ')')
      .call(d3.axisBottom(xSc).ticks(6))
      .call(function (a) {
        a.select('.domain').attr('stroke', axC);
        a.selectAll('text').attr('fill', textColor).attr('font-size', '11px');
        a.selectAll('line').attr('stroke', axC);
      });

    /* area + line */
    var area = d3.area()
      .x(function (r) { return xSc(r.t); }).y0(d.h).y1(function (r) { return ySc(r.n); })
      .curve(d3.curveMonotoneX);
    var line = d3.line()
      .x(function (r) { return xSc(r.t); }).y(function (r) { return ySc(r.n); })
      .curve(d3.curveMonotoneX);

    g.append('path').datum(data).attr('fill', 'url(#' + fillId + ')').attr('d', area);
    g.append('path').datum(data).attr('fill', 'none').attr('stroke', accent)
      .attr('stroke-width', 2).attr('d', line);

    /* dots */
    var dotR = data.length > 30 ? 2.5 : 4;
    g.selectAll('.act-dot').data(data).enter().append('circle')
      .attr('cx', function (r) { return xSc(r.t); })
      .attr('cy', function (r) { return ySc(r.n); })
      .attr('r', dotR).attr('fill', accent).attr('stroke', surfColor).attr('stroke-width', 1.5)
      .on('mouseover', function (evt, r) {
        tipShow(evt, '<strong>' + r.n + '</strong> request' + (r.n !== 1 ? 's' : '')
          + '<br><span style="opacity:.7">' + r.t.toLocaleString() + '</span>');
      })
      .on('mouseout', tipHide);
  }

  /* ════════════════════════════════════════════════════════════
     Chart 2 — Status code donut
     ════════════════════════════════════════════════════════════ */
  function renderStatusDonut(el, status) {
    d3.select(el).selectAll('*').remove();
    var total = Object.values(status).reduce(function (a, b) { return a + b; }, 0);

    var statusColors = {
      '2xx': css('--silk-chart-2xx') || '#10b981',
      '3xx': css('--silk-chart-3xx') || '#3b82f6',
      '4xx': css('--silk-chart-4xx') || '#f59e0b',
      '5xx': css('--silk-chart-5xx') || '#ef4444',
    };

    var pieData = Object.entries(status)
      .map(function (kv) { return { label: kv[0], count: kv[1], color: statusColors[kv[0]] }; });

    var parentW = el.parentElement ? el.parentElement.getBoundingClientRect().width : 260;
    var LEGEND_H = 28;
    var donutH   = 200;
    var totalH   = donutH + LEGEND_H;
    d3.select(el).attr('width', parentW).attr('height', totalH);

    /* donut group centred in the donut area */
    var g = d3.select(el).append('g')
      .attr('transform', 'translate(' + (parentW / 2) + ',' + (donutH / 2) + ')');

    if (total === 0) {
      g.append('text').attr('text-anchor', 'middle').attr('dominant-baseline', 'middle')
        .attr('fill', css('--silk-text-muted')).attr('font-size', '12px').text('No data');
      return;
    }

    var outerR    = Math.min(parentW / 2, donutH / 2) - 14;
    var innerR    = outerR * 0.58;
    var arc       = d3.arc().innerRadius(innerR).outerRadius(outerR);
    var arcHover  = d3.arc().innerRadius(innerR).outerRadius(outerR + 5);
    var pie       = d3.pie().value(function (d) { return d.count; }).sort(null).padAngle(0.03);
    var surfColor = css('--silk-surface');

    g.selectAll('.arc').data(pie(pieData)).enter().append('path')
      .attr('d', arc)
      .attr('fill', function (d) { return d.data.color; })
      .attr('stroke', surfColor).attr('stroke-width', 2)
      .on('mouseover', function (evt, d) {
        d3.select(this).attr('d', arcHover);
        var pct = total > 0 ? ((d.data.count / total) * 100).toFixed(1) : 0;
        tipShow(evt, '<strong>' + d.data.label + '</strong>: ' + d.data.count + ' (' + pct + '%)');
      })
      .on('mouseout', function (evt, d) { d3.select(this).attr('d', arc); tipHide(); });

    /* centre labels */
    g.append('text').attr('text-anchor', 'middle').attr('y', -6)
      .attr('font-size', '26px').attr('font-weight', '300')
      .attr('fill', css('--silk-text-primary')).text(total);
    g.append('text').attr('text-anchor', 'middle').attr('y', 14)
      .attr('font-size', '10px').attr('letter-spacing', '0.06em')
      .attr('fill', css('--silk-text-muted')).text('REQUESTS');

    /* legend row — rendered in absolute SVG coords below the donut area */
    var legG  = d3.select(el).append('g')
      .attr('transform', 'translate(0,' + donutH + ')');
    var keys  = Object.keys(status).filter(function (k) { return status[k] > 0; });
    var slotW = parentW / Math.max(keys.length, 1);
    keys.forEach(function (k, i) {
      var lx = i * slotW + slotW / 2;
      legG.append('rect').attr('x', lx - 18).attr('y', 8).attr('width', 8).attr('height', 8)
        .attr('fill', statusColors[k]).attr('rx', 2);
      legG.append('text').attr('x', lx - 7).attr('y', 15)
        .attr('font-size', '10px').attr('fill', css('--silk-text-secondary'))
        .attr('font-weight', '600').text(k);
    });
  }

  /* ════════════════════════════════════════════════════════════
     Chart 3 — HTTP Method horizontal lollipop
     ════════════════════════════════════════════════════════════ */
  function renderMethods(el, methods) {
    d3.select(el).selectAll('*').remove();
    if (!methods || methods.length === 0) { emptyState(el, 'No data', 120); return; }

    var methodColors = {
      'GET':    css('--silk-method-get')    || '#2a7a3a',
      'POST':   css('--silk-method-post')   || '#1a4a8a',
      'PUT':    css('--silk-method-put')    || '#8a5010',
      'PATCH':  css('--silk-method-patch')  || '#5a2080',
      'DELETE': css('--silk-method-delete') || '#8a1a1a',
    };

    var m  = { top: 14, right: 36, bottom: 14, left: 62 };
    var fh = m.top + m.bottom + methods.length * 36 + 10;
    var d  = setupSvg(el, m, fh);
    var g  = d3.select(el).append('g').attr('transform', 'translate(' + m.left + ',' + m.top + ')');

    var yMax = d3.max(methods, function (r) { return r.count; }) || 1;
    var xSc  = d3.scaleLinear().domain([0, yMax]).range([0, d.w]);
    var ySc  = d3.scaleBand().domain(methods.map(function (r) { return r.method; }))
      .range([0, d.h]).padding(0.4);

    var textColor = css('--silk-text-secondary');
    var axC       = css('--silk-border');

    /* grid */
    g.append('g')
      .call(d3.axisTop(xSc).ticks(4).tickSize(-d.h).tickFormat(''))
      .call(function (a) {
        a.select('.domain').remove();
        a.selectAll('line').attr('stroke', axC).attr('stroke-dasharray', '3,3').attr('opacity', 0.5);
      });

    /* lollipops */
    methods.forEach(function (row) {
      var color = methodColors[row.method] || textColor;
      var cy    = ySc(row.method) + ySc.bandwidth() / 2;
      var cx    = xSc(row.count);

      /* track */
      g.append('line')
        .attr('x1', 0).attr('y1', cy).attr('x2', cx).attr('y2', cy)
        .attr('stroke', color).attr('stroke-width', 2.5)
        .attr('stroke-linecap', 'round').attr('opacity', 0.55);

      /* dot */
      g.append('circle')
        .attr('cx', cx).attr('cy', cy).attr('r', 7).attr('fill', color)
        .attr('stroke', css('--silk-surface')).attr('stroke-width', 2)
        .on('mouseover', function (evt) {
          tipShow(evt, '<strong>' + row.method + '</strong>: ' + row.count);
          d3.select(this).attr('r', 9);
        })
        .on('mouseout', function () { d3.select(this).attr('r', 7); tipHide(); });

      /* count label */
      g.append('text')
        .attr('x', cx + 11).attr('y', cy)
        .attr('dominant-baseline', 'middle')
        .attr('font-size', '11px').attr('font-weight', '700')
        .attr('fill', color).text(row.count);
    });

    /* Y axis */
    g.append('g').call(d3.axisLeft(ySc).tickSize(0))
      .call(function (a) {
        a.select('.domain').remove();
        a.selectAll('text').attr('fill', textColor).attr('font-size', '12px').attr('font-weight', '600');
      });
  }

  /* ════════════════════════════════════════════════════════════
     Chart 4 — Response-time histogram (gradient bars)
     ════════════════════════════════════════════════════════════ */
  function renderRTHist(el, rtHist) {
    d3.select(el).selectAll('*').remove();
    if (!rtHist || rtHist.length === 0) { emptyState(el, 'No data', 200); return; }

    var bucketColors = [
      css('--silk-perf-very-good'),
      css('--silk-perf-good'),
      css('--silk-perf-ok'),
      css('--silk-perf-bad'),
      css('--silk-perf-very-bad'),
      css('--silk-perf-very-bad'),
    ];

    var m = { top: 20, right: 8, bottom: 52, left: 36 };
    var d = setupSvg(el, m, 200);
    var g = d3.select(el).append('g').attr('transform', 'translate(' + m.left + ',' + m.top + ')');

    var xSc = d3.scaleBand()
      .domain(rtHist.map(function (r) { return r.label; }))
      .range([0, d.w]).padding(0.22);
    var yMax = d3.max(rtHist, function (r) { return r.count; }) || 1;
    var ySc  = d3.scaleLinear().domain([0, yMax * 1.2]).range([d.h, 0]);

    var gridC = css('--silk-border');
    var axC   = css('--silk-border');
    var txtC  = css('--silk-text-secondary');

    g.append('g')
      .call(d3.axisLeft(ySc).ticks(4).tickSize(-d.w).tickFormat(''))
      .call(function (a) {
        a.select('.domain').remove();
        a.selectAll('line').attr('stroke', gridC).attr('stroke-dasharray', '3,3').attr('opacity', 0.5);
      });

    g.append('g')
      .call(d3.axisLeft(ySc).ticks(4).tickFormat(d3.format('d')))
      .call(function (a) {
        a.select('.domain').attr('stroke', axC);
        a.selectAll('text').attr('fill', txtC).attr('font-size', '11px');
        a.selectAll('line').attr('stroke', axC);
      });

    g.append('g').attr('transform', 'translate(0,' + d.h + ')')
      .call(d3.axisBottom(xSc).tickSize(0))
      .call(function (a) {
        a.select('.domain').attr('stroke', axC);
        a.selectAll('text').attr('fill', txtC).attr('font-size', '10px')
          .attr('transform', 'rotate(-35)').attr('text-anchor', 'end').attr('dy', '0.35em');
        a.selectAll('line').attr('stroke', axC);
      });

    rtHist.forEach(function (row, i) {
      var color = bucketColors[Math.min(i, bucketColors.length - 1)];
      var barH  = d.h - ySc(row.count);

      /* gradient def per bar */
      var defs  = d3.select(el).append('defs');
      var gId   = 'rt-bar-' + el.id + '-' + i;
      var bg = defs.append('linearGradient').attr('id', gId)
        .attr('x1', '0%').attr('x2', '0%').attr('y1', '0%').attr('y2', '100%');
      bg.append('stop').attr('offset', '0%').attr('stop-color', color).attr('stop-opacity', '1');
      bg.append('stop').attr('offset', '100%').attr('stop-color', color).attr('stop-opacity', '0.55');

      g.append('rect')
        .attr('x', xSc(row.label)).attr('y', ySc(row.count))
        .attr('width', xSc.bandwidth()).attr('height', Math.max(barH, 0))
        .attr('fill', 'url(#' + gId + ')').attr('rx', 4)
        .on('mouseover', function (evt) {
          tipShow(evt, '<strong>' + row.label + '</strong>: ' + row.count + ' request' + (row.count !== 1 ? 's' : ''));
          d3.select(this).attr('opacity', 0.8);
        })
        .on('mouseout', function () { d3.select(this).attr('opacity', 1); tipHide(); });

      /* value label on top of bar */
      if (row.count > 0) {
        g.append('text')
          .attr('x', xSc(row.label) + xSc.bandwidth() / 2)
          .attr('y', ySc(row.count) - 4)
          .attr('text-anchor', 'middle').attr('font-size', '10px')
          .attr('fill', color).attr('font-weight', '600').text(row.count);
      }
    });
  }

  /* ════════════════════════════════════════════════════════════
     Chart 5 — Latency percentile (gradient area + annotated dots)
     ════════════════════════════════════════════════════════════ */
  function renderPercentile(el, data) {
    d3.select(el).selectAll('*').remove();

    var PCT_KEYS = [25, 50, 75, 95, 99];
    var points = PCT_KEYS.map(function (p) {
      return { label: 'p' + p, val: data[String(p)] || 0 };
    });

    var allZero = points.every(function (p) { return p.val === 0; });

    var m  = { top: 28, right: 20, bottom: 36, left: 52 };
    var d  = setupSvg(el, m, 180);
    var g  = d3.select(el).append('g').attr('transform', 'translate(' + m.left + ',' + m.top + ')');

    var maxVal = allZero ? 1 : d3.max(points, function (p) { return p.val; });
    var xSc = d3.scalePoint().domain(points.map(function (p) { return p.label; })).range([0, d.w]).padding(0.3);
    var ySc = d3.scaleLinear().domain([0, maxVal * 1.35]).range([d.h, 0]);

    /* gradient defs */
    var defs = d3.select(el).append('defs');

    /* horizontal gradient for line */
    var lineGradId = 'pct-line-' + el.id;
    var lg = defs.append('linearGradient').attr('id', lineGradId)
      .attr('x1', '0%').attr('x2', '100%');
    lg.append('stop').attr('offset', '0%').attr('stop-color', css('--silk-perf-very-good'));
    lg.append('stop').attr('offset', '50%').attr('stop-color', css('--silk-perf-ok'));
    lg.append('stop').attr('offset', '100%').attr('stop-color', css('--silk-perf-very-bad'));

    /* vertical gradient for area fill */
    var areaGradId = 'pct-area-' + el.id;
    var ag = defs.append('linearGradient').attr('id', areaGradId)
      .attr('x1', '0%').attr('x2', '0%').attr('y1', '0%').attr('y2', '100%');
    ag.append('stop').attr('offset', '0%')
      .attr('stop-color', css('--silk-perf-ok')).attr('stop-opacity', '0.18');
    ag.append('stop').attr('offset', '100%')
      .attr('stop-color', css('--silk-perf-ok')).attr('stop-opacity', '0');

    var gridC = css('--silk-border');
    var axC   = css('--silk-border');
    var txtC  = css('--silk-text-secondary');
    var sfcC  = css('--silk-surface');

    /* grid */
    g.append('g')
      .call(d3.axisLeft(ySc).ticks(4).tickSize(-d.w).tickFormat(''))
      .call(function (a) {
        a.select('.domain').remove();
        a.selectAll('line').attr('stroke', gridC).attr('stroke-dasharray', '3,3').attr('opacity', 0.5);
      });

    /* Y axis */
    g.append('g')
      .call(d3.axisLeft(ySc).ticks(4).tickFormat(function (v) { return v + 'ms'; }))
      .call(function (a) {
        a.select('.domain').attr('stroke', axC);
        a.selectAll('text').attr('fill', txtC).attr('font-size', '11px');
        a.selectAll('line').attr('stroke', axC);
      });

    /* area */
    var area = d3.area()
      .x(function (p) { return xSc(p.label); }).y0(d.h).y1(function (p) { return ySc(p.val); })
      .curve(d3.curveCatmullRom.alpha(0.5));
    g.append('path').datum(points).attr('fill', 'url(#' + areaGradId + ')').attr('d', area);

    /* line */
    var line = d3.line()
      .x(function (p) { return xSc(p.label); }).y(function (p) { return ySc(p.val); })
      .curve(d3.curveCatmullRom.alpha(0.5));
    g.append('path').datum(points).attr('fill', 'none')
      .attr('stroke', 'url(#' + lineGradId + ')').attr('stroke-width', 2.5)
      .attr('stroke-linecap', 'round').attr('d', line);

    /* X axis */
    g.append('g').attr('transform', 'translate(0,' + d.h + ')')
      .call(d3.axisBottom(xSc))
      .call(function (a) {
        a.select('.domain').attr('stroke', axC);
        a.selectAll('text').attr('fill', txtC).attr('font-size', '11px');
        a.selectAll('line').attr('stroke', axC);
      });

    /* dots + value labels */
    points.forEach(function (p) {
      var cx    = xSc(p.label);
      var cy    = ySc(p.val);
      var color = perfColor(p.val);

      /* drop line */
      g.append('line').attr('x1', cx).attr('y1', cy + 6).attr('x2', cx).attr('y2', d.h)
        .attr('stroke', color).attr('stroke-width', 1).attr('stroke-dasharray', '2,3').attr('opacity', 0.35);

      /* dot */
      g.append('circle').attr('cx', cx).attr('cy', cy).attr('r', 6)
        .attr('fill', color).attr('stroke', sfcC).attr('stroke-width', 2.5)
        .on('mouseover', function (evt) {
          tipShow(evt, '<strong>' + p.label + '</strong>: ' + p.val + 'ms');
          d3.select(this).attr('r', 8);
        })
        .on('mouseout', function () { d3.select(this).attr('r', 6); tipHide(); });

      /* value label above dot */
      g.append('text').attr('x', cx).attr('y', cy - 11)
        .attr('text-anchor', 'middle').attr('font-size', '10px')
        .attr('font-weight', '700').attr('fill', color)
        .text(p.val > 0 ? p.val + 'ms' : '—');
    });
  }

  /* ════════════════════════════════════════════════════════════
     Chart 6 — Queries-per-request histogram
     ════════════════════════════════════════════════════════════ */
  function renderQueryHist(el, queryHist) {
    d3.select(el).selectAll('*').remove();
    if (!queryHist || queryHist.length === 0) { emptyState(el, 'No data', 200); return; }

    /* colour by bucket index — green→red as query count rises */
    var bucketColors = [
      css('--silk-perf-very-good'),
      css('--silk-perf-good'),
      css('--silk-perf-ok'),
      css('--silk-perf-bad'),
      css('--silk-perf-very-bad'),
      css('--silk-perf-very-bad'),
    ];

    var m = { top: 20, right: 8, bottom: 52, left: 36 };
    var d = setupSvg(el, m, 200);
    var g = d3.select(el).append('g').attr('transform', 'translate(' + m.left + ',' + m.top + ')');

    var xSc = d3.scaleBand()
      .domain(queryHist.map(function (r) { return r.label; }))
      .range([0, d.w]).padding(0.22);
    var yMax = d3.max(queryHist, function (r) { return r.count; }) || 1;
    var ySc  = d3.scaleLinear().domain([0, yMax * 1.2]).range([d.h, 0]);

    var gridC = css('--silk-border');
    var axC   = css('--silk-border');
    var txtC  = css('--silk-text-secondary');

    g.append('g')
      .call(d3.axisLeft(ySc).ticks(4).tickSize(-d.w).tickFormat(''))
      .call(function (a) {
        a.select('.domain').remove();
        a.selectAll('line').attr('stroke', gridC).attr('stroke-dasharray', '3,3').attr('opacity', 0.5);
      });

    g.append('g')
      .call(d3.axisLeft(ySc).ticks(4).tickFormat(d3.format('d')))
      .call(function (a) {
        a.select('.domain').attr('stroke', axC);
        a.selectAll('text').attr('fill', txtC).attr('font-size', '11px');
        a.selectAll('line').attr('stroke', axC);
      });

    g.append('g').attr('transform', 'translate(0,' + d.h + ')')
      .call(d3.axisBottom(xSc).tickSize(0))
      .call(function (a) {
        a.select('.domain').attr('stroke', axC);
        a.selectAll('text').attr('fill', txtC).attr('font-size', '10px')
          .attr('transform', 'rotate(-35)').attr('text-anchor', 'end').attr('dy', '0.35em');
      });

    queryHist.forEach(function (row, i) {
      var color = bucketColors[Math.min(i, bucketColors.length - 1)];
      var barH  = d.h - ySc(row.count);

      var defs  = d3.select(el).append('defs');
      var gId   = 'qh-bar-' + el.id + '-' + i;
      var bg = defs.append('linearGradient').attr('id', gId)
        .attr('x1', '0%').attr('x2', '0%').attr('y1', '0%').attr('y2', '100%');
      bg.append('stop').attr('offset', '0%').attr('stop-color', color).attr('stop-opacity', '1');
      bg.append('stop').attr('offset', '100%').attr('stop-color', color).attr('stop-opacity', '0.5');

      g.append('rect')
        .attr('x', xSc(row.label)).attr('y', ySc(row.count))
        .attr('width', xSc.bandwidth()).attr('height', Math.max(barH, 0))
        .attr('fill', 'url(#' + gId + ')').attr('rx', 4)
        .on('mouseover', function (evt) {
          tipShow(evt, '<strong>' + row.label + ' queries</strong>: '
            + row.count + ' request' + (row.count !== 1 ? 's' : ''));
          d3.select(this).attr('opacity', 0.8);
        })
        .on('mouseout', function () { d3.select(this).attr('opacity', 1); tipHide(); });

      if (row.count > 0) {
        g.append('text')
          .attr('x', xSc(row.label) + xSc.bandwidth() / 2)
          .attr('y', ySc(row.count) - 4)
          .attr('text-anchor', 'middle').attr('font-size', '10px')
          .attr('fill', color).attr('font-weight', '600').text(row.count);
      }
    });
  }

  /* ════════════════════════════════════════════════════════════
     Master render — draw all charts
     ════════════════════════════════════════════════════════════ */
  function renderAll(chartData) {
    var get = function (id) { return document.getElementById(id); };
    renderActivity(get('silk-chart-activity'),       chartData.timeline    || []);
    renderStatusDonut(get('silk-chart-status'),       chartData.status      || {});
    renderMethods(get('silk-chart-methods'),          chartData.methods     || []);
    renderRTHist(get('silk-chart-rt-hist'),           chartData.rt_hist     || []);
    renderPercentile(get('silk-chart-request'),       chartData.request     || {});
    renderPercentile(get('silk-chart-query'),         chartData.sql         || {});
    renderQueryHist(get('silk-chart-query-hist'),     chartData.query_hist  || []);
  }

  /* ════════════════════════════════════════════════════════════
     Boot
     ════════════════════════════════════════════════════════════ */
  document.addEventListener('DOMContentLoaded', function () {
    if (window.lucide) lucide.createIcons();

    var dataEl = document.getElementById('silk-chart-data');
    if (!dataEl || !window.d3) return;

    var chartData;
    try { chartData = JSON.parse(dataEl.textContent); } catch (e) { return; }

    renderAll(chartData);

    document.addEventListener('silk-scheme-changed', function () { renderAll(chartData); });

    var rzTimer;
    window.addEventListener('resize', function () {
      clearTimeout(rzTimer);
      rzTimer = setTimeout(function () { renderAll(chartData); }, 150);
    });
  });
}());
