function initFilterButton() {
    $('#filter-button').click(function () {
        $(this).toggleClass('active');
        $('body').toggleClass('cbp-spmenu-push-toleft');
        $('#cbp-spmenu-s2').toggleClass('cbp-spmenu-open');
        initFilters();
    });
}
function submitFilters() {
    $('#filter-form2').submit();
}
function submitEmptyFilters() {
    $('#cbp-spmenu-s2 :input:not([type=hidden])').val('');
    submitFilters();
}
