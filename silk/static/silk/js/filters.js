var filters = [];

///
/// Filter Types
///

function Filter(value, desc) {
    this.value = value;
    this.desc = desc;
}

function SecondsFilter(value) {
    Filter.call(this, value, '>' + value + ' seconds ago');
    this.name = 'SecondsFilter';
}
SecondsFilter.prototype = Object.create(Filter.prototype, {});

function BeforeDateFilter(value) {
    Filter.call(this, value, '<' + value);
    this.name = 'BeforeDateFilter';
}
BeforeDateFilter.prototype = Object.create(Filter.prototype, {});

function AfterDateFilter(value) {
    Filter.call(this, value, '>' + value);
    this.name = 'AfterDateFilter';
}
AfterDateFilter.prototype = Object.create(Filter.prototype, {});

function PathFilter(value) {
    Filter.call(this, value, 'Path == ' + value);
    this.name = 'PathFilter';
}
PathFilter.prototype = Object.create(Filter.prototype, {});

function ViewNameFilter(value) {
    Filter.call(this, value, 'View == ' + value);
    this.name = 'ViewNameFilter';
}
ViewNameFilter.prototype = Object.create(Filter.prototype, {});

function NameFilter(value) {
    Filter.call(this, value, 'Name == ' + value);
    this.name = 'NameFilter';
}
NameFilter.prototype = Object.create(Filter.prototype, {});

function FunctionNameFilter(value) {
    Filter.call(this, value, 'Function Name == ' + value);
    this.name = 'FunctionNameFilter';
}

FunctionNameFilter.prototype = Object.create(Filter.prototype, {});


function NumQueriesFilter(value) {
    Filter.call(this, value, '#queries >= ' + value);
    this.name = 'NumQueriesFilter';
}

NumQueriesFilter.prototype = Object.create(Filter.prototype, {});

function TimeSpentOnQueriesFilter(value) {
    Filter.call(this, value, 'DB Time >= ' + value);
    this.name = 'TimeSpentOnQueriesFilter';
}

TimeSpentOnQueriesFilter.prototype = Object.create(Filter.prototype, {});

function OverallTimeFilter(value) {
    Filter.call(this, value, 'Time >= ' + value);
    this.name = 'OverallTimeFilter';
}

OverallTimeFilter.prototype = Object.create(Filter.prototype, {});

///
/// Filter Operations
///

function filterExists(filterType) {
    for (var idx in filters) {
        var filter = filters[idx];
        if (filter instanceof filterType) return true;
    }
    return false;
}

function deleteFilter(button) {
    var tableRow = $(button).parent().parent();
    var find = $('#active-filter-section').find('.active-filter');
    console.log(find);
    var idx = find.index(tableRow);
    filters.splice(idx, 1);
    tableRow.remove();
    console.log(filters);
    configureDisabled();
}

function addSecondsFilter() {
    addFilter($('input[name="seconds"]'), SecondsFilter);
}

function addBeforeDateFilter() {
    addFilter($('input[name="before-date"]'), BeforeDateFilter);
}


function addAfterDateFilter() {
    addFilter($('input[name="after-date"]'), AfterDateFilter);
}

function addNameFilter() {
    addFilter($('select[name="name"]'), NameFilter);
}

function addFunctionNameFilter() {
    addFilter($('select[name="function-name"]'), FunctionNameFilter);
}

function addViewNameFilter() {
    addFilter($('select[name="view-name"]'), ViewNameFilter);
}

function addFilter(selector, filter) {
    if (!selector.attr('disabled')) {
        var val = selector.val();
        if (val.toString().trim()) {
            filters.push(new filter(val));
            renderFilters();
            selector.val(null);
        }
    }
}
function addPathFilter() {
    addFilter($('select[name="path"]'), PathFilter);
}

function addNumQueriesFilter() {
    addFilter($('input[name="num-queries"]'), NumQueriesFilter);
}

function addOverallTimeFilter() {
    addFilter($('input[name="overall-time"]'), OverallTimeFilter);
}

function addTimeSpentOnQueriesFilter() {
    addFilter($('input[name="time-spent-on-queries"]'), TimeSpentOnQueriesFilter);
}

///
/// Rendering
///

function clear() {
    $('#active-filter-section').find('.active-filter').remove();
}

