$(document).ready(function () {
    initFilters();
    var $inputs = $('.resizing-input');
    $inputs.focusout(function () {
        $('#filter-form').submit();
    });
});
