/**
 * Get the view name filter param dictionary for use in generating uri query parameters.
 * @param viewName
 */
function viewNameFilter(viewName) {
  return {
    'viewName': viewName
  }
}

/**
 * Get the revision filter param dictionary for use in generating uri query parameters.
 * @param revision The revision to filter by.
 */
function revisionFilter(revision) {
  return {
    'revision': revision
  }
}

/**
 * Get the date filter param dictionary for use in generating uri query parameters.
 * @param date The date to filter by.
 */
function dateFilter(date) {
  date = new Date(date);
  return {
    'afterDate': strftime('%Y/%m/%d 00:00', date),
    'beforeDate': strftime('%Y/%m/%d 23:59', date)
  }
}

/**
 * Get the group-by parameter dictionary for use in generating uri query parameters.
 * @param group The attribute which should be used for grouping distribution charts.
 * @returns {{group-by: *}}
 */
function groupBy(group) {
  return {'group-by': group}
}

// mapping of filter by parameters to function for generating filter query parameters
var filterFunctions = {
  'view_name': viewNameFilter,
  'date': dateFilter,
  'revision': revisionFilter
};

/**
 * Make URI parameters from a dictionary.
 * @param obj dictionary to convert to parameters.
 * @returns {string}
 */
function makeURIParameters(obj) {
  var str = [];
  for (var p in obj) {
    if (obj.hasOwnProperty(p)) {
      str.push(encodeURIComponent(p) + "=" + encodeURIComponent(obj[p]));
    }
  }
  return str.join("&");
}

/**
 * Initialise the distribution chart.
 * @param distributionUrl
 */
function initChart(distributionUrl) {

  var inputURIParams = $.url('?');
  var groupByParam = inputURIParams === undefined ? 'date' : inputURIParams.group_by || 'date';
  var level = inputURIParams === undefined ? 0 : parseInt(inputURIParams.level) || 0;
  var locationWithoutQuery = location.href.split("?")[0];
  var filterParams = {};
  var filterName = '';
  var filterParamValue = '';

  // parse the input uri parameters to get the filter to apply
  for (var paramName in inputURIParams) {
    if (paramName in filterFunctions) {
      filterName = paramName;
      var filter = filterFunctions[paramName];
      filterParamValue = inputURIParams[paramName];
      filterValue = filter(filterParamValue);
      filterParams = Object.assign(filterParams, filterValue);
    }
  }

  // generate the chart title
  var viewTitleValue = 'all';
  var groupTitleValue = 'all';
  var groupTitle = groupByParam;
  if (level === 1) {
    groupTitle = filterName;
    groupTitleValue = filterParamValue;
  } else if (level === 2) {
    viewTitleValue = filterParamValue;
  }
  var title = 'view: <i>' + viewTitleValue + '</i> | ' +
    groupTitle + ': <i>' + groupTitleValue + '</i>'
  ;
  $('#title').html(title);

  var groupParams = groupBy(groupByParam);
  var outputURIParams = makeURIParameters(Object.assign(filterParams, groupParams));
  var url = [distributionUrl, outputURIParams].join("?");

  d3.csv(url, function (error, data) {

    var maxValue = 0;

    data.forEach(function (d) {
      d.value = +d.value;
      if (d.value > maxValue) {
        maxValue = d.value;
      }
    });

    var chart = makeDistroChart({
      data: data,
      xName: 'group',
      yName: 'value',
      axisLabels: {xAxis: null, yAxis: 'Time Taken (ms)'},
      selector: "#chart-distro1",
      chartSize: {height: window.innerHeight - 110, width: window.innerWidth},
      constrainExtremes: false,
      margin: {top: 20, right: 20, bottom: 80, left: 60}

    });

    for (const groupName in chart.groupObjs) {
      const groupObj = chart.groupObjs[groupName];
      groupObj.g
        .on('mouseover.opacity', function () {
          groupObj.g.transition().duration(300).attr('opacity', 0.5).style('cursor', 'pointer');
        })
        .on('mouseout.opacity', function () {
          groupObj.g.transition().duration(300).attr('opacity', 1).style('cursor', 'default');
          return false;
        })
        .on('click.opacity', function () {
          var outputLinkParams = Object.assign({}, inputURIParams);
          outputLinkParams[groupByParam] = groupName;
          if (level === 0) {
            outputLinkParams['group_by'] = 'view_name';
            outputLinkParams['level'] = 1;
            window.location = [locationWithoutQuery, makeURIParameters(outputLinkParams)].join('?');
          }
          else if (level === 1) {
            outputLinkParams['group_by'] = filterName;
            outputLinkParams['level'] = 2;
            delete outputLinkParams[filterName];
            window.location = [locationWithoutQuery, makeURIParameters(outputLinkParams)].join('?');
          }
          else {
            // go to normal silk view
            outputLinkParams = {
                viewName: filterParamValue
            };
            if (groupParams['group-by'] === 'date') {
              outputLinkParams['afterDate'] = strftime('%Y/%m/%d 00:00', new Date(groupName));
              outputLinkParams['beforeDate'] = strftime('%Y/%m/%d 23:59', new Date(groupName));
            }
            else if (groupParams['group-by'] === 'revision') {
              outputLinkParams['revision'] = groupName;
            }
            //console.log('/silk/requests')
            window.location = ['/silk/requests', makeURIParameters(outputLinkParams)].join('?');
          }
        })
      ;
    }

    chart.renderBoxPlot();
    //chart.renderDataPlots();
    //chart.renderNotchBoxes({showNotchBox: false});
    //chart.renderViolinPlot({showViolinPlot: true});

    var minQuartile3 = Number.MAX_VALUE;
    var maxQuartile3 = 0;
    Object.keys(chart.groupObjs).forEach(function(key, index) {
        minQuartile3 = Math.min(minQuartile3, chart.groupObjs[key].metrics.quartile3);
        maxQuartile3 = Math.max(maxQuartile3, chart.groupObjs[key].metrics.quartile3);
    });

    var colors = [
      '#b4c400',
      '#c29800',
      '#bf5c00',
      '#bd0000',
      '#b80015'
    ];
    var scale = d3.scale.quantize().domain([minQuartile3, maxQuartile3]).range(colors);

    if (minQuartile3 === maxQuartile3) {
      function getColor(cName) { return colors[0]; }
    } else {
      function getColor(cName) { return scale(chart.groupObjs[cName].metrics.quartile3); }
    }

    // trend lines (only show when group is revision or date)
    if (level !== 1) {
      chart.dataPlots.change({showLines: ['quartile3']});
    }
  });
}
