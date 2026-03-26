document.addEventListener('DOMContentLoaded', function() {
    var viewSelect = document.getElementById('view-select');
    var urlSelect = document.getElementById('url-select');
    if (viewSelect && urlSelect) {
        viewSelect.addEventListener('change', function() {
            urlSelect.selectedIndex = 0;
        });
    }
});