/**
 * Get the view name filter param dictionary for use in generating uri query parameters.
 * @param viewName
 * @returns {{filter-viewname-typ: [string], filter-viewname-value: [*]}}
 */
function viewNameFilter(viewName) {
    return {
        'filter-viewname-typ': ['ViewNameFilter'],
        'filter-viewname-value': [viewName]
    }
}

/**
 * Get the revision filter param dictionary for use in generating uri query parameters.
 * @param revision The revision to filter by.
 * @returns {{filter-revision-typ: [string], filter-revision-value: [*]}}
 */
function revisionFilter(revision) {
    return {
        'filter-revision-typ': ['RevisionFilter'],
        'filter-revision-value': [revision]
    }
}

/**
 * Get the date filter param dictionary for use in generating uri query parameters.
 * @param date The date to filter by.
 * @returns {{
 *      filter-afterdate-typ: [string],
 *      filter-afterdate-value: [*],
 *      filter-beforedate-typ: [string],
 *      filter-beforedate-value: [*]
 * }}
 */
function dateFilter(date) {
    date = new Date(date);
    var after = strftime('%Y/%m/%d 00:00', date);
    var before = strftime('%Y/%m/%d 23:59', date);
    return {
        'filter-afterdate-typ': ['AfterDateFilter'],
        'filter-afterdate-value': [after],
        'filter-beforedate-typ': ['BeforeDateFilter'],
        'filter-beforedate-value': [before]
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
 * Get the color that should be used for a plot mapping a value to the range 0..maxValue
 * @param value the value to get the color for.
 * @param maxValue the max color of the range to map
 * @returns {string}
 */
function getColor(value, maxValue) {
    var colors = [
        '#b4c400',
        '#c29800',
        '#bf5c00',
        '#bd0000',
        '#b80015'
    ];
    var index = Math.floor((value / maxValue) * colors.length);
    index = Math.max(0, Math.min(index, colors.length - 1));
    return colors[index];
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
                    if (level == 0) {
                        outputLinkParams['group_by'] = 'view_name';
                        outputLinkParams['level'] = 1;
                        window.location = [locationWithoutQuery, makeURIParameters(outputLinkParams)].join('?');
                    }
                    else if (level == 1) {
                        outputLinkParams['group_by'] = filterName;
                        outputLinkParams['level'] = 2;
                        delete outputLinkParams[filterName];
                        window.location = [locationWithoutQuery, makeURIParameters(outputLinkParams)].join('?');
                    }
                })
            ;
        }

        chart.renderBoxPlot();
        chart.boxPlots.show({
            reset: true,
            showWhiskers: true,
            showOutliers: true,
            boxWidth: 10,
            lineWidth: 1,
            colors: function (cName) {
                return getColor(chart.groupObjs[cName].metrics.quartile3, maxValue);
            }
        });

        // chart.renderViolinPlot();
        // chart.violinPlots.show({
        //     reset: true,
        //     clamp: 0,
        //     colors: function (cName) {
        //         return getColor(chart.groupObjs[cName].metrics.quartile3, maxValue);
        //     }
        // });
    });
}