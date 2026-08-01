function initFilterButton() {
    $('#filter-button').click(function () {
        $(this).toggleClass('active');
        $('body').toggleClass('cbp-spmenu-push-toleft');
        $('#cbp-spmenu-s2').toggleClass('cbp-spmenu-open');
        initFilters();
    });
}
