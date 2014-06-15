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
    var $input = $('input[name="seconds"]');
    if (!$input.attr('disabled')) {
        var seconds = $input.val();
        filters.push(new SecondsFilter(seconds));
        $input.val('');
        renderFilters();
    }
}

function addBeforeDateFilter() {
    var $input = $('input[name="before-date"]');
    if (!$input.attr('disabled')) {
        filters.push(new BeforeDateFilter($input.val()));
        $input.val('');
        renderFilters();
    }
}


function addAfterDateFilter() {
    var $input = $('input[name="after-date"]');
    if (!$input.attr('disabled')) {
        filters.push(new AfterDateFilter($input.val()));
        $input.val('');
        renderFilters();
    }
}

function addNameFilter() {
    var $input = $('select[name="name"]');
    if (!$input.attr('disabled')) {
        filters.push(new NameFilter($input.val()));
        renderFilters();
    }
}

function addFunctionNameFilter() {
    var $input = $('select[name="function-name"]');
    if (!$input.attr('disabled')) {
        filters.push(new FunctionNameFilter($input.val()));
        renderFilters();
    }
}

function addViewNameFilter() {
    var $input = $('select[name="view-name"]');
    if (!$input.attr('disabled')) {
        filters.push(new ViewNameFilter($input.val()));
        renderFilters();
    }
}

function addPathFilter() {
    var $input = $('select[name="path"]');
    if (!$input.attr('disabled')) {
        filters.push(new PathFilter($input.val()));
        renderFilters();
    }
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

/**
 * This should be overridden in the views that implement filtering.
 */
function configureDisabled() {
    configureDisabledForDateTime();
    configureDisabledForView();
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