function configureDisabledForDateTime() {
    var secondsFilterExists = filterExists(SecondsFilter);
    var beforeDateFilterExists = filterExists(BeforeDateFilter);
    var afterDateFilterExists = filterExists(AfterDateFilter);
    var $beforeDate = $('#before-date-filter');
    var $afterDate = $('#after-date-filter');
    var $seconds = $('#seconds-filter');
    var $beforeDateInput = $beforeDate.find('input[name="before-date"]');
    var $afterDateInput = $afterDate.find('input[name="after-date"]');
    var $secondsInput = $seconds.find('input[name="seconds"]');
    var beforeDateDisabled = secondsFilterExists || beforeDateFilterExists;
    var afterDateDisabled = secondsFilterExists || afterDateFilterExists;
    var secondsDisabled = secondsFilterExists || beforeDateFilterExists || afterDateFilterExists;
    $beforeDateInput.attr('disabled', beforeDateDisabled);
    $afterDateInput.attr('disabled', afterDateDisabled);
    $secondsInput.attr('disabled', secondsDisabled);
    if (beforeDateDisabled) {
        $beforeDate.find('.add-button').addClass('disabled');
    }
    else {
        $beforeDate.find('.add-button').removeClass('disabled');
    }
    if (afterDateDisabled) {
        $afterDate.find('.add-button').addClass('disabled');
    }
    else {
        $afterDate.find('.add-button').removeClass('disabled');
    }
    if (secondsDisabled) {
        $seconds.find('.add-button').addClass('disabled');
    }
    else {
        $seconds.find('.add-button').removeClass('disabled');
    }
}

function configureDisabledForView() {
    var viewFilterExists = filterExists(ViewNameFilter) || filterExists(PathFilter);
    $('select[name="path"]').attr('disabled', viewFilterExists);
    $('select[name="view-name"]').attr('disabled', viewFilterExists);
    var $addButtons = $('.view-filter .add-button');
    if (viewFilterExists) {
        $addButtons.addClass('disabled');
    }
    else {
        $addButtons.removeClass('disabled');
    }
}

function configureDisabledForNames() {
    var nameFilterExists = filterExists(NameFilter) || filterExists(FunctionNameFilter);
    $('select[name="name"]').attr('disabled', nameFilterExists);
    $('select[name="function-name"]').attr('disabled', nameFilterExists);
    var $addButtons = $('.name-filter .add-button');
    if (nameFilterExists) {
        $addButtons.addClass('disabled');
    }
    else {
        $addButtons.removeClass('disabled');
    }
}

function configureDisabledForDatabase() {
    _configureDisabled('input[name="num-queries"]', NumQueriesFilter, '#num-queries-filter');
    _configureDisabled('input[name="time-spent-on-queries"]', TimeSpentOnQueriesFilter, '#time-spent-on-queries-filter');
}


function _configureDisabled(inputSelector, filterClass, filterSelector) {
    var sel = $(inputSelector);
    var exists = filterExists(filterClass);
    var $addButtons = $(filterSelector).find('.add-button');
    sel.attr('disabled', exists);
    if (exists) {
        $addButtons.addClass('disabled');
    }
    else {
        $addButtons.removeClass('disabled');
    }
}

function configureDisabledForOverallTime() {
    _configureDisabled('input[name="overall-time"]', OverallTimeFilter, '#overall-time-filter');
}

function configureDisabled() {
    configureDisabledForDateTime();
    configureDisabledForView();
    configureDisabledForNames();
    configureDisabledForDatabase();
    configureDisabledForOverallTime();
    $('#no-active-filters').css('display', filters.length ? 'none' : 'block');
}

/**
 * Render HTML representations of filters
 * @private
 */
function _renderFilters() {
    clear();
    for (var idx in filters) {
        var filter = filters[idx];
        var $tr = $('<tr class="active-filter"></tr>');
        var $deleteTd = $('<td></td>');
        var $button = $('<button class="add-button delete-button" onclick="deleteFilter(this);">-</button>');
        var $typ = $('<input class="typ" form="filter-form2" type="hidden" value="' + filter.name + '" name="filter-' + idx + '-typ">');
        var $value = $('<input class="value" form="filter-form2" type="hidden" value="' + filter.value + '" name="filter-' + idx + '-value">');
        $deleteTd.append($typ);
        $deleteTd.append($value);
        $deleteTd.append($button);
        var $span = $('<span>' + filter.desc + '</span>');
        var $describeTd = $('<td></td>');
        $describeTd.append($span);
        $tr.append($deleteTd);
        $tr.append($describeTd);
        $('#active-filter-section').append($tr);
    }
}

function renderFilters() {
    _renderFilters();
    configureDisabled();
}

///
/// Initialisation
///

function _initFilters() {
    var $filters = $('#active-filter-section').find('.active-filter');
    $filters.each(function () {
        var filter = $(this);
        console.log(filter);
        var typ = $(filter).find('.typ').val();
        var value = $(filter).find('.value').val();
        var f = window[typ];
        if (f) {
            filters.push(new f(value));
        }
        else {
            console.error('Unknown profile "' + typ + '" when parsing ', filter);
        }
    });
}

/**
 * Entry point for filter initialisation.
 */
function initFilters() {
    _initFilters(filters);
    configureDisabled();
